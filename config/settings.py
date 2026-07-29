# Konfigurasi default untuk Cuanku

# Daftar ticker default untuk screening
DEFAULT_TICKERS = [
    "BBRI.JK", "BBCA.JK", "TLKM.JK", "ASII.JK", "BMRI.JK",
    "UNVR.JK", "BBNI.JK", "INDF.JK", "GGRM.JK", "ICBP.JK",
    "KLBF.JK", "PTBA.JK", "ADRO.JK", "ANTM.JK", "INCO.JK",
    "SMGR.JK", "UNTR.JK", "MDKA.JK", "AMMN.JK", "MDKA.JK"
]

# Sektor saham
SECTORS = {
    "BBRI.JK": "Banking", "BBCA.JK": "Banking", "BMRI.JK": "Banking", "BBNI.JK": "Banking",
    "TLKM.JK": "Telco", "ISAT.JK": "Telco", "EXCL.JK": "Telco",
    "ASII.JK": "Consumer", "UNVR.JK": "Consumer", "INDF.JK": "Consumer",
    "ICBP.JK": "Consumer", "KLBF.JK": "Consumer", "GGRM.JK": "Consumer",
    "ANTM.JK": "Mining", "PTBA.JK": "Mining", "ADRO.JK": "Mining",
    "INCO.JK": "Mining", "MDKA.JK": "Mining", "AMMN.JK": "Mining",
    "SMGR.JK": "Infrastructure", "UNTR.JK": "Mining",
}

# Bobot scoring untuk composite score
SCORING_WEIGHTS = {
    "rsi_score": 0.15,
    "macd_score": 0.20,
    "ema_score": 0.20,
    "bb_score": 0.15,
    "adx_score": 0.15,
    "volume_score": 0.15
}

# Parameter indikator
INDICATOR_PARAMS = {
    "rsi_period": 14,
    "ema_fast": 20,
    "ema_slow": 50,
    "sma_long": 200,
    "bb_period": 20,
    "bb_std": 2,
    "adx_period": 14,
    "atr_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9
}
