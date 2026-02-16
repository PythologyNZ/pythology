//+------------------------------------------------------------------+
//|                                    Pending_Reversal_EA.mq5       |
//|                                    Quantum Entanglement Trading  |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Quantum Entanglement Trading"
#property link      ""
#property version   "1.00"
#property description "Pending Reversal Strategy - Bollinger Bounce"

// Risk mode enum - MUST BE DECLARED BEFORE INPUTS
enum ENUM_RISK_MODE
{
   RISK_PERCENT,    // Percentage of balance
   RISK_FIXED       // Fixed lot size
};

// Input Parameters
input group "Risk Management"
input ENUM_RISK_MODE RiskMode = RISK_PERCENT;  // Risk Mode
input double   RiskPercent = 1.0;              // Risk per trade (%) - if using percentage
input double   FixedLotSize = 0.1;             // Fixed lot size - if using fixed
input group "Strategy Parameters"
input int      EMA_Period = 100;               // EMA Period
input int      BB_Period = 10;                 // Bollinger Bands Period
input double   BB_Deviation = 2.3;             // BB Deviation
input double   Risk_Reward = 2.0;              // Risk:Reward Ratio
input double   Min_Confidence = 65.0;          // Minimum confidence (%)
input group "General"
input int      MagicNumber = 88888;            // Magic Number
input string   TradeComment = "PendingRev";    // Trade Comment

// Global Variables
int handleEMA_High, handleEMA_Low, handleBB;
double emaHigh[], emaLow[], bbUpper[], bbMiddle[], bbLower[];

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   // Create EMA on High
   handleEMA_High = iMA(_Symbol, PERIOD_CURRENT, EMA_Period, 0, MODE_EMA, PRICE_HIGH);
   
   // Create EMA on Low
   handleEMA_Low = iMA(_Symbol, PERIOD_CURRENT, EMA_Period, 0, MODE_EMA, PRICE_LOW);
   
   // Create Bollinger Bands
   handleBB = iBands(_Symbol, PERIOD_CURRENT, BB_Period, 0, BB_Deviation, PRICE_CLOSE);
   
   // Check if indicators loaded
   if(handleEMA_High == INVALID_HANDLE || handleEMA_Low == INVALID_HANDLE || handleBB == INVALID_HANDLE)
   {
      Print("Failed to create indicator handles!");
      return(INIT_FAILED);
   }
   
   // Set arrays as series
   ArraySetAsSeries(emaHigh, true);
   ArraySetAsSeries(emaLow, true);
   ArraySetAsSeries(bbUpper, true);
   ArraySetAsSeries(bbMiddle, true);
   ArraySetAsSeries(bbLower, true);
   
   Print("Pending Reversal EA initialized successfully!");
   Print("Symbol: ", _Symbol);
   Print("Timeframe: ", PeriodToString(PERIOD_CURRENT));
   Print("Risk Mode: ", RiskMode == RISK_PERCENT ? "Percentage" : "Fixed Lot");
   if(RiskMode == RISK_PERCENT)
      Print("Risk per trade: ", RiskPercent, "%");
   else
      Print("Fixed lot size: ", FixedLotSize);
   Print("Risk:Reward: ", Risk_Reward, ":1");
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   IndicatorRelease(handleEMA_High);
   IndicatorRelease(handleEMA_Low);
   IndicatorRelease(handleBB);
   
   Print("Pending Reversal EA stopped. Reason: ", reason);
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
   if(CopyBuffer(handleEMA_High, 0, 0, 3, emaHigh) < 3) return false;
   if(CopyBuffer(handleEMA_Low, 0, 0, 3, emaLow) < 3) return false;
   if(CopyBuffer(handleBB, 0, 0, 3, bbUpper) < 3) return false;
   if(CopyBuffer(handleBB, 1, 0, 3, bbMiddle) < 3) return false;
   if(CopyBuffer(handleBB, 2, 0, 3, bbLower) < 3) return false;
   
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
   
   double prev_high = iHigh(_Symbol, PERIOD_CURRENT, 1);
   double prev_low = iLow(_Symbol, PERIOD_CURRENT, 1);
   double prev_close = iClose(_Symbol, PERIOD_CURRENT, 1);
   
   // LONG Setup: Uptrend + BB bounce
   if(close > emaLow[0])  // In uptrend
   {
      // Price touched or broke lower BB on current or previous bar
      if(low <= bbLower[0] || prev_low <= bbLower[1])
      {
         // Current bar closed back above lower BB (bounce confirmed)
         if(close > bbLower[0])
         {
            return 1;  // BUY signal
         }
      }
   }
   
   // SHORT Setup: Downtrend + BB bounce
   if(close < emaHigh[0])  // In downtrend
   {
      // Price touched or broke upper BB on current or previous bar
      if(high >= bbUpper[0] || prev_high >= bbUpper[1])
      {
         // Current bar closed back below upper BB (bounce confirmed)
         if(close < bbUpper[0])
         {
            return -1;  // SELL signal
         }
      }
   }
   
   return 0;  // No signal
}

