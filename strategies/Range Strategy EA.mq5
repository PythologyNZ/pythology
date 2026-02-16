//+------------------------------------------------------------------+
//|                                          Range_Strategy_EA.mq5   |
//|                                    Quantum Entanglement Trading  |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Quantum Entanglement Trading"
#property link      ""
#property version   "1.00"
#property description "Range Strategy - 2x ATR SL - Compounding"

// Input Parameters
input double   FixedLotSize = 0.1;             // Fixed lot size
input int      ATR_Period = 14;                // ATR Period
input double   SL_Multiplier = 2.0;            // Stop Loss (x ATR)
input int      EMA_Fast = 14;                  // Fast EMA
input int      EMA_Medium = 50;                // Medium EMA
input int      EMA_Slow = 200;                 // Slow EMA
input int      RSI_Period = 14;                // RSI Period
input int      ADX_Period = 14;                // ADX Period
input double   Min_ADX = 20.0;                 // Minimum ADX for entry
input double   Min_Confidence = 65.0;          // Minimum confidence (%)
input int      MagicNumber = 77777;            // Magic Number
input string   TradeComment = "Range_EA";      // Trade Comment

// Global Variables
int handleATR, handleEMA_Fast, handleEMA_Medium, handleEMA_Slow;
int handleRSI, handleADX;
double atr[], emaFast[], emaMedium[], emaSlow[], rsi[], adx[];
double plusDI[], minusDI[];

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   // Initialize indicators
   handleATR = iATR(_Symbol, PERIOD_CURRENT, ATR_Period);
   handleEMA_Fast = iMA(_Symbol, PERIOD_CURRENT, EMA_Fast, 0, MODE_EMA, PRICE_CLOSE);
   handleEMA_Medium = iMA(_Symbol, PERIOD_CURRENT, EMA_Medium, 0, MODE_EMA, PRICE_CLOSE);
   handleEMA_Slow = iMA(_Symbol, PERIOD_CURRENT, EMA_Slow, 0, MODE_EMA, PRICE_CLOSE);
   handleRSI = iRSI(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE);
   handleADX = iADX(_Symbol, PERIOD_CURRENT, ADX_Period);
   
   // Check if indicators loaded
   if(handleATR == INVALID_HANDLE || handleEMA_Fast == INVALID_HANDLE || 
      handleEMA_Medium == INVALID_HANDLE || handleEMA_Slow == INVALID_HANDLE ||
      handleRSI == INVALID_HANDLE || handleADX == INVALID_HANDLE)
   {
      Print("Failed to create indicator handles!");
      return(INIT_FAILED);
   }
   
   // Set arrays as series
   ArraySetAsSeries(atr, true);
   ArraySetAsSeries(emaFast, true);
   ArraySetAsSeries(emaMedium, true);
   ArraySetAsSeries(emaSlow, true);
   ArraySetAsSeries(rsi, true);
   ArraySetAsSeries(adx, true);
   ArraySetAsSeries(plusDI, true);
   ArraySetAsSeries(minusDI, true);
   
   Print("Range Strategy EA initialized successfully!");
   Print("Symbol: ", _Symbol);
   Print("Timeframe: ", PeriodToString(PERIOD_CURRENT));
   Print("Fixed lot size: ", FixedLotSize);
   Print("SL Multiplier: ", SL_Multiplier, "x ATR");
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Release indicator handles
   IndicatorRelease(handleATR);
   IndicatorRelease(handleEMA_Fast);
   IndicatorRelease(handleEMA_Medium);
   IndicatorRelease(handleEMA_Slow);
   IndicatorRelease(handleRSI);
   IndicatorRelease(handleADX);
   
   Print("Range Strategy EA stopped. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
{
   // Only trade on new bar
   static datetime lastBar = 0;
   datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
   
   if(currentBar == lastBar)
      return;
   
   lastBar = currentBar;
   
   // Check if we already have a position
   if(PositionSelect(_Symbol))
      return;
   
   // Update indicator data
   if(!UpdateIndicators())
      return;
   
   // Analyze market and get signal
   int signal = AnalyzeMarket();
   
   if(signal == 1) // BUY signal
   {
      OpenBuyTrade();
   }
   else if(signal == -1) // SELL signal
   {
      OpenSellTrade();
   }
}

//+------------------------------------------------------------------+
//| Update all indicator data                                          |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
   if(CopyBuffer(handleATR, 0, 0, 3, atr) < 3) return false;
   if(CopyBuffer(handleEMA_Fast, 0, 0, 3, emaFast) < 3) return false;
   if(CopyBuffer(handleEMA_Medium, 0, 0, 3, emaMedium) < 3) return false;
   if(CopyBuffer(handleEMA_Slow, 0, 0, 3, emaSlow) < 3) return false;
   if(CopyBuffer(handleRSI, 0, 0, 3, rsi) < 3) return false;
   if(CopyBuffer(handleADX, 0, 0, 3, adx) < 3) return false;
   if(CopyBuffer(handleADX, 1, 0, 3, plusDI) < 3) return false;
   if(CopyBuffer(handleADX, 2, 0, 3, minusDI) < 3) return false;
   
   return true;
}

