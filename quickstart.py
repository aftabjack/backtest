"""
Quick start script for immediate backtesting.
Run this to see the engine in action immediately.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from data_handlers.loader import DataLoader, resample_data
from engine.backtest import Backtester
from analytics.reports import ReportGenerator
from examples.moving_average_strategy import MovingAverageCrossover

import config


def quick_backtest():
    """Run a quick backtest demonstration."""
    print("\n" + "="*80)
    print("QUICK START - CRYPTO BACKTESTING ENGINE")
    print("="*80 + "\n")

    try:
        # Load data
        print("📊 Loading data...")
        loader = DataLoader(data_dir=str(config.DATA_DIR))

        # Load data from 2023 (more volatility = more trades)
        data = loader.load_data(
            exchange='Combined_Index',
            start_date='2023-01-01',
            end_date='2023-03-31'
        )

        print(f"✓ Loaded {len(data):,} rows of ETH/USD data")

        # Resample to 1-hour bars for faster demo with more trades
        print("\n⏱️  Resampling to 1-hour timeframe...")
        data = resample_data(data, timeframe='1H')
        print(f"✓ Resampled to {len(data):,} bars")

        # Initialize RSI strategy (more active than MA crossover)
        print("\n🎯 Initializing RSI Mean Reversion strategy...")
        from examples.rsi_strategy import RSIStrategy
        strategy = RSIStrategy(
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70
        )
        print(f"✓ Strategy: {strategy}")

        # Run backtest
        print("\n🚀 Running backtest...")
        backtester = Backtester(
            strategy=strategy,
            initial_capital=10000.0,
            commission_rate=0.001,
            position_size=1.0
        )

        results = backtester.run(data)

        # Print summary
        print("\n" + "="*80)
        print("QUICK RESULTS SUMMARY")
        print("="*80)
        print(f"\n💰 Initial Capital:  ${results['initial_capital']:>12,.2f}")
        print(f"💵 Final Equity:     ${results['final_equity']:>12,.2f}")
        print(f"📈 Total Return:     {results['total_return']:>12,.2f}%")
        print(f"📊 Total Trades:     {results['total_trades']:>12}")
        print(f"✅ Winning Trades:   {results['winning_trades']:>12}")
        print(f"❌ Losing Trades:    {results['losing_trades']:>12}")
        print(f"🎯 Win Rate:         {results['win_rate']:>12,.2f}%")
        print(f"💎 Profit Factor:    {results['profit_factor']:>12,.2f}")
        print(f"📉 Max Drawdown:     {results['max_drawdown']:>12,.2f}%")
        print(f"📊 Sharpe Ratio:     {results['sharpe_ratio']:>12,.2f}")

        # Generate report
        print("\n" + "="*80)
        print("📄 Generating detailed report...")
        report_gen = ReportGenerator(output_dir=str(config.OUTPUT_DIR))
        report_path = report_gen.generate_full_report(
            results=results,
            save_charts=True,
            show_charts=False
        )

        print("\n" + "="*80)
        print("✅ BACKTEST COMPLETE!")
        print("="*80)
        print(f"\n📁 Full report saved to: {report_path}")
        print("\nFiles generated:")
        print("  • results.json           - Detailed results in JSON format")
        print("  • trades.csv             - Complete trade history")
        print("  • equity_curve.csv       - Equity over time")
        print("  • report.txt             - Text summary report")
        print("  • equity_curve.png       - Equity curve visualization")
        print("  • drawdown.png           - Drawdown analysis chart")
        print("  • trade_distribution.png - Trade P&L distribution")
        print("  • monthly_returns.png    - Monthly returns heatmap")
        print("  • returns_comparison.png - Strategy vs Buy & Hold")

        print("\n💡 Next steps:")
        print("  1. Check the generated charts in the output folder")
        print("  2. Review the detailed report.txt file")
        print("  3. Analyze trades.csv for individual trade performance")
        print("  4. Run 'python main.py' for more options:")
        print("     - Compare multiple strategies")
        print("     - Optimize parameters")
        print("     - Test different timeframes")
        print("\n  5. Create your own custom strategy by extending BaseStrategy")
        print("     (See examples/ folder for templates)")

        print("\n🎉 Happy backtesting!\n")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure you have downloaded the ETH/USD data to csv_data/ folder")
        print("   Data should be available from the Kaggle dataset")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    quick_backtest()
