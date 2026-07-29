import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    """Inisialisasi koneksi Supabase menggunakan secrets"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = get_supabase_client()
        self.db_path = "supabase"  # Dummy untuk kompatibilitas
    
    def _connect(self):
        """Dummy method agar kode with db._connect() tidak error"""
        class MockConn:
            def __enter__(self): 
                return self
            def __exit__(self, *args): 
                pass
            def execute(self, *args): 
                raise NotImplementedError("Gunakan method bawaan class ini")
        return MockConn()

    def get_prices(self, ticker: str, limit: int = 500) -> pd.DataFrame:
        """Ambil data harga untuk ticker tertentu"""
        try:
            # Query tanpa .order() - kita sort manual di Python
            response = self.supabase.table("price_data") \
                .select("*") \
                .eq("ticker", ticker) \
                .execute()
            
            if not response.data:
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            
            # Sort descending by date dan limit
            if not df.empty and 'date' in df.columns:
                df = df.sort_values("date", ascending=False).head(limit)
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching prices for {ticker}: {str(e)}")
            return pd.DataFrame()

    def get_all_latest_prices(self) -> pd.DataFrame:
        """Ambil harga terbaru semua saham"""
        try:
            # Query sederhana tanpa .order() yang bermasalah
            response = self.supabase.table("price_data") \
                .select("ticker, date, close") \
                .execute()
            
            if not response.data:
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            
            # Sort dan ambil yang terbaru per ticker di Python
            if not df.empty and 'date' in df.columns:
                df = df.sort_values("date", ascending=False)
                df = df.drop_duplicates(subset=["ticker"], keep="first")
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching latest prices: {str(e)}")
            return pd.DataFrame()

    def get_indicators(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        """Ambil data indikator untuk ticker tertentu"""
        try:
            response = self.supabase.table("indicators") \
                .select("*") \
                .eq("ticker", ticker) \
                .execute()
            
            if not response.data:
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            
            # Sort descending by date dan limit
            if not df.empty and 'date' in df.columns:
                df = df.sort_values("date", ascending=False).head(limit)
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching indicators for {ticker}: {str(e)}")
            return pd.DataFrame()

    def get_latest_scores(self, min_score: float = 0, sector: str = None, limit: int = 100) -> pd.DataFrame:
        """Ambil score terbaru dengan filtering"""
        try:
            # Build query dasar
            query = self.supabase.table("scores").select("*")
            
            # Filter min_score
            if min_score > 0:
                query = query.gte("composite_score", min_score)
            
            # Filter sector
            if sector and sector != "All":
                query = query.eq("sector", sector)
            
            # Execute query TANPA .order() - sort manual di Python
            response = query.execute()
            
            # Check jika data kosong
            if not response.data:
                return pd.DataFrame()
            
            # Convert ke DataFrame
            df = pd.DataFrame(response.data)
            
            # Sort descending by composite_score dan limit
            if not df.empty and 'composite_score' in df.columns:
                df = df.sort_values("composite_score", ascending=False).head(limit)
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching scores: {str(e)}")
            return pd.DataFrame()

    def add_watchlist(self, ticker: str, notes: str = None, target_price: float = None):
        """Tambah ke watchlist"""
        try:
            self.supabase.table("watchlist").insert({
                "ticker": ticker,
                "notes": notes,
                "target_price": target_price
            }).execute()
        except Exception as e:
            st.error(f"Error adding watchlist: {str(e)}")

    def get_watchlist(self) -> pd.DataFrame:
        """Ambil watchlist"""
        try:
           