//+------------------------------------------------------------------+
//| Analyze market and return signal                                  |
//| Returns: 1 = BUY, -1 = SELL, 0 = NONE                            |
//+------------------------------------------------------------------+
int AnalyzeMarket()
{
   double close = iClose(_Symbol, PERIOD_CURRENT, 0);
   double high = iHigh(_Symbol, PERIOD_CURRENT, 0);
   double low = iLow(_Symbol, PERIOD_CURRENT, 0);
   
   // Check ADX - need trending market
   if(adx[0] < Min_ADX)
      return 0;
   
   // Calculate confidence score
   double confidence = 0;
   int bullishSignals = 0;
   int bearishSignals = 0;
   
   // EMA Trend (40% weight)
   if(emaFast[0] > emaMedium[0] && emaMedium[0] > emaSlow[0])
   {
      bullishSignals++;
      confidence += 15;
   }
   else if(emaFast[0] < emaMedium[0] && emaMedium[0] < emaSlow[0])
   {
      bearishSignals++;
      confidence += 15;
   }
   
   // Price vs EMA (15% weight)
   if(close > emaFast[0])
   {
      bullishSignals++;
      confidence += 10;
   }
   else if(close < emaFast[0])
   {
      bearishSignals++;
      confidence += 10;
   }
   
   // RSI (20% weight)
   if(rsi[0] > 50 && rsi[0] < 70)
   {
      bullishSignals++;
      confidence += 10;
   }
   else if(rsi[0] < 50 && rsi[0] > 30)
   {
      bearishSignals++;
      confidence += 10;
   }
   
   // ADX + DI (25% weight)
   if(plusDI[0] > minusDI[0] && adx[0] > 25)
   {
      bullishSignals++;
      confidence += 15;
   }
   else if(minusDI[0] > plusDI[0] && adx[0] > 25)
   {
      bearishSignals++;
      confidence += 15;
   }
   
   // Need minimum confidence
   if(confidence < Min_Confidence)
      return 0;
   
   // More bullish than bearish signals?
   if(bullishSignals > bearishSignals && bullishSignals >= 3)
      return 1;
   
   // More bearish than bullish signals?
   if(bearishSignals > bullishSignals && bearishSignals >= 3)
      return -1;
   
   return 0;
}

//+------------------------------------------------------------------+
//| Open Buy Trade                                                     |
//+------------------------------------------------------------------+
void OpenBuyTrade()
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double sl = ask - (atr[0] * SL_Multiplier);
   double tp = 0; // No TP - let it run
   
   // Calculate lot size
   double lotSize = CalculateLotSize(ask, sl);
   
   if(lotSize < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
   {
      Print("Lot size too small: ", lotSize);
      return;
   }
   
   // Prepare trade request
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = _Symbol;
   request.volume = lotSize;
   request.type = ORDER_TYPE_BUY;
   request.price = ask;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = MagicNumber;
   request.comment = TradeComment;
   
   // Send order
   if(OrderSend(request, result))
   {
      Print("BUY order opened: ", result.order);
      Print("Volume: ", lotSize);
      Print("Entry: ", ask);
      Print("SL: ", sl);
   }
   else
   {
      Print("Error opening BUY order: ", GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Open Sell Trade                                                    |
//+------------------------------------------------------------------+
void OpenSellTrade()
{
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl = bid + (atr[0] * SL_Multiplier);
   double tp = 0; // No TP - let it run
   
   // Calculate lot size
   double lotSize = CalculateLotSize(bid, sl);
   
   if(lotSize < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
   {
      Print("Lot size too small: ", lotSize);
      return;
   }
   
   // Prepare trade request
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = _Symbol;
   request.volume = lotSize;
   request.type = ORDER_TYPE_SELL;
   request.price = bid;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = MagicNumber;
   request.comment = TradeComment;
   
   // Send order
   if(OrderSend(request, result))
   {
      Print("SELL order opened: ", result.order);
      Print("Volume: ", lotSize);
      Print("Entry: ", bid);
      Print("SL: ", sl);
   }
   else
   {
      Print("Error opening SELL order: ", GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Calculate lot size based on risk percentage                       |
//+------------------------------------------------------------------+
double CalculateLotSize(double entryPrice, double stopLoss)
{
   double lotSize = FixedLotSize;
   
   // Ensure it meets broker requirements
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double stepSize = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   if(lotSize < minLot) lotSize = minLot;
   if(lotSize > maxLot) lotSize = maxLot;
   
   // Round to step
   lotSize = MathFloor(lotSize / stepSize) * stepSize;
   
   Print("Using fixed lot size: ", lotSize);
   return NormalizeDouble(lotSize, 2);
}

//+------------------------------------------------------------------+
//| Period to string converter                                         |
//+------------------------------------------------------------------+
string PeriodToString(ENUM_TIMEFRAMES period)
{
   switch(period)
   {
      case PERIOD_M1:  return "M1";
      case PERIOD_M5:  return "M5";
      case PERIOD_M15: return "M15";
      case PERIOD_M30: return "M30";
      case PERIOD_H1:  return "H1";
      case PERIOD_H4:  return "H4";
      case PERIOD_D1:  return "D1";
      case PERIOD_W1:  return "W1";
      case PERIOD_MN1: return "MN1";
      default: return "Unknown";
   }
}
//+------------------------------------------------------------------+