import pandas as pd
from datetime import datetime

class AlertMonitor:
    def __init__(self, db):
        self.db = db
    
    def add(self, ticker: str, condition_type: str, target_value: float):
        """Tambah alert baru"""
        with self.db._connect() as conn:
            conn.execute("""
                INSERT INTO alerts (ticker, condition_type, target_value, triggered)
                VALUES (?, ?, ?, 0)
            """, (ticker, condition_type, target_value))
            conn.commit()
    
    def delete(self, alert_id: int):
        """Hapus alert"""
        with self.db._connect() as conn:
            conn.execute("DELETE FROM alerts WHERE id=?", (alert_id,))
            conn.commit()
    
    def get_active(self) -> pd.DataFrame:
        """Ambil alert yang aktif"""
        with self.db._connect() as conn:
            return pd.read_sql_query("""
                SELECT * FROM alerts WHERE triggered = 0 ORDER BY created_at DESC
            """, conn)
    
    def check_all(self) -> list:
        """Cek semua alert"""
        active_alerts = self.get_active()
        triggered = []
        
        for _, alert in active_alerts.iterrows():
            ticker = alert['ticker']
            condition = alert['condition_type']
            target = alert['target_value']
            
            # Ambil harga terbaru
            prices = self.db.get_prices(ticker, limit=1)
            
            if prices.empty:
                continue
            
            current_price = prices.iloc[0]['close']
            
            is_triggered = False
            
            if condition == 'PRICE_ABOVE' and current_price > target:
                is_triggered = True
            elif condition == 'PRICE_BELOW' and current_price < target:
                is_triggered = True
            # Tambahkan kondisi lain sesuai kebutuhan
            
            if is_triggered:
                triggered.append({
                    'ticker': ticker,
                    'condition': condition,
                    'target': target,
                    'price_now': current_price
                })
                
                # Update status triggered
                with self.db._connect() as conn:
                    conn.execute("""
                        UPDATE alerts SET triggered = 1, triggered_at = ? WHERE id = ?
                    """, (datetime.now(), alert['id']))
                    conn.commit()
        
        return triggered
