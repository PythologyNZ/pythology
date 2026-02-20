"""
PYTHOLOGY - USD STRENGTH INDEX V2.0 (ORGANIZED)
================================================
Auto-updates data, organized folders, auto-cleanup

Author: Brent Robertson (Pythology)
Date: February 20, 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import MetaTrader5 as mt5
import os
import shutil

print("=" * 80)
print("PYTHOLOGY - USD STRENGTH INDEX V2.0")
print("=" * 80)
print("\nOrganized data management with auto-cleanup\n")

# ============================================================================
# FOLDER SETUP
# ============================================================================

# Create folders if they don't exist
DATA_FOLDER = 'data'
RESULTS_FOLDER = 'results'

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

print(f"✓ Data folder: {DATA_FOLDER}/")
print(f"✓ Results folder: {RESULTS_FOLDER}/")

# ============================================================================
# CONFIGURATION
# ============================================================================

USD_PAIRS = {
    'EURUSD': {'weight': 0.576, 'inverse': True},
    'USDJPY': {'weight': 0.136, 'inverse': False},
    'GBPUSD': {'weight': 0.119, 'inverse': True},
    'USDCAD': {'weight': 0.091, 'inverse': False},
    'USDCHF': {'weight': 0.036, 'inverse': False},
    'AUDUSD': {'weight': 0.025, 'inverse': True},
    'NZDUSD': {'weight': 0.017, 'inverse': True}
}

TIMEFRAME = mt5.TIMEFRAME_H1
BARS_TO_FETCH = 1000

# Normalize weights
total_weight = sum(p['weight'] for p in USD_PAIRS.values())
for pair in USD_PAIRS:
    USD_PAIRS[pair]['weight'] = USD_PAIRS[pair]['weight'] / total_weight

# ============================================================================
# CONNECT TO MT5 & UPDATE DATA
# ============================================================================

print("\n" + "=" * 80)
print("UPDATING DATA FROM MT5")
print("=" * 80 + "\n")

if not mt5.initialize():
    print("✗ Failed to initialize MT5!")
    mt5.shutdown()
    exit()

print("✓ Connected to MT5")

pair_data = {}
temp_files = []

for pair in USD_PAIRS.keys():
    
    print(f"Fetching {pair}...", end=" ")
    
    try:
        rates = mt5.copy_rates_from_pos(pair, TIMEFRAME, 0, BARS_TO_FETCH)
        
        if rates is None or len(rates) == 0:
            print(f"✗ No data")
            continue
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        df = df.rename(columns={
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'tick_volume': 'volume'
        })
        
        df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
        # Save to data folder
        filename = os.path.join(DATA_FOLDER, f"{pair}_H1.csv")
        df.to_csv(filename, index=False)
        temp_files.append(filename)
        
        # Store in memory
        df_indexed = df.set_index('time')
        pair_data[pair] = df_indexed
        
        print(f"✓ {len(df)} bars")
        
    except Exception as e:
        print(f"✗ Error: {e}")

mt5.shutdown()

print(f"\n✓ Updated {len(pair_data)}/{len(USD_PAIRS)} pairs")

# ============================================================================
# CALCULATE USD STRENGTH INDEX
# ============================================================================

if len(pair_data) > 0:
    print("\n" + "=" * 80)
    print("CALCULATING USD STRENGTH INDEX")
    print("=" * 80)
    
    # Find common time range
    common_index = None
    
    for pair, df in pair_data.items():
        if common_index is None:
            common_index = df.index
        else:
            common_index = common_index.intersection(df.index)
    
    print(f"\nCommon timeframe: {len(common_index)} bars")
    
    # Calculate USD index
    usd_index_values = []
    timestamps = []
    
    for timestamp in common_index[-500:]:
        
        index_value = 100
        
        for pair, config in USD_PAIRS.items():
            if pair in pair_data:
                
                price = pair_data[pair].loc[timestamp, 'close']
                first_price = pair_data[pair].iloc[0]['close']
                pct_change = (price / first_price - 1) * 100
                
                if config['inverse']:
                    pct_change = -pct_change
                
                weighted_contribution = pct_change * config['weight']
                index_value += weighted_contribution
        
        usd_index_values.append(index_value)
        timestamps.append(timestamp)
    
    usd_index = pd.DataFrame({
        'value': usd_index_values
    }, index=timestamps)
    
    # ========================================================================
    # ANALYSIS
    # ========================================================================
    
    current_value = usd_index['value'].iloc[-1]
    previous_value = usd_index['value'].iloc[-2]
    change_1h = current_value - previous_value
    
    high_24h = usd_index['value'].iloc[-24:].max()
    low_24h = usd_index['value'].iloc[-24:].min()
    
    high_7d = usd_index['value'].iloc[-168:].max() if len(usd_index) >= 168 else high_24h
    low_7d = usd_index['value'].iloc[-168:].min() if len(usd_index) >= 168 else low_24h
    
    print("\n" + "=" * 80)
    print("USD STRENGTH INDEX - CURRENT STATE")
    print("=" * 80)
    print(f"\nCurrent Value: {current_value:.2f}")
    print(f"1-Hour Change: {change_1h:+.2f} ({change_1h/previous_value*100:+.2f}%)")
    print(f"\n24-Hour Range: {low_24h:.2f} - {high_24h:.2f}")
    print(f"7-Day Range:   {low_7d:.2f} - {high_7d:.2f}")
    
    # Trend
    sma_20 = usd_index['value'].iloc[-20:].mean()
    sma_50 = usd_index['value'].iloc[-50:].mean()
    
    if current_value > sma_20 > sma_50:
        trend = "BULLISH (USD Strengthening)"
        trend_color = '#27ae60'
    elif current_value < sma_20 < sma_50:
        trend = "BEARISH (USD Weakening)"
        trend_color = '#e74c3c'
    else:
        trend = "NEUTRAL (USD Consolidating)"
        trend_color = '#f39c12'
    
    print(f"\nTrend: {trend}")
    
    # ========================================================================
    # VISUALIZATION
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("CREATING VISUALIZATION")
    print("=" * 80)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), height_ratios=[2, 1])
    
    ax1.plot(usd_index.index, usd_index['value'], 
             linewidth=2, color='#3498db', label='USD Index')
    
    sma_20_values = usd_index['value'].rolling(window=20).mean()
    sma_50_values = usd_index['value'].rolling(window=50).mean()
    
    ax1.plot(usd_index.index, sma_20_values, 
             linewidth=1.5, color='#e67e22', linestyle='--', label='20-Period SMA', alpha=0.7)
    ax1.plot(usd_index.index, sma_50_values, 
             linewidth=1.5, color='#e74c3c', linestyle='--', label='50-Period SMA', alpha=0.7)
    
    ax1.scatter(usd_index.index[-1], current_value, 
               s=200, color=trend_color, zorder=5, edgecolors='black', linewidth=2)
    
    ax1.axhline(y=100, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='Baseline (100)')
    
    ax1.set_xlabel('Time', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Index Value', fontsize=13, fontweight='bold')
    ax1.set_title('USD Strength Index\nComposite Dollar Index from Major Pairs (Live Data)',
                  fontsize=16, fontweight='bold', pad=15)
    ax1.legend(fontsize=11, loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    ax1.annotate(f'{current_value:.2f}',
                xy=(usd_index.index[-1], current_value),
                xytext=(10, 10), textcoords='offset points',
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=trend_color, alpha=0.7),
                color='white')
    
    roc = usd_index['value'].diff()
    colors = ['#27ae60' if x > 0 else '#e74c3c' for x in roc]
    
    ax2.bar(usd_index.index, roc, color=colors, alpha=0.7, width=0.03)
    ax2.axhline(y=0, color='black', linewidth=1)
    
    ax2.set_xlabel('Time', fontsize=13, fontweight='bold')
    ax2.set_ylabel('1-Hour Change', fontsize=13, fontweight='bold')
    ax2.set_title('USD Index - Rate of Change', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    info_text = f"""
    Current: {current_value:.2f}
    1H Change: {change_1h:+.2f}
    Trend: {trend.split('(')[0].strip()}
    Updated: LIVE
    """
    
    fig.text(0.98, 0.98, info_text.strip(),
             ha='right', va='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fig.text(0.99, 0.01, f'Generated: {timestamp} | Pythology © 2026 | LIVE DATA', 
             ha='right', fontsize=9, style='italic', alpha=0.7)
    
    output_file = os.path.join(RESULTS_FOLDER, 'Pythology_USD_Strength_Index.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"\n✓ Chart saved: {output_file}")
    
    plt.show()
    
    # Save index data to results folder
    index_file = os.path.join(RESULTS_FOLDER, 'USD_Strength_Index.csv')
    usd_index.to_csv(index_file)
    print(f"✓ Index data saved: {index_file}")
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("CLEANUP")
    print("=" * 80)
    
    print("\nDeleting temporary CSV files...")
    deleted_count = 0
    
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            deleted_count += 1
            print(f"  ✓ Deleted: {os.path.basename(temp_file)}")
        except Exception as e:
            print(f"  ✗ Failed to delete {os.path.basename(temp_file)}: {e}")
    
    print(f"\n✓ Cleaned up {deleted_count}/{len(temp_files)} temp files")
    
    print("\n" + "=" * 80)
    print("USD STRENGTH INDEX COMPLETE!")
    print("=" * 80)
    print("\n✓ All data is LIVE and up-to-date")
    print("✓ Organized in folders")
    print("✓ Temp files cleaned up")
    print("\nRun anytime for fresh analysis!")

else:
    print("\n✗ No data available!")

print("\n🚀 Pythology - Organized & Clean")