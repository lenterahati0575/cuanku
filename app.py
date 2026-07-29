import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date
from database.db_manager import DatabaseManager
from data.yf_downloader import YFDownloader
from indicators.engine import IndicatorEngine
from screener.scorer import CompositeScorer
from portfolio.tracker import PortfolioTracker
from journal.manager import JournalManager
from alerts.monitor import AlertMonitor
from utils.exporter import ExcelExporter

st.set_page_config(page_title="Cuanku", layout="wide", page_icon="📊")

# ── Init ──
db = DatabaseManager()
downloader = YFDownloader(db)
scorer = CompositeScorer()
portfolio = PortfolioTracker(db)
journal = JournalManager(db)
alerts = AlertMonitor(db)
exporter = ExcelExporter(db)

st.sidebar.title("📊 Cuanku")
menu = st.sidebar.radio("Menu", [
    "🔍 Screener", "⭐ Watchlist", "💼 Portfolio",
    "📓 Journal", "🔔 Alerts", "⚙️ Data Manager", "📤 Export"
])

# ═══════════════════════════════════════════════════════
# 1. SCREENER
# ═══════════════════════════════════════════════════════
if menu == "🔍 Screener":
    st.title("🔍 Stock Screener")
    c1, c2, c3 = st.columns(3)
    with c1:
        min_score = st.slider("Min Composite Score", 0, 100, 60)
    with c2:
        sector = st.selectbox("Sektor", ["All", "Banking", "Mining", "Consumer", "Telco", "Technology", "Energy"])
    with c3:
        top_n = st.number_input("Top N", 10, 200, 25)
    
    if st.button("🔄 Run Screening & Ranking", type="primary"):
        with st.spinner("Menghitung indikator & composite score untuk semua saham..."):
            scorer.rank_all(db)
        st.success("Screening selesai!")
    
    sector_filter = None if sector == "All" else sector
    df_screen = db.get_latest_scores(min_score=min_score, sector=sector_filter, limit=top_n)
    
    if not df_screen.empty:
        st.metric("Saham memenuhi kriteria", len(df_screen))
        st.dataframe(df_screen, use_container_width=True, hide_index=True)
        
        # Chart top pick
        top = df_screen.iloc[0]
        st.subheader(f"📈 {top['ticker']} | Score: {top['composite_score']} | {top['signals']}")
        df_price = db.get_prices(top["ticker"], limit=120)
        
        if not df_price.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=df_price["date"],
                open=df_price["open"], high=df_price["high"],
                low=df_price["low"], close=df_price["close"],
                name="Candlestick"
            )])
            
            # Add EMA20
            fig.add_trace(go.Scatter(
                x=df_price["date"], 
                y=df_price["close"].ewm(span=20).mean(),
                mode="lines", 
                name="EMA20", 
                line=dict(color="orange", width=1)
            ))
            
            fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data score. Klik **Run Screening** atau download data di menu Data Manager.")

# ═══════════════════════════════════════════════════════
# 2. WATCHLIST
# ═══════════════════════════════════════════════════════
elif menu == "⭐ Watchlist":
    st.title("⭐ Watchlist")
    
    with st.expander("➕ Tambah ke Watchlist"):
        col1, col2, col3 = st.columns(3)
        with col1:
            wl_ticker = st.text_input("Ticker", "BBRI.JK").upper().strip()
        with col2:
            wl_target = st.number_input("Target Price", min_value=0, value=0, step=50)
        with col3:
            wl_notes = st.text_input("Notes", "Breakout soon")
        
        if st.button("Tambah", type="primary"):
            db.add_watchlist(wl_ticker, wl_notes, wl_target if wl_target > 0 else None)
            st.success(f"{wl_ticker} ditambahkan!")
    
    wl = db.get_watchlist()
    
    if not wl.empty and "ticker" in wl.columns:
        prices = db.get_all_latest_prices()
        
        if not prices.empty and "ticker" in prices.columns and "close" in prices.columns:
            wl = wl.merge(prices[["ticker", "close"]], on="ticker", how="left")
            wl["gap_to_target"] = wl.apply(
                lambda r: f"{((r['target_price'] - r['close'])/r['close']*100):.1f}%" 
                if pd.notna(r.get("target_price")) and pd.notna(r.get("close")) and r['close'] != 0 
                else "-", 
                axis=1
            )
            
            cols_to_show = ["ticker", "notes", "target_price", "close", "gap_to_target", "added_date"]
            cols_to_show = [c for c in cols_to_show if c in wl.columns]
            st.dataframe(wl[cols_to_show], use_container_width=True, hide_index=True)
        else:
            st.dataframe(wl, use_container_width=True, hide_index=True)
            st.info(" Belum ada data harga. Download data di menu Data Manager untuk melihat harga terbaru.")
        
        # Hapus
        to_remove = st.selectbox("Hapus dari watchlist", wl["ticker"].tolist())
        if st.button("🗑️ Hapus", type="secondary"):
            db.delete_watchlist(to_remove)
            st.rerun()
    else:
        st.info("Watchlist kosong. Tambahkan saham di atas.")

