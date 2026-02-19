# MACHINE LEARNING & AI EXPERIENCE

**Brent Robertson - Pythology**  
**Contact:** pythology@outlook.com  
**Portfolio:** github.com/PythologyNZ/pythology  

---

## OVERVIEW

In addition to quantitative trading strategy development, I have hands-on experience building advanced neural network architectures for financial market prediction, including cutting-edge 2D State Space Models and Transformer-based systems.

---

## PROJECT 1: CHIMERA - 2D STATE SPACE MODEL FOR FOREX PREDICTION

### Concept
Built a novel 2D State Space Model (Chimera architecture) for predicting market reversals in forex markets, based on recent research: *"Chimera: Effectively Modeling Multivariate Time Series with 2-Dimensional State Space Models"*

### Architecture Details

**Core Innovation:**
- Dual-dimension modeling: Temporal axis + Feature axis
- Bidirectional LSTM for temporal patterns (2 layers, 128 hidden units)
- Bidirectional LSTM for cross-feature relationships
- Multi-head attention mechanism (4 heads) for pattern emphasis
- 3-class output: DOWN (-1), NEUTRAL (0), UP (+1)

**Network Structure:**
```python
class Chimera2DSSM(nn.Module):
    - Temporal LSTM: Input(14 features) → Hidden(64) → Bidirectional → Output(128)
    - Feature Projection: 50 timesteps → 64 dimensions
    - Variable LSTM: Process features across time
    - Multi-head Attention: 4 heads, dropout 0.2
    - Classifier: 256 → 128 → 64 → 3 classes
```

**Input Features (14 dimensions):**
- OHLC (Open, High, Low, Close)
- Wave Trend indicators (fast/slow, 2D: wt1, wt2)
- RSI (Relative Strength Index)
- ATR (Average True Range)
- Bollinger Bands (upper, middle, lower)
- Sigma Score (statistical deviation)

**Training Parameters:**
- Lookback window: 50 bars
- Batch size: 32
- Learning rate: 0.001 (Adam optimizer)
- Epochs: 100 with early stopping
- Validation split: 20%
- Dropout: 0.2 throughout

### Implementation

**Technologies:**
- PyTorch (deep learning framework)
- Flask (REST API server for real-time predictions)
- ONNX (model export for cross-platform deployment)
- MT5 integration via HTTP requests

**Production Setup:**
- Flask server running locally (port 5000)
- Real-time prediction endpoint (`/predict`)
- Health monitoring endpoint (`/health`)
- Statistics tracking endpoint (`/stats`)
- Accepts 50x14 feature matrix, returns probability distribution

### Challenges & Learnings

**Technical Challenges:**
- Server-MT5 communication latency issues
- Model struggled with real-time market noise vs training data
- Needed more sophisticated feature engineering
- Required larger dataset for convergence

**Key Learnings:**
- Understanding of bidirectional LSTM architecture
- Implementation of attention mechanisms
- Production model deployment (Flask API)
- Model serialization (PyTorch → ONNX)
- Real-time inference pipeline design

**What I'd Do Differently:**
- Implement proper feature normalization per market regime
- Add ensemble approach with multiple lookback windows
- Use more sophisticated data augmentation
- Implement online learning for model adaptation

---

## PROJECT 2: SENTINEL FOREX AI - TRANSFORMER HYBRID MODEL

### Concept
Developed a Transformer-based architecture for XAUUSD (Gold) H1 timeframe direction prediction, leveraging self-attention mechanisms for temporal pattern recognition.

### Architecture Details

**Core Components:**
```python
class ForexTransformer(nn.Module):
    - Input Projection: Features → d_model (64 dimensions)
    - Transformer Encoder: 3 layers, 8 attention heads
    - Output Classifier: d_model → 32 → 2 classes (UP/DOWN)
```

**Transformer Configuration:**
- Model dimension (d_model): 64
- Number of attention heads: 8
- Number of encoder layers: 3
- Dropout rate: 0.1
- Batch-first processing for efficiency

**Sequence Parameters:**
- Sequence length: 96 bars (4 days of hourly data)
- Prediction horizon: 1 hour ahead
- Binary classification: UP vs DOWN

### Training Methodology

**Data Pipeline:**
- Custom `XAUUSDDataPipeline` class
- Automated feature engineering
- Sequence creation with sliding window
- StandardScaler normalization
- Train/validation split (80/20) with stratification

**Training Details:**
- Optimizer: Adam
- Learning rate: 0.001
- Batch size: 64
- Epochs: 50
- Loss function: CrossEntropyLoss
- Validation frequency: Every 10 epochs

**Best Practices Implemented:**
- Random seed management for reproducibility
- Separate validation set for hyperparameter tuning
- Model checkpointing (save best validation accuracy)
- Comprehensive logging and metrics tracking

### Results & Analysis

**Model Performance:**
- Successfully trained on multi-year XAUUSD dataset
- Validation accuracy tracked across training
- Model saved in dual format:
  - `sentinel_forex_model_best.pth` (best validation checkpoint)
  - `sentinel_forex_model_final.pth` (with full metadata + scaler)

