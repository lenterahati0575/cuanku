import pandas as pd
from datetime import datetime

class BacktestEngine:
    def __init__(self, db):
        self.db = db
    
    def run(self, ticker: str, strategy: str = "composite_score", 
            entry_threshold: int = 70, exit_threshold: int = 50,
            stop_loss_pct: float = 7.0, take_profit_pct: float = 15.0,
            max_holding_days: int = 30) -> dict:
        """Run backtest"""
        try:
            prices = self.db.get_prices(ticker, limit=500)
            indicators = self.db.get_indicators(ticker, limit=500)
            
            if prices.empty or indicators.empty:
                return None
            
            # Merge data
            df = prices.merge(indicators, on=['ticker', 'date'], how='inner')
            df = df.sort_values('date')
            
            # Simulasi trading sederhana
            trades = []
            equity = 100000000  # Modal awal 100 juta
            equity_curve = []
            
            in_position = False
            entry_price = 0
            entry_date = None
            
            for idx, row in df.iterrows():
                date = row['date']
                price = row['close']
                score = row.get('composite_score', 50)
                
                # Entry logic
                if not in_position and score >= entry_threshold:
                    in_position = True
                    entry_price = price
                    entry_date = date
                
                # Exit logic
                elif in_position:
                    holding_days = (date - entry_date).days if entry_date else 0
                    pnl_pct = (price - entry_price) / entry_price * 100
                    
                    exit_signal = False
                    exit_reason = ""
                    
                    if score <= exit_threshold:
                        exit_signal = True
                        exit_reason = "Score Exit"
                    elif pnl_pct <= -stop_loss_pct:
                        exit_signal = True
                        exit_reason = "Stop Loss"
                    elif pnl_pct >= take_profit_pct:
                        exit_signal = True
                        exit_reason = "Take Profit"
                    elif holding_days >= max_holding_days:
                        exit_signal = True
                        exit_reason = "Max Holding"
                    
                    if exit_signal:
                        pnl = (price - entry_price) * 100  # 1 lot = 100 shares
                        equity += pnl
                        trades.append({
                            "entry_date": entry_date,
                            "exit_date": date,
                            "entry_price": entry_price,
                            "exit_price": price,
                            "pnl": pnl,
                            "pnl_pct": pnl_pct,
                            "reason": exit_reason
                        })
                        in_position = False
                
                equity_curve.append({"date": date, "equity": equity})
            
            # Hitung statistik
            if not trades:
                return {
                    "trades": 0,
                    "total_return": 0,
                    "cagr": 0,
                    "max_drawdown": 0,
                    "win_rate": 0,
                    "avg_return_per_trade": 0,
                    "equity_curve": equity_curve,
                    "trade_list": []
                }
            
            winning_trades = [t for t in trades if t['pnl'] > 0]
            win_rate = len(winning_trades) / len(trades) * 100
            
            total_return = (equity - 100000000) / 100000000 * 100
            avg_return = sum(t['pnl_pct'] for t in trades) / len(trades)
            
            return {
                "trades": len(trades),
                "total_return": total_return,
                "cagr": total_return,  # Simplified
                "max_drawdown": 0,  # Perlu kalkulasi lebih lanjut
                "win_rate": win_rate,
                "avg_return_per_trade": avg_return,
                "equity_curve": equity_curve,
                "trade_list": trades
            }
        except Exception as e:
            print(f"Error backtest: {e}")
            return None
