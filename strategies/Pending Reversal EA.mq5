//+------------------------------------------------------------------+
//|                                    Pending_Reversal_EA.mq5       |
//|                        Quantum Entanglement Trading - Pythology  |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Quantum Entanglement Trading - Pythology"
#property link      ""
#property version   "1.00"
#property description "Pending Reversal Strategy - Bollinger Bounce"

// Input Parameters
input double   FixedLotSize = 0.1;             // Fixed lot size
input int      EMA_Period = 100;               // EMA Period
input int      BB_Period = 10;                 // Bollinger Bands Period
input double   BB_Deviation = 2.3;             // BB Deviation
input double   Risk_Reward = 2.0;              // Risk:Reward Ratio
input double   Min_Confidence = 65.0;          // Minimum confidence (%)
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
   
   // Calculate lot size - SIMPLIFIED
   double lotSize = FixedLotSize;
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double stepSize = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   // Ensure minimum
   if(lotSize < minLot) lotSize = minLot;
   if(lotSize > maxLot) lotSize = maxLot;
   
   // Round to step
   lotSize = NormalizeDouble(MathRound(lotSize / stepSize) * stepSize, 2);
   
   Print("Attempting BUY: Lot=", lotSize, " Min=", minLot, " Max=", maxLot, " Step=", stepSize);
   
   if(lotSize < minLot)
   {
      Print("ERROR: Lot size ", lotSize, " below minimum ", minLot, " - cannot trade!");
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
   request.deviation = 50;  // Increased slippage tolerance
   request.magic = MagicNumber;
   request.comment = TradeComment;
   request.type_filling = ORDER_FILLING_FOK;  // Fill or Kill - most compatible
   
   // Try FOK first
   if(!OrderSend(request, result))
   {
      Print("FOK failed (", result.retcode, "), trying IOC...");
      request.type_filling = ORDER_FILLING_IOC;  // Immediate or Cancel
      
      if(!OrderSend(request, result))
      {
         Print("IOC failed (", result.retcode, "), trying RETURN...");
         request.type_filling = ORDER_FILLING_RETURN;  // Return execution
         
         if(!OrderSend(request, result))
         {
            Print("All filling types failed! Last error: ", result.retcode);
            Print("RetCode: ", result.retcode, " Deal: ", result.deal, " Order: ", result.order);
            return;
         }
      }
   }
   
   Print("BUY order opened: ", result.order);
   Print("Volume: ", lotSize);
   Print("Entry: ", ask);
   Print("SL: ", sl, " (", slDistance / _Point, " points)");
   Print("TP: ", tp, " (", (tp - ask) / _Point, " points)");
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
   
   // Calculate lot size - SIMPLIFIED
   double lotSize = FixedLotSize;
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double stepSize = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   // Ensure minimum
   if(lotSize < minLot) lotSize = minLot;
   if(lotSize > maxLot) lotSize = maxLot;
   
   // Round to step
   lotSize = NormalizeDouble(MathRound(lotSize / stepSize) * stepSize, 2);
   
   Print("Attempting SELL: Lot=", lotSize, " Min=", minLot, " Max=", maxLot, " Step=", stepSize);
   
   if(lotSize < minLot)
   {
      Print("ERROR: Lot size ", lotSize, " below minimum ", minLot, " - cannot trade!");
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
   request.deviation = 50;
   request.magic = MagicNumber;
   request.comment = TradeComment;
   request.type_filling = ORDER_FILLING_FOK;
   
   // Try FOK first
   if(!OrderSend(request, result))
   {
      Print("FOK failed (", result.retcode, "), trying IOC...");
      request.type_filling = ORDER_FILLING_IOC;
      
      if(!OrderSend(request, result))
      {
         Print("IOC failed (", result.retcode, "), trying RETURN...");
         request.type_filling = ORDER_FILLING_RETURN;
         
         if(!OrderSend(request, result))
         {
            Print("All filling types failed! Last error: ", result.retcode);
            Print("RetCode: ", result.retcode, " Deal: ", result.deal, " Order: ", result.order);
            return;
         }
      }
   }
   
   Print("SELL order opened: ", result.order);
   Print("Volume: ", lotSize);
   Print("Entry: ", bid);
   Print("SL: ", sl, " (", slDistance / _Point, " points)");
   Print("TP: ", tp, " (", (bid - tp) / _Point, " points)");
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