"""
NEW STRATEGY AGENTS
===================
5 strategies from external sources to backtest:

1. Daily Breakout and Moving Average (D1)
2. Pending the Reversal (M15/H1)
3. Psychological Reversal (H1)
4. Speculative (M15)
5. ADX and Momentum (M5)
"""

import pandas as pd
import numpy as np
from typing import Dict
import sys
sys.path.insert(0, '/mnt/user-data/uploads')
from agent_framework import TradingAgent


class DailyBreakoutAgent(TradingAgent):
    """
    Daily Breakout and Moving Average Strategy
    
    Timeframe: D1
    Instruments: All
    
    Indicators:
    - 20 SMA Low
    - 34 EMA
    - ADX(13)
    
    Entry:
    - LONG: 34EMA > 20SMA AND ADX(13) > 25
    - SHORT: 34EMA < 20SMA AND ADX(13) > 25
    
    Exit:
    - When MAs cross
    - TP: 100-150 points
    - SL: 30-50 points
    """
    
    def __init__(self):
        super().__init__(
            name="Daily Breakout",
            description="EMA/SMA crossover with ADX on D1",
            preferred_timeframes=["D1"],
            preferred_assets=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "BTCUSD", "XAUUSD", "XAGUSD", "GER40", "SP500", "NAS100"]
        )
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                session: str, market_structure: Dict) -> Dict:
        
        result = {
            'signal': 'NONE',
            'confidence': 0,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reasoning': '',
            'metadata': {}
        }
        
        if len(df) < 50:
            result['reasoning'] = "Insufficient data"
            return result
        
        latest = df.iloc[-1]
        
        # Calculate 20 SMA of lows and 34 EMA manually
        sma_low = df['low'].rolling(20).mean().iloc[-1]
        ema_34 = df['close'].ewm(span=34, adjust=False).mean().iloc[-1]
        adx = latest['adx']
        close = latest['close']
        atr = latest['atr']
        
        # Need trending market
        if adx < 25:
            result['reasoning'] = f"ADX too low ({adx:.1f})"
            return result
        
        # Fixed TP/SL in points (convert to price)
        if 'USD' in symbol or 'XAU' in symbol or 'XAG' in symbol:
            point_value = 0.0001 if 'JPY' not in symbol else 0.01
            if 'XAU' in symbol:
                point_value = 0.01
            elif 'XAG' in symbol:
                point_value = 0.001
        else:
            point_value = 1.0  # Indices
        
        tp_points = 125 * point_value  # 100-150 average
        sl_points = 40 * point_value   # 30-50 average
        
        confidence = 70
        
        # LONG Signal
        if ema_34 > sma_low:
            if adx > 30:
                confidence += 10
            if adx > 40:
                confidence += 10
            
            result = {
                'signal': 'BUY',
                'confidence': min(100, confidence),
                'entry_price': close,
                'stop_loss': close - sl_points,
                'take_profit': close + tp_points,
                'reasoning': f"Bullish: EMA34 > SMA20, ADX={adx:.1f}",
                'metadata': {'adx': adx, 'ema_34': ema_34, 'sma_low': sma_low}
            }
        
        # SHORT Signal
        elif ema_34 < sma_low:
            if adx > 30:
                confidence += 10
            if adx > 40:
                confidence += 10
            
            result = {
                'signal': 'SELL',
                'confidence': min(100, confidence),
                'entry_price': close,
                'stop_loss': close + sl_points,
                'take_profit': close - tp_points,
                'reasoning': f"Bearish: EMA34 < SMA20, ADX={adx:.1f}",
                'metadata': {'adx': adx, 'ema_34': ema_34, 'sma_low': sma_low}
            }
        
        return result


