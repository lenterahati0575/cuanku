import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
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
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, *args): raise NotImplementedError("Gunakan method bawaan class ini")
        return MockConn()

    def get_prices(self, ticker: str, limit: int = 500) -> pd.DataFrame:
        response = self.supabase.table("price_data").select("*").eq("ticker", ticker).order("date", desc=True).limit(limit).execute()
        return pd.DataFrame(response.data)

    def get_all_latest_prices(self) -> pd.DataFrame:
        response = self.supabase.table("price_data").select("ticker, date, close").order("date", desc=True).execute()
        df = pd.DataFrame(response.data)
        return df.drop_duplicates(subset=["ticker"], keep="first") if not df.empty else df

    def get_indicators(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        response = self.supabase.table("indicators").select("*").eq("ticker", ticker).order("date", desc=True).limit(limit).execute()
        return pd.DataFrame(response.data)

    def get_latest_scores(self, min_score: float = 0, sector: str = None, limit: int = 100) -> pd.DataFrame:
        query = self.supabase.table("scores").select("*").gte("composite_score", min_score)
        if sector:
            query = query.eq("sector", sector)
        response = query.order("composite_score", desc=True).limit(limit).execute()
        return pd.DataFrame(response.data)

    def add_watchlist(self, ticker: str, notes: str = None, target_price: float = None):
        self.supabase.table("watchlist").insert({"ticker": ticker, "notes": notes, "target_price": target_price}).execute()

    def get_watchlist(self) -> pd.DataFrame:
        response = self.supabase.table("watchlist").select("*").order("added_date", desc=True).execute()
        return pd.DataFrame(response.data)

    def delete_watchlist(self, ticker: str):
        self.supabase.table("watchlist").delete().eq("ticker", ticker).execute()

    def get_fundamentals(self) -> pd.DataFrame:
        response = self.supabase.table("fundamentals").select("*").execute()
        return pd.DataFrame(response.data)

    def get_backtests(self) -> pd.DataFrame:
        response = self.supabase.table("backtests").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(response.data)

    def save_indicators(self, df: pd.DataFrame, ticker: str):
        records = df.to_dict(orient="records")
        for row in records:
            row["ticker"] = ticker
        if records:
            self.supabase.table("indicators").upsert(records, on_conflict="ticker,date").execute()
