import pandas as pd
from datetime import date

class JournalManager:
    def __init__(self, db):
        self.db = db
    
    def add(self, date_str: str, ticker: str, action: str, quantity: int, 
            price: float, setup: str, emotion: str, review: str, pnl: float = None):
        """Tambah entry journal"""
        with self.db._connect() as conn:
            conn.execute("""
                INSERT INTO journal (date, ticker, action, quantity, price, setup, emotion, review, pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_str, ticker, action, quantity, price, setup, emotion, review, pnl))
            conn.commit()
    
    def delete(self, entry_id: int):
        """Hapus entry journal"""
        with self.db._connect() as conn:
            conn.execute("DELETE FROM journal WHERE id=?", (entry_id,))
            conn.commit()
    
    def get_df(self) -> pd.DataFrame:
        """Ambil semua entry journal"""
        with self.db._connect() as conn:
            return pd.read_sql_query("""
                SELECT * FROM journal ORDER BY date DESC
            """, conn)
    
    def stats(self) -> dict:
        """Statistik trading"""
        df = self.get_df()
        
        if df.empty:
            return {
                'trades': 0,
                'win_rate': 0,
                'avg_pnl': 0,
                'best': 0
            }
        
        sell_trades = df[df['action'] == 'SELL']
        total_trades = len(sell_trades)
        
        if total_trades == 0:
            return {
                'trades': 0,
                'win_rate': 0,
                'avg_pnl': 0,
                'best': 0
            }
        
        winning = sell_trades[sell_trades['pnl'] > 0]
        win_rate = (len(winning) / total_trades) * 100
        
        avg_pnl = sell_trades['pnl'].mean()
        best = sell_trades['pnl'].max()
        
        return {
            'trades': total_trades,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'best': best
        }