class PendingReversalAgent(TradingAgent):
    """
    Pending the Reversal Strategy
    
    Timeframe: M15 and above
    
    Indicators:
    - EMA(100, High)
    - EMA(100, Low)
    - Bollinger Bands(10, 2.3)
    
    Entry:
    - LONG: Uptrend, price above EMA low, touches/breaks lower BB, bounces back
    - SHORT: Downtrend, price below EMA high, touches/breaks upper BB, bounces back
    
    Exit:
    - Touches opposite BB
    - SL: Nearest local low/high
    - TP: 2:1 to SL
    """
    
    def __init__(self):
        super().__init__(
            name="Pending Reversal",
            description="Bollinger bounce with EMA confirmation",
            preferred_timeframes=["M15", "H1"],
            preferred_assets=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "BTCUSD", "XAUUSD", "XAGUSD", "GER40", "SP500", "NAS100"]
        )
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                session: str, market_structure: Dict) -> Dict:
        
        result = {
            'signal': 'NONE',
            'confidence': 0,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reasoning': '',
            'metadata': {}
        }
        
        if len(df) < 110:
            result['reasoning'] = "Insufficient data"
            return result
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Calculate EMAs on high/low
        ema_high = df['high'].ewm(span=100, adjust=False).mean().iloc[-1]
        ema_low = df['low'].ewm(span=100, adjust=False).mean().iloc[-1]
        
        # Bollinger Bands
        bb_upper = latest['bb_upper']
        bb_lower = latest['bb_lower']
        bb_middle = latest['bb_middle']
        
        close = latest['close']
        high = latest['high']
        low = latest['low']
        
        # Find recent local high/low (20 bars)
        recent_high = df['high'].iloc[-20:].max()
        recent_low = df['low'].iloc[-20:].max()
        
        confidence = 65
        
        # LONG Setup
        if close > ema_low:  # Uptrend
            # Price touched or broke lower BB
            if low <= bb_lower or prev['low'] <= bb_lower:
                # Bounced back above lower BB
                if close > bb_lower:
                    sl = recent_low
                    tp = close + (2 * (close - sl))
                    
                    confidence += 15
                    
                    result = {
                        'signal': 'BUY',
                        'confidence': min(100, confidence),
                        'entry_price': close,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'reasoning': "Uptrend BB bounce",
                        'metadata': {'bb_lower': bb_lower, 'ema_low': ema_low}
                    }
        
        # SHORT Setup  
        elif close < ema_high:  # Downtrend
            # Price touched or broke upper BB
            if high >= bb_upper or prev['high'] >= bb_upper:
                # Bounced back below upper BB
                if close < bb_upper:
                    sl = recent_high
                    tp = close - (2 * (sl - close))
                    
                    confidence += 15
                    
                    result = {
                        'signal': 'SELL',
                        'confidence': min(100, confidence),
                        'entry_price': close,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'reasoning': "Downtrend BB bounce",
                        'metadata': {'bb_upper': bb_upper, 'ema_high': ema_high}
                    }
        
        return result


class PsychologicalReversalAgent(TradingAgent):
    """
    Psychological Reversal Strategy
    
    Timeframe: H1
    No indicators - pure price action
    
    Entry:
    - LONG: Downtrend, price breaks previous high with high volatility, 
            closes at same level within 1-2 hours (fake breakout)
    - SHORT: Uptrend, price breaks previous low with high volatility,
             closes at same level within 1-2 hours (fake breakdown)
    
    Exit:
    - TP: Height of breakdown/breakout
    - SL: At support/resistance level
    """
    
    def __init__(self):
        super().__init__(
            name="Psychological Reversal",
            description="Fake breakout/breakdown reversal trading",
            preferred_timeframes=["H1"],
            preferred_assets=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "BTCUSD", "XAUUSD", "XAGUSD", "GER40", "SP500", "NAS100"]
        )
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                session: str, market_structure: Dict) -> Dict:
        
        result = {
            'signal': 'NONE',
            'confidence': 0,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reasoning': '',
            'metadata': {}
        }
        
        if len(df) < 50:
            result['reasoning'] = "Insufficient data"
            return result
        
        latest = df.iloc[-1]
        
        # Look back 20 bars for highs/lows
        lookback = df.iloc[-20:-1]
        prev_high = lookback['high'].max()
        prev_low = lookback['low'].min()
        
        close = latest['close']
        high = latest['high']
        low = latest['low']
        open_price = latest['open']
        atr = latest['atr']
        
        # Check if current candle is volatile (high volatility)
        candle_range = high - low
        if candle_range < atr * 1.5:
            result['reasoning'] = "Not enough volatility"
            return result
        
        confidence = 70
        
        # LONG Setup: Fake breakdown in downtrend
        # Price broke below previous low but closed back at or above it
        if low < prev_low and close >= (prev_low - atr * 0.2):
            # This is a fake breakdown - reversal likely
            sl = low
            tp_distance = abs(low - prev_low)
            tp = close + tp_distance
            
            result = {
                'signal': 'BUY',
                'confidence': min(100, confidence + 10),
                'entry_price': close,
                'stop_loss': sl,
                'take_profit': tp,
                'reasoning': "Fake breakdown - buyers trapped sellers",
                'metadata': {'prev_low': prev_low, 'breakdown_size': tp_distance}
            }
        
        # SHORT Setup: Fake breakout in uptrend
        # Price broke above previous high but closed back at or below it
        elif high > prev_high and close <= (prev_high + atr * 0.2):
            # This is a fake breakout - reversal likely
            sl = high
            tp_distance = abs(high - prev_high)
            tp = close - tp_distance
            
            result = {
                'signal': 'SELL',
                'confidence': min(100, confidence + 10),
                'entry_price': close,
                'stop_loss': sl,
                'take_profit': tp,
                'reasoning': "Fake breakout - sellers trapped buyers",
                'metadata': {'prev_high': prev_high, 'breakout_size': tp_distance}
            }
        
        return result


