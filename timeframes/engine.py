import pandas as pd

class MultiTimeframeEngine:
    @staticmethod
    def analyze_all_tfs(db, ticker: str) -> dict:
        """Analisis multi-timeframe"""
        try:
            # Untuk simplicity, kita gunakan data daily saja
            # Di production, perlu data weekly dan monthly terpisah
            indicators = db.get_indicators(ticker, limit=100)
            
            if indicators.empty:
                return None
            
            latest = indicators.iloc[0]
            
            # Hitung score untuk setiap timeframe (simplified)
            daily_score = MultiTimeframeEngine._calculate_tf_score(latest)
            weekly_score = daily_score * 0.9  # Simplified
            monthly_score = daily_score * 0.8  # Simplified
            
            alignment_score = (daily_score + weekly_score + monthly_score) / 3
            
            if alignment_score >= 80:
                alignment = "Strong Bullish"
            elif alignment_score >= 60:
                alignment = "Bullish"
            elif alignment_score >= 40:
                alignment = "Neutral"
            else:
                alignment = "Bearish"
            
            return {
                "ticker": ticker,
                "scores": {
                    "daily": daily_score,
                    "weekly": weekly_score,
                    "monthly": monthly_score
                },
                "alignment": alignment,
                "alignment_score": alignment_score,
                "details": {
                    "daily": latest.to_dict(),
                    "weekly": {},
                    "monthly": {}
                }
            }
        except Exception as e:
            print(f"Error analyze_all_tfs: {e}")
            return None
    
    @staticmethod
    def _calculate_tf_score(indicators: pd.Series) -> float:
        """Hitung score untuk satu timeframe"""
        score = 50
        
        rsi = indicators.get('rsi_14', 50)
        if 40 <= rsi <= 60:
            score += 15
        elif rsi < 30 or rsi > 70:
            score -= 10
        
        macd_hist = indicators.get('macd_hist', 0)
        if macd_hist > 0:
            score += 15
        else:
            score -= 5
        
        adx = indicators.get('adx_14', 0)
        if adx > 25:
            score += 10
        
        return max(0, min(100, score))
