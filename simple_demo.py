"""
SIMPLE DEMO - Backtesting Engine for Absolute Beginners
========================================================

This is the SIMPLEST possible example.
Even if you're new to Python, you can understand and run this!

What this does:
1. Loads cryptocurrency price data (ETH/USD)
2. Tests a simple trading strategy
3. Shows you if you would have made money or lost money

That's it! Nothing complicated.
"""

# ============================================================================
# STEP 1: Import the tools we need
# ============================================================================
# Think of these like importing different apps on your phone
# Each one does something specific for us

from data_handlers.loader import DataLoader          # Loads price data
from engine.backtest import Backtester               # Tests our strategy
from examples.moving_average_strategy import MovingAverageCrossover  # A simple strategy


# ============================================================================
# STEP 2: Load the price data
# ============================================================================
print("\n" + "="*60)
print("STEP 1: Loading Price Data")
print("="*60)

# Create a data loader (like opening a file reader)
loader = DataLoader()

# Load ETH/USD prices from January to March 2023
# Think of this like getting a spreadsheet with dates and prices
data = loader.load_data(
    exchange='Combined_Index',      # Which exchange to use
    start_date='2023-01-01',       # Start date
    end_date='2023-03-31'          # End date
)

print(f"✓ Loaded {len(data):,} rows of price data")
print(f"  Date range: {data.index[0]} to {data.index[-1]}")
print(f"  Starting price: ${data['close'].iloc[0]:.2f}")
print(f"  Ending price: ${data['close'].iloc[-1]:.2f}")


# ============================================================================
# STEP 3: Choose a trading strategy
# ============================================================================
print("\n" + "="*60)
print("STEP 2: Creating Trading Strategy")
print("="*60)

# We'll use a simple "Moving Average Crossover" strategy
# What it does:
#   - BUY when short-term average crosses above long-term average
#   - SELL when short-term average crosses below long-term average
#
# Think of it like:
#   - If recent prices are higher than older prices → Buy (price going up!)
#   - If recent prices are lower than older prices → Sell (price going down!)

strategy = MovingAverageCrossover(
    fast_period=10,     # Look at last 10 periods for "recent" price
    slow_period=30,     # Look at last 30 periods for "older" price
    ma_type='EMA'       # Type of average (EMA is smoother than SMA)
)

print(f"✓ Strategy created: {strategy.get_name()}")
print(f"  Fast period: 10 (recent trend)")
print(f"  Slow period: 30 (longer trend)")
print(f"  Logic: Buy when recent > older, Sell when recent < older")


# ============================================================================
# STEP 4: Run the backtest
# ============================================================================
print("\n" + "="*60)
print("STEP 3: Testing Strategy on Historical Data")
print("="*60)

# Create a backtester with $10,000 starting capital
# This simulates: "What if I had $10,000 and used this strategy?"
backtester = Backtester(
    strategy=strategy,
    initial_capital=10000.0    # Start with $10,000
)

print("Running backtest...")
print("(This simulates trading based on the strategy)")

# Run the backtest - this tests our strategy on the historical data
results = backtester.run(data)

print("✓ Backtest complete!")


# ============================================================================
# STEP 5: Show the results in SIMPLE terms
# ============================================================================
print("\n" + "="*60)
print("RESULTS - Did We Make Money?")
print("="*60)

# Extract the important numbers
starting_money = results['initial_capital']
ending_money = results['final_equity']
profit_or_loss = ending_money - starting_money
return_percentage = results['total_return']
num_trades = results['total_trades']
wins = results['winning_trades']
losses = results['losing_trades']

# Show results in plain English
print(f"\n💰 Your Money:")
print(f"   Started with:  ${starting_money:,.2f}")
print(f"   Ended with:    ${ending_money:,.2f}")

if profit_or_loss > 0:
    print(f"   Profit:        ${profit_or_loss:,.2f} ✅ (You made money!)")
    print(f"   Return:        {return_percentage:.2f}% ✅")
else:
    print(f"   Loss:          ${abs(profit_or_loss):,.2f} ❌ (You lost money)")
    print(f"   Return:        {return_percentage:.2f}% ❌")

