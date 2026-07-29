import pandas as pd
import numpy as np
from datetime import date

class CompositeScorer:
    def rank_all(self, db):
        """Hitung composite score untuk semua saham"""
        # Ambil semua ticker dari database
        all_prices = db.get_all_latest_prices()
        tickers = all_prices['ticker'].tolist()
        
        for ticker in tickers:
            try:
                # Ambil data indikator
                indicators = db.get_indicators(ticker, limit=1)
                
                if indicators.empty:
                    continue
                
                latest = indicators.iloc[0]
                
                # Hitung score berdasarkan indikator
                score = self._calculate_score(latest)
                signals = self._generate_signals(latest)
                
                # Simpan score
                db.save_score(
                    ticker=ticker,
                    date=date.today(),
                    composite_score=score,
                    signals=signals,
                    sector=None
                )
            except Exception as e:
                continue
    
    def _calculate_score(self, indicators: pd.Series) -> float:
        """Hitung composite score dari indikator"""
        score = 50  # Base score
        
        # RSI scoring (30-70 range ideal)
        rsi = indicators.get('rsi_14', 50)
        if 40 <= rsi <= 60:
            score += 15
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            score += 5
        elif rsi < 30 or rsi > 70:
            score -= 10
        
        # MACD scoring
        macd_hist = indicators.get('macd_hist', 0)
        if macd_hist > 0:
            score += 15
        else:
            score -= 5
        
        # EMA scoring (price above EMA20)
        ema_20 = indicators.get('ema_20', 0)
        # Note: kita tidak punya access ke current price di sini, skip
        
        # ADX scoring (trend strength)
        adx = indicators.get('adx_14', 0)
        if adx > 25:
            score += 10
        elif adx < 20:
            score -= 5
        
        # Bollinger Band position
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        # Skip karena tidak ada current price
        
        # Normalize score 0-100
        score = max(0, min(100, score))
        
        return round(score, 1)
    
    def _generate_signals(self, indicators: pd.Series) -> str:
        """Generate trading signals dari indikator"""
        signals = []
        
        rsi = indicators.get('rsi_14', 50)
        if rsi < 30:
            signals.append("RSI Oversold")
        elif rsi > 70:
            signals.append("RSI Overbought")
        
        macd_hist = indicators.get('macd_hist', 0)
        if macd_hist > 0:
            signals.append("MACD Bullish")
        else:
            signals.append("MACD Bearish")
        
        adx = indicators.get('adx_14', 0)
        if adx > 25:
            signals.append("Strong Trend")
        
        return ", ".join(signals) if signals else "Neutral"
