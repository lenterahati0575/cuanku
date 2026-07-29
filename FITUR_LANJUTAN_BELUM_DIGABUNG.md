# Fitur Lanjutan yang Belum Digabung ke app.py

`app.py` di repo ini adalah **versi dasar yang lengkap dan berfungsi** (7 menu: Screener, Watchlist,
Portfolio, Journal, Alerts, Data Manager, Export). Ini sudah bisa langsung dipakai.

Percakapan asli berlanjut dengan beberapa putaran fitur TAMBAHAN setelah versi dasar ini, berupa
**patch/tambahan**, bukan penggantian total. Supaya tidak berisiko salah gabung otomatis, daftar di
bawah ini menunjukkan fitur apa saja yang ada, dan baris berapa di file transkrip asli
(`skrip_dasboad_saham.txt`) kalau mau ditambahkan manual satu-per-satu (lewat Claude Code, lebih aman
sambil dites tiap tahap).

## 1. Tab AI Summary, PDF Report, Discovery
- Modul pendukung SUDAH diekstrak bersih: `ai/summarizer.py`, `reports/pdf_generator.py`, `data/ticker_discovery.py`
- Bagian yang BELUM digabung: kode UI tab-nya di app.py
- Lokasi di transkrip asli: baris ~2930-3160

## 2. Alert Scheduler & Notifier (auto-check alert berjalan otomatis)
- Modul `alerts/scheduler.py` dan `alerts/notifier.py` — BELUM diekstrak
- Lokasi di transkrip asli: baris ~2078-2330

## 3. Fundamentals, Multi-Timeframe, Backtest (3 tab tambahan lagi)
- Modul baru yang disebut: `fundamentals/fetcher.py`, `timeframes/engine.py`, `backtest/engine.py` — BELUM diekstrak
- Lokasi di transkrip asli: baris ~3766-3997

## 4. Dark Mode (config/theme.py)
- Modul SUDAH diekstrak bersih: `config/theme.py`
- Bagian yang BELUM digabung: pemanggilan `apply_theme()` dan `theme_toggle()` di app.py
- Lokasi di transkrip asli: baris ~4045-4150

## 5. Caching Performance (@st.cache_data / @st.cache_resource)
- Ini optimasi kecepatan, bukan fitur baru — perlu ditambahkan `@st.cache_data` di atas fungsi-fungsi
  yang ambil data dari database/download
- Lokasi di transkrip asli: baris ~4149-4295, ~4343-4440

## 6. Deploy ke Cloud (Render/Streamlit Cloud)
- Ada catatan konfigurasi start command untuk deploy
- Lokasi di transkrip asli: baris ~4296

---

**Saran**: tambahkan fitur-fitur ini satu-per-satu lewat Claude Code (bukan sekaligus), tes tiap kali
selesai 1 fitur, supaya kalau ada yang error gampang dilacak sumbernya. File transkrip asli
(`skrip_dasboad_saham.txt`) tetap disimpan sebagai referensi kalau perlu lihat kode lengkapnya.