//+------------------------------------------------------------------+
//| Open Buy Trade                                                     |
//+------------------------------------------------------------------+
void OpenBuyTrade()
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   
   // Find recent low for SL (last 20 bars)
   double sl = ask;
   for(int i = 1; i <= 20; i++)
   {
      double tempLow = iLow(_Symbol, PERIOD_CURRENT, i);
      if(tempLow < sl)
         sl = tempLow;
   }
   
   // TP based on Risk:Reward
   double slDistance = ask - sl;
   double tp = ask + (slDistance * Risk_Reward);
   
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
      Print("SL: ", sl, " (", slDistance / _Point, " points)");
      Print("TP: ", tp, " (", (tp - ask) / _Point, " points)");
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
   
   // Find recent high for SL (last 20 bars)
   double sl = bid;
   for(int i = 1; i <= 20; i++)
   {
      double tempHigh = iHigh(_Symbol, PERIOD_CURRENT, i);
      if(tempHigh > sl)
         sl = tempHigh;
   }
   
   // TP based on Risk:Reward
   double slDistance = sl - bid;
   double tp = bid - (slDistance * Risk_Reward);
   
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
      Print("SL: ", sl, " (", slDistance / _Point, " points)");
      Print("TP: ", tp, " (", (bid - tp) / _Point, " points)");
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
   // If using fixed lot size mode, return that
   if(RiskMode == RISK_FIXED)
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
      
      Print("Using FIXED lot size: ", lotSize);
      return NormalizeDouble(lotSize, 2);
   }
   
   // Otherwise calculate based on risk percentage
   double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = accountBalance * (RiskPercent / 100.0);
   double pointValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   
   double slDistance = MathAbs(entryPrice - stopLoss);
   double slPoints = slDistance / tickSize;
   
   double lotSize = riskAmount / (slPoints * pointValue);
   
   // Round to step
   double stepSize = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   lotSize = MathFloor(lotSize / stepSize) * stepSize;
   
   // Check limits
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   
   // CRITICAL: Ensure we meet minimum lot size
   if(lotSize < minLot) 
   {
      Print("Calculated lot ", lotSize, " below minimum ", minLot, " - using minimum");
      lotSize = minLot;
   }
   if(lotSize > maxLot) 
   {
      Print("Calculated lot ", lotSize, " above maximum ", maxLot, " - using maximum");
      lotSize = maxLot;
   }
   
   // For indices (min lot 0.1), ensure we're at least at minimum
   if(StringFind(_Symbol, "NAS") >= 0 || StringFind(_Symbol, "SP") >= 0 || 
      StringFind(_Symbol, "GER") >= 0 || StringFind(_Symbol, "UK") >= 0 || 
      StringFind(_Symbol, "DJ") >= 0)
   {
      if(lotSize < 0.1)
      {
         Print("Index detected - forcing minimum 0.1 lot");
         lotSize = 0.1;
      }
   }
   
   Print("Using PERCENTAGE-based lot size: ", lotSize, " (", RiskPercent, "% of $", accountBalance, ")");
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