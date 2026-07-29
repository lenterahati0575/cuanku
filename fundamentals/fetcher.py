import pandas as pd
import yfinance as yf

class FundamentalFetcher:
    def __init__(self, db):
        self.db = db
    
    def fetch(self, ticker: str):
        """Fetch fundamental data dari Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            data = {
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "roe": info.get("returnOnEquity"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "dividend_yield": info.get("dividendYield", 0),
                "eps": info.get("trailingEps"),
                "book_value": info.get("bookValue"),
                "market_cap": info.get("marketCap"),
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon")
            }
            
            self.db.save_fundamental(ticker, data)
        except Exception as e:
            print(f"Error fetching fundamentals for {ticker}: {e}")
    
    def get_fundamental_score(self, ticker: str) -> dict:
        """Hitung fundamental score"""
        try:
            fundamentals = self.db.get_fundamentals()
            row = fundamentals[fundamentals['ticker'] == ticker]
            
            if row.empty:
                return {"score": 0, "label": "N/A", "details": {}, "raw": {}}
            
            row = row.iloc[0]
            score = 50
            details = {}
            
            # PE Ratio scoring
            pe = row.get('pe_ratio', 0)
            if pe and 0 < pe < 15:
                score += 10
                details['pe'] = 90
            elif pe and 15 <= pe < 25:
                score += 5
                details['pe'] = 70
            else:
                details['pe'] = 30
            
            # ROE scoring
            roe = row.get('roe', 0)
            if roe and roe > 0.15:
                score += 15
                details['roe'] = 90
            elif roe and roe > 0.10:
                score += 10
                details['roe'] = 70
            else:
                details['roe'] = 30
            
            # Dividend Yield
            div_yield = row.get('dividend_yield', 0)
            if div_yield and div_yield > 0.03:
                score += 10
                details['dividend'] = 90
            elif div_yield and div_yield > 0.01:
                score += 5
                details['dividend'] = 70
            else:
                details['dividend'] = 30
            
            score = max(0, min(100, score))
            
            if score >= 70:
                label = "Excellent"
            elif score >= 50:
                label = "Good"
            else:
                label = "Average"
            
            return {
                "score": score,
                "label": label,
                "details": details,
                "raw": row.to_dict()
            }
        except Exception as e:
            print(f"Error get_fundamental_score: {e}")
            return {"score": 0, "label": "N/A", "details": {}, "raw": {}}
