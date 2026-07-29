-- Tabel price_data
CREATE TABLE IF NOT EXISTS price_data (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL, high REAL, low REAL, close REAL, volume BIGINT,
    UNIQUE(ticker, date)
);

-- Tabel indicators
CREATE TABLE IF NOT EXISTS indicators (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    rsi_14 REAL, macd REAL, macd_signal REAL, macd_hist REAL,
    ema_20 REAL, ema_50 REAL, sma_200 REAL,
    bb_upper REAL, bb_lower REAL, adx_14 REAL, atr_14 REAL,
    stochastic_k REAL, stochastic_d REAL, cci_20 REAL,
    williams_r REAL, roc REAL, momentum REAL, vwap REAL,
    UNIQUE(ticker, date)
);

-- Tabel scores
CREATE TABLE IF NOT EXISTS scores (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    composite_score REAL,
    signals TEXT,
    sector TEXT,
    UNIQUE(ticker, date)
);

-- Tabel watchlist
CREATE TABLE IF NOT EXISTS watchlist (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    notes TEXT,
    target_price REAL,
    added_date DATE DEFAULT CURRENT_DATE
);

-- Tabel portfolio
CREATE TABLE IF NOT EXISTS portfolio (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    name TEXT,
    sector TEXT,
    shares INTEGER,
    avg_price REAL,
    last_updated DATE DEFAULT CURRENT_DATE
);

-- Tabel journal
CREATE TABLE IF NOT EXISTS journal (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    ticker TEXT NOT NULL,
    action TEXT NOT NULL,
    quantity INTEGER,
    price REAL,
    setup TEXT,
    emotion TEXT,
    review TEXT,
    pnl REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabel alerts
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    condition_type TEXT NOT NULL,
    target_value REAL,
    triggered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    triggered_at TIMESTAMP WITH TIME ZONE
);

-- Tabel fundamentals
CREATE TABLE IF NOT EXISTS fundamentals (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    pe_ratio REAL, pb_ratio REAL, roe REAL, debt_to_equity REAL,
    current_ratio REAL, dividend_yield REAL, eps REAL,
    book_value REAL, market_cap REAL, revenue REAL, net_income REAL,
    updated_at DATE DEFAULT CURRENT_DATE
);

-- Tabel backtests
CREATE TABLE IF NOT EXISTS backtests (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    strategy TEXT NOT NULL,
    start_date DATE, end_date DATE,
    total_return REAL, cagr REAL, max_drawdown REAL,
    win_rate REAL, total_trades INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabel stocks
CREATE TABLE IF NOT EXISTS stocks (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    name TEXT, sector TEXT, subsector TEXT,
    listed_date DATE, is_active BOOLEAN DEFAULT TRUE
);
