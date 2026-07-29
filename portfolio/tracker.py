import pandas as pd
from datetime import date

class PortfolioTracker:
    def __init__(self, db):
        self.db = db
    
    def buy(self, ticker: str, shares: int, price: float):
        """Beli saham"""
        # Cek apakah sudah ada posisi
        df = self.get_df()
        existing = df[df['ticker'] == ticker]
        
        if not existing.empty:
            # Update posisi existing
            old_shares = existing['shares'].values[0]
            old_avg = existing['avg_price'].values[0]
            new_shares = old_shares + shares
            new_avg = ((old_shares * old_avg) + (shares * price)) / new_shares
            
            # Update di database (hapus lama, insert baru)
            with self.db._connect() as conn:
                conn.execute("DELETE FROM portfolio WHERE ticker=?", (ticker,))
                conn.execute("""
                    INSERT INTO portfolio (ticker, shares, avg_price, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (ticker, new_shares, new_avg, date.today()))
                conn.commit()
        else:
            # Insert posisi baru
            with self.db._connect() as conn:
                conn.execute("""
                    INSERT INTO portfolio (ticker, shares, avg_price, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (ticker, shares, price, date.today()))
                conn.commit()
    
    def sell(self, ticker: str, shares: int, price: float):
        """Jual saham"""
        df = self.get_df()
        existing = df[df['ticker'] == ticker]
        
        if existing.empty:
            return False, "Tidak ada posisi untuk dijual"
        
        old_shares = existing['shares'].values[0]
        old_avg = existing['avg_price'].values[0]
        
        if shares > old_shares:
            return False, f"Jumlah lot melebihi posisi ({old_shares // 100} lot)"
        
        new_shares = old_shares - shares
        realized_pl = (price - old_avg) * shares
        
        if new_shares == 0:
            # Hapus posisi
            with self.db._connect() as conn:
                conn.execute("DELETE FROM portfolio WHERE ticker=?", (ticker,))
                conn.commit()
        else:
            # Update posisi
            with self.db._connect() as conn:
                conn.execute("DELETE FROM portfolio WHERE ticker=?", (ticker,))
                conn.execute("""
                    INSERT INTO portfolio (ticker, shares, avg_price, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (ticker, new_shares, old_avg, date.today()))
                conn.commit()
        
        return True, f"Realized P/L: Rp {realized_pl:,.0f}"
    
    def get_df(self) -> pd.DataFrame:
        """Ambil semua posisi portfolio"""
        with self.db._connect() as conn:
            df = pd.read_sql_query("""
                SELECT * FROM portfolio ORDER BY ticker
            """, conn)
        
        if df.empty:
            return df
        
        # Tambahkan kolom calculated
        df['market_value'] = df['shares'] * df['avg_price']  # Simplified
        df['unrealized_pl'] = 0  # Perlu current price untuk hitung ini
        
        return df
    
    def get_summary(self) -> dict:
        """Ringkasan portfolio"""
        df = self.get_df()
        
        if df.empty:
            return {
                'total_value': 0,
                'total_cost': 0,
                'unrealized': 0,
                'realized': 0,
                'win_rate': 0,
                'positions': 0
            }
        
        total_value = df['market_value'].sum()
        total_cost = (df['shares'] * df['avg_price']).sum()
        unrealized = total_value - total_cost
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'unrealized': unrealized,
            'realized': 0,  # Perlu tracking terpisah
            'win_rate': 0,  # Perlu tracking terpisah
            'positions': len(df)
        }
