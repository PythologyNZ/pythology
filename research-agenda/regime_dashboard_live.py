"""
PYTHOLOGY - LIVE REGIME DASHBOARD
==================================
Auto-updating market regime monitor

Author: Brent Robertson (Pythology)
Date: February 20, 2026
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import time
import os

# Use a font that exists on Windows
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

print("=" * 80)
print("PYTHOLOGY - LIVE REGIME DASHBOARD")
print("=" * 80)
print("\nAuto-Updating Market Monitor")
print("Press Ctrl+C to stop\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

PAIRS = {
    'NAS100': 'NASDAQ 100',
    'GER40': 'DAX 40',
    'SP500': 'S&P 500',
    'BTCUSD': 'Bitcoin',
    'XAUUSD': 'Gold'
}

TIMEFRAMES = ['H1', 'M15']

ADX_TREND_THRESHOLD = 25.0
ADX_RANGE_THRESHOLD = 20.0

UPDATE_INTERVAL = 300  # 5 minutes (in seconds)

# ============================================================================
# ADX CALCULATION
# ============================================================================

def calculate_adx(df, period=14):
    """Calculate ADX from OHLC data"""
    
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    
    tr1 = high - low
    tr2 = abs(high - np.roll(close, 1))
    tr3 = abs(low - np.roll(close, 1))
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    
    up_move = high - np.roll(high, 1)
    down_move = np.roll(low, 1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    atr = pd.Series(tr).rolling(window=period).mean().values
    plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean().values / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean().values / atr
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
    adx = pd.Series(dx).rolling(window=period).mean().values
    
    return adx[-1] if len(adx) > 0 and not np.isnan(adx[-1]) else 0

def classify_regime(adx_value):
    """Classify market regime based on ADX"""
    
    if adx_value >= ADX_TREND_THRESHOLD:
        return "STRONG TREND", "🟢 TREND FOLLOW", "#27ae60"
    elif adx_value >= ADX_RANGE_THRESHOLD:
        return "WEAK TREND", "⚠️  SKIP TRADING", "#f39c12"
    else:
        return "RANGING", "🟢 MEAN REVERSION", "#3498db"

# ============================================================================
# REGIME CHANGE DETECTION
# ============================================================================

previous_regimes = {}

def detect_regime_changes(current_results):
    """Detect and alert on regime changes"""
    
    global previous_regimes
    
    changes = []
    
    for result in current_results:
        key = f"{result['pair']}_{result['timeframe']}"
        current_regime = result['regime']
        
        if key in previous_regimes:
            if previous_regimes[key] != current_regime:
                changes.append({
                    'pair': result['name'],
                    'timeframe': result['timeframe'],
                    'old': previous_regimes[key],
                    'new': current_regime,
                    'adx': result['adx']
                })
        
        previous_regimes[key] = current_regime
    
    return changes

# ============================================================================
# DASHBOARD GENERATION
# ============================================================================

def generate_dashboard(results, update_num):
    """Generate dashboard visualization"""
    
    df_results = pd.DataFrame(results)
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.3, wspace=0.3)
    
    # --- TOP: REGIME TABLE ---
    ax_table = fig.add_subplot(gs[0, :])
    ax_table.axis('tight')
    ax_table.axis('off')
    
    table_data = []
    table_data.append(['Asset', 'TF', 'ADX', 'Regime', 'Strategy'])
    
    for _, row in df_results.iterrows():
        table_data.append([
            row['name'],
            row['timeframe'],
            f"{row['adx']:.1f}",
            row['regime'],
            row['recommendation']
        ])
    
    table = ax_table.table(
        cellText=table_data,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    for i in range(5):
        cell = table[(0, i)]
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(weight='bold', color='white', fontsize=13)
    
    for idx, (i, row) in enumerate(df_results.iterrows(), start=1):
        for j in range(5):
            cell = table[(idx, j)]
            cell.set_facecolor('#ecf0f1' if idx % 2 == 0 else 'white')
            
            if j == 3:
                cell.set_text_props(weight='bold', color=row['color'])
    
    ax_table.set_title('PYTHOLOGY LIVE REGIME DASHBOARD\nReal-Time Market State Monitor',
                       fontsize=18, fontweight='bold', pad=20)
    
    # --- BOTTOM LEFT: ADX DISTRIBUTION ---
    ax_dist = fig.add_subplot(gs[1, 0])
    
    timeframes_split = df_results.groupby('timeframe')
    
    for tf, group in timeframes_split:
        ax_dist.scatter(group['pair'], group['adx'], 
                       label=tf, s=200, alpha=0.7, edgecolors='black', linewidth=2)
    
    ax_dist.axhline(y=ADX_TREND_THRESHOLD, color='green', linestyle='--', 
                   linewidth=2, label=f'Trend Threshold ({ADX_TREND_THRESHOLD})')
    ax_dist.axhline(y=ADX_RANGE_THRESHOLD, color='orange', linestyle='--', 
                   linewidth=2, label=f'Range Threshold ({ADX_RANGE_THRESHOLD})')
    
    ax_dist.set_xlabel('Asset', fontsize=13, fontweight='bold')
    ax_dist.set_ylabel('ADX Value', fontsize=13, fontweight='bold')
    ax_dist.set_title('ADX Distribution by Asset', fontsize=14, fontweight='bold')
    ax_dist.legend(fontsize=10)
    ax_dist.grid(True, alpha=0.3)
    ax_dist.set_ylim(0, max(df_results['adx'].max() + 5, 35))
    
    # --- BOTTOM RIGHT: REGIME SUMMARY ---
    ax_summary = fig.add_subplot(gs[1, 1])
    
    regime_counts = df_results['regime'].value_counts()
    colors_map = {
        'STRONG TREND': '#27ae60',
        'WEAK TREND': '#f39c12',
        'RANGING': '#3498db'
    }
    colors = [colors_map.get(regime, '#95a5a6') for regime in regime_counts.index]
    
    wedges, texts, autotexts = ax_summary.pie(
        regime_counts.values,
        labels=regime_counts.index,
        autopct='%1.0f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12, 'weight': 'bold'}
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(14)
        autotext.set_weight('bold')
    
    ax_summary.set_title('Market Regime Distribution', fontsize=14, fontweight='bold')
    
    total_pairs = len(df_results)
    tradeable = len(df_results[df_results['regime'].isin(['STRONG TREND', 'RANGING'])])
    skip = len(df_results[df_results['regime'] == 'WEAK TREND'])
    
    summary_text = f"""
    Total Pairs: {total_pairs}
    Tradeable: {tradeable} ({tradeable/total_pairs*100:.0f}%)
    Skip Trading: {skip} ({skip/total_pairs*100:.0f}%)
    
    Update #{update_num}
    """
    
    fig.text(0.75, 0.12, summary_text.strip(),
             fontsize=11, ha='center', va='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fig.text(0.99, 0.01, f'Updated: {timestamp} | Pythology © 2026 | LIVE', 
             ha='right', fontsize=9, style='italic', alpha=0.7)
    
    output_file = 'Pythology_Regime_Dashboard_LIVE.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return output_file

# ============================================================================
# MAIN LOOP
# ============================================================================

update_count = 0

print("Starting live monitoring...")
print(f"Update interval: {UPDATE_INTERVAL} seconds ({UPDATE_INTERVAL/60:.1f} minutes)")
print("\n" + "=" * 80 + "\n")

try:
    while True:
        update_count += 1
        
        print(f"[Update #{update_count}] {datetime.now().strftime('%H:%M:%S')}")
        
        # Analyze all pairs
        results = []
        
        for pair, name in PAIRS.items():
            for tf in TIMEFRAMES:
                filename = f"{pair}_{tf}.csv"
                
                try:
                    df = pd.read_csv(filename)
                    adx = calculate_adx(df, period=14)
                    regime, recommendation, color = classify_regime(adx)
                    
                    results.append({
                        'pair': pair,
                        'name': name,
                        'timeframe': tf,
                        'adx': adx,
                        'regime': regime,
                        'recommendation': recommendation,
                        'color': color
                    })
                    
                except Exception as e:
                    pass
        
        if len(results) > 0:
            # Detect regime changes
            changes = detect_regime_changes(results)
            
            if changes:
                print("\n🚨 REGIME CHANGES DETECTED:")
                for change in changes:
                    print(f"  {change['pair']} ({change['timeframe']}): "
                          f"{change['old']} → {change['new']} (ADX: {change['adx']:.1f})")
            
            # Generate dashboard
            output_file = generate_dashboard(results, update_count)
            
            # Print summary
            df_temp = pd.DataFrame(results)
            tradeable = len(df_temp[df_temp['regime'].isin(['STRONG TREND', 'RANGING'])])
            
            print(f"  Tradeable: {tradeable}/{len(results)} pairs")
            print(f"  Dashboard: {output_file}")
        
        print()
        
        # Wait for next update
        if update_count == 1:
            print(f"Waiting {UPDATE_INTERVAL} seconds for next update...")
            print("(Dashboard will refresh automatically)")
            print("\nPress Ctrl+C to stop\n")
        
        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print("\n\n" + "=" * 80)
    print("LIVE MONITORING STOPPED")
    print("=" * 80)
    print(f"\nTotal updates: {update_count}")
    print("Dashboard saved as: Pythology_Regime_Dashboard_LIVE.png")
    print("\n🚀 Pythology - Live Regime Monitoring")