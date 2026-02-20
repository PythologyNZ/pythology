"""
PYTHOLOGY - SYNTHETIC FX GENERATOR
===================================
Part 2: Create synthetic currency pairs from major USD pairs

Generate crosses that don't exist naturally:
- EURGBP, EURJPY, EURCHF, EURAUD, etc.
- Find arbitrage opportunities
- Track correlations

Author: Brent Robertson (Pythology)
Date: February 20, 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import MetaTrader5 as mt5
import os

print("=" * 80)
print("PYTHOLOGY - SYNTHETIC FX GENERATOR")
print("=" * 80)
print("\nCreating synthetic currency pairs from major USD pairs\n")

# ============================================================================
# FOLDER SETUP
# ============================================================================

DATA_FOLDER = 'data'
RESULTS_FOLDER = 'results'

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Major USD pairs
USD_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'NZDUSD', 'USDCAD']

TIMEFRAME = mt5.TIMEFRAME_H1
BARS_TO_FETCH = 500  # Last 500 H1 bars (~3 weeks)

# Synthetic pairs we want to create
SYNTHETIC_PAIRS = {
    'EURGBP': {'numerator': 'EURUSD', 'denominator': 'GBPUSD'},
    'EURJPY': {'numerator': 'EURUSD', 'denominator': 'USDJPY', 'invert_denom': True},
    'EURCHF': {'numerator': 'EURUSD', 'denominator': 'USDCHF', 'invert_denom': True},
    'EURAUD': {'numerator': 'EURUSD', 'denominator': 'AUDUSD'},
    'GBPJPY': {'numerator': 'GBPUSD', 'denominator': 'USDJPY', 'invert_denom': True},
    'GBPCHF': {'numerator': 'GBPUSD', 'denominator': 'USDCHF', 'invert_denom': True},
    'AUDJPY': {'numerator': 'AUDUSD', 'denominator': 'USDJPY', 'invert_denom': True},
    'NZDJPY': {'numerator': 'NZDUSD', 'denominator': 'USDJPY', 'invert_denom': True},
    'AUDNZD': {'numerator': 'AUDUSD', 'denominator': 'NZDUSD'},
}

# ============================================================================
# FETCH DATA FROM MT5
# ============================================================================

print("=" * 80)
print("FETCHING USD PAIR DATA")
print("=" * 80 + "\n")

if not mt5.initialize():
    print("✗ Failed to connect to MT5!")
    exit()

print("✓ Connected to MT5\n")

pair_data = {}
temp_files = []

for pair in USD_PAIRS:
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
        
        # Save temporarily
        filename = os.path.join(DATA_FOLDER, f"{pair}_H1.csv")
        df.to_csv(filename, index=False)
        temp_files.append(filename)
        
        # Store in memory with time index
        df = df.set_index('time')
        pair_data[pair] = df
        
        print(f"✓ {len(df)} bars")
        
    except Exception as e:
        print(f"✗ Error: {e}")

mt5.shutdown()

print(f"\n✓ Loaded {len(pair_data)}/{len(USD_PAIRS)} pairs")

# ============================================================================
# CREATE SYNTHETIC PAIRS
# ============================================================================

if len(pair_data) >= 2:
    print("\n" + "=" * 80)
    print("CREATING SYNTHETIC PAIRS")
    print("=" * 80 + "\n")
    
    synthetic_data = {}
    
    for synthetic_pair, config in SYNTHETIC_PAIRS.items():
        
        numerator_pair = config['numerator']
        denominator_pair = config['denominator']
        invert_denom = config.get('invert_denom', False)
        
        # Check if we have both required pairs
        if numerator_pair not in pair_data or denominator_pair not in pair_data:
            print(f"✗ {synthetic_pair}: Missing required pairs")
            continue
        
        print(f"Creating {synthetic_pair}...", end=" ")
        
        # Get data
        num_df = pair_data[numerator_pair]
        denom_df = pair_data[denominator_pair]
        
        # Find common timestamps
        common_times = num_df.index.intersection(denom_df.index)
        
        if len(common_times) < 10:
            print(f"✗ Insufficient overlap")
            continue
        
        # Calculate synthetic prices
        synthetic_df = pd.DataFrame(index=common_times)
        
        if invert_denom:
            # For pairs like EURJPY: EUR/USD × USD/JPY = EUR/JPY
            synthetic_df['open'] = num_df.loc[common_times, 'open'] * denom_df.loc[common_times, 'open']
            synthetic_df['high'] = num_df.loc[common_times, 'high'] * denom_df.loc[common_times, 'high']
            synthetic_df['low'] = num_df.loc[common_times, 'low'] * denom_df.loc[common_times, 'low']
            synthetic_df['close'] = num_df.loc[common_times, 'close'] * denom_df.loc[common_times, 'close']
        else:
            # For pairs like EURGBP: EUR/USD ÷ GBP/USD = EUR/GBP
            synthetic_df['open'] = num_df.loc[common_times, 'open'] / denom_df.loc[common_times, 'open']
            synthetic_df['high'] = num_df.loc[common_times, 'high'] / denom_df.loc[common_times, 'high']
            synthetic_df['low'] = num_df.loc[common_times, 'low'] / denom_df.loc[common_times, 'low']
            synthetic_df['close'] = num_df.loc[common_times, 'close'] / denom_df.loc[common_times, 'close']
        
        synthetic_data[synthetic_pair] = synthetic_df
        
        current_price = synthetic_df['close'].iloc[-1]
        print(f"✓ {len(synthetic_df)} bars | Current: {current_price:.4f}")
    
    print(f"\n✓ Created {len(synthetic_data)}/{len(SYNTHETIC_PAIRS)} synthetic pairs")
    
    # ========================================================================
    # SAVE SYNTHETIC PAIR DATA
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("SAVING SYNTHETIC PAIR DATA")
    print("=" * 80 + "\n")
    
    for pair, df in synthetic_data.items():
        filename = os.path.join(RESULTS_FOLDER, f"{pair}_SYNTHETIC.csv")
        df.to_csv(filename)
        print(f"✓ Saved: {filename}")
    
    # ========================================================================
    # ARBITRAGE SCANNER
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("ARBITRAGE OPPORTUNITY SCANNER")
    print("=" * 80 + "\n")
    
    arbitrage_opportunities = []
    
    # Check if actual pairs exist and compare to synthetic
    for synthetic_pair in synthetic_data.keys():
        
        # Try to get actual pair from MT5
        if mt5.initialize():
            try:
                actual_rates = mt5.copy_rates_from_pos(synthetic_pair, TIMEFRAME, 0, 1)
                
                if actual_rates is not None and len(actual_rates) > 0:
                    actual_price = actual_rates[0]['close']
                    synthetic_price = synthetic_data[synthetic_pair]['close'].iloc[-1]
                    
                    difference = ((actual_price - synthetic_price) / synthetic_price) * 100
                    
                    if abs(difference) > 0.1:  # More than 0.1% difference
                        arbitrage_opportunities.append({
                            'pair': synthetic_pair,
                            'actual': actual_price,
                            'synthetic': synthetic_price,
                            'difference_pct': difference
                        })
                        
                        print(f"{synthetic_pair}:")
                        print(f"  Actual:    {actual_price:.4f}")
                        print(f"  Synthetic: {synthetic_price:.4f}")
                        print(f"  Difference: {difference:+.2f}%")
                        
                        if difference > 0:
                            print(f"  → Actual OVERPRICED (sell actual, buy components)")
                        else:
                            print(f"  → Actual UNDERPRICED (buy actual, sell components)")
                        print()
            except:
                pass
            
            mt5.shutdown()
    
    if len(arbitrage_opportunities) == 0:
        print("✓ No significant arbitrage opportunities found")
        print("  (All pairs trading within 0.1% of synthetic values)")
    
    # ========================================================================
    # CORRELATION MATRIX
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("CORRELATION ANALYSIS")
    print("=" * 80 + "\n")
    
    # Combine all close prices
    all_closes = pd.DataFrame()
    
    for pair, df in synthetic_data.items():
        all_closes[pair] = df['close']
    
    # Calculate correlation matrix
    correlation_matrix = all_closes.corr()
    
    print("Correlation Matrix:")
    print(correlation_matrix.round(2))
    
    # Find highest correlations (excluding diagonal)
    correlations = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            correlations.append({
                'pair1': correlation_matrix.columns[i],
                'pair2': correlation_matrix.columns[j],
                'correlation': correlation_matrix.iloc[i, j]
            })
    
    correlations = sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)
    
    print("\nTop 5 Correlations:")
    for i, corr in enumerate(correlations[:5], 1):
        print(f"{i}. {corr['pair1']} vs {corr['pair2']}: {corr['correlation']:.3f}")
    
    # ========================================================================
    # VISUALIZATION
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("CREATING VISUALIZATIONS")
    print("=" * 80)
    
    # Create comprehensive dashboard
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # --- TOP LEFT: Price Chart (4 major synthetics) ---
    ax1 = fig.add_subplot(gs[0, 0])
    
    major_pairs = ['EURGBP', 'EURJPY', 'GBPJPY', 'EURCHF']
    
    for pair in major_pairs:
        if pair in synthetic_data:
            # Normalize to 100 at start for comparison
            prices = synthetic_data[pair]['close']
            normalized = (prices / prices.iloc[0]) * 100
            ax1.plot(normalized.index, normalized, label=pair, linewidth=2)
    
    ax1.set_xlabel('', fontsize=11, fontweight='bold')  # Remove "Time" label
    ax1.set_ylabel('Normalized Price (Base=100)', fontsize=11, fontweight='bold')
    ax1.set_title('Synthetic Pair Performance (Normalized)', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # --- TOP RIGHT: Correlation Heatmap ---
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Create heatmap with better formatting
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='RdYlGn', 
                center=0, square=False, ax=ax2, 
                cbar_kws={'label': 'Correlation', 'shrink': 0.8},
                annot_kws={'size': 7}, linewidths=0.5, linecolor='white',
                vmin=-1, vmax=1)
    
    # Title with more padding
    ax2.set_title('Synthetic Pair Correlation Matrix', fontsize=13, fontweight='bold', pad=15)
    
    # Rotate and align labels properly
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=8)
    ax2.set_yticklabels(ax2.get_yticklabels(), rotation=0, fontsize=8)
    
    # Adjust layout to prevent overlap
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    
    # --- MIDDLE LEFT: Current Prices Table ---
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis('tight')
    ax3.axis('off')
    
    table_data = [['Synthetic Pair', 'Current Price', '24h Change']]
    
    for pair, df in synthetic_data.items():
        current = df['close'].iloc[-1]
        prev_24h = df['close'].iloc[-24] if len(df) >= 24 else df['close'].iloc[0]
        change_pct = ((current - prev_24h) / prev_24h) * 100
        
        table_data.append([
            pair,
            f"{current:.4f}",
            f"{change_pct:+.2f}%"
        ])
    
    table = ax3.table(cellText=table_data, cellLoc='center', loc='center',
                      bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header
    for i in range(3):
        table[(0, i)].set_facecolor('#2c3e50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color by change
    for i in range(1, len(table_data)):
        change_str = table_data[i][2]
        if '+' in change_str:
            table[(i, 2)].set_facecolor('#d5f4e6')
        else:
            table[(i, 2)].set_facecolor('#fadbd8')
    
    ax3.set_title('Synthetic Pair Prices', fontsize=13, fontweight='bold', pad=20)
    
    # --- MIDDLE RIGHT: Arbitrage Opportunities ---
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('tight')
    ax4.axis('off')
    
    if len(arbitrage_opportunities) > 0:
        arb_data = [['Pair', 'Actual', 'Synthetic', 'Diff %']]
        
        for opp in arbitrage_opportunities[:5]:
            arb_data.append([
                opp['pair'],
                f"{opp['actual']:.4f}",
                f"{opp['synthetic']:.4f}",
                f"{opp['difference_pct']:+.2f}%"
            ])
        
        arb_table = ax4.table(cellText=arb_data, cellLoc='center', loc='center',
                              bbox=[0, 0, 1, 1])
        arb_table.auto_set_font_size(False)
        arb_table.set_fontsize(10)
        arb_table.scale(1, 2)
        
        for i in range(4):
            arb_table[(0, i)].set_facecolor('#2c3e50')
            arb_table[(0, i)].set_text_props(weight='bold', color='white')
        
        # No title needed - table is self-explanatory
    else:
        ax4.text(0.5, 0.5, 'No Arbitrage Opportunities\n\nAll pairs trading within\n0.1% of synthetic values',
                ha='center', va='center', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        # No title needed
    
    # --- BOTTOM: Volatility Comparison ---
    ax5 = fig.add_subplot(gs[2, :])
    
    volatilities = {}
    for pair, df in synthetic_data.items():
        returns = df['close'].pct_change().dropna()
        vol = returns.std() * np.sqrt(252 * 24) * 100  # Annualized volatility
        volatilities[pair] = vol
    
    pairs_sorted = sorted(volatilities.keys(), key=lambda x: volatilities[x], reverse=True)
    vols_sorted = [volatilities[p] for p in pairs_sorted]
    
    colors = ['#e74c3c' if v > 20 else '#f39c12' if v > 15 else '#27ae60' for v in vols_sorted]
    
    ax5.barh(pairs_sorted, vols_sorted, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax5.set_xlabel('Annualized Volatility (%)', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Synthetic Pair', fontsize=11, fontweight='bold')
    ax5.set_title('Volatility Comparison (Annualized %)', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (pair, vol) in enumerate(zip(pairs_sorted, vols_sorted)):
        ax5.text(vol + 0.5, i, f'{vol:.1f}%', va='center', fontsize=10, fontweight='bold')
    
    # Overall title and timestamp
    fig.suptitle('PYTHOLOGY - SYNTHETIC FX GENERATOR\nCross-Currency Pairs Created from Major USD Pairs',
                 fontsize=16, fontweight='bold', y=0.98)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fig.text(0.99, 0.01, f'Generated: {timestamp} | Pythology © 2026 | LIVE DATA', 
             ha='right', fontsize=9, style='italic', alpha=0.7)
    
    # Save
    output_file = os.path.join(RESULTS_FOLDER, 'Pythology_Synthetic_FX_Dashboard.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"\n✓ Dashboard saved: {output_file}")
    
    plt.show()
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("CLEANUP")
    print("=" * 80)
    
    print("\nDeleting temporary files...")
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            print(f"  ✓ Deleted: {os.path.basename(temp_file)}")
        except:
            pass
    
    print("\n" + "=" * 80)
    print("SYNTHETIC FX GENERATOR COMPLETE!")
    print("=" * 80)
    print(f"\n✓ Created {len(synthetic_data)} synthetic pairs")
    print(f"✓ Saved to: {RESULTS_FOLDER}/")
    print(f"✓ Cleaned up temp files")
    print("\nSynthetic pairs available for trading analysis!")

else:
    print("\n✗ Insufficient data to create synthetic pairs!")

print("\n🚀 Pythology - Synthetic FX Generator")