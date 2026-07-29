import pandas as pd
from io import BytesIO
from datetime import datetime

class ExcelExporter:
    def __init__(self, db):
        self.db = db
    
    def export_all(self, min_score: float = 0, sector: str = None) -> BytesIO:
        """Export semua data ke Excel"""
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Screener Results
            scores = self.db.get_latest_scores(min_score=min_score, sector=sector, limit=200)
            if not scores.empty:
                scores.to_excel(writer, sheet_name='Screener', index=False)
            
            # Sheet 2: Watchlist
            watchlist = self.db.get_watchlist()
            if not watchlist.empty:
                watchlist.to_excel(writer, sheet_name='Watchlist', index=False)
            
            # Sheet 3: Portfolio
            with self.db._connect() as conn:
                portfolio = pd.read_sql_query("SELECT * FROM portfolio", conn)
                if not portfolio.empty:
                    portfolio.to_excel(writer, sheet_name='Portfolio', index=False)
            
            # Sheet 4: Journal
            with self.db._connect() as conn:
                journal = pd.read_sql_query("SELECT * FROM journal", conn)
                if not journal.empty:
                    journal.to_excel(writer, sheet_name='Journal', index=False)
            
            # Sheet 5: Alerts
            with self.db._connect() as conn:
                alerts = pd.read_sql_query("SELECT * FROM alerts", conn)
                if not alerts.empty:
                    alerts.to_excel(writer, sheet_name='Alerts', index=False)
        
        output.seek(0)
        return output
