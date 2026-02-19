# PROJECT 1: CROSS-ASSET LIQUIDITY FLOW MAPPER

**Category:** Cross-Asset Dynamics & Information Flow  
**Priority:** High  
**Timeline:** 3-4 months (with institutional data)  
**Status:** Planned (Q2 2026)  
**Complexity:** Advanced  

---

## EXECUTIVE SUMMARY

Markets don't move in isolation. The Cross-Asset Liquidity Flow Mapper creates a real-time influence network showing how information and liquidity flow between major asset classes, enabling traders to position based on leading indicators rather than lagging price action.

---

## THEORETICAL FOUNDATION

### Core Hypothesis
Financial markets form a complex network where:
- Information propagates through interconnected assets
- Certain assets act as "drivers" while others "follow"
- These relationships are dynamic and regime-dependent
- Traditional correlation misses causal relationships

### Mathematical Framework

**1. Granger Causality Networks**
- Tests if past values of asset X improve prediction of asset Y
- Constructs directed graphs of influence
- Identifies lead-lag relationships

**2. Transfer Entropy**
- Measures information flow from X to Y
- Captures non-linear dependencies
- Quantifies directional information transfer

```
TE(X→Y) = Σ p(y_t+1, y_t, x_t) log[p(y_t+1|y_t, x_t) / p(y_t+1|y_t)]
```

**3. Dynamic Bayesian Networks**
- Models conditional dependencies
- Adapts to regime changes
- Provides probabilistic influence estimates

**4. Time-Lagged Correlation Matrices**
- Identifies optimal lag periods
- Detects delayed transmission
- Validates causality hypotheses

---

## ASSETS TO MODEL

### Primary Universe:
1. **Currency Index:** DXY (US Dollar Index)
2. **Bonds:** US10Y (10-Year Treasury Yield)
3. **Precious Metals:** XAUUSD (Gold)
4. **Energy:** WTI/Brent Crude Oil
5. **Equity:** SPX (S&P 500)
6. **Volatility:** VIX
7. **Major FX Pairs:** EURUSD, GBPUSD, USDJPY, AUDUSD, NZDUSD, USDCAD

### Relationships to Model:
- DXY → All FX pairs
- US10Y → DXY, EURUSD
- Gold → DXY, inflation expectations
- Oil → CAD, commodity currencies
- SPX → Risk appetite, VIX
- VIX → All risk assets

---

## IMPLEMENTATION PHASES

### Phase 1: Data Infrastructure (2-3 weeks)
**Objectives:**
- Collect historical data (5+ years) for all assets
- Align timestamps across different markets
- Handle timezone conversions
- Clean and validate data quality

**Deliverables:**
- Unified database with all asset time series
- Data quality report
- Missing data handling procedures

---

### Phase 2: Static Analysis (3-4 weeks)
**Objectives:**
- Compute Granger causality on full historical dataset
- Calculate transfer entropy matrices
- Identify dominant influence pathways
- Validate against known market relationships

**Methods:**
```python
# Granger Causality (using statsmodels)
from statsmodels.tsa.stattools import grangercausalitytests

# Transfer Entropy (custom implementation or jpype)
# Bayesian Networks (pgmpy, bnlearn)
```

**Deliverables:**
- Static influence network diagram
- Ranked list of predictive relationships
- Lag period optimization results

---

### Phase 3: Dynamic/Regime-Dependent Analysis (4-5 weeks)
**Objectives:**
- Implement rolling window analysis
- Detect regime changes (volatility, trend strength)
- Compute conditional influence (high vol vs low vol)
- Build adaptive network that updates in real-time

**Regime Detection Methods:**
- Hidden Markov Models (HMM)
- GARCH-based volatility regimes
- Trend strength indicators (ADX)

**Deliverables:**
- Real-time influence score calculator
- Regime classification system
- Dynamic network visualization

---

### Phase 4: Trading Integration (3-4 weeks)
**Objectives:**
- Define trading rules based on influence shifts
- Implement position sizing based on network centrality
- Create alerts for major influence changes
- Backtest edge hypothesis

**Trading Logic:**
```
IF DXY shows high causality to EURUSD
AND DXY breaks key level
AND lag period = 2-4 hours
THEN position EURUSD in direction of DXY move
```

**Deliverables:**
- Executable trading signals
- Backtested performance metrics
- Risk management integration

---

### Phase 5: Production Deployment (2-3 weeks)
**Objectives:**
- Real-time data pipeline
- Automated calculation updates
- Dashboard for monitoring
- Alert system

---

## DATA REQUIREMENTS

### Historical Data:
- 5-10 years daily data (minimum)
- Intraday data (1-hour bars preferred, 15-min optimal)
- High-quality, gap-free time series

### Real-Time Data:
- Streaming quotes for all 11+ assets
- Update frequency: 1-minute to 1-hour
- Low latency (<1 second)

