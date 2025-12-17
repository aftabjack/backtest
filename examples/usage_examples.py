"""
COMPLETE USAGE EXAMPLES FOR YOUR BACKTESTING ENGINE

This file demonstrates all the ways to use your backtesting engine:
1. Basic single strategy backtest
2. Custom strategy creation
3. Parameter optimization
4. Strategy comparison
5. Different timeframes
6. Multiple exchanges
7. Advanced configuration

Run each example independently by uncommenting the section you want.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from data_handlers.loader import DataLoader, resample_data
from engine.backtest import Backtester
from analytics.reports import ReportGenerator
from analytics.metrics import StrategyComparison

# Import built-in strategies
from examples.moving_average_strategy import MovingAverageCrossover
from examples.rsi_strategy import RSIStrategy
from examples.bollinger_bands_strategy import BollingerBandsStrategy
from examples.macd_strategy import MACDStrategy

import config


# ==============================================================================
# EXAMPLE 1: BASIC BACKTEST
# ==============================================================================
def example_1_basic_backtest():
    """
    Simple backtest with a single strategy.
    Perfect for beginners!
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: BASIC BACKTEST")
    print("="*80 + "\n")

    # Step 1: Load data
    print("Loading data...")
    loader = DataLoader()
    data = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-03-31'
    )
    print(f"✓ Loaded {len(data):,} rows\n")

    # Step 2: Create strategy
    print("Creating strategy...")
    strategy = MovingAverageCrossover(
        fast_period=10,
        slow_period=30,
        ma_type='EMA'
    )
    print(f"✓ Strategy: {strategy}\n")

    # Step 3: Create backtester
    print("Setting up backtester...")
    backtester = Backtester(
        strategy=strategy,
        initial_capital=10000.0,
        commission_rate=0.001,  # 0.1%
        position_size=1.0        # 100%
    )
    print("✓ Backtester ready\n")

    # Step 4: Run backtest
    print("Running backtest...")
    results = backtester.run(data)

    # Step 5: Display results
    backtester.print_results()

    print(f"\n✅ Example 1 complete!")
    print(f"   Total Return: {results['total_return']:.2f}%")
    print(f"   Total Trades: {results['total_trades']}")


# ==============================================================================
# EXAMPLE 2: BACKTEST WITH FULL REPORT
# ==============================================================================
def example_2_with_report():
    """
    Backtest with comprehensive report generation.
    Includes charts, CSV exports, and visualizations.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: BACKTEST WITH FULL REPORT")
    print("="*80 + "\n")

    # Load data
    loader = DataLoader()
    data = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-06-30'
    )

    # Resample to hourly for faster processing
    data = resample_data(data, '1H')
    print(f"Loaded {len(data):,} hourly bars\n")

    # Create and run strategy
    strategy = RSIStrategy(
        rsi_period=14,
        oversold_threshold=30,
        overbought_threshold=70
    )

    backtester = Backtester(strategy, initial_capital=10000)
    results = backtester.run(data)
    backtester.print_results()

    # Generate comprehensive report
    print("\nGenerating full report with charts...")
    report_gen = ReportGenerator(output_dir='output')
    report_path = report_gen.generate_full_report(
        results=results,
        save_charts=True,
        show_charts=False  # Set to True to display charts
    )

    print(f"\n✅ Example 2 complete!")
    print(f"   Report saved to: {report_path}")
    print(f"   Check the output folder for charts!")


# ==============================================================================
# EXAMPLE 3: CREATE CUSTOM STRATEGY
# ==============================================================================
def example_3_custom_strategy():
    """
    Create your own custom trading strategy.
    This example shows a simple price-based strategy.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: CUSTOM STRATEGY")
    print("="*80 + "\n")

    from strategies.base_strategy import BaseStrategy, SignalType, IndicatorMixin
    import pandas as pd

    # Define custom strategy
    class SimpleMomentumStrategy(BaseStrategy, IndicatorMixin):
        """
        Buy when price > 20-period SMA and RSI > 50
        Sell when price < 20-period SMA or RSI < 50
        """

        def __init__(self, sma_period=20, rsi_period=14):
            params = {
                'sma_period': sma_period,
                'rsi_period': rsi_period
            }
            super().__init__(name='Simple Momentum', params=params)
            self.sma_period = sma_period
            self.rsi_period = rsi_period

        def calculate_indicators(self):
            # Calculate SMA and RSI
            self.data['sma'] = self.calculate_sma(
                self.data['close'],
                self.sma_period
            )
            self.data['rsi'] = self.calculate_rsi(
                self.data['close'],
                self.rsi_period
            )
            return self.data

        def generate_signals(self, data):
            df = data.copy()
            df['signal'] = SignalType.HOLD.value

            # Track if we're in a position
            in_position = False

            for i in range(1, len(df)):
                # Skip if indicators not ready
                if pd.isna(df['sma'].iloc[i]) or pd.isna(df['rsi'].iloc[i]):
                    continue

                price = df['close'].iloc[i]
                sma = df['sma'].iloc[i]
                rsi = df['rsi'].iloc[i]

                # Buy signal: price above SMA and RSI > 50
                if not in_position and price > sma and rsi > 50:
                    df.iloc[i, df.columns.get_loc('signal')] = SignalType.BUY.value
                    in_position = True

                # Sell signal: price below SMA or RSI < 50
                elif in_position and (price < sma or rsi < 50):
                    df.iloc[i, df.columns.get_loc('signal')] = SignalType.SELL.value
                    in_position = False

            return df

        def get_parameters(self):
            return self.params

    # Use the custom strategy
    loader = DataLoader()
    data = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-03-31'
    )
    data = resample_data(data, '1H')

    # Create and test custom strategy
    custom_strategy = SimpleMomentumStrategy(sma_period=20, rsi_period=14)
    backtester = Backtester(custom_strategy, initial_capital=10000)
    results = backtester.run(data)
    backtester.print_results()

    print(f"\n✅ Example 3 complete!")
    print(f"   You created and tested a custom strategy!")


