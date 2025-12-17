"""
Main entry point for backtesting engine.
Run different strategies and generate reports.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from data_handlers.loader import DataLoader, resample_data
from engine.backtest import Backtester
from analytics.reports import ReportGenerator
from analytics.metrics import PerformanceMetrics, StrategyComparison

# Import example strategies
from examples.moving_average_strategy import MovingAverageCrossover
from examples.rsi_strategy import RSIStrategy
from examples.bollinger_bands_strategy import BollingerBandsStrategy
from examples.macd_strategy import MACDStrategy

import config


def run_single_strategy_backtest():
    """Run a single strategy backtest with visualization."""
    print("\n" + "="*80)
    print("CRYPTO BACKTESTING ENGINE")
    print("="*80 + "\n")

    # Load data
    print("Loading data...")
    loader = DataLoader(data_dir=str(config.DATA_DIR))

    # Get data info
    info = loader.get_data_info(exchange=config.DEFAULT_EXCHANGE)
    print(f"\nDataset Information:")
    print(f"  Exchange: {info['exchange']}")
    print(f"  Symbol: {info['symbol']}")
    print(f"  Total rows: {info['rows']:,}")
    print(f"  Date range: {info['start_date']} to {info['end_date']}")
    print(f"  Duration: {info['duration_days']} days")
    print(f"  Price range: ${info['price_range']['min']:.2f} - ${info['price_range']['max']:.2f}")

    # Load subset of data (last 30 days for faster testing)
    # For full backtest, remove start_date parameter
    data = loader.load_data(
        exchange=config.DEFAULT_EXCHANGE,
        start_date='2024-09-01',  # Adjust as needed
        end_date='2024-10-01'
    )

    print(f"\nLoaded {len(data):,} rows for backtesting")

    # Resample to 5-minute bars (optional, for faster testing)
    # Comment out for 1-minute backtesting
    print("Resampling to 5-minute bars...")
    data = resample_data(data, timeframe='5T')
    print(f"Resampled to {len(data):,} rows")

    # Initialize strategy
    print("\nInitializing strategy...")
    strategy = MovingAverageCrossover(
        fast_period=10,
        slow_period=30,
        ma_type='EMA'
    )

    # Alternative strategies (uncomment to use):
    # strategy = RSIStrategy(rsi_period=14, oversold_threshold=30, overbought_threshold=70)
    # strategy = BollingerBandsStrategy(period=20, std_dev=2.0)
    # strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)

    # Initialize backtester
    backtester = Backtester(
        strategy=strategy,
        initial_capital=config.DEFAULT_INITIAL_CAPITAL,
        commission_rate=config.DEFAULT_COMMISSION_RATE,
        position_size=config.DEFAULT_POSITION_SIZE,
        slippage=config.DEFAULT_SLIPPAGE
    )

    # Run backtest
    results = backtester.run(data)

    # Print results
    backtester.print_results()

    # Generate report
    print("\nGenerating report and charts...")
    report_gen = ReportGenerator(output_dir=str(config.OUTPUT_DIR))
    report_path = report_gen.generate_full_report(
        results=results,
        save_charts=True,
        show_charts=False  # Set to True to display charts
    )

    print(f"\n✓ Complete! Check the report at: {report_path}")


def run_strategy_comparison():
    """Run multiple strategies and compare results."""
    print("\n" + "="*80)
    print("STRATEGY COMPARISON")
    print("="*80 + "\n")

    # Load data
    print("Loading data...")
    loader = DataLoader(data_dir=str(config.DATA_DIR))
    data = loader.load_data(
        exchange=config.DEFAULT_EXCHANGE,
        start_date='2024-09-01',
        end_date='2024-10-01'
    )

    # Resample to 5-minute for faster comparison
    data = resample_data(data, timeframe='5T')
    print(f"Loaded {len(data):,} rows\n")

    # Define strategies to compare
    strategies = [
        MovingAverageCrossover(fast_period=10, slow_period=30, ma_type='EMA'),
        RSIStrategy(rsi_period=14, oversold_threshold=30, overbought_threshold=70),
        BollingerBandsStrategy(period=20, std_dev=2.0),
        MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    ]

    results_list = []

    # Run each strategy
    for strategy in strategies:
        print(f"\nRunning: {strategy.get_name()}")
        print("-" * 80)

        backtester = Backtester(
            strategy=strategy,
            initial_capital=config.DEFAULT_INITIAL_CAPITAL,
            commission_rate=config.DEFAULT_COMMISSION_RATE,
            position_size=config.DEFAULT_POSITION_SIZE
        )

        results = backtester.run(data)
        results_list.append(results)

        # Print summary
        print(f"Total Return: {results['total_return']:.2f}%")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")

    # Compare strategies
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80 + "\n")

    comparison_df = StrategyComparison.compare_strategies(results_list)
    print(comparison_df.to_string(index=False))

    # Save comparison
    output_path = config.OUTPUT_DIR / 'strategy_comparison.csv'
    comparison_df.to_csv(output_path, index=False)
    print(f"\n✓ Comparison saved to: {output_path}")


def run_parameter_optimization():
    """Run parameter optimization for a strategy."""
    print("\n" + "="*80)
    print("PARAMETER OPTIMIZATION")
    print("="*80 + "\n")

    # Load data
    loader = DataLoader(data_dir=str(config.DATA_DIR))
    data = loader.load_data(
        exchange=config.DEFAULT_EXCHANGE,
        start_date='2024-09-01',
        end_date='2024-10-01'
    )
    data = resample_data(data, timeframe='5T')

    print(f"Loaded {len(data):,} rows\n")
    print("Optimizing Moving Average Crossover parameters...")
    print("-" * 80)

    best_result = None
    best_return = -float('inf')

    # Grid search over parameter space
    fast_periods = [5, 10, 15, 20]
    slow_periods = [20, 30, 40, 50]

    total_tests = len(fast_periods) * len(slow_periods)
    test_count = 0

    results_list = []

    for fast in fast_periods:
        for slow in slow_periods:
            if fast >= slow:
                continue

            test_count += 1
            print(f"\nTest {test_count}: fast={fast}, slow={slow}")

            strategy = MovingAverageCrossover(
                fast_period=fast,
                slow_period=slow,
                ma_type='EMA'
            )

            backtester = Backtester(
                strategy=strategy,
                initial_capital=config.DEFAULT_INITIAL_CAPITAL,
                commission_rate=config.DEFAULT_COMMISSION_RATE,
                position_size=config.DEFAULT_POSITION_SIZE
            )

            results = backtester.run(data)
            results_list.append(results)

            print(f"  Return: {results['total_return']:.2f}%, "
                  f"Win Rate: {results['win_rate']:.2f}%, "
                  f"Sharpe: {results['sharpe_ratio']:.2f}")

            if results['total_return'] > best_return:
                best_return = results['total_return']
                best_result = results

    # Print best result
    print("\n" + "="*80)
    print("OPTIMIZATION RESULTS")
    print("="*80 + "\n")
    print(f"Best Parameters:")
    for key, value in best_result['parameters'].items():
        print(f"  {key}: {value}")

    print(f"\nBest Performance:")
    print(f"  Total Return: {best_result['total_return']:.2f}%")
    print(f"  Win Rate: {best_result['win_rate']:.2f}%")
    print(f"  Sharpe Ratio: {best_result['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {best_result['max_drawdown']:.2f}%")

    # Save all results
    comparison_df = StrategyComparison.compare_strategies(results_list)
    output_path = config.OUTPUT_DIR / 'parameter_optimization.csv'
    comparison_df.to_csv(output_path, index=False)
    print(f"\n✓ Optimization results saved to: {output_path}")


def main():
    """Main function with menu."""
    config.OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "="*80)
    print("CRYPTO BACKTESTING ENGINE")
    print("="*80 + "\n")

    print("Select mode:")
    print("1. Run single strategy backtest (with full report)")
    print("2. Compare multiple strategies")
    print("3. Parameter optimization")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == '1':
        run_single_strategy_backtest()
    elif choice == '2':
        run_strategy_comparison()
    elif choice == '3':
        run_parameter_optimization()
    elif choice == '4':
        print("Exiting...")
        return
    else:
        print("Invalid choice!")


if __name__ == '__main__':
    main()
