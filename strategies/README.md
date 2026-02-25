# Trading Strategies

MT5 Expert Advisors -- currently forward testing live.

## Active Strategies

| Strategy              | File                          | Assets                          | Timeframe |
|-----------------------|-------------------------------|---------------------------------|-----------|
| Pending Reversal EA   | `Pending Reversal EA.mq5`    | NAS100, GER40, BTCUSD, XAUUSD  | H1        |
| Range Strategy EA     | `Range Strategy EA.mq5`      | GER40                           | H4        |

## Strategy Overview

### Pending Reversal EA

Bollinger Band bounce strategy with EMA trend filtering. Uses a 100-period EMA channel for trend direction and 10-period Bollinger Bands (2.3 deviation) for mean-reversion entries. Risk:Reward ratio of 2:1 with dynamic stop loss placement based on recent swing lows/highs.

### Range Strategy EA

Multi-indicator confluence system combining triple EMA alignment (14/50/200), RSI momentum confirmation, and ADX trend strength filtering. Uses ATR-based stop losses (2x ATR) for volatility-adaptive risk management.
