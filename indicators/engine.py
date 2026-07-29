import pandas as pd
import numpy as np

class IndicatorEngine:
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Hitung semua indikator teknikal"""
        df = df.copy()
        
        # EMA
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # SMA
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # RSI
        df['rsi_14'] = IndicatorEngine._calculate_rsi(df['close'], 14)
        
        # MACD
        macd, signal, hist = IndicatorEngine._calculate_macd(df['close'])
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_hist'] = hist
        
        # Bollinger Bands
        bb_upper, bb_lower = IndicatorEngine._calculate_bollinger(df['close'])
        df['bb_upper'] = bb_upper
        df['bb_lower'] = bb_lower
        
        # ADX
        df['adx_14'] = IndicatorEngine._calculate_adx(df, 14)
        
        # ATR
        df['atr_14'] = IndicatorEngine._calculate_atr(df, 14)
        
        # VWAP
        df['vwap'] = IndicatorEngine._calculate_vwap(df)
        
        # Stochastic
        stoch_k, stoch_d = IndicatorEngine._calculate_stochastic(df)
        df['stochastic_k'] = stoch_k
        df['stochastic_d'] = stoch_d
        
        # CCI
        df['cci_20'] = IndicatorEngine._calculate_cci(df, 20)
        
        # Williams %R
        df['williams_r'] = IndicatorEngine._calculate_williams_r(df, 14)
        
        # ROC
        df['roc'] = df['close'].pct_change(periods=10) * 100
        
        # Momentum
        df['momentum'] = df['close'] - df['close'].shift(10)
        
        return df
    
    @staticmethod
    def _calculate_rsi(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def _calculate_macd(series: pd.Series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    @staticmethod
    def _calculate_bollinger(series: pd.Series, period=20, std_dev=2):
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, lower
    
    @staticmethod
    def _calculate_adx(df: pd.DataFrame, period: int) -> pd.Series:
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return tr.rolling(window=period).mean()
    
    @staticmethod
    def _calculate_vwap(df: pd.DataFrame) -> pd.Series:
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    
    @staticmethod
    def _calculate_stochastic(df: pd.DataFrame, period=14):
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        
        stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
        stoch_d = stoch_k.rolling(window=3).mean()
        
        return stoch_k, stoch_d
    
    @staticmethod
    def _calculate_cci(df: pd.DataFrame, period=20) -> pd.Series:
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
        return (tp - sma) / (0.015 * mad)
    
    @staticmethod
    def _calculate_williams_r(df: pd.DataFrame, period=14) -> pd.Series:
        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        return -100 * (high_max - df['close']) / (high_max - low_min)
