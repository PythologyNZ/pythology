# PYTHOLOGY RESEARCH AGENDA
## The Science of Algorithmic Trading — 10 Year Vision

**Founder & Chief Strategy Architect:** Brent Robertson
**Contact:** pythology@outlook.com
**Portfolio:** github.com/PythologyNZ/pythology
**Last Updated:** March 2026

---

## EXECUTIVE SUMMARY

Pythology's research agenda represents a comprehensive 10-year vision for advancing systematic trading through the application of advanced mathematics, physics, and computer science to financial markets.

**Current Status:**
- **Phase 1 (Complete):** Core profitable strategies deployed and forward testing — 66.7%+ win rate, profit factor 14.29 confirmed on live demo
- **Phase 2 (In Progress):** Advanced research prototypes — 11 buildable projects with current infrastructure
- **Phase 3 (Planned):** Institutional-grade microstructure projects — unlocked via data partnerships

**Research Philosophy:**
We treat markets as complex adaptive systems rather than purely stochastic processes. Our approach combines:
- Econophysics and complexity theory
- Information theory and causality analysis
- Machine learning and statistical modelling
- Smart Money Concepts (SMC) — order flow, liquidity dynamics, and institutional behaviour

**Phase 2 Design Principle:**
Every Phase 2 project is buildable today using OHLCV data, MT5 integration, and Python. No institutional data dependencies. No team required. This is deliberate — the goal is to prove that a solo researcher with the right frameworks can build institutional-grade tools from first principles.

---

## PHASE 1 — COMPLETE ✅

### Core Trading Infrastructure
- ✅ **Sentinel SMC Engine** — Smart Money Concepts signal detection across FX, metals, crypto, indices, stocks
  - Order Block detection with market structure confirmation
  - Liquidity sweep identification
  - Fair Value Gap (FVG) and displacement analysis
  - Coil/Impulse compression-expansion pattern detection
  - Multi-timeframe structure: M5 entry confirmation, M15/H1/Daily/Weekly trend alignment
- ✅ **Swing-Based Trailing Stop System** — Trails behind confirmed M15/H1 swing highs/lows, not ATR steps
- ✅ **ML Regime Classifier v4** — Binary CNN + Random Forest ensemble, AUC 0.644, production-validated
  - Forward-looking labels: "does a significant move follow in the next 5 bars?"
  - Grade A/B/C signal tiering integrated into Sentinel entry logic
- ✅ **Volatility Forecasting Surface** — 95.2% directional accuracy (Apple: 99.9%)
- ✅ **Synthetic FX Pair Generator** — Novel cross-pair construction revealing hidden relationships
- ✅ **News Event Filter** — ForexFactory calendar integration, auto-standdown before high-impact events
- ✅ **Universal Strategy Optimizer** — Parameter sweep and validation framework

---

## PHASE 2 — IN PROGRESS 🔄

*All Phase 2 projects buildable with current infrastructure. Sequenced by build priority and dependency.*

---

### PROJECT 1 — Self-Evolving Strategy Generator
**Category:** Meta-Strategy | **Priority:** 🔴 High | **Timeline:** 2–3 months | **Status:** Starting

**Concept:**
Define Sentinel's entry logic as a "genome" — the weights and thresholds for each confirmation signal (OB strength, FVG size, sweep distance, coil score, regime confidence, timeframe alignment). A genetic algorithm breeds, mutates, and selects the fittest parameter combinations across historical trade data.

**What it solves:**
Manual parameter tuning is human-limited. Markets evolve — what worked in a trending regime may fail in ranging conditions. This system discovers optimal parameter sets automatically, per asset class and per regime type.

**Implementation Plan:**
- Define parameter genome: entry thresholds, confirmation weights, ATR multipliers, coil sensitivity, trailing step size
- Fitness function: Sharpe ratio + profit factor + max drawdown penalty on backtested trades
- Genetic operations: crossover (blend two winning genomes), mutation (random parameter shift), selection (top 20% survive)
- Output: asset-specific and regime-specific parameter sets pushed into Sentinel's config
- Integration: evolve on a rolling 90-day window, re-publish parameters weekly

**Expected outcome:**
Sentinel gains a wider, smarter scope of entry parameters. Stops relying on hand-tuned values — discovers configurations a human would never think to test.

---

### PROJECT 2 — Walk-Forward Optimizer
**Category:** Meta-Strategy | **Priority:** 🔴 High | **Timeline:** 3–4 weeks | **Status:** Starting

**Concept:**
Continuously re-optimises Sentinel's parameters on a rolling window. Prevents parameter decay as market regimes shift. Feeds validated parameter sets into Project 1's genome pool.