**Challenges:**
- Market direction prediction proved difficult (inherent noise)
- Needed more sophisticated feature engineering
- Required longer training periods
- Hyperparameter tuning was time-intensive

**Key Insights:**
- Transformers excel at capturing long-range dependencies
- Self-attention provides interpretability via attention weights
- Financial markets require domain-specific feature engineering
- Ensemble methods would likely improve robustness

---

## TECHNICAL SKILLS DEMONSTRATED

### Deep Learning Frameworks:
- **PyTorch:** Model architecture design, training loops, optimization
- **Neural Network Design:** LSTMs, Transformers, Attention mechanisms
- **Model Deployment:** Flask APIs, ONNX export, production inference

### Machine Learning Concepts:
- Bidirectional RNNs for temporal modeling
- Multi-head attention mechanisms
- State space models for time series
- Sequence-to-sequence architectures
- Binary and multi-class classification

### Software Engineering:
- Python OOP (custom classes, inheritance)
- RESTful API design (Flask)
- Model serialization and versioning
- Data pipeline architecture
- Error handling and logging

### Data Science:
- Feature engineering for financial data
- Time series preprocessing
- Train/test/validation methodology
- Hyperparameter optimization
- Model evaluation metrics

---

## APPLICATIONS TO QUANTITATIVE FINANCE

### How ML Enhances Trading:
1. **Pattern Recognition:** Neural networks detect non-linear patterns humans miss
2. **Regime Detection:** Models can classify market states (trending vs ranging)
3. **Feature Importance:** Attention weights reveal which indicators matter most
4. **Ensemble Strategies:** ML models complement rule-based systems
5. **Adaptive Learning:** Models can retrain as markets evolve

### Integration with Pythology Strategies:
- Use ML for signal filtering (confirm rule-based signals)
- Employ transformers for volatility regime classification
- Leverage attention for dynamic indicator weighting
- Build hybrid systems (ML + traditional technical analysis)

---

## FUTURE ML PROJECTS (Research Pipeline)

### Planned Developments:
1. **Ensemble Meta-Learner:** Combine multiple model architectures
2. **Reinforcement Learning:** For position sizing and trade timing
3. **Graph Neural Networks:** For cross-asset relationship modeling
4. **Few-Shot Learning:** Rapid adaptation to new market regimes
5. **Explainable AI:** Interpretable models for risk management

---

## CODE REPOSITORIES

**Available Files:**
- `train_chimera.py` - Complete Chimera 2D-SSM training pipeline
- `chimera_server.py` - Flask API for real-time predictions
- `transformer_model.py` - Sentinel Forex Transformer architecture
- `chimera_model.pth` - Trained model weights
- `chimera_model.onnx` - Exported ONNX format
- `Chimera_Live_Predictions.mq5` - MT5 integration code

**Notebook/Documentation:**
- Full implementation with detailed comments
- Architecture diagrams and explanations
- Training logs and performance metrics

---

## RELEVANCE TO APPLIED QUANTITATIVE ANALYST ROLES

### DataAnnotation (AI Training):
- **Direct Experience:** Training and evaluating neural network models
- **Model Assessment:** Understanding architecture strengths/weaknesses
- **Problem Solving:** Debugging convergence issues, improving predictions
- **Technical Writing:** Documenting model architectures and decisions

### Novartis Norge (Junior Quant Analyst):
- **Quantitative Modeling:** Experience with statistical and ML models
- **Programming:** Production-quality Python code
- **Research:** Self-directed learning of cutting-edge architectures
- **Problem-Solving:** Tackling complex prediction problems systematically

---

## KEY TAKEAWAYS

**What I Learned:**
- Deep learning is powerful but requires careful feature engineering
- Financial markets are noisy - models must be robust
- Production deployment is as important as model performance
- Ensemble methods and hybrid approaches often outperform single models

**What Makes Me Different:**
- Self-taught deep learning from academic papers
- Built production systems, not just notebooks
- Understand both ML theory and practical trading application
- Can bridge gap between data science and financial markets

**What I Bring:**
- Ability to learn and implement cutting-edge research
- Strong Python and PyTorch skills
- Production deployment experience
- Systematic problem-solving methodology
- Passion for continuous learning and improvement

---

## CONCLUSION

While these projects didn't produce perfect market prediction systems (no ML model does!), they demonstrate my ability to:
- Understand and implement advanced neural architectures
- Build production-ready ML systems
- Debug and iterate on complex models
- Apply ML to real-world financial problems
- Document and communicate technical concepts

**Most importantly:** I'm not afraid to tackle ambitious projects, learn from challenges, and continuously improve my approach.

---

**Contact:** pythology@outlook.com  
**GitHub:** github.com/PythologyNZ/pythology  
**LinkedIn:** /in/brentrobertson-pythology  

---

© 2026 Pythology - Machine Learning for Systematic Trading
