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
    
    def save_prices(self, df: pd.DataFrame, ticker: str):
        records = df.to_dict(orient="records")
        for row in records:
            row["ticker"] = ticker
        self.supabase.table("price_data").upsert(records, on_conflict="ticker,date").execute()
    
    def get_prices(self, ticker: str, limit: int = 500) -> pd.DataFrame:
        response = self.supabase.table("price_data") \
            .select("*") \
            .eq("ticker", ticker) \
            .order("date", desc=True) \
            .limit(limit) \
            .execute()
        return pd.DataFrame(response.data)
    
    def get_all_latest_prices(self) -> pd.DataFrame:
        response = self.supabase.table("price_data") \
            .select("ticker, date, close") \
            .order("date", desc=True) \
            .execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            return df.drop_duplicates(subset=["ticker"], keep="first")
        return df
    
    def save_indicators(self, df: pd.DataFrame, ticker: str):
        records = df.to_dict(orient="records")
        for row in records:
            row["ticker"] = ticker
        self.supabase.table("indicators").upsert(records, on_conflict="ticker,date").execute()
    
    def get_indicators(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        response = self.supabase.table("indicators") \
            .select("*") \
            .eq("ticker", ticker) \
            .order("date", desc=True) \
            .limit(limit) \
            .execute()
        return pd.DataFrame(response.data)
    
    def get_latest_scores(self, min_score: float = 0, sector: str = None, limit: int = 100) -> pd.DataFrame:
        query = self.supabase.table("scores").select("*").gte("composite_score", min_score)
        if sector:
            query = query.eq("sector", sector)
        response = query.order("composite_score", desc=True).limit(limit).execute()
        return pd.DataFrame(response.data)
    
    def add_watchlist(self, ticker: str, notes: str = None, target_price: float = None):
        self.supabase.table("watchlist").insert({
            "ticker": ticker,
            "notes": notes,
            "target_price": target_price
        }).execute()
    
    def get_watchlist(self) -> pd.DataFrame:
        response = self.supabase.table("watchlist").select("*").order("added_date", desc=True).execute()
        return pd.DataFrame(response.data)
    
    def get_fundamentals(self) -> pd.DataFrame:
        response = self.supabase.table("fundamentals").select("*").execute()
        return pd.DataFrame(response.data)
    
    def save_fundamental(self, ticker: str, data: dict):
        data["ticker"] = ticker
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        self.supabase.table("fundamentals").upsert(data, on_conflict="ticker").execute()
    
    def get_backtests(self) -> pd.DataFrame:
        response = self.supabase.table("backtests").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(response.data)
    
    def save_backtest(self, ticker: str, strategy: str, result: dict):
        record = {
            "ticker": ticker,
            "strategy": strategy,
            "start_date": result.get("start_date"),
            "end_date": result.get("end_date"),
            "total_return": result.get("total_return"),
            "cagr": result.get("cagr"),
            "max_drawdown": result.get("max_drawdown"),
            "win_rate": result.get("win_rate"),
            "total_trades": result.get("total_trades")
        }
        self.supabase.table("backtests").insert(record).execute()