**Implementation Plan:**
- Rolling 90-day in-sample / 30-day out-of-sample validation windows
- Optimise: entry thresholds, confirmation requirements, trailing stop sensitivity per asset
- Track parameter stability — flag when parameters shift significantly (regime change signal in itself)
- Publish optimised config to Sentinel automatically

**Expected outcome:**
Sentinel stays calibrated to current market conditions without manual intervention. Parameter drift becomes an early warning system.

---

### PROJECT 3 — Strategy Edge Decomposition Engine
**Category:** Meta-Strategy | **Priority:** 🔴 High | **Timeline:** 1–2 months | **Status:** Pending trade DB (4 weeks data)

**Concept:**
Systematically decompose where Sentinel's edge actually comes from. Not just win rate — *which specific confluence of signals* produces the best outcomes, and under what conditions does that edge disappear.

**Implementation Plan:**
- Mine Sentinel's trade database (building now — 4 weeks to sufficient data)
- Decompose performance by: signal type, asset class, session, regime, day of week, news proximity, coil vs standard entry
- Build edge heatmap: "Grade A OB + FVG + sweep on GER40 during London open = 71% win rate, 2.3R avg"
- Identify edge killers: conditions where any entry type underperforms
- Feed findings back into signal grading and position sizing

**Expected outcome:**
Replace intuition with data on exactly what works. Institutional-quality signal attribution that can be shown to fund managers as evidence of systematic edge.

---

### PROJECT 4 — Drawdown DNA Analyzer
**Category:** Risk Intelligence | **Priority:** 🔴 High | **Timeline:** 1–2 months | **Status:** Pending trade DB

**Concept:**
Analyse Sentinel's losing trades to find the DNA they share. Build a pre-entry filter that recognises high-risk conditions before they become losses.

**Implementation Plan:**
- Cluster losing trades by shared characteristics: time of day, session, news proximity, low volume conditions, counter-trend entries, spread widening, regime mismatch
- Build "DNA fingerprint" of losing trade conditions
- Pre-entry check: score incoming signal against loss DNA — if match score >threshold, reduce size or skip
- Track: does avoiding high-DNA conditions improve overall performance?

**Expected outcome:**
Sentinel learns from its own mistakes systematically. Drawdown periods become shorter as the system recognises and avoids the conditions that caused them.

---

### PROJECT 5 — Adaptive Position Sizing Engine
**Category:** Risk Intelligence | **Priority:** 🟡 Medium | **Timeline:** 3–4 weeks | **Status:** Starting

**Concept:**
Move beyond fixed percentage risk sizing. Position size adapts dynamically to current conditions.

**Sizing inputs:**
- Regime confidence score (ML classifier output) — higher confidence = larger size
- Recent Sentinel performance (hot/cold streak adjustment — Kelly-inspired)
- Asset correlation matrix — reduce combined exposure when holding correlated positions
- Volatility percentile — scale down in abnormally high volatility environments
- Signal grade (A/B/C from ensemble filter)

**Expected outcome:**
Risk-adjusted returns improve. Biggest positions taken when conditions are most favourable. Exposure automatically reduces during uncertain or correlated periods.

---

### PROJECT 6 — Economic Event Impact Scorer
**Category:** Market Intelligence | **Priority:** 🟡 Medium | **Timeline:** 1–2 months | **Status:** ForexFactory data already integrated

**Concept:**
ForexFactory calendar data is already flowing into Sentinel for news avoidance. This project extends that into a full impact scoring system — not just "avoid news" but "quantify how this event type historically moves each asset."

**Implementation Plan:**
- Build historical database: event type × asset × outcome (pip/point move, direction, duration)
- Score model: "NFP release historically moves XAUUSD 40+ points within 15 minutes 73% of the time"
- Pre-trade filter levels: AVOID (within 30min), REDUCE SIZE (within 2hr), NORMAL (beyond 2hr)
- Post-event opportunity: some setups are strongest immediately after event volatility settles — detect and flag

**Expected outcome:**
Sentinel stops treating all news as equal. High-impact events become opportunities to size down *and* opportunities to re-enter post-spike with high confidence.

---

### PROJECT 7 — Session Handoff Pattern Detector
**Category:** Market Intelligence | **Priority:** 🟡 Medium | **Timeline:** 2–3 months | **Status:** Morning briefing MVP planned

**Concept:**
Markets behave differently across sessions — Asia, London, New York — and the behaviour of one session often predicts the next. Build an ML model that detects inter-session patterns and generates a pre-session briefing.

