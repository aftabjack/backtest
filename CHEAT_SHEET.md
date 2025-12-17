# 🚀 Backtesting Engine - Cheat Sheet

## ⚡ One-Liners

```python
# Simplest possible backtest
from data_handlers.loader import DataLoader; from engine.backtest import Backtester; from examples.moving_average_strategy import MovingAverageCrossover; Backtester(MovingAverageCrossover(10, 30), 10000).run(DataLoader().load_data(exchange='Combined_Index', start_date='2023-01-01'))
```

---

## 📊 Load Data

```python
from data_handlers.loader import DataLoader, resample_data

# Basic
data = DataLoader().load_data(exchange='Combined_Index', start_date='2023-01-01')

# Different exchange
data = DataLoader().load_data(exchange='Binance', start_date='2023-01-01')

# Date range
data = DataLoader().load_data(exchange='Combined_Index', start_date='2023-01-01', end_date='2023-12-31')

# Resample
data_1h = resample_data(data, '1H')   # Hourly
data_daily = resample_data(data, '1D') # Daily
```

---

## 🎯 Create Strategy

```python
from examples.moving_average_strategy import MovingAverageCrossover
from examples.rsi_strategy import RSIStrategy
from examples.bollinger_bands_strategy import BollingerBandsStrategy
from examples.macd_strategy import MACDStrategy

# Choose one
strategy = MovingAverageCrossover(10, 30, 'EMA')
strategy = RSIStrategy(14, 30, 70)
strategy = BollingerBandsStrategy(20, 2.0)
strategy = MACDStrategy(12, 26, 9)
```

---

## 🚀 Run Backtest

```python
from engine.backtest import Backtester

# Basic
backtester = Backtester(strategy, initial_capital=10000)
results = backtester.run(data)
backtester.print_results()

# With config
backtester = Backtester(strategy, initial_capital=10000, commission_rate=0.001, position_size=1.0)
results = backtester.run(data)
```

---

## 📈 Get Results

```python
# Key metrics
results['total_return']      # % return
results['sharpe_ratio']      # Risk-adjusted return
results['max_drawdown']      # Max loss %
results['win_rate']          # % winning trades
results['total_trades']      # Number of trades
results['profit_factor']     # Profit/Loss ratio

# DataFrames
results['equity_curve']      # Equity over time
results['trades']            # All trades
results['signals']           # All signals
```

---

## 📊 Generate Report

```python
from analytics.reports import ReportGenerator

ReportGenerator().generate_full_report(results, save_charts=True)
```

---

## 🔧 Custom Strategy Template

```python
from strategies.base_strategy import BaseStrategy, SignalType, IndicatorMixin

class MyStrategy(BaseStrategy, IndicatorMixin):
    def __init__(self, period=20):
        super().__init__('My Strategy', {'period': period})
        self.period = period

    def calculate_indicators(self):
        self.data['sma'] = self.calculate_sma(self.data['close'], self.period)
        return self.data

    def generate_signals(self, data):
        df = data.copy()
        df['signal'] = SignalType.HOLD.value
        df.loc[df['close'] > df['sma'], 'signal'] = SignalType.BUY.value
        df.loc[df['close'] < df['sma'], 'signal'] = SignalType.SELL.value
        return df

    def get_parameters(self):
        return self.params
```

---

## 🎯 Common Patterns

### Parameter Optimization
```python
best = {'return': -float('inf')}
for fast in [5, 10, 15]:
    for slow in [20, 30, 40]:
        results = Backtester(MovingAverageCrossover(fast, slow), 10000).run(data)
        if results['total_return'] > best['return']:
            best = {'fast': fast, 'slow': slow, 'return': results['total_return']}
```

### Strategy Comparison
```python
from analytics.metrics import StrategyComparison
strategies = [MovingAverageCrossover(10, 30), RSIStrategy(14, 30, 70)]
results = [Backtester(s, 10000).run(data) for s in strategies]
comparison = StrategyComparison.compare_strategies(results)
```

### Multiple Timeframes
```python
for tf in ['5T', '15T', '1H', '4H']:
    data_tf = resample_data(data, tf)
    results = Backtester(strategy, 10000).run(data_tf)
    print(f"{tf}: {results['total_return']:.2f}%")
```

---

## 📝 Built-in Indicators

```python
# In your strategy's calculate_indicators() method:

self.calculate_sma(self.data['close'], period=20)
self.calculate_ema(self.data['close'], period=20)
self.calculate_rsi(self.data['close'], period=14)
self.calculate_bollinger_bands(self.data['close'], period=20, std_dev=2.0)
self.calculate_macd(self.data['close'], fast=12, slow=26, signal=9)
self.calculate_atr(self.data['high'], self.data['low'], self.data['close'], period=14)
```

---

## ⚙️ Configuration

```python
Backtester(
    strategy=strategy,
    initial_capital=10000.0,    # Starting capital
    commission_rate=0.001,      # 0.1%
    position_size=1.0,          # 100%
    allow_short=False,          # No shorts
    slippage=0.0005            # 0.05%
)
```

---

## 🔍 Available Exchanges

```python
'Combined_Index'  # ⭐ Recommended
'Binance'
'Coinbase'
'OKX'
'BitMEX'
'Bitfinex'
'Bitstamp'
'KuCoin'
```

---

## 📊 Timeframe Codes

```python
'1T'   # 1 minute
'5T'   # 5 minutes
'15T'  # 15 minutes
'30T'  # 30 minutes
'1H'   # 1 hour
'4H'   # 4 hours
'1D'   # 1 day
```

---

## 🎯 Quick Commands

```bash
python quickstart.py                    # Quick demo
python main.py                          # Interactive menu
python examples/usage_examples.py       # All examples
python verify_setup.py                  # Check setup
```

---

## 📈 Metric Targets

| Metric | Good | Great |
|--------|------|-------|
| Return | >10% | >50% |
| Sharpe | >1.0 | >2.0 |
| Win Rate | >50% | >60% |
| Profit Factor | >1.5 | >2.0 |
| Max Drawdown | <20% | <10% |

---

## 🆘 Quick Fixes

```python
# Too slow?
data = resample_data(data, '1H')  # Use hourly

# No trades?
print(f"Buy signals: {(signals['signal'] == 1).sum()}")
print(f"Sell signals: {(signals['signal'] == -1).sum()}")

# Position not opening?
# Check commission settings (already fixed!)

# Want more trades?
# Adjust strategy parameters to be more aggressive
```

---

## 📚 File Quick Reference

| File | Purpose |
|------|---------|
| `quickstart.py` | Quick demo |
| `main.py` | Interactive app |
| `examples/usage_examples.py` | 9 examples |
| `examples/*.py` | Strategy templates |
| `QUICK_REFERENCE.md` | Detailed code |
| `USAGE_SUMMARY.md` | This guide |

---

**Copy, paste, modify, run! 🚀**
