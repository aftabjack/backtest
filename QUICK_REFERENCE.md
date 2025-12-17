# 🚀 Quick Reference Guide

## 📖 Table of Contents
1. [Basic Usage](#basic-usage)
2. [Load Data](#load-data)
3. [Create Strategy](#create-strategy)
4. [Run Backtest](#run-backtest)
5. [Generate Reports](#generate-reports)
6. [Custom Strategy](#custom-strategy)
7. [Common Patterns](#common-patterns)

---

## 🎯 Basic Usage

### Simplest Possible Backtest (5 lines)

```python
from data_handlers.loader import DataLoader
from engine.backtest import Backtester
from examples.moving_average_strategy import MovingAverageCrossover

data = DataLoader().load_data(exchange='Combined_Index', start_date='2023-01-01')
results = Backtester(MovingAverageCrossover(10, 30), initial_capital=10000).run(data)
```

That's it! 🎉

---

## 📊 Load Data

### Basic Loading
```python
from data_handlers.loader import DataLoader

loader = DataLoader()

# Load specific period
data = loader.load_data(
    exchange='Combined_Index',
    start_date='2023-01-01',
    end_date='2023-12-31'
)
```

### Different Exchanges
```python
# Available exchanges
exchanges = ['Binance', 'Coinbase', 'BitMEX', 'Bitfinex',
             'Bitstamp', 'Combined_Index', 'KuCoin', 'OKX']

data = loader.load_data(exchange='Binance', start_date='2023-01-01')
```

### Resample Timeframes
```python
from data_handlers.loader import resample_data

# Convert to different timeframes
data_5m = resample_data(data, '5T')    # 5 minutes
data_15m = resample_data(data, '15T')  # 15 minutes
data_1h = resample_data(data, '1H')    # 1 hour
data_4h = resample_data(data, '4H')    # 4 hours
data_daily = resample_data(data, '1D') # Daily
```

### Data Info
```python
info = loader.get_data_info(exchange='Combined_Index')
print(f"Total rows: {info['rows']:,}")
print(f"Date range: {info['start_date']} to {info['end_date']}")
print(f"Price range: ${info['price_range']['min']:.2f} - ${info['price_range']['max']:.2f}")
```

---

## 🎯 Create Strategy

### Use Built-in Strategies

```python
from examples.moving_average_strategy import MovingAverageCrossover
from examples.rsi_strategy import RSIStrategy
from examples.bollinger_bands_strategy import BollingerBandsStrategy
from examples.macd_strategy import MACDStrategy

# Moving Average
strategy = MovingAverageCrossover(
    fast_period=10,
    slow_period=30,
    ma_type='EMA'  # or 'SMA'
)

# RSI
strategy = RSIStrategy(
    rsi_period=14,
    oversold_threshold=30,
    overbought_threshold=70
)

# Bollinger Bands
strategy = BollingerBandsStrategy(
    period=20,
    std_dev=2.0
)

# MACD
strategy = MACDStrategy(
    fast_period=12,
    slow_period=26,
    signal_period=9
)
```

---

## 🚀 Run Backtest

### Basic Backtest
```python
from engine.backtest import Backtester

backtester = Backtester(
    strategy=strategy,
    initial_capital=10000
)

results = backtester.run(data)
backtester.print_results()
```

### With Configuration
```python
backtester = Backtester(
    strategy=strategy,
    initial_capital=10000.0,
    commission_rate=0.001,    # 0.1% commission
    position_size=1.0,        # 100% of capital
    allow_short=False,        # No short selling
    slippage=0.0005          # 0.05% slippage
)

results = backtester.run(data)
```

### Access Results
```python
# Performance metrics
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Total Trades: {results['total_trades']}")

# Get DataFrames
equity_curve = results['equity_curve']
trades = results['trades']
signals = results['signals']

# Save to CSV
trades.to_csv('my_trades.csv')
equity_curve.to_csv('my_equity.csv')
```

---

## 📈 Generate Reports

### Full Report with Charts
```python
from analytics.reports import ReportGenerator

report_gen = ReportGenerator(output_dir='output')
report_path = report_gen.generate_full_report(
    results=results,
    save_charts=True,
    show_charts=False  # Set True to display
)

print(f"Report saved to: {report_path}")
```

This generates:
- `equity_curve.png` - Performance chart
- `drawdown.png` - Risk visualization
- `trade_distribution.png` - Win/loss analysis
- `monthly_returns.png` - Calendar heatmap
- `returns_comparison.png` - vs Buy & Hold
- `trades.csv` - Trade log
- `results.json` - Full data
- `report.txt` - Summary

---

## 🔧 Custom Strategy

### Template
```python
from strategies.base_strategy import BaseStrategy, SignalType, IndicatorMixin
import pandas as pd

class MyStrategy(BaseStrategy, IndicatorMixin):
    """Your custom strategy description."""

    def __init__(self, param1=10, param2=20):
        params = {'param1': param1, 'param2': param2}
        super().__init__(name='My Strategy', params=params)
        self.param1 = param1
        self.param2 = param2

    def calculate_indicators(self):
        """Calculate your indicators."""
        # Use built-in indicators
        self.data['sma'] = self.calculate_sma(self.data['close'], self.param1)
        self.data['rsi'] = self.calculate_rsi(self.data['close'], self.param2)
        return self.data

    def generate_signals(self, data):
        """Generate BUY/SELL/HOLD signals."""
        df = data.copy()
        df['signal'] = SignalType.HOLD.value

        in_position = False

        for i in range(1, len(df)):
            # Skip if indicators not ready
            if pd.isna(df['sma'].iloc[i]):
                continue

            # Your strategy logic
            if not in_position and df['close'].iloc[i] > df['sma'].iloc[i]:
                df.iloc[i, df.columns.get_loc('signal')] = SignalType.BUY.value
                in_position = True

            elif in_position and df['close'].iloc[i] < df['sma'].iloc[i]:
                df.iloc[i, df.columns.get_loc('signal')] = SignalType.SELL.value
                in_position = False

        return df

    def get_parameters(self):
        """Return strategy parameters."""
        return self.params

# Use it
strategy = MyStrategy(param1=20, param2=14)
backtester = Backtester(strategy, initial_capital=10000)
results = backtester.run(data)
```

### Available Built-in Indicators

```python
# In your calculate_indicators() method:

# Moving Averages
self.data['sma'] = self.calculate_sma(self.data['close'], period=20)
self.data['ema'] = self.calculate_ema(self.data['close'], period=20)

# RSI
self.data['rsi'] = self.calculate_rsi(self.data['close'], period=14)

# Bollinger Bands
upper, middle, lower = self.calculate_bollinger_bands(
    self.data['close'], period=20, std_dev=2.0
)
self.data['bb_upper'] = upper
self.data['bb_middle'] = middle
self.data['bb_lower'] = lower

# MACD
macd_line, signal_line, histogram = self.calculate_macd(
    self.data['close'],
    fast_period=12,
    slow_period=26,
    signal_period=9
)
self.data['macd'] = macd_line
self.data['macd_signal'] = signal_line
self.data['macd_hist'] = histogram

# ATR (Average True Range)
self.data['atr'] = self.calculate_atr(
    self.data['high'],
    self.data['low'],
    self.data['close'],
    period=14
)
```

---

## 🎯 Common Patterns

### 1. Parameter Optimization

```python
best_return = -float('inf')
best_params = None

for fast in [5, 10, 15, 20]:
    for slow in [20, 30, 40, 50]:
        if fast >= slow:
            continue

        strategy = MovingAverageCrossover(fast, slow)
        backtester = Backtester(strategy, initial_capital=10000)
        results = backtester.run(data)

        if results['total_return'] > best_return:
            best_return = results['total_return']
            best_params = (fast, slow)

print(f"Best params: fast={best_params[0]}, slow={best_params[1]}")
print(f"Best return: {best_return:.2f}%")
```

### 2. Strategy Comparison

```python
from analytics.metrics import StrategyComparison

strategies = [
    MovingAverageCrossover(10, 30),
    RSIStrategy(14, 30, 70),
    BollingerBandsStrategy(20, 2.0),
    MACDStrategy(12, 26, 9)
]

results_list = []
for strategy in strategies:
    backtester = Backtester(strategy, initial_capital=10000)
    results = backtester.run(data)
    results_list.append(results)

# Compare
comparison = StrategyComparison.compare_strategies(results_list)
print(comparison)

# Save
comparison.to_csv('strategy_comparison.csv')
```

### 3. Walk-Forward Testing

```python
# Train on first period, test on second
train_data = loader.load_data(start_date='2023-01-01', end_date='2023-06-30')
test_data = loader.load_data(start_date='2023-07-01', end_date='2023-12-31')

# Optimize on training data
# ... run optimization ...

# Test on unseen data
best_strategy = MovingAverageCrossover(best_fast, best_slow)
backtester = Backtester(best_strategy, initial_capital=10000)
results = backtester.run(test_data)

print(f"Out-of-sample return: {results['total_return']:.2f}%")
```

### 4. Multiple Timeframes

```python
timeframes = ['5T', '15T', '1H', '4H', '1D']

for tf in timeframes:
    data_resampled = resample_data(data, tf)
    backtester = Backtester(strategy, initial_capital=10000)
    results = backtester.run(data_resampled)

    print(f"{tf}: Return={results['total_return']:.2f}%, "
          f"Trades={results['total_trades']}")
```

### 5. Risk Management

```python
# Conservative settings
backtester = Backtester(
    strategy=strategy,
    initial_capital=10000,
    commission_rate=0.002,   # Higher commission
    position_size=0.5,       # Only 50% of capital
    slippage=0.001          # Account for slippage
)

results = backtester.run(data)

# Check risk metrics
if results['max_drawdown'] > 20:
    print("❌ Too much drawdown!")
elif results['sharpe_ratio'] < 1.0:
    print("⚠️ Poor risk-adjusted returns")
else:
    print("✅ Risk metrics acceptable")
```

---

## 📝 Complete Example

```python
# Complete workflow in one script
from data_handlers.loader import DataLoader, resample_data
from engine.backtest import Backtester
from examples.moving_average_strategy import MovingAverageCrossover
from analytics.reports import ReportGenerator

# 1. Load data
loader = DataLoader()
data = loader.load_data(
    exchange='Combined_Index',
    start_date='2023-01-01',
    end_date='2023-12-31'
)
data = resample_data(data, '1H')  # Use hourly data

# 2. Create strategy
strategy = MovingAverageCrossover(
    fast_period=10,
    slow_period=30,
    ma_type='EMA'
)

# 3. Configure backtester
backtester = Backtester(
    strategy=strategy,
    initial_capital=10000.0,
    commission_rate=0.001,
    position_size=1.0
)

# 4. Run backtest
results = backtester.run(data)

# 5. Print results
backtester.print_results()

# 6. Generate report
report_gen = ReportGenerator()
report_path = report_gen.generate_full_report(results, save_charts=True)

# 7. Access specific metrics
print(f"\nKey Metrics:")
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")

print(f"\nReport: {report_path}")
```

---

## 🎯 Quick Commands

```bash
# Run examples
python examples/usage_examples.py

# Quick demo
python quickstart.py

# Full application
python main.py

# Verify setup
python verify_setup.py
```

---

## 📚 More Help

- Full documentation: [README.md](README.md)
- Getting started: [GETTING_STARTED.md](GETTING_STARTED.md)
- All examples: [examples/usage_examples.py](examples/usage_examples.py)
- Strategy templates: [examples/](examples/)

---

**Happy Backtesting! 🚀**