**Implementation Plan:**
- Pull M15 data for each completed session across all Sentinel assets
- Extract session features: range size, directional bias, high/low timing, volume profile, breakout vs consolidation
- After 4–6 weeks of data: train classifier on session transitions
- Patterns to detect: "Asia tight range → London/NY breakout", "London swept highs → NY reversal", "All three sessions trending same direction → continuation trade"
- Morning briefing output: plain-language summary before Asia open with probability estimates

**Expected outcome:**
Sentinel enters each session with context. High-probability session setups get priority. Contrarian setups flagged as lower confidence.

---

### PROJECT 8 — Correlation Breakdown Detector
**Category:** Market Intelligence | **Priority:** 🟡 Medium | **Timeline:** 1–2 months | **Status:** Starting

**Concept:**
Normal inter-market correlations (Gold vs DXY, Oil vs CAD, VIX vs SPX) are well-established. When these correlations break down — assets that normally move together diverge or invert — it signals a regime shift or large institutional positioning underway. These moments often precede significant moves.

**Implementation Plan:**
- Build rolling correlation matrix across all Sentinel assets (20-day and 5-day windows)
- Detect significant deviation from historical norm (z-score based)
- Flag active divergences: "Gold and DXY both rising — USD correlation broken, watch for resolution"
- Feed divergence signals into Sentinel as context layer — can confirm or veto OB entries

**Expected outcome:**
Early warning system for regime shifts. Correlation breakdowns become high-conviction entry signals rather than confusing noise.

---

### PROJECT 9 — Intermarket Divergence Signals
**Category:** Market Intelligence | **Priority:** 🟡 Medium | **Timeline:** 1–2 months | **Status:** Starting

**Concept:**
Extend correlation analysis into directional divergence signals — specifically looking for cases where price action in one asset strongly predicts an imminent move in another.

**Key divergence pairs:**
- DXY up + Gold up → Gold correction incoming
- NAS100 ripping + VIX not falling → false rally, fade incoming
- Oil surging + Energy stocks lagging → catch-up trade
- Bond yields rising + equities also rising → one of them is wrong
- GBP/USD and EUR/USD diverging → EUR or GBP specific catalyst, not USD-driven

**Implementation Plan:**
- Define divergence conditions for 10–15 key pairs
- Backtest divergence → resolution timing on historical data
- Score divergences by historical resolution rate and average move size
- Integrate as Sentinel pre-entry confirmation: divergence in same direction = confirmation, against = caution flag

**Expected outcome:**
Multi-market context layer for Sentinel. Entries aligned with intermarket confirmation carry higher size. Entries against divergence signals get reduced or skipped.

---

### PROJECT 10 — Fractal Dimension & Market Compression Detector
**Category:** Volatility & Regime | **Priority:** 🟠 Lower | **Timeline:** 2–3 months | **Status:** Planned

**Concept:**
Fractal dimension measures the "roughness" of a price series — a trending market has low fractal dimension (smooth, directional), a ranging market has high fractal dimension (choppy, mean-reverting). Detecting compression (fractal dimension dropping toward trending state) before it happens is a leading indicator for breakout.

**Implementation Plan:**
- Calculate Hurst Exponent and Fractal Dimension on rolling windows across all assets
- Build compression score: trending toward directional state = compression building
- Combine with ATR percentile and Bollinger Band Width for multi-dimensional compression signal
- Feed into Coil detection in Sentinel — fractal compression + ATR shrink = very high conviction coil

**Expected outcome:**
Coil detection becomes significantly more robust. Fractal compression is a mathematically-grounded confirmation that compression is genuine, not just low-volatility noise.

---

### PROJECT 11 — Regime Stability & Structural Fragility Index
**Category:** Volatility & Regime | **Priority:** 🟠 Lower | **Timeline:** 2–3 months | **Status:** Planned

**Concept:**
A market regime (trend, range, reversal) is not just a label — it has a stability score. A regime that is "fragile" is about to break. Build an index that measures how close each asset is to a regime change.

**Implementation Plan:**
- Multi-timeframe regime detection: M15, H1, Daily, Weekly all classified
- Stability score: agreement across timeframes = stable, disagreement = fragile
- Rate of change: how fast is the regime classification shifting?
- Fragility spike = high probability of imminent structure break
- Integrate with Sentinel: fragile regime = look for MSS/CHoCH entry, stable regime = trend continuation entries

**Expected outcome:**
Sentinel knows *when* to expect structure breaks vs when to ride trend. Regime fragility becomes a leading indicator rather than a lagging observation.

---

## PHASE 3 — INSTITUTIONAL PARTNERSHIPS REQUIRED 🏛️

*The following projects require institutional data infrastructure: tick data, Level 2 order book, high-frequency sequences, or significant cloud compute. These are planned for activation once data partnerships are established.*