print(f"\n📊 Trading Activity:")
print(f"   Total trades:  {num_trades}")
print(f"   Winning:       {wins} trades")
print(f"   Losing:        {losses} trades")

if num_trades > 0:
    win_rate = (wins / num_trades) * 100
    print(f"   Win rate:      {win_rate:.1f}%")


# ============================================================================
# STEP 6: More detailed metrics (optional)
# ============================================================================
print(f"\n📈 More Details (for advanced users):")
print(f"   Sharpe Ratio:  {results['sharpe_ratio']:.2f}")
print(f"   (measures risk-adjusted return - higher is better)")
print(f"   ")
print(f"   Max Drawdown:  {results['max_drawdown']:.2f}%")
print(f"   (biggest drop from peak - lower is better)")


# ============================================================================
# DONE!
# ============================================================================
print("\n" + "="*60)
print("✅ Demo Complete!")
print("="*60)

print("\n💡 What Just Happened:")
print("   1. We loaded 3 months of ETH/USD price data")
print("   2. We tested a Moving Average trading strategy")
print("   3. The strategy decided when to buy and sell")
print("   4. We calculated if we would have made money")

print("\n🎯 Next Steps:")
print("   • Try changing the dates (line 39)")
print("   • Try different strategy parameters (line 58-60)")
print("   • Try different strategies from examples/ folder")
print("   • Run 'python examples/usage_examples.py' for more examples")

print("\n📚 Learn More:")
print("   • Quick guide: CHEAT_SHEET.md")
print("   • Full examples: examples/usage_examples.py")
print("   • Documentation: START_HERE.md")

print("\n🚀 Happy Trading!\n")


# ============================================================================
# BONUS: Save detailed results to a file
# ============================================================================
# Uncomment these lines if you want to save results to CSV files:

# print("💾 Saving results to files...")
# results['trades'].to_csv('my_trades.csv')
# results['equity_curve'].to_csv('my_equity.csv')
# print("   ✓ Saved to: my_trades.csv and my_equity.csv")


# ============================================================================
# BONUS: Generate a full report with charts
# ============================================================================
# Uncomment these lines if you want to generate charts:

# from analytics.reports import ReportGenerator
# print("\n📊 Generating charts...")
# report_gen = ReportGenerator()
# report_path = report_gen.generate_full_report(results, save_charts=True)
# print(f"   ✓ Charts saved to: {report_path}")


# ============================================================================
# EXPLANATIONS FOR BEGINNERS
# ============================================================================

"""
COMMON QUESTIONS:

Q: What is a "backtest"?
A: Testing a trading strategy on old data to see if it would have worked.
   Like: "If I used this strategy last year, would I have made money?"

Q: What is a "strategy"?
A: A set of rules for when to buy and sell.
   Example: "Buy when price goes up, sell when price goes down"

Q: What is "Moving Average"?
A: The average price over a period. Like taking the average of the last 10 days.
   It smooths out the price to see the trend.

Q: What do the numbers mean?
A: - Return: How much % profit or loss you made
   - Sharpe Ratio: Return adjusted for risk (higher = better)
   - Max Drawdown: Biggest loss from peak (lower = better)
   - Win Rate: What % of trades were profitable

Q: Can I change the strategy?
A: Yes! Look at examples/ folder for more strategies.
   Or create your own by copying an example.

Q: Is this real trading?
A: No! This is simulation using historical data.
   It shows what WOULD have happened, not what WILL happen.

Q: Can I lose real money with this?
A: No! This is just testing. No real money involved.
   It's like a video game - practice with fake money.

Q: How do I use this for real trading?
A: STOP! Don't use this for real trading without understanding it fully.
   This is for learning and testing only.

Q: What if I get errors?
A: Run 'python verify_setup.py' to check your installation.
   Make sure you have all the required packages installed.

Q: Where can I learn more?
A: 1. Start with START_HERE.md
   2. Read CHEAT_SHEET.md for quick examples
   3. Run examples/usage_examples.py for detailed examples
   4. Read GETTING_STARTED.md for complete guide
"""
