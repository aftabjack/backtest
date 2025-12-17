"""
Simple Backtest Demo
====================

Demonstrates the easiest way to use the backtesting engine.
"""

from backtest_engine import BacktestEngine
from examples.moving_average_strategy import MovingAverageCrossover

# Step 1: Create engine
engine = BacktestEngine()

# Step 2: Create strategy
strategy = MovingAverageCrossover(fast_period=10, slow_period=30)

# Step 3: Run backtest
results = engine.backtest(
    strategy=strategy,
    start_date='2023-01-01',
    end_date='2023-03-31',
    initial_capital=10000
)

# Step 4: View results
engine.print_results()

# Step 5: Generate report
engine.generate_report()

print("\n✅ Done! Check output/ folder for charts.")
