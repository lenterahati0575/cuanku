# Cuanku

Aplikasi screening saham Indonesia (IDX) — scan, ranking, watchlist, portfolio, journal, alert, dan export, dalam satu dashboard.

**Berjalan 100% di cloud** — tidak ada yang perlu diinstal di laptop. Cukup browser.

## Fitur

| Fitur | Status |
|---|---|
| Scan saham IDX (mulai ~55 saham likuid, bisa expand ke 900) | ✅ Siap pakai |
| Downloader Yahoo Finance dengan cache & update incremental | ✅ Siap pakai |
| Database Supabase (Postgres, permanen, tidak reset) | ✅ Siap pakai |
| Engine indikator: EMA, SMA, RSI, MACD, ATR, ADX, Bollinger, VWAP, OBV | ✅ Siap pakai |
| Composite Scoring Engine + Ranking otomatis | ✅ Siap pakai |
| Watchlist, Portfolio, Trading Journal | ✅ Siap pakai |
| Alert (cek manual) | ✅ Siap pakai |
| Export Excel (semua data) | ✅ Siap pakai |
| AI Summary, PDF Report, Discovery 900 saham | 🟡 Modul sudah ada, tab UI belum digabung — lihat `FITUR_LANJUTAN_BELUM_DIGABUNG.md` |
| Alert otomatis berjalan sendiri (scheduler) | 🟡 Belum digabung |
| Fundamentals, Multi-Timeframe, Backtest | 🟡 Belum digabung |
| Dark Mode | 🟡 Modul sudah ada, belum digabung |

## Setup — Semua Lewat Browser (Tidak Ada Instalasi)

Polanya sama persis seperti proyek Dashboard Packing Plant.

### Langkah 1 — Supabase (Database)

1. Buka https://supabase.com → Sign up → **New Project**
2. Kasih nama bebas (misal "cuanku"), catat Database Password
3. Tunggu ~2 menit sampai project selesai dibuat
4. Menu kiri → **SQL Editor** → **New query**
5. Buka file `sql/01_schema.sql` di folder ini, copy semua isinya, tempel ke SQL Editor → **Run**
6. **Project Settings** (ikon gerigi) → **API** → catat **Project URL** dan **anon public key**

### Langkah 2 — GitHub (Simpan Kode)

1. Buka https://github.com → buat repository baru (boleh **Private**)
2. Klik **uploading an existing file** → seret semua file & folder dari folder ini (termasuk `ai/`, `alerts/`, dst) → **Commit changes**

### Langkah 3 — Streamlit Community Cloud (Jalankan sebagai Web App)

1. Buka https://share.streamlit.io → Sign in pakai akun GitHub
2. **Create app** → pilih repository ini → **Main file path**: `app.py`
3. **Advanced settings** → **Secrets**, tempel:
   ```
   SUPABASE_URL = "https://xxxxx.supabase.co"
   SUPABASE_KEY = "eyJhbGc...(anon public key dari Langkah 1)"
   ```
4. Klik **Deploy** — tunggu beberapa menit

Selesai — Cuanku punya alamat sendiri (`https://nama-app.streamlit.app`), bisa dibuka dari browser mana saja, laptop mana saja.

## Setelah Deploy — Isi Data Pertama Kali

1. Buka aplikasinya, masuk ke menu **⚙️ Data Manager**
2. Klik **⬇️ Download / Update Data** — ini akan ambil data harga + hitung indikator untuk semua ticker di `config/settings.py`
3. Setelah selesai, menu **🔍 Screener** akan mulai menampilkan hasil

## Struktur Folder

```
├── app.py                    # Entry point
├── sql/
│   └── 01_schema.sql          # Skema database, jalankan di Langkah 1
├── config/
│   ├── settings.py             # Daftar ticker, sektor, bobot scoring
│   └── theme.py                 # Dark/Light mode (belum digabung ke app.py)
├── database/
│   └── db_manager.py             # Koneksi Supabase + semua fungsi save/get
├── data/
│   ├── yf_downloader.py           # Download harga dari Yahoo Finance
│   └── ticker_discovery.py        # Auto-fetch daftar 900 saham IDX (belum digabung)
├── indicators/engine.py            # Hitung EMA/RSI/MACD/dst
├── screener/scorer.py               # Composite scoring & ranking
├── portfolio/tracker.py              # Kelola portfolio
├── journal/manager.py                 # Trading journal
├── alerts/monitor.py                   # Cek kondisi alert
├── ai/summarizer.py                     # Analisis otomatis (rule-based + opsional OpenAI)
├── reports/pdf_generator.py              # Export laporan ke PDF (belum digabung ke app.py)
├── utils/exporter.py                      # Export ke Excel
├── requirements.txt
├── .gitignore
└── FITUR_LANJUTAN_BELUM_DIGABUNG.md        # Fitur yang belum digabung + cara lanjutkan
```

## Kalau Mau Fitur AI Summary (Opsional)

`ai/summarizer.py` punya 2 mode:
- **Rule-based** (default) — tidak perlu API key
- **LLM-enhanced** (opsional) — narasi lebih natural, perlu API key OpenAI

Untuk mode LLM: di Streamlit Cloud, tambahkan di **Secrets** yang sama (Langkah 3):
```
OPENAI_API_KEY = "sk-xxxxx"
```

## Melanjutkan Pengembangan

Lihat `FITUR_LANJUTAN_BELUM_DIGABUNG.md` untuk daftar fitur yang modulnya sudah ada tapi belum
disambungkan ke `app.py`. Disarankan tambah satu-per-satu lewat Claude Code (atau chat ini),
tes tiap selesai 1 fitur.