| Project | Description | Data Required |
|---------|-------------|---------------|
| P3-1 | Information Flow & Transfer Entropy Network | Tick data, Level 2 |
| P3-2 | Market Microstructure Imbalance Detector | Level 2, tick data |
| P3-3 | Liquidity Topology Mapping | Order book depth |
| P3-4 | Path-Dependence & Order Memory | Tick sequences |
| P3-5 | Market as Non-Linear Dynamical System | High-frequency data |
| P3-6 | Phase Transition Detection | Multiple HF sources |
| P3-7 | Microstructure Entropy Collapse | Order flow + executions |

*Note: Prototyping work on Phase 2 projects (particularly Projects 8–11) will build the theoretical foundation and codebase that Phase 3 projects extend. The transition from Phase 2 → Phase 3 is an infrastructure upgrade, not a methodology change.*

---

## IMPLEMENTATION ROADMAP

### Month 1–2 (Now):
- 🔄 **Project 1** — Self-Evolving Strategy Generator: genome design + GA framework
- 🔄 **Project 2** — Walk-Forward Optimizer: rolling window validation live
- 🔄 **Project 5** — Adaptive Position Sizing: regime-aware sizing integrated into Sentinel
- 🔄 **Project 8** — Correlation Breakdown Detector: rolling correlation matrix + divergence alerts

### Month 2–3:
- 🔄 **Project 3** — Strategy Edge Decomposition: trade DB has sufficient data, mine it
- 🔄 **Project 4** — Drawdown DNA Analyzer: loss clustering + pre-entry DNA filter
- 🔄 **Project 6** — Economic Event Impact Scorer: ForexFactory historical scoring model
- 🔄 **Project 9** — Intermarket Divergence Signals: directional pair signals

### Month 3–5:
- 🔄 **Project 7** — Session Handoff Pattern Detector: ML model on 6+ weeks session data
- 🔄 **Project 10** — Fractal Dimension & Market Compression
- 🔄 **Project 11** — Regime Stability & Structural Fragility Index

### Year 2–3:
- Integration of all Phase 2 components into unified Sentinel intelligence layer
- Phase 3 activation via institutional data partnerships
- Production deployment at scale

---

## RESOURCE REQUIREMENTS MATRIX

| Project | Data Needs | Compute | Timeline | Status |
|---------|-----------|---------|----------|--------|
| 1 — Self-Evolving Strategy Generator | Sentinel trade history | Medium | 2–3 months | 🔴 Starting |
| 2 — Walk-Forward Optimizer | MT5 OHLCV historical | Low | 3–4 weeks | 🔴 Starting |
| 3 — Edge Decomposition Engine | Trade database | Low | 1–2 months | ⏳ Needs 4wk data |
| 4 — Drawdown DNA Analyzer | Trade database | Low | 1–2 months | ⏳ Needs 4wk data |
| 5 — Adaptive Position Sizing | Live regime scores | Low | 3–4 weeks | 🔴 Starting |
| 6 — Event Impact Scorer | ForexFactory historical | Low | 1–2 months | 🟡 Planned |
| 7 — Session Handoff Detector | M15 multi-asset | Medium | 2–3 months | 🟡 Planned |
| 8 — Correlation Breakdown | Multi-asset OHLCV | Low | 1–2 months | 🔴 Starting |
| 9 — Intermarket Divergence | Multi-asset OHLCV | Low | 1–2 months | 🟡 Planned |
| 10 — Fractal Dimension | Historical OHLCV | Medium | 2–3 months | 🟠 Later |
| 11 — Regime Stability Index | Multi-TF OHLCV | Medium | 2–3 months | 🟠 Later |

---

## EXPECTED OUTCOMES BY PHASE

### Phase 2 Complete — Sentinel becomes:
- **Self-calibrating:** Parameters evolve with market conditions automatically
- **Self-aware:** Knows its own edge, its own failure modes, and adapts
- **Context-rich:** Session history, intermarket signals, economic events all feeding decisions
- **Risk-intelligent:** Sizing adapts to confidence, correlation, and regime stability

### Phase 3 Complete — Sentinel becomes:
- **Microstructure-aware:** Order flow and institutional positioning visible in real time
- **Entropy-sensitive:** Detects market compression and phase transitions before they're visible
- **Full institutional grade:** Capable of running on funded accounts at scale

---

## COMPETITIVE POSITIONING

> *"Most retail algorithmic systems optimise for one thing: entry accuracy. Pythology's Phase 2 pipeline targets something fundamentally different — a system that understands its own edge, learns from its own mistakes, adapts to regime changes in real time, and integrates multi-market context before every decision. This is not a trading bot. It is a systematic research platform that happens to trade."*

---

*Pythology — The Science of Algorithmic Trading*
*github.com/PythologyNZ/pythology*
