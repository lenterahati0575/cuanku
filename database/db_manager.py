import sqlite3
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="idx_screener.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _connect(self):
        """Koneksi ke database"""
        return sqlite3.connect(self.db_path)
    
    def _init_tables(self):
        """Inisialisasi tabel-tabel database"""
        with self._connect() as conn:
            # Tabel price_data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    date DATE NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    UNIQUE(ticker, date)
                )
            """)
            
            # Tabel indicators
            conn.execute("""
                CREATE TABLE IF NOT EXISTS indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    date DATE NOT NULL,
                    rsi_14 REAL,
                    macd REAL,
                    macd_signal REAL,
                    macd_hist REAL,
                    ema_20 REAL,
                    ema_50 REAL,
                    sma_200 REAL,
                    bb_upper REAL,
                    bb_lower REAL,
                    adx_14 REAL,
                    atr_14 REAL,
                    stochastic_k REAL,
                    stochastic_d REAL,
                    cci_20 REAL,
                    williams_r REAL,
                    roc REAL,
                    momentum REAL,
                    vwap REAL,
                    UNIQUE(ticker, date)
                )
            """)
            
            # Tabel scores
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    date DATE NOT NULL,
                    composite_score REAL,
                    signals TEXT,
                    sector TEXT,
                    UNIQUE(ticker, date)
                )
            """)
            
            # Tabel watchlist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    notes TEXT,
                    target_price REAL,
                    added_date DATE DEFAULT CURRENT_DATE
                )
            """)
            
            # Tabel portfolio
            conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    name TEXT,
                    sector TEXT,
                    shares INTEGER,
                    avg_price REAL,
                    last_updated DATE DEFAULT CURRENT_DATE
                )
            """)
            
            # Tabel journal
            conn.execute("""
                CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    ticker TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER,
                    price REAL,
                    setup TEXT,
                    emotion TEXT,
                    review TEXT,
                    pnl REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabel alerts
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    condition_type TEXT NOT NULL,
                    target_value REAL,
                    triggered INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP
                )
            """)
            
            # Tabel fundamentals
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fundamentals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    pe_ratio REAL,
                    pb_ratio REAL,
                    roe REAL,
                    debt_to_equity REAL,
                    current_ratio REAL,
                    dividend_yield REAL,
                    eps REAL,
                    book_value REAL,
                    market_cap REAL,
                    revenue REAL,
                    net_income REAL,
                    updated_at DATE DEFAULT CURRENT_DATE,
                    UNIQUE(ticker)
                )
            """)
            
            # Tabel backtests
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backtests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    start_date DATE,
                    end_date DATE,
                    total_return REAL,
                    cagr REAL,
                    max_drawdown REAL,
                    win_rate REAL,
                    total_trades INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabel stocks (untuk discovery)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL UNIQUE,
                    name TEXT,
                    sector TEXT,
                    subsector TEXT,
                    listed_date DATE,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            conn.commit()
    
    def save_prices(self, df, ticker):
        """Simpan data harga"""
        with self._connect() as conn:
            for _, row in df.iterrows():
                conn.execute("""
                    INSERT OR REPLACE INTO price_data 
                    (ticker, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ticker, row['date'], row['open'], row['high'], 
                      row['low'], row['close'], row.get('volume', 0)))
    
    def get_prices(self, ticker, limit=500):
        """Ambil data harga"""
        with self._connect() as conn:
            return pd.read_sql_query("""
                SELECT * FROM price_data 
                WHERE ticker = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, conn, params=(ticker, limit))
    
    def get_all_latest_prices(self):
        """Ambil harga terbaru semua saham"""
        with self._connect() as conn:
            return pd.read_sql_query("""
                SELECT ticker, MAX(date) as date, close 
                FROM price_data 
                GROUP BY ticker
            """, conn)
    
    def save_indicators(self, df, ticker):
        """Simpan data indikator"""
        with self._connect() as conn:
            for _, row in df.iterrows():
                conn.execute("""
                    INSERT OR REPLACE INTO indicators 
                    (ticker, date, rsi_14, macd, macd_signal, macd_hist, 
                     ema_20, ema_50, sma_200, bb_upper, bb_lower, 
                     adx_14, atr_14, stochastic_k, stochastic_d, 
                     cci_20, williams_r, roc, momentum, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ticker, row.get('date'), row.get('rsi_14'), row.get('macd'),
                      row.get('macd_signal'), row.get('macd_hist'), row.get('ema_20'),
                      row.get('ema_50'), row.get('sma_200'), row.get('bb_upper'),
                      row.get('bb_lower'), row.get('adx_14'), row.get('atr_14'),
                      row.get('stochastic_k'), row.get('stochastic_d'),
                      row.get('cci_20'), row.get('williams_r'), row.get('roc'),
                      row.get('momentum'), row.get('vwap')))
    
    def get_indicators(self, ticker, limit=100):
        """Ambil data indikator"""
        with self._connect() as conn:
            return pd.read_sql_query("""
                SELECT * FROM indicators 
                WHERE ticker = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, conn, params=(ticker, limit))
    
    def save_score(self, ticker, date, composite_score, signals, sector=None):
        """Simpan score"""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO scores 
                (ticker, date, composite_score, signals, sector)
                VALUES (?, ?, ?, ?, ?)
            """, (ticker, date, composite_score, signals, sector))
    
    def get_latest_scores(self, min_score=0, sector=None, limit=100):
        """Ambil score terbaru"""
        with self._connect() as conn:
            query = """
                SELECT * FROM scores 
                WHERE composite_score >= ?
            """
            params = [min_score]
            
            if sector:
                query += " AND sector = ?"
                params.append(sector)
            
            query += " ORDER BY composite_score DESC LIMIT ?"
            params.append(limit)
            
            return pd.read_sql_query(query, conn, params=params)
    
    def add_watchlist(self, ticker, notes=None, target_price=None):
        """Tambah ke watchlist"""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO watchlist (ticker, notes, target_price)
                VALUES (?, ?, ?)
            """, (ticker, notes, target_price))
    
    def get_watchlist(self):
        """Ambil watchlist"""
        with self._connect() as conn:
            return pd.read_sql_query("""
                SELECT * FROM watchlist ORDER BY added_date DESC
            """, conn)
    
    def get_fundamentals(self):
        """Ambil data fundamental"""
        with self._connect() as conn:
            return pd.read_sql_query("""
                SELECT * FROM fundamentals
            """, conn)
    
    def save_fundamental(self, ticker, data):
        """Simpan data fundamental"""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO fundamentals 
                (ticker, pe_ratio, pb_ratio, roe, debt_to_equity, 
                 current_ratio, dividend_yield, eps, book_value, 
                 market_cap, revenue, net_income, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, data.get('pe_ratio'), data.get('pb_ratio'), 
                  data.get('roe'), data.get('debt_to_equity'),
                  data.get('current_ratio'), data.get('dividend_yield'),
                  data.get('eps'), data.get('book_value'),
                  data.get('market_cap'), data.get('revenue'),
                  data.get('net_income'), datetime.now().date()))
    
    def get_backtests(self):
        """Ambil history backtest"""
        with self._connect() as conn:
            return pd.read_sql_query("""
                SELECT * FROM backtests ORDER BY created_at DESC
            """, conn)
    
    def save_backtest(self, ticker, strategy, result):
        """Simpan hasil backtest"""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO backtests 
                (ticker, strategy, start_date, end_date, total_return, 
                 cagr, max_drawdown, win_rate, total_trades)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, strategy, result.get('start_date'), 
                  result.get('end_date'), result.get('total_return'),
                  result.get('cagr'), result.get('max_drawdown'),
                  result.get('win_rate'), result.get('total_trades')))