# ==============================================================================
# EXAMPLE 4: PARAMETER OPTIMIZATION
# ==============================================================================
def example_4_parameter_optimization():
    """
    Find the best parameters for a strategy.
    Tests multiple combinations and ranks by performance.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: PARAMETER OPTIMIZATION")
    print("="*80 + "\n")

    # Load data
    loader = DataLoader()
    data = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-06-30'
    )
    data = resample_data(data, '1H')
    print(f"Loaded {len(data):,} bars\n")

    # Define parameter ranges to test
    fast_periods = [5, 10, 15, 20]
    slow_periods = [30, 40, 50, 60]

    print(f"Testing {len(fast_periods) * len(slow_periods)} combinations...")
    print("This may take a few minutes...\n")

    best_result = None
    best_sharpe = -float('inf')
    all_results = []

    # Test all combinations
    test_num = 0
    for fast in fast_periods:
        for slow in slow_periods:
            if fast >= slow:
                continue

            test_num += 1
            strategy = MovingAverageCrossover(
                fast_period=fast,
                slow_period=slow,
                ma_type='EMA'
            )

            backtester = Backtester(strategy, initial_capital=10000)
            results = backtester.run(data)

            print(f"Test {test_num}: fast={fast}, slow={slow} → "
                  f"Return={results['total_return']:.2f}%, "
                  f"Sharpe={results['sharpe_ratio']:.2f}")

            all_results.append(results)

            # Track best
            if results['sharpe_ratio'] > best_sharpe:
                best_sharpe = results['sharpe_ratio']
                best_result = results

    # Display best parameters
    print("\n" + "="*80)
    print("BEST PARAMETERS FOUND")
    print("="*80)
    print(f"\nStrategy: {best_result['strategy']}")
    print(f"Parameters: {best_result['parameters']}")
    print(f"\nPerformance:")
    print(f"  Total Return: {best_result['total_return']:.2f}%")
    print(f"  Sharpe Ratio: {best_result['sharpe_ratio']:.2f}")
    print(f"  Win Rate: {best_result['win_rate']:.2f}%")
    print(f"  Max Drawdown: {best_result['max_drawdown']:.2f}%")

    print(f"\n✅ Example 4 complete!")
    print(f"   Tested {test_num} parameter combinations")


# ==============================================================================
# EXAMPLE 5: COMPARE MULTIPLE STRATEGIES
# ==============================================================================
def example_5_compare_strategies():
    """
    Compare performance of different strategies side-by-side.
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: STRATEGY COMPARISON")
    print("="*80 + "\n")

    # Load data
    loader = DataLoader()
    data = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-06-30'
    )
    data = resample_data(data, '1H')
    print(f"Loaded {len(data):,} bars\n")

    # Define strategies to compare
    strategies = [
        MovingAverageCrossover(fast_period=10, slow_period=30, ma_type='EMA'),
        RSIStrategy(rsi_period=14, oversold_threshold=30, overbought_threshold=70),
        BollingerBandsStrategy(period=20, std_dev=2.0),
        MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    ]

    results_list = []

    # Run each strategy
    for i, strategy in enumerate(strategies, 1):
        print(f"\n[{i}/{len(strategies)}] Testing: {strategy.get_name()}")
        print("-" * 60)

        backtester = Backtester(strategy, initial_capital=10000)
        results = backtester.run(data)
        results_list.append(results)

        print(f"  Return: {results['total_return']:.2f}%")
        print(f"  Trades: {results['total_trades']}")
        print(f"  Win Rate: {results['win_rate']:.2f}%")
        print(f"  Sharpe: {results['sharpe_ratio']:.2f}")

    # Create comparison table
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80 + "\n")

    comparison_df = StrategyComparison.compare_strategies(results_list)
    print(comparison_df.to_string(index=False))

    # Save comparison
    comparison_df.to_csv('output/strategy_comparison_example.csv', index=False)

    print(f"\n✅ Example 5 complete!")
    print(f"   Comparison saved to output/strategy_comparison_example.csv")


