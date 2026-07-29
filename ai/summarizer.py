import pandas as pd
from datetime import datetime

class AISummarizer:
    def __init__(self, db):
        self.db = db
        self.use_llm = False  # Set True jika ada OPENAI_API_KEY
    
    def market_overview(self, top_n=50) -> dict:
        """Ringkasan market dari top N saham"""
        try:
            scores = self.db.get_latest_scores(min_score=0, limit=top_n)
            
            if scores.empty:
                return None
            
            bullish = len(scores[scores['composite_score'] >= 60])
            bearish = len(scores[scores['composite_score'] < 40])
            
            # Hitung avg score per sektor
            if 'sector' in scores.columns:
                sector_avg = scores.groupby('sector')['composite_score'].mean().to_dict()
                top_sector = max(sector_avg, key=sector_avg.get) if sector_avg else "N/A"
            else:
                sector_avg = {}
                top_sector = "N/A"
            
            if bullish > bearish:
                mood = "Bullish"
            elif bearish > bullish:
                mood = "Bearish"
            else:
                mood = "Neutral"
            
            return {
                "market_mood": mood,
                "bullish_count": bullish,
                "bearish_count": bearish,
                "top_sector": top_sector,
                "sector_avg": sector_avg
            }
        except Exception as e:
            print(f"Error market_overview: {e}")
            return None
    
    def analyze_ticker(self, ticker: str) -> dict:
        """Analisis teknikal per saham"""
        try:
            prices = self.db.get_prices(ticker, limit=60)
            indicators = self.db.get_indicators(ticker, limit=1)
            
            if prices.empty or indicators.empty:
                return None
            
            latest_price = prices.iloc[0]['close']
            latest_ind = indicators.iloc[0]
            
            # Hitung score sederhana
            score = 50
            signals = []
            
            rsi = latest_ind.get('rsi_14', 50)
            if rsi < 30:
                score += 20
                signals.append("RSI Oversold - Potensi Rebound")
            elif rsi > 70:
                score -= 20
                signals.append("RSI Overbought - Hati-hati")
            
            macd_hist = latest_ind.get('macd_hist', 0)
            if macd_hist > 0:
                score += 15
                signals.append("MACD Bullish")
            else:
                score -= 10
                signals.append("MACD Bearish")
            
            adx = latest_ind.get('adx_14', 0)
            if adx > 25:
                signals.append("Trend Kuat (ADX > 25)")
            
            score = max(0, min(100, score))
            
            if score >= 70:
                verdict = "Strong Buy"
                color = "green"
            elif score >= 55:
                verdict = "Buy"
                color = "green"
            elif score >= 45:
                verdict = "Hold"
                color = "orange"
            else:
                verdict = "Sell"
                color = "red"
            
            # Key levels
            support = prices['low'].min()
            resistance = prices['high'].max()
            vwap = latest_ind.get('vwap', latest_price)
            
            return {
                "price": latest_price,
                "score": score,
                "verdict": verdict,
                "color": color,
                "signals": signals,
                "key_levels": {
                    "support": support,
                    "resistance": resistance,
                    "vwap": vwap
                }
            }
        except Exception as e:
            print(f"Error analyze_ticker: {e}")
            return None
    
    def llm_summary(self, ticker: str) -> str:
        """Generate narasi AI (butuh OPENAI_API_KEY)"""
        return "[LLM not configured]"
    
    def generate_full_report(self, limit=20) -> list:
        """Generate report untuk top N saham"""
        try:
            scores = self.db.get_latest_scores(min_score=0, limit=limit)
            reports = []
            
            for _, row in scores.iterrows():
                analysis = self.analyze_ticker(row['ticker'])
                if analysis:
                    reports.append({
                        "ticker": row['ticker'],
                        "score": analysis['score'],
                        "verdict": analysis['verdict'],
                        "signals": analysis['signals']
                    })
            
            return reports
        except Exception as e:
            print(f"Error generate_full_report: {e}")
            return []