class SpeculativeAgent(TradingAgent):
    """
    Speculative Strategy
    
    Timeframe: M15
    Instruments: EURUSD, GBPUSD only
    
    Indicators:
    - ZigZag (Depth 100)
    - RSI(14)
    
    Entry:
    - LONG: ZigZag at LOW + RSI oversold (<30)
    - SHORT: ZigZag at HIGH + RSI overbought (>70)
    
    Exit:
    - TP: 60-100 points
    - SL: 15-20 points
    """
    
    def __init__(self):
        super().__init__(
            name="Speculative",
            description="ZigZag + RSI extreme reversal",
            preferred_timeframes=["M15"],
            preferred_assets=["EURUSD", "GBPUSD"]
        )
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                session: str, market_structure: Dict) -> Dict:
        
        result = {
            'signal': 'NONE',
            'confidence': 0,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reasoning': '',
            'metadata': {}
        }
        
        if len(df) < 150:
            result['reasoning'] = "Insufficient data"
            return result
        
        latest = df.iloc[-1]
        
        # Simple ZigZag approximation (find local highs/lows in last 100 bars)
        lookback = 100
        recent_data = df.iloc[-lookback:]
        
        # Find if we're at a local high or low
        max_high = recent_data['high'].max()
        min_low = recent_data['low'].min()
        
        high = latest['high']
        low = latest['low']
        close = latest['close']
        rsi = latest['rsi']
        
        # Define point value
        point_value = 0.0001  # For EURUSD/GBPUSD
        
        tp_points = 80 * point_value  # 60-100 avg
        sl_points = 17 * point_value  # 15-20 avg
        
        confidence = 65
        
        # LONG Setup: At low with oversold RSI
        if abs(low - min_low) < (0.0010) and rsi < 30:  # Near zigzag low
            if rsi < 25:
                confidence += 15
            
            result = {
                'signal': 'BUY',
                'confidence': min(100, confidence),
                'entry_price': close,
                'stop_loss': close - sl_points,
                'take_profit': close + tp_points,
                'reasoning': f"ZigZag low + RSI oversold ({rsi:.1f})",
                'metadata': {'rsi': rsi, 'zigzag_low': min_low}
            }
        
        # SHORT Setup: At high with overbought RSI
        elif abs(high - max_high) < (0.0010) and rsi > 70:  # Near zigzag high
            if rsi > 75:
                confidence += 15
            
            result = {
                'signal': 'SELL',
                'confidence': min(100, confidence),
                'entry_price': close,
                'stop_loss': close + sl_points,
                'take_profit': close - tp_points,
                'reasoning': f"ZigZag high + RSI overbought ({rsi:.1f})",
                'metadata': {'rsi': rsi, 'zigzag_high': max_high}
            }
        
        return result