### Sources:
- Bloomberg/Reuters (institutional)
- Alpha Vantage, IEX Cloud (retail)
- FRED (bonds, economic data)
- Quandl/Nasdaq Data Link

---

## COMPUTATIONAL REQUIREMENTS

### Processing:
- Python scientific stack (NumPy, Pandas, SciPy)
- Statsmodels (Granger causality)
- JPYPE or custom code (Transfer Entropy)
- pgmpy (Bayesian Networks)

### Infrastructure:
- Medium compute (8-16 core CPU)
- 16-32GB RAM
- GPU optional but helpful for Bayesian inference
- Database: PostgreSQL/TimescaleDB

### Latency:
- Historical analysis: Batch processing acceptable
- Real-time updates: <30 seconds per calculation

---

## EXPECTED EDGE

### Primary Edge:
**Trade the driver, not the follower**
- Anticipate FX moves from bond yield shifts
- Position before DXY influence propagates
- Enter before correlation catches up

### Quantified Expectations:
- **Predictive Power:** 5-15% improvement in directional accuracy
- **Timing Edge:** 2-6 hour lead time on major moves
- **Risk Reduction:** 10-20% lower drawdowns via early signals

### Example Scenarios:
1. **US10Y spikes → EURUSD weakens**
   - Traditional: React to EURUSD price
   - This system: Position when US10Y shows influence activation

2. **Oil rallies → CAD strengthens**
   - Detect oil influence before CAD prices it in
   - Exit CAD shorts early when oil correlation rises

---

## RISK FACTORS

### Model Risks:
- Spurious correlations in certain regimes
- Lag periods may shift unexpectedly
- Relationships break during structural changes

### Data Risks:
- Quality issues in alternative data sources
- Time alignment errors across markets
- Missing data during key events

### Operational Risks:
- Real-time pipeline failures
- Computation delays during volatility spikes
- False signals during regime transitions

### Mitigation:
- Regime-conditional models
- Robust data validation
- Confidence scoring on signals
- Regular model retraining

---

## SUCCESS METRICS

### Development Metrics:
- ✅ Granger causality results match literature
- ✅ Transfer entropy shows stable relationships
- ✅ Network structure makes economic sense
- ✅ Regime detection accuracy >70%

### Trading Metrics:
- Win rate improvement: +5-10% vs baseline
- Sharpe ratio improvement: +0.2-0.5
- Maximum drawdown reduction: 10-20%
- Profitable in >60% of regimes tested

### Operational Metrics:
- Real-time update latency: <30 seconds
- System uptime: >99.5%
- Data quality score: >95%

---

## MILESTONES & DELIVERABLES

**Month 1:**
- ✅ Data infrastructure complete
- ✅ Static Granger analysis results
- ✅ Initial influence network diagram

**Month 2:**
- ✅ Transfer entropy implementation
- ✅ Bayesian network structure
- ✅ Regime detection system

**Month 3:**
- ✅ Dynamic/rolling window analysis
- ✅ Trading signal generation
- ✅ Backtest results

**Month 4:**
- ✅ Real-time pipeline
- ✅ Dashboard/monitoring
- ✅ Production deployment

---

## FUTURE EXTENSIONS

1. **Expand Asset Universe:**
   - Crypto (BTC, ETH)
   - Additional commodities
   - Emerging market currencies

2. **Higher Frequency:**
   - Tick-level analysis
   - Intraday regime detection
   - Sub-hour influence tracking

3. **Alternative Data:**
   - News sentiment flows
   - Twitter/social media analysis
   - Order flow from exchanges

4. **Machine Learning:**
   - Neural networks for influence prediction
   - Reinforcement learning for optimal timing
   - Ensemble methods combining multiple causality measures

---

## ACADEMIC REFERENCES

1. Granger, C.W.J. (1969). "Investigating Causal Relations by Econometric Models"
2. Schreiber, T. (2000). "Measuring Information Transfer"
3. Dimpfl, T. & Peter, F.J. (2013). "Using Transfer Entropy to Measure Information Flows Between Financial Markets"
4. Billio, M. et al. (2012). "Econometric Measures of Connectedness and Systemic Risk"
5. Barigozzi, M. & Brownlees, C. (2019). "NETS: Network Estimation for Time Series"

---

## CONCLUSION

The Cross-Asset Liquidity Flow Mapper represents a sophisticated approach to understanding market interconnections. By quantifying influence rather than just correlation, it provides a genuine edge in anticipating cross-market moves.

**Key Value Propositions:**
- Trade based on causality, not correlation
- Anticipate moves before price reflects them
- Adapt to changing market regimes
- Institutional-grade research applied systematically

**Next Steps:**
1. Secure access to institutional data feeds
2. Build data infrastructure
3. Implement static analysis as proof of concept
4. Develop dynamic/real-time capabilities

---

**Project Lead:** Brent Robertson  
**Status:** Awaiting institutional partnership for data access  
**Estimated Start:** Q2 2026  

---

© 2026 Pythology - Proprietary Research