# ==============================================================================
# EXAMPLE 6: DIFFERENT TIMEFRAMES
# ==============================================================================
def example_6_different_timeframes():
    """
    Test same strategy on different timeframes.
    Shows how timeframe affects performance.
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: DIFFERENT TIMEFRAMES")
    print("="*80 + "\n")

    # Load raw 1-minute data
    loader = DataLoader()
    data_1m = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-03-31'
    )

    # Test on different timeframes
    timeframes = [
        ('5T', '5-minute'),
        ('15T', '15-minute'),
        ('1H', '1-hour'),
        ('4H', '4-hour'),
    ]

    strategy = MovingAverageCrossover(fast_period=10, slow_period=30)

    print("Testing strategy on multiple timeframes...\n")

    results_by_timeframe = []

    for tf_code, tf_name in timeframes:
        # Resample data
        data = resample_data(data_1m, tf_code)

        print(f"Testing on {tf_name} bars ({len(data):,} bars)...")

        # Run backtest
        backtester = Backtester(strategy, initial_capital=10000)
        results = backtester.run(data)

        results_by_timeframe.append({
            'Timeframe': tf_name,
            'Bars': len(data),
            'Return %': results['total_return'],
            'Trades': results['total_trades'],
            'Win Rate %': results['win_rate'],
            'Sharpe': results['sharpe_ratio'],
            'Max DD %': results['max_drawdown']
        })

    # Display comparison
    import pandas as pd
    comparison_df = pd.DataFrame(results_by_timeframe)

    print("\n" + "="*80)
    print("TIMEFRAME COMPARISON")
    print("="*80 + "\n")
    print(comparison_df.to_string(index=False))

    print(f"\n✅ Example 6 complete!")
    print(f"   Strategy tested on {len(timeframes)} timeframes")


# ==============================================================================
# EXAMPLE 7: MULTIPLE EXCHANGES
# ==============================================================================
def example_7_multiple_exchanges():
    """
    Compare how strategy performs on different exchanges.
    """
    print("\n" + "="*80)
    print("EXAMPLE 7: MULTIPLE EXCHANGES")
    print("="*80 + "\n")

    # Define exchanges to test
    exchanges = ['Binance', 'Coinbase', 'Combined_Index']

    strategy = RSIStrategy(rsi_period=14, oversold_threshold=30, overbought_threshold=70)

    print("Testing strategy on multiple exchanges...\n")

    results_by_exchange = []
    loader = DataLoader()

    for exchange in exchanges:
        print(f"Loading data from {exchange}...")

        try:
            data = loader.load_data(
                exchange=exchange,
                start_date='2023-01-01',
                end_date='2023-03-31'
            )
            data = resample_data(data, '1H')

            print(f"  Running backtest on {len(data):,} bars...")

            backtester = Backtester(strategy, initial_capital=10000)
            results = backtester.run(data)

            results_by_exchange.append({
                'Exchange': exchange,
                'Return %': results['total_return'],
                'Trades': results['total_trades'],
                'Win Rate %': results['win_rate'],
                'Sharpe': results['sharpe_ratio']
            })

            print(f"  ✓ Return: {results['total_return']:.2f}%\n")

        except Exception as e:
            print(f"  ✗ Error: {e}\n")

    # Display comparison
    import pandas as pd
    comparison_df = pd.DataFrame(results_by_exchange)

    print("="*80)
    print("EXCHANGE COMPARISON")
    print("="*80 + "\n")
    print(comparison_df.to_string(index=False))

    print(f"\n✅ Example 7 complete!")


# ==============================================================================
# EXAMPLE 8: ADVANCED CONFIGURATION
# ==============================================================================
def example_8_advanced_config():
    """
    Advanced backtesting configuration.
    Shows all available settings.
    """
    print("\n" + "="*80)
    print("EXAMPLE 8: ADVANCED CONFIGURATION")
    print("="*80 + "\n")

    loader = DataLoader()
    data = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-03-31'
    )
    data = resample_data(data, '1H')

    strategy = MovingAverageCrossover(fast_period=10, slow_period=30)

    # Advanced configuration
    backtester = Backtester(
        strategy=strategy,
        initial_capital=50000.0,      # Larger capital
        commission_rate=0.002,         # Higher commission (0.2%)
        position_size=0.5,             # Only use 50% of capital
        allow_short=False,             # No short selling
        slippage=0.001                 # 0.1% slippage
    )

    print("Configuration:")
    print(f"  Initial Capital: ${backtester.initial_capital:,.2f}")
    print(f"  Commission Rate: {backtester.commission_rate*100:.2f}%")
    print(f"  Position Size: {backtester.position_size*100:.0f}%")
    print(f"  Allow Short: {backtester.allow_short}")
    print(f"  Slippage: {backtester.slippage*100:.2f}%")
    print()

    results = backtester.run(data)
    backtester.print_results()

    print(f"\n✅ Example 8 complete!")


# ==============================================================================
# EXAMPLE 9: QUICK DATA EXPLORATION
# ==============================================================================
def example_9_data_exploration():
    """
    Explore the available data before backtesting.
    """
    print("\n" + "="*80)
    print("EXAMPLE 9: DATA EXPLORATION")
    print("="*80 + "\n")

    loader = DataLoader()

    # Get info about the dataset
    print("Getting dataset information...\n")

    info = loader.get_data_info(exchange='Combined_Index')

    print("Dataset Information:")
    print(f"  Exchange: {info['exchange']}")
    print(f"  Symbol: {info['symbol']}")
    print(f"  Total Rows: {info['rows']:,}")
    print(f"  Date Range: {info['start_date']} to {info['end_date']}")
    print(f"  Duration: {info['duration_days']:,} days")
    print(f"\n  Price Range:")
    print(f"    Min: ${info['price_range']['min']:.2f}")
    print(f"    Max: ${info['price_range']['max']:.2f}")
    print(f"    Mean: ${info['price_range']['mean']:.2f}")
    print(f"\n  Volume Stats:")
    print(f"    Total: {info['volume_stats']['total']:,.0f}")
    print(f"    Mean: {info['volume_stats']['mean']:,.0f}")
    print(f"    Max: {info['volume_stats']['max']:,.0f}")

    # Load a sample
    print("\n" + "-"*80)
    print("Loading sample data...")

    sample = loader.load_data(
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-01-07'
    )

    print(f"Sample data (first week of 2023):")
    print(sample.head(10))

    print(f"\n✅ Example 9 complete!")


# ==============================================================================
# MAIN MENU
# ==============================================================================
def main():
    """Run examples with a menu."""
    print("\n" + "="*80)
    print("BACKTESTING ENGINE - USAGE EXAMPLES")
    print("="*80)

    examples = {
        '1': ('Basic Backtest', example_1_basic_backtest),
        '2': ('Backtest with Full Report', example_2_with_report),
        '3': ('Create Custom Strategy', example_3_custom_strategy),
        '4': ('Parameter Optimization', example_4_parameter_optimization),
        '5': ('Compare Multiple Strategies', example_5_compare_strategies),
        '6': ('Different Timeframes', example_6_different_timeframes),
        '7': ('Multiple Exchanges', example_7_multiple_exchanges),
        '8': ('Advanced Configuration', example_8_advanced_config),
        '9': ('Data Exploration', example_9_data_exploration),
    }

    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Run ALL examples")
    print("  q. Quit")

    choice = input("\nEnter your choice: ").strip()

    if choice == 'q':
        print("Goodbye!")
        return
    elif choice == '0':
        print("\nRunning ALL examples (this will take a while)...\n")
        for name, func in examples.values():
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}\n")
    elif choice in examples:
        name, func = examples[choice]
        func()
    else:
        print("Invalid choice!")


if __name__ == '__main__':
    # Uncomment to run specific examples directly:

    # example_1_basic_backtest()
    # example_2_with_report()
    # example_3_custom_strategy()
    # example_4_parameter_optimization()
    # example_5_compare_strategies()
    # example_6_different_timeframes()
    # example_7_multiple_exchanges()
    # example_8_advanced_config()
    # example_9_data_exploration()

    # Or run the menu:
    main()