class ADXMomentumAgent(TradingAgent):
    """
    ADX and Momentum Strategy
    
    Timeframe: M5
    Instruments: Major forex pairs
    
    Indicators:
    - ADX(14) with D+/D-
    - Momentum(14)
    - Parabolic SAR(0.02, 0.02)
    
    Entry:
    - LONG: ADX > 25, D+ > 25 and > D-, Momentum > 100
    - SHORT: ADX > 25, D- > 25 and > D+, Momentum < 100
    
    Exit:
    - SL: 5-7 points
    - TP: 14-16 points
    - Can use EMA55 as filter
    """
    
    def __init__(self):
        super().__init__(
            name="ADX Momentum",
            description="ADX + Momentum trend following on M5",
            preferred_timeframes=["M5"],
            preferred_assets=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
        )
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                session: str, market_structure: Dict) -> Dict:
        
        result = {
            'signal': 'NONE',
            'confidence': 0,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reasoning': '',
            'metadata': {}
        }
        
        if len(df) < 60:
            result['reasoning'] = "Insufficient data"
            return result
        
        latest = df.iloc[-1]
        
        adx = latest['adx']
        
        # Get DI+ and DI- from ADX calculation
        # Calculate manually if not available
        high = df['high']
        low = df['low']
        close = df['close']
        
        dm_plus = (high - high.shift(1)).clip(lower=0)
        dm_minus = (low.shift(1) - low).clip(lower=0)
        tr = pd.DataFrame({
            'hl': high - low,
            'hc': abs(high - close.shift(1)),
            'lc': abs(low - close.shift(1))
        }).max(axis=1)
        
        atr_14 = tr.rolling(14).mean()
        di_plus = 100 * (dm_plus.rolling(14).mean() / atr_14)
        di_minus = 100 * (dm_minus.rolling(14).mean() / atr_14)
        
        d_plus = di_plus.iloc[-1]
        d_minus = di_minus.iloc[-1]
        
        # Momentum (Rate of Change)
        momentum = ((close / close.shift(14)) * 100).iloc[-1]
        
        close_price = latest['close']
        
        # Calculate EMA 55 manually if not present
        if 'ema_55' in latest:
            ema_55 = latest['ema_55']
        else:
            ema_55 = df['close'].ewm(span=55, adjust=False).mean().iloc[-1]
        
        # Point value
        point_value = 0.0001 if 'JPY' not in symbol else 0.01
        
        tp_points = 15 * point_value  # 14-16 avg
        sl_points = 6 * point_value   # 5-7 avg
        
        confidence = 70
        
        # Need trending market
        if adx < 25:
            result['reasoning'] = f"ADX too low ({adx:.1f})"
            return result
        
        # LONG Setup
        if d_plus > 25 and d_plus > d_minus and momentum > 100:
            # Optional EMA filter
            if close_price > ema_55:
                confidence += 10
            
            result = {
                'signal': 'BUY',
                'confidence': min(100, confidence),
                'entry_price': close_price,
                'stop_loss': close_price - sl_points,
                'take_profit': close_price + tp_points,
                'reasoning': f"Bullish momentum: ADX={adx:.1f}, D+={d_plus:.1f}, Mom={momentum:.1f}",
                'metadata': {'adx': adx, 'd_plus': d_plus, 'd_minus': d_minus, 'momentum': momentum}
            }
        
        # SHORT Setup
        elif d_minus > 25 and d_minus > d_plus and momentum < 100:
            # Optional EMA filter
            if close_price < ema_55:
                confidence += 10
            
            result = {
                'signal': 'SELL',
                'confidence': min(100, confidence),
                'entry_price': close_price,
                'stop_loss': close_price + sl_points,
                'take_profit': close_price - tp_points,
                'reasoning': f"Bearish momentum: ADX={adx:.1f}, D-={d_minus:.1f}, Mom={momentum:.1f}",
                'metadata': {'adx': adx, 'd_plus': d_plus, 'd_minus': d_minus, 'momentum': momentum}
            }
        
        return result


# Export all agents
def get_new_strategy_agents():
    """Return all 5 new strategy agents"""
    return [
        DailyBreakoutAgent(),
        PendingReversalAgent(),
        PsychologicalReversalAgent(),
        SpeculativeAgent(),
        ADXMomentumAgent()
    ]


if __name__ == "__main__":
    agents = get_new_strategy_agents()
    print("✅ Created 5 new strategy agents:")
    for agent in agents:
        print(f"  - {agent.name}: {agent.description}")
        print(f"    Timeframes: {agent.preferred_timeframes}")
        print(f"    Assets: {agent.preferred_assets[:3]}...")
        print()