import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date
import json

# --- FUNGSI TEMA (Pengganti config.theme yang hilang) ---
def apply_theme():
    """Menerapkan styling CSS kustom ke aplikasi."""
    st.markdown("""
    <style>
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }
        div[data-testid="stMetric"] {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 10px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

def theme_toggle():
    """Menambahkan opsi toggle tema di sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.caption(" Tip: Untuk mengubah tema (Light/Dark), edit file di `.streamlit/config.toml`")
# --------------------------------------------------------

@st.cache_resource
def get_db():
    from database.db_manager import DatabaseManager
    return DatabaseManager()

@st.cache_data(ttl=3600, show_spinner=False)
def cached_prices(ticker, limit=500):
    return db.get_prices(ticker, limit)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_indicators(ticker, limit=100):
    return db.get_indicators(ticker, limit)

@st.cache_data(ttl=600, show_spinner=False)
def cached_scores(min_score=0, sector=None, limit=100):
    return db.get_latest_scores(min_score, sector, limit)

@st.cache_data(ttl=600, show_spinner=False)
def run_screening_cached():
    scorer.rank_all(db)
    return db.get_latest_scores(min_score=0, limit=200)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_fundamentals_all():
    return db.get_fundamentals()

@st.cache_data(ttl=3600, show_spinner=False)
def cached_ticker_list():
    with db._connect() as conn:
        return pd.read_sql_query("SELECT DISTINCT ticker FROM price_data", conn)["ticker"].tolist()

@st.cache_data(ttl=3600, show_spinner=False)
def cached_backtests():
    return db.get_backtests()

db = get_db()

from data.yf_downloader import YFDownloader
from indicators.engine import IndicatorEngine
from screener.scorer import CompositeScorer
from portfolio.tracker import PortfolioTracker
from journal.manager import JournalManager
from alerts.monitor import AlertMonitor
from utils.exporter import ExcelExporter
from ai.summarizer import AISummarizer
from reports.pdf_generator import ReportGenerator
from data.ticker_discovery import TickerDiscovery
from fundamentals.fetcher import FundamentalFetcher
from timeframes.engine import MultiTimeframeEngine
from backtest.engine import BacktestEngine
from alerts.scheduler import AlertScheduler
from alerts.notifier import StreamlitNotifier

downloader = YFDownloader(db)
scorer = CompositeScorer()
portfolio = PortfolioTracker(db)
journal = JournalManager(db)
alerts = AlertMonitor(db)
exporter = ExcelExporter(db)

# Terapkan tema
apply_theme()

st.set_page_config(page_title="IDX Screener Pro", layout="wide", page_icon="📊")

st.sidebar.title("📊 IDX Screener Pro")
menu = st.sidebar.radio("Menu", [
    " Screener", "⭐ Watchlist", "💼 Portfolio", "📓 Journal", "🔔 Alerts",
    "🤖 AI Summary", "📄 PDF Report", "📊 Fundamentals", "⏳ Multi-Timeframe",
    "📈 Backtest", "🌐 Discovery", "⚙️ Data Manager", "📤 Export"
])

# Toggle tema di sidebar
theme_toggle()

if menu == "🔍 Screener":
    st.title("🔍 Stock Screener")
    c1, c2, c3 = st.columns(3)
    with c1: min_score = st.slider("Min Composite Score", 0, 100, 60)
    with c2: sector = st.selectbox("Sektor", ["All", "Banking", "Mining", "Consumer", "Telco", "Technology", "Energy"])
    with c3: top_n = st.number_input("Top N", 10, 200, 25)
    
    if st.button("🔄 Run Screening & Ranking", type="primary"):
        with st.spinner("Menghitung..."):
            run_screening_cached.clear()
            df_screen = run_screening_cached()
            st.success("Selesai!")
    else:
        sector_filter = None if sector == "All" else sector
        df_screen = cached_scores(min_score=min_score, sector=sector_filter, limit=top_n)
        
    if not df_screen.empty:
        st.metric("Saham memenuhi kriteria", len(df_screen))
        st.dataframe(df_screen, use_container_width=True, hide_index=True)
        top = df_screen.iloc[0]
        st.subheader(f"📈 {top['ticker']} | Score: {top['composite_score']} | {top['signals']}")
        df_price = cached_prices(top["ticker"], limit=120)
        if not df_price.empty:
            fig = go.Figure(data=[go.Candlestick(x=df_price["date"], open=df_price["open"], high=df_price["high"], low=df_price["low"], close=df_price["close"])])
            fig.add_trace(go.Scatter(x=df_price["date"], y=df_price["close"].ewm(span=20).mean(), mode="lines", name="EMA20", line=dict(color="orange", width=1)))
            fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data score. Klik Run Screening atau download data di menu Data Manager.")

elif menu == "⭐ Watchlist":
    st.title("⭐ Watchlist")
    with st.expander(" Tambah ke Watchlist"):
        c1, c2, c3 = st.columns(3)
        with c1: wl_ticker = st.text_input("Ticker", "BBRI.JK").upper().strip()
        with c2: wl_target = st.number_input("Target Price", min_value=0, value=0, step=50)
        with c3: wl_notes = st.text_input("Notes", "Breakout soon")
        if st.button("Tambah", type="primary"):
            db.add_watchlist(wl_ticker, wl_notes, wl_target if wl_target > 0 else None)
            st.success(f"{wl_ticker} ditambahkan!")
            
    wl = db.get_watchlist()
    if not wl.empty:
        prices = db.get_all_latest_prices()[["ticker", "close"]]
        wl = wl.merge(prices, on="ticker", how="left")
        wl["gap_to_target"] = wl.apply(lambda r: f"{((r['target_price']-r['close'])/r['close']*100):.1f}%" if pd.notna(r.get("target_price")) and r.get("close") else "-", axis=1)
        st.dataframe(wl[["ticker", "notes", "target_price", "close", "gap_to_target", "added_date"]], use_container_width=True, hide_index=True)
        to_remove = st.selectbox("Hapus dari watchlist", wl["ticker"].tolist())
        if st.button("️ Hapus", type="secondary"):
            with db._connect() as conn:
                conn.execute("DELETE FROM watchlist WHERE ticker=?", (to_remove,))
                conn.commit()
            st.rerun()
    else:
        st.info("Watchlist kosong.")

elif menu == "💼 Portfolio":
    st.title("💼 Portfolio Tracker")
    summary = portfolio.get_summary()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Value", f"Rp {summary['total_value']:,.0f}")
    c2.metric("Unrealized P/L", f"Rp {summary['unrealized']:,.0f}", f"{(summary['unrealized']/summary['total_cost']*100 if summary['total_cost'] else 0):.1f}%")
    c3.metric("Realized P/L", f"Rp {summary['realized']:,.0f}")
    c4.metric("Win Rate", f"{summary['win_rate']:.0f}%")
    c5.metric("Positions", summary["positions"])
    
    tab_buy, tab_sell = st.tabs(["🟢 Beli", "🔴 Jual"])
    with tab_buy:
        c1, c2, c3 = st.columns(3)
        with c1: p_ticker = st.text_input("Ticker", "BBRI.JK", key="buy_t").upper().strip()
        with c2: p_shares = st.number_input("Jumlah Lot", min_value=1, value=1, key="buy_l")
        with c3: p_price = st.number_input("Harga per Saham", min_value=1, value=4500, step=10, key="buy_p")
        if st.button("Execute BUY", type="primary"):
            portfolio.buy(p_ticker, p_shares*100, p_price)
            st.success(f"Beli {p_shares} lot {p_ticker} @ {p_price}")
            
    with tab_sell:
        df_pos = portfolio.get_df()
        if not df_pos.empty:
            c1, c2, c3 = st.columns(3)
            with c1: s_ticker = st.selectbox("Ticker", df_pos["ticker"].tolist(), key="sell_t")
            with c2:
                max_lot = int(df_pos[df_pos["ticker"]==s_ticker]["shares"].values[0]/100)
                s_shares = st.number_input("Jumlah Lot", min_value=1, max_value=max_lot, value=1, key="sell_l")
            with c3: s_price = st.number_input("Harga Jual", min_value=1, value=4500, step=10, key="sell_p")
            if st.button("Execute SELL", type="primary"):
                ok, msg = portfolio.sell(s_ticker, s_shares*100, s_price)
                if ok: st.success(f"Jual {s_shares} lot {s_ticker}. {msg}")
                else: st.error(msg)
        else:
            st.info("Tidak ada posisi untuk dijual.")
            
    st.subheader("Holdings")
    df_pos = portfolio.get_df()
    if not df_pos.empty:
        st.dataframe(df_pos[["ticker", "name", "sector", "shares", "avg_price", "current_price", "unrealized_pl", "market_value"]], use_container_width=True, hide_index=True)
    else:
        st.info("Portfolio kosong.")

elif menu == "📓 Journal":
    st.title("📓 Trading Journal")
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
            journal.add(j_date.strftime("%Y-%m-%d"), j_ticker, j_action, j_qty*100, j_price, j_setup, j_emotion, j_review, j_pnl if j_action=="SELL" else None)
            st.success("Journal tersimpan!")
            
    stats = journal.stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", int(stats["trades"]))
    c2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
    c3.metric("Avg P/L", f"Rp {stats['avg_pnl']:,.0f}")
    c4.metric("Best Trade", f"Rp {stats['best']:,.0f}")
    
    df_j = journal.get_df()
    if not df_j.empty:
        st.dataframe(df_j, use_container_width=True, hide_index=True)
        del_id = st.number_input("Hapus ID", min_value=1, step=1)
        if st.button("🗑️ Hapus Entry"):
            journal.delete(del_id)
            st.rerun()
    else:
        st.info("Belum ada journal.")

elif menu == "🔔 Alerts":
    st.title("🔔 Alert Scheduler & Monitor")
    scheduler = AlertScheduler(interval_minutes=15)
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("▶️ Start Auto-Check", type="primary", disabled=scheduler.is_running()):
            ok, msg = scheduler.start()
            if ok: st.success(msg)
            else: st.warning(msg)
    with c2:
        if st.button("⏹️ Stop Auto-Check", type="secondary", disabled=not scheduler.is_running()):
            ok, msg = scheduler.stop()
            if ok: st.error(msg)
            else: st.warning(msg)
    with c3:
        status = scheduler.status()
        StreamlitNotifier.show_scheduler_status(status["running"], status["interval_minutes"])
        last_triggered = scheduler.get_last_triggered()
        if last_triggered:
            StreamlitNotifier.show_triggered(last_triggered)
            scheduler._last_triggered = []
            
    st.divider()
    if st.button("🔍 Check Alerts Sekarang", type="secondary"):
        with st.spinner("Mengecek..."):
            triggered = alerts.check_all()
            if triggered: StreamlitNotifier.show_triggered(triggered)
            else: st.info("Tidak ada alert yang ter-trigger.")
            
    st.divider()
    with st.expander("➕ Buat Alert Baru"):
        c1, c2, c3 = st.columns(3)
        with c1: a_ticker = st.text_input("Ticker", "BBCA.JK").upper().strip()
        with c2: a_type = st.selectbox("Kondisi", ["PRICE_ABOVE", "PRICE_BELOW", "RSI_ABOVE", "RSI_BELOW", "MACD_BULLISH"])
        with c3: a_target = st.number_input("Target Value", value=8500, step=100)
        if st.button("Simpan Alert", type="primary"):
            alerts.add(a_ticker, a_type, a_target)
            st.success(f"Alert {a_ticker} tersimpan!")
            
    st.subheader(" Active Alerts")
    df_al = alerts.get_active()
    if not df_al.empty:
        st.dataframe(df_al, use_container_width=True, hide_index=True)
        del_a = st.number_input("Hapus Alert ID", min_value=1, step=1)
        if st.button("🗑️ Hapus Alert"):
            alerts.delete(del_a)
            st.rerun()
    else:
        st.info("Tidak ada alert aktif.")
        
    st.subheader("📜 Triggered History")
    with db._connect() as conn:
        df_hist = pd.read_sql_query("SELECT * FROM alerts WHERE triggered=1 ORDER BY created_at DESC LIMIT 20", conn)
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada alert yang pernah ter-trigger.")

elif menu == "🤖 AI Summary":
    st.title("🤖 AI Technical Analysis")
    ai = AISummarizer(db)
    st.subheader("📊 Market Overview")
    overview = ai.market_overview(top_n=50)
    if overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Market Mood", overview["market_mood"])
        c2.metric("Bullish", overview["bullish_count"])
        c3.metric("Bearish", overview["bearish_count"])
        c4.metric("Top Sector", overview["top_sector"])
        with st.expander("📈 Sector Performance"):
            sec_df = pd.DataFrame([{"Sector":k, "Avg Score":round(v,1)} for k,v in overview["sector_avg"].items()]).sort_values("Avg Score", ascending=False)
            st.dataframe(sec_df, use_container_width=True, hide_index=True)
    else:
        st.info("Jalankan screening dulu.")
        
    st.divider()
    st.subheader("🔍 Analisis Per Saham")
    with db._connect() as conn:
        all_tickers = pd.read_sql_query("SELECT DISTINCT ticker FROM indicators ORDER BY ticker", conn)["ticker"].tolist()
    if not all_tickers:
        st.warning("Belum ada data indikator.")
    else:
        selected = st.selectbox("Pilih Ticker", all_tickers)
        if selected:
            with st.spinner("Menganalisis..."):
                analysis = ai.analyze_ticker(selected)
                if analysis:
                    col1, col2 = st.columns([1,2])
                    with col1:
                        st.metric("Harga", f"Rp {analysis['price']:,.0f}")
                        st.metric("AI Score", analysis["score"])
                        color = {"green": "normal", "red": "inverse", "orange": "off"}.get(analysis["color"], "off")
                        st.metric("Verdict", analysis["verdict"].split()[0], delta_color=color)
                    with col2:
                        st.write("Sinyal Teknikal:")
                        for sig in analysis["signals"]:
                            st.write(f"• {sig}")
                        kl = analysis["key_levels"]
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Support", f"Rp {kl['support']:,.0f}")
                        c2.metric("Resistance", f"Rp {kl['resistance']:,.0f}")
                        c3.metric("VWAP", f"Rp {kl['vwap']:,.0f}")
                    if ai.use_llm:
                        with st.spinner("Generating AI narrative..."):
                            narrative = ai.llm_summary(selected)
                            if narrative and not narrative.startswith("["):
                                st.info(f"📝 AI Narrative:\n\n{narrative}")
                            else:
                                st.caption("💡 Tambahkan OPENAI_API_KEY untuk narasi AI.")
                    df_p = cached_prices(selected, limit=60)
                    if not df_p.empty:
                        fig = go.Figure(data=[go.Candlestick(x=df_p["date"], open=df_p["open"], high=df_p["high"], low=df_p["low"], close=df_p["close"])])
                        fig.update_layout(height=350, template="plotly_dark", xaxis_rangeslider_visible=False, title=f"{selected} — Last 60 Days")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Data tidak cukup.")
                    
    st.divider()
    if st.button("🚀 Generate AI Report untuk Top 20", type="primary"):
        with st.spinner("Menganalisis 20 saham..."):
            reports = ai.generate_full_report(limit=20)
            for r in reports:
                with st.container(border=True):
                    st.write(f"{r['ticker']} — {r['verdict']} (Score: {r['score']})")
                    st.caption(" | ".join(r['signals'][:3]) + "...")

elif menu == "📄 PDF Report":
    st.title("📄 PDF Report Generator")
    report = ReportGenerator(db)
    c1, c2 = st.columns(2)
    with c1:
        report_tickers = st.text_area("Tickers khusus (kosongkan = semua)", " ")
        tickers_list = [t.strip().upper() for t in report_tickers.split(",") if t.strip()] or None
    with c2:
        filename = st.text_input("Nama File", f"IDX_Report_{datetime.now().strftime('%Y%m%d')}.pdf")
    if st.button("📑 Generate PDF Report", type="primary"):
        with st.spinner("Membuat laporan..."):
            try:
                path = report.generate(tickers=tickers_list, output_path=f"/mnt/agents/output/{filename}")
                st.success("Report berhasil dibuat!")
                with open(path, "rb") as f:
                    st.download_button(label="⬇️ Download PDF Report", data=f, file_name=filename, mime="application/pdf")
            except Exception as e:
                st.error(f"Gagal generate PDF: {e}")
    st.info("💡 Report mencakup: Market Overview, Analisis 25 saham, Portfolio Summary, Disclaimer.")

elif menu == "📊 Fundamentals":
    st.title("📊 Fundamental Analysis")
    ff = FundamentalFetcher(db)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Fetch Fundamentals (Batch)", type="primary"):
            with db._connect() as conn:
                tickers = pd.read_sql_query("SELECT DISTINCT ticker FROM price_data", conn)["ticker"].tolist()
            if tickers:
                bar = st.progress(0)
                for i, t in enumerate(tickers[:50]):
                    ff.fetch(t)
                    bar.progress((i+1)/min(len(tickers),50))
                st.success("Fundamental data diperbarui!")
            else:
                st.error("Download price data dulu.")
    with c2:
        f_ticker = st.text_input("Cek Ticker", "BBRI.JK").upper().strip()
        if st.button(" Analisis Fundamental"):
            score = ff.get_fundamental_score(f_ticker)
            if score["label"] != "N/A":
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Fundamental Score", score["score"])
                    st.metric("Kategori", score["label"])
                with col2:
                    st.write("Breakdown:")
                    for k, v in score["details"].items():
                        st.progress(int(v), text=f"{k.upper()}: {v}")
                raw = score["raw"]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("PE Ratio", f"{raw.get('pe_ratio','N/A')}")
                c2.metric("PBV", f"{raw.get('pb_ratio','N/A')}")
                c3.metric("ROE", f"{raw.get('roe','N/A')}")
                c4.metric("Div Yield", f"{raw.get('dividend_yield',0):.2f}%")
            else:
                st.warning("Data fundamental tidak tersedia.")
                
    st.divider()
    st.subheader("📋 Fundamental Screener")
    df_f = ff.db.get_fundamentals()
    if not df_f.empty:
        df_scores = cached_scores(min_score=0, limit=200)
        if not df_scores.empty:
            merged = df_f.merge(df_scores[["ticker", "composite_score"]], on="ticker", how="left")
            merged["fund_score"] = merged["ticker"].apply(lambda x: ff.get_fundamental_score(x)["score"])
            merged["total_score"] = (merged["composite_score"].fillna(50)*0.6 + merged["fund_score"]*0.4).round(1)
            st.dataframe(merged.sort_values("total_score", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_f, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data fundamental.")

elif menu == "⏳ Multi-Timeframe":
    st.title("⏳ Multi-Timeframe Analysis")
    tf_ticker = st.text_input("Ticker", "BBRI.JK").upper().strip()
    if st.button("🔍 Analyze All Timeframes", type="primary"):
        with st.spinner("Menghitung Daily, Weekly, Monthly..."):
            result = MultiTimeframeEngine.analyze_all_tfs(db, tf_ticker)
            if result:
                st.subheader(f"{result['ticker']} — Alignment: {result['alignment']}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Daily Score", result["scores"]["daily"])
                c2.metric("Weekly Score", result["scores"]["weekly"])
                c3.metric("Monthly Score", result["scores"]["monthly"])
                c4.metric("Alignment", result["alignment_score"])
                colors = {"daily": "#3b82f6", "weekly": "#10b981", "monthly": "#f59e0b"}
                for tf, score in result["scores"].items():
                    st.progress(int(score), text=f"{tf.upper()}: {score} — {'Bullish' if score >= 60 else 'Bearish' if score <= 40 else 'Neutral'}")
                if result["alignment_score"] >= 80: st.success("🟢 Semua timeframe align BULLISH — sinyal kuat!")
                elif result["alignment_score"] <= 25: st.error("🔴 Semua timeframe align BEARISH — hati-hati!")
                else: st.warning("🟡 Timeframe mixed — tunggu konfirmasi.")
                with st.expander(" Detail Indikator per Timeframe"):
                    for tf in ["daily", "weekly", "monthly"]:
                        d = result["details"].get(tf, {})
                        if d: st.write(f"{tf.upper()} — EMA20: {d.get('ema_20',0):.0f}, RSI: {d.get('rsi_14',0):.1f}, MACD Hist: {d.get('macd_hist',0):.2f}, ADX: {d.get('adx_14',0):.1f}")
            else:
                st.error("Data tidak cukup. Pastikan punya data daily minimal 1 tahun.")
                
    st.divider()
    st.subheader("📊 Batch Multi-TF Ranking")
    if st.button("🚀 Rank All Stocks by Timeframe Alignment", type="secondary"):
        with db._connect() as conn:
            tickers = pd.read_sql_query("SELECT DISTINCT ticker FROM price_data", conn)["ticker"].tolist()
        results = []
        bar = st.progress(0)
        for i, t in enumerate(tickers[:30]):
            try:
                r = MultiTimeframeEngine.analyze_all_tfs(db, t)
                if r: results.append({"ticker":t, "daily":r["scores"]["daily"], "weekly":r["scores"]["weekly"], "monthly":r["scores"]["monthly"], "alignment":r["alignment"], "align_score":r["alignment_score"]})
            except: pass
            bar.progress((i+1)/min(len(tickers),30))
        if results:
            df_tf = pd.DataFrame(results).sort_values("align_score", ascending=False)
            st.dataframe(df_tf, use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada data.")

elif menu == "📈 Backtest":
    st.title("📈 Strategy Backtest")
    bt = BacktestEngine(db)
    c1, c2, c3 = st.columns(3)
    with c1:
        bt_ticker = st.text_input("Ticker", "BBRI.JK").upper().strip()
        bt_strategy = st.selectbox("Strategi", ["composite_score", "ema_cross", "rsi_reversal"])
    with c2:
        bt_entry = st.slider("Entry Score Threshold", 50, 90, 70)
        bt_exit = st.slider("Exit Score Threshold", 20, 60, 50)
    with c3:
        bt_sl = st.number_input("Stop Loss %", 1.0, 20.0, 7.0)
        bt_tp = st.number_input("Take Profit %", 5.0, 50.0, 15.0)
        bt_hold = st.number_input("Max Holding Days", 5, 90, 30)
        
    if st.button(" Run Backtest", type="primary"):
        with st.spinner("Simulasi trading historis..."):
            result = bt.run(bt_ticker, strategy=bt_strategy, entry_threshold=bt_entry, exit_threshold=bt_exit, stop_loss_pct=bt_sl, take_profit_pct=bt_tp, max_holding_days=bt_hold)
            if result and result["trades"] > 0:
                st.success(f"Backtest selesai: {result['trades']} trades")
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Total Return", f"{result['total_return']:.1f}%")
                m2.metric("CAGR", f"{result['cagr']:.1f}%")
                m3.metric("Max Drawdown", f"{result['max_drawdown']:.1f}%")
                m4.metric("Win Rate", f"{result['win_rate']:.1f}%")
                m5.metric("Avg Return/Trade", f"{result['avg_return_per_trade']:.2f}%")
                eq_df = pd.DataFrame(result["equity_curve"])
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=eq_df["date"], y=eq_df["equity"], mode="lines", name="Equity", line=dict(color="#10b981")))
                fig.update_layout(title="Equity Curve", template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Trade History")
                st.dataframe(pd.DataFrame(result["trade_list"]), use_container_width=True, hide_index=True)
            else:
                st.warning("Tidak ada trade yang tereksekusi. Coba ubah parameter.")
                
    st.divider()
    st.subheader("📜 Backtest History")
    df_bt = cached_backtests()
    if not df_bt.empty:
        st.dataframe(df_bt, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada backtest yang tersimpan.")

elif menu == " Discovery":
    st.title("🌐 IDX Ticker Discovery")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌐 Fetch dari Wikipedia", type="primary"):
            with st.spinner("Mengambil daftar saham dari Wikipedia..."):
                df_wiki = TickerDiscovery.fetch_from_wikipedia()
                if not df_wiki.empty:
                    st.success(f"Ditemukan {len(df_wiki)} saham di Wikipedia!")
                    st.dataframe(df_wiki, use_container_width=True, hide_index=True)
                    if st.button("💾 Simpan ke Database", key="save_wiki"):
                        count = TickerDiscovery.save_to_db(db)
                        st.success(f"{count} ticker tersimpan!")
                else:
                    st.error("Gagal fetch dari Wikipedia.")
    with c2:
        if st.button("📋 Gunakan Static Extended List (~300 liquid)", type="secondary"):
            static = TickerDiscovery.fetch_static_extended()
            st.success(f"Static list: {len(static)} ticker")
            st.write(static[:50])
            st.caption(f"... dan {len(static)-50} lainnya")
            if st.button("💾 Simpan Static ke Database", key="save_static"):
                count = TickerDiscovery.save_to_db(db)
                st.success(f"{count} ticker tersimpan!")
                
    st.divider()
    st.subheader("📊 Database Stocks")
    with db._connect() as conn:
        db_stocks = pd.read_sql_query("SELECT * FROM stocks ORDER BY ticker", conn)
    st.metric("Total Ticker di DB", len(db_stocks))
    st.dataframe(db_stocks, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("⬇️ Batch Download Semua Ticker di DB")
    if st.button("🚀 Download Semua (Incremental)", type="primary"):
        tickers = db_stocks["ticker"].tolist()
        if not tickers:
            st.error("Database kosong. Lakukan discovery dulu.")
        else:
            bar = st.progress(0)
            status = st.empty()
            success, failed = 0, 0
            for i, t in enumerate(tickers):
                try:
                    status.text(f"Downloading {t}... ({i+1}/{len(tickers)})")
                    df = downloader.download(t)
                    if df is not None and not df.empty:
                        df_ind = IndicatorEngine.calculate_all(df)
                        db.save_indicators(df_ind, t)
                        success += 1
                    else: failed += 1
                except: failed += 1
                bar.progress((i+1)/len(tickers))
            status.empty()
            st.success(f"Selesai! Success: {success}, Failed: {failed}")
            
    if st.button(" Run Screening untuk Semua", type="secondary"):
        with st.spinner("Menghitung score..."):
            scorer.rank_all(db)
            st.success("Ranking selesai!")

elif menu == "⚙️ Data Manager":
    st.title("⚙️ Data Manager")
    tickers_input = st.text_area("Tickers (pisah koma)", "BBRI.JK, BBCA.JK, TLKM.JK, ANTM.JK, ASII.JK")
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬇️ Download / Update Data", type="primary"):
            cached_prices.clear(); cached_indicators.clear(); cached_scores.clear(); run_screening_cached.clear()
            bar = st.progress(0)
            for i, t in enumerate(tickers):
                try:
                    df = downloader.download(t)
                    if df is not None and not df.empty:
                        df_ind = IndicatorEngine.calculate_all(df)
                        db.save_indicators(df_ind, t)
                except Exception as e:
                    st.error(f"{t}: {e}")
                bar.progress((i+1)/len(tickers))
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
    df_p = cached_prices(preview_ticker, limit=10)
    st.dataframe(df_p, use_container_width=True)

elif menu == "📤 Export":
    st.title("📤 Export Data")
    c1, c2 = st.columns(2)
    with c1: exp_score = st.slider("Min Score (Screener)", 0, 100, 50)
    with c2: exp_sector = st.selectbox("Sektor (Screener)", ["All", "Banking", "Mining", "Consumer", "Telco", "Technology", "Energy"])
    sec = None if exp_sector == "All" else exp_sector
    if st.button("📥 Download Excel (All Sheets)", type="primary"):
        xlsx = exporter.export_all(min_score=exp_score, sector=sec)
        st.download_button(label="Klik untuk Download", data=xlsx, file_name=f"IDX_Screener_Pro_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