# ═══════════════════════════════════════════════════════
# 3. PORTFOLIO
# ═══════════════════════════════════════════════════════
elif menu == "💼 Portfolio":
    st.title("💼 Portfolio Tracker")
    
    # ── Summary Cards ──
    summary = portfolio.get_summary()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Value", f"Rp {summary['total_value']:,.0f}")
    c2.metric("Unrealized P/L", f"Rp {summary['unrealized']:,.0f}",
              f"{(summary['unrealized']/summary['total_cost']*100 if summary['total_cost'] else 0):.1f}%")
    c3.metric("Realized P/L", f"Rp {summary['realized']:,.0f}")
    c4.metric("Win Rate", f"{summary['win_rate']:.0f}%")
    c5.metric("Positions", summary["positions"])
    
    # ── Buy / Sell Form ──
    tab_buy, tab_sell = st.tabs(["🟢 Beli", " Jual"])
    
    with tab_buy:
        c1, c2, c3 = st.columns(3)
        with c1:
            p_ticker = st.text_input("Ticker", "BBRI.JK", key="buy_t").upper().strip()
        with c2:
            p_shares = st.number_input("Jumlah Lot", min_value=1, value=1, key="buy_l")
        with c3:
            p_price = st.number_input("Harga per Saham", min_value=1, value=4500, step=10, key="buy_p")
        
        if st.button("Execute BUY", type="primary"):
            portfolio.buy(p_ticker, p_shares * 100, p_price)  # 1 lot = 100 shares
            st.success(f"Beli {p_shares} lot {p_ticker} @ {p_price}")
    
    with tab_sell:
        df_pos = portfolio.get_df()
        if not df_pos.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                s_ticker = st.selectbox("Ticker", df_pos["ticker"].tolist(), key="sell_t")
            with c2:
                max_lot = int(df_pos[df_pos["ticker"] == s_ticker]["shares"].values[0] / 100)
                s_shares = st.number_input("Jumlah Lot", min_value=1, max_value=max_lot, value=1, key="sell_l")
            with c3:
                s_price = st.number_input("Harga Jual", min_value=1, value=4500, step=10, key="sell_p")
            
            if st.button("Execute SELL", type="primary"):
                ok, msg = portfolio.sell(s_ticker, s_shares * 100, s_price)
                if ok:
                    st.success(f"Jual {s_shares} lot {s_ticker}. {msg}")
                else:
                    st.error(msg)
        else:
            st.info("Tidak ada posisi untuk dijual.")
    
    # ── Holdings Table ──
    st.subheader("Holdings")
    df_pos = portfolio.get_df()
    
    if not df_pos.empty:
        st.dataframe(
            df_pos[["ticker", "name", "sector", "shares", "avg_price", "current_price",
                    "unrealized_pl", "market_value"]], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Portfolio kosong.")

# ═══════════════════════════════════════════════════════
# 4. TRADING JOURNAL
# ═══════════════════════════════════════════════════════
elif menu == "📓 Journal":
    st.title(" Trading Journal")
    
    with st.expander("➕ Entry Baru"):
        c1, c2, c3 = st.columns(3)
        with c1:
            j_date = st.date_input("Tanggal", date.today())
            j_ticker = st.text_input("Ticker", "BBRI.JK").upper().strip()
        with c2:
            j_action = st.selectbox("Aksi", ["BUY", "SELL"])
            j_qty = st.number_input("Quantity (lot)", min_value=1, value=1)
            j_price = st.number_input("Harga", min_value=1, value=4500, step=10)
        with c3:
            j_setup = st.text_input("Setup", "EMA Cross")
            j_emotion = st.selectbox("Emosi", ["Tenang", "FOMO", "Takut", "Serakah", "Biasa saja"])
            j_pnl = st.number_input("P/L (isi jika SELL)", value=0, step=100000)
        
        j_review = st.text_area("Review / Catatan", "Sesuai trading plan...")
        
        if st.button("Simpan Entry", type="primary"):
            journal.add(
                j_date.strftime("%Y-%m-%d"), j_ticker, j_action,
                j_qty * 100, j_price, j_setup, j_emotion, j_review,
                j_pnl if j_action == "SELL" else None
            )
            st.success("Journal tersimpan!")
    
    # Stats
    stats = journal.stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", int(stats["trades"]))
    c2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
    c3.metric("Avg P/L", f"Rp {stats['avg_pnl']:,.0f}")
    c4.metric("Best Trade", f"Rp {stats['best']:,.0f}")
    
    df_j = journal.get_df()
    
    if not df_j.empty:
        st.dataframe(df_j, use_container_width=True, hide_index=True)
        
        # Delete
        del_id = st.number_input("Hapus ID", min_value=1, step=1)
        if st.button("🗑️ Hapus Entry"):
            journal.delete(del_id)
            st.rerun()
    else:
        st.info("Belum ada journal.")

# ═══════════════════════════════════════════════════════
# 5. ALERTS
# ══════════════════════════════════════════════════════
elif menu == " Alerts":
    st.title("🔔 Price & Indicator Alerts")
    
    with st.expander("➕ Buat Alert Baru"):
        c1, c2, c3 = st.columns(3)
        with c1:
            a_ticker = st.text_input("Ticker", "BBCA.JK").upper().strip()
        with c2:
            a_type = st.selectbox("Kondisi", [
                "PRICE_ABOVE", "PRICE_BELOW", "RSI_ABOVE", "RSI_BELOW", "MACD_BULLISH"
            ])
        with c3:
            a_target = st.number_input("Target Value", value=8500, step=100)
        
        if st.button("Simpan Alert", type="primary"):
            alerts.add(a_ticker, a_type, a_target)
            st.success(f"Alert {a_ticker} tersimpan!")
    
    if st.button("🔍 Check Alerts Now", type="secondary"):
        triggered = alerts.check_all()
        if triggered:
            for t in triggered:
                st.success(f" {t['ticker']} — {t['condition']} terpenuhi! (Target: {t['target']}, Now: {t['price_now']})")
        else:
            st.info("Tidak ada alert yang ter-trigger saat ini.")
    
    df_al = alerts.get_active()
    
    if not df_al.empty:
        st.subheader("Active Alerts")
        st.dataframe(df_al, use_container_width=True, hide_index=True)
        
        del_a = st.number_input("Hapus Alert ID", min_value=1, step=1)
        if st.button("️ Hapus Alert"):
            alerts.delete(del_a)
            st.rerun()
    else:
        st.info("Tidak ada alert aktif.")

# ═══════════════════════════════════════════════════════
# 6. DATA MANAGER
# ═══════════════════════════════════════════════════════
elif menu == "️ Data Manager":
    st.title("️ Data Manager")
    
    tickers_input = st.text_area("Tickers (pisah koma)", "BBRI.JK, BBCA.JK, TLKM.JK, ANTM.JK, ASII.JK")
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("⬇️ Download / Update Data", type="primary"):
            bar = st.progress(0)
            for i, t in enumerate(tickers):
                try:
                    df = downloader.download(t)
                    if df is not None and not df.empty:
                        df_ind = IndicatorEngine.calculate_all(df)
                        db.save_indicators(df_ind, t)
                except Exception as e:
                    st.error(f"{t}: {e}")
                bar.progress((i + 1) / len(tickers))
            st.success("Download & indikator selesai!")
    
    with c2:
        if st.button(" Clear Database"):
            import os
            if os.path.exists(db.db_path):
                os.remove(db.db_path)
                st.success("Database dihapus. Refresh halaman.")
                st.stop()
    
    st.subheader("Data Preview")
    preview_ticker = st.selectbox("Lihat data", tickers)
    df_p = db.get_prices(preview_ticker, limit=10)
    st.dataframe(df_p, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 7. EXPORT
# ═══════════════════════════════════════════════════════
elif menu == "📤 Export":
    st.title(" Export Data")
    
    c1, c2 = st.columns(2)
    with c1:
        exp_score = st.slider("Min Score (Screener)", 0, 100, 50)
    with c2:
        exp_sector = st.selectbox("Sektor (Screener)", ["All", "Banking", "Mining", "Consumer", "Telco", "Technology", "Energy"])
    
    sec = None if exp_sector == "All" else exp_sector
    
    if st.button("📥 Download Excel (All Sheets)", type="primary"):
        xlsx = exporter.export_all(min_score=exp_score, sector=sec)
        st.download_button(
            label="Klik untuk Download",
            data=xlsx,
            file_name=f"IDX_Screener_Pro_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
