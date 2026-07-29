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
        self.supabase = get_supabase_client()
        self.db_path = "supabase"

    def _connect(self):
        class MockConn:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def execute(self, *args):
                raise NotImplementedError("Gunakan method bawaan class ini")
        return MockConn()

    def get_prices(self, ticker, limit=500):
        try:
            response = self.supabase.table("price_data").select("*").eq("ticker", ticker).execute()
            if not response.data:
                return pd.DataFrame()
            df = pd.DataFrame(response.data)
            if not df.empty and "date" in df.columns:
                df = df.sort_values("date", ascending=False).head(limit)
            return df
        except Exception as e:
            st.error(f"Error get_prices: {e}")
            return pd.DataFrame()

    def get_all_latest_prices(self):
        try:
            response = self.supabase.table("price_data").select("ticker, date, close").execute()
            if not response.data:
                return pd.DataFrame()
            df = pd.DataFrame(response.data)
            if not df.empty:
                # Normalisasi nama kolom (hapus spasi jika ada)
                df.columns = df.columns.str.strip()
                if "date" in df.columns and "ticker" in df.columns:
                    df = df.sort_values("date", ascending=False)
                    df = df.drop_duplicates(subset=["ticker"], keep="first")
            return df
        except Exception as e:
            st.error(f"Error get_all_latest_prices: {e}")
            return pd.DataFrame()

    def get_indicators(self, ticker, limit=100):
        try:
            response = self.supabase.table("indicators").select("*").eq("ticker", ticker).execute()
            if not response.data:
                return pd.DataFrame()
            df = pd.DataFrame(response.data)
            if not df.empty and "date" in df.columns:
                df = df.sort_values("date", ascending=False).head(limit)
            return df
        except Exception as e:
            st.error(f"Error get_indicators: {e}")
            return pd.DataFrame()

    def get_latest_scores(self, min_score=0, sector=None, limit=100):
        try:
            query = self.supabase.table("scores").select("*")
            if min_score > 0:
                query = query.gte("composite_score", min_score)
            if sector and sector != "All":
                query = query.eq("sector", sector)
            response = query.execute()
            if not response.data:
                return pd.DataFrame()
            df = pd.DataFrame(response.data)
            if not df.empty and "composite_score" in df.columns:
                df = df.sort_values("composite_score", ascending=False).head(limit)
            return df
        except Exception as e:
            st.error(f"Error get_latest_scores: {e}")
            return pd.DataFrame()

    def add_watchlist(self, ticker, notes=None, target_price=None):
        try:
            self.supabase.table("watchlist").insert({
                "ticker": ticker,
                "notes": notes,
                "target_price": target_price
            }).execute()
        except Exception as e:
            st.error(f"Error add_watchlist: {e}")

    def get_watchlist(self):
        try:
            response = self.supabase.table("watchlist").select("*").execute()
            if not response.data:
                return pd.DataFrame()
            df = pd.DataFrame(response.data)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Error get_watchlist: {e}")
            return pd.DataFrame()

    def delete_watchlist(self, ticker):
        try:
            self.supabase.table("watchlist").delete().eq("ticker", ticker).execute()
        except Exception as e:
            st.error(f"Error delete_watchlist: {e}")

    def get_fundamentals(self):
        try:
            response = self.supabase.table("fundamentals").select("*").execute()
            if not response.data:
                return pd.DataFrame()
            return pd.DataFrame(response.data)
        except Exception as e:
            st.error(f"Error get_fundamentals: {e}")
            return pd.DataFrame()

    def get_backtests(self):
        try:
            response = self.supabase.table("backtests").select("*").execute()
            if not response.data:
                return pd.DataFrame()
            return pd.DataFrame(response.data)
        except Exception as e:
            st.error(f"Error get_backtests: {e}")
            return pd.DataFrame()

    def save_indicators(self, df, ticker):
        try:
            records = df.to_dict(orient="records")
            for row in records:
                row["ticker"] = ticker
            if records:
                self.supabase.table("indicators").upsert(records, on_conflict="ticker,date").execute()
        except Exception as e:
            st.error(f"Error save_indicators: {e}")

    def save_prices(self, df, ticker):
        try:
            records = df.to_dict(orient="records")
            for row in records:
                row["ticker"] = ticker
            if records:
                self.supabase.table("price_data").upsert(records, on_conflict="ticker,date").execute()
        except Exception as e:
            st.error(f"Error save_prices: {e}")

    def save_score(self, ticker, date, composite_score, signals, sector=None):
        try:
            self.supabase.table("scores").upsert({
                "ticker": ticker,
                "date": date,
                "composite_score": composite_score,
                "signals": signals,
                "sector": sector
            }, on_conflict="ticker,date").execute()
        except Exception as e:
            st.error(f"Error save_score: {e}")
