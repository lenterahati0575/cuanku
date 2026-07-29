import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

class YFDownloader:
    def __init__(self, db):
        self.db = db
    
    def download(self, ticker: str, period: str = "2y") -> pd.DataFrame:
        """Download data harga dari Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return None
            
            # Reset index dan rename kolom
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Hapus kolom yang tidak perlu
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            # Konversi tipe data
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(int)
            
            # Simpan ke database
            self.db.save_prices(df, ticker)
            
            return df
            
        except Exception as e:
            st.error(f"Error downloading {ticker}: {e}")
            return None
    
    def download_multiple(self, tickers: list, period: str = "2y") -> dict:
        """Download multiple tickers"""
        results = {}
        for ticker in tickers:
            df = self.download(ticker, period)
            if df is not None:
                results[ticker] = df
        return results
