# 📖 Usage Summary - Your Backtesting Engine

## 🎯 Three Ways to Use Your Engine

### 1️⃣ **Quick Demo** (Fastest - 30 seconds)
```bash
python quickstart.py
```
- Pre-configured strategy
- Automatic report generation
- See results immediately

### 2️⃣ **Interactive Menu** (Easiest)
```bash
python main.py
```
Choose from:
- Single strategy backtest
- Compare 4 strategies
- Parameter optimization

### 3️⃣ **Custom Python Script** (Most Flexible)
```bash
python examples/usage_examples.py
```
- 9 complete examples
- Copy and modify for your needs
- Full control

---

## 📊 Basic Code Pattern

```python
# This is all you need!
from data_handlers.loader import DataLoader
from engine.backtest import Backtester
from examples.moving_average_strategy import MovingAverageCrossover

# Load → Create → Run
data = DataLoader().load_data(exchange='Combined_Index', start_date='2023-01-01')
strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
results = Backtester(strategy, initial_capital=10000).run(data)

print(f"Return: {results['total_return']:.2f}%")
```

---

## 🎨 Built-in Strategies

| Strategy | Code | Parameters |
|----------|------|------------|
| **Moving Average** | `MovingAverageCrossover(10, 30)` | fast, slow, ma_type |
| **RSI** | `RSIStrategy(14, 30, 70)` | period, oversold, overbought |
| **Bollinger Bands** | `BollingerBandsStrategy(20, 2.0)` | period, std_dev |
| **MACD** | `MACDStrategy(12, 26, 9)` | fast, slow, signal |

---

## 🔧 Configuration Options

```python
backtester = Backtester(
    strategy=your_strategy,
    initial_capital=10000.0,    # Starting money
    commission_rate=0.001,      # 0.1% per trade
    position_size=1.0,          # Use 100% of capital
    allow_short=False,          # No short selling
    slippage=0.0005            # 0.05% slippage
)
```

---

## 📈 What You Get Back

```python
results = {
    'total_return': 15.5,           # % return
    'sharpe_ratio': 2.3,            # Risk-adjusted return
    'max_drawdown': 8.2,            # Max loss %
    'win_rate': 65.0,               # % winning trades
    'total_trades': 24,             # Number of trades
    'profit_factor': 2.1,           # Profit/Loss ratio
    'equity_curve': DataFrame,      # Equity over time
    'trades': DataFrame,            # All trades
    'signals': DataFrame            # All signals
}
```

---

## 🎯 Common Tasks

### Load Different Timeframes
```python
from data_handlers.loader import resample_data

data_5m = resample_data(data, '5T')    # 5 minutes
data_1h = resample_data(data, '1H')    # 1 hour
data_daily = resample_data(data, '1D') # Daily
```

### Compare Strategies
```python
strategies = [
    MovingAverageCrossover(10, 30),
    RSIStrategy(14, 30, 70),
    BollingerBandsStrategy(20, 2.0)
]

for strategy in strategies:
    results = Backtester(strategy, 10000).run(data)
    print(f"{strategy.get_name()}: {results['total_return']:.2f}%")
```

### Find Best Parameters
```python
best_return = -float('inf')

for fast in [5, 10, 15, 20]:
    for slow in [30, 40, 50]:
        strategy = MovingAverageCrossover(fast, slow)
        results = Backtester(strategy, 10000).run(data)

        if results['total_return'] > best_return:
            best_return = results['total_return']
            best_params = (fast, slow)

print(f"Best: fast={best_params[0]}, slow={best_params[1]}")
```

### Generate Full Report
```python
from analytics.reports import ReportGenerator

report_gen = ReportGenerator()
report_path = report_gen.generate_full_report(results, save_charts=True)
```

---

## 🏗️ Create Custom Strategy

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

        # Your logic here
        df.loc[df['close'] > df['sma'], 'signal'] = SignalType.BUY.value
        df.loc[df['close'] < df['sma'], 'signal'] = SignalType.SELL.value

        return df

    def get_parameters(self):
        return self.params
```

---

## 📦 Available Data

| Exchange | Size | Date Range |
|----------|------|------------|
| Combined_Index ⭐ | 290 MB | 2016-2024 |
| Binance | 526 MB | 2016-2024 |
| Coinbase | 270 MB | 2016-2024 |
| OKX | 361 MB | 2016-2024 |
| BitMEX | 200 MB | 2016-2024 |
| Bitfinex | 225 MB | 2016-2024 |
| Bitstamp | 235 MB | 2016-2024 |
| KuCoin | 283 MB | 2016-2024 |

**Total:** 4.7 million+ data points!

---

## 📊 Performance Metrics Explained

| Metric | Good Value | What It Means |
|--------|------------|---------------|
| **Total Return** | >10% | Overall profit/loss |
| **Sharpe Ratio** | >1.0 | Return per unit of risk |
| **Win Rate** | >50% | % of profitable trades |
| **Profit Factor** | >1.5 | Gross profit ÷ Gross loss |
| **Max Drawdown** | <20% | Worst peak-to-trough loss |
| **Sortino Ratio** | >1.0 | Like Sharpe, only downside risk |

---

## 🎓 Learning Path

1. **Start Here:** Run `python quickstart.py`
2. **Explore:** Run `python examples/usage_examples.py` (choose example 1)
3. **Understand:** Read through examples 1-9 in [usage_examples.py](examples/usage_examples.py)
4. **Experiment:** Modify parameters in quickstart.py
5. **Create:** Build your own strategy (see example 3)
6. **Optimize:** Find best parameters (see example 4)
7. **Compare:** Test multiple strategies (see example 5)

---

## 🚀 Quick Start Commands

```bash
# Verify everything works
python verify_setup.py

# Quick demo
python quickstart.py

# Interactive menu
python main.py

# All examples
python examples/usage_examples.py

# Check data
ls -lh csv_data/
```

---

## 💡 Pro Tips

1. **Start Small:** Test on 1-3 months before running full dataset
2. **Use Higher Timeframes:** 1H is faster than 1m (100x speedup)
3. **Realistic Settings:** Include commissions (0.1-0.2% typical)
4. **Avoid Overfitting:** Test on different time periods
5. **Check Drawdown:** High returns with huge drawdown = risky
6. **Walk-Forward:** Optimize on period A, test on period B

---

## 📚 Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Code snippets | Need specific code |
| [USAGE_SUMMARY.md](USAGE_SUMMARY.md) ⭐ | Overview (this file) | Starting out |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Complete guide | Deep dive |
| [README.md](README.md) | Full documentation | Everything |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Technical details | Architecture |

---

## 🎯 Quick Recipes

### Recipe 1: "Just Show Me Results"
```bash
python quickstart.py
open output/RSI_Strategy_report/equity_curve.png
```

### Recipe 2: "Test My Idea"
```python
# Edit quickstart.py, change line 47:
strategy = RSIStrategy(rsi_period=10, oversold_threshold=25, overbought_threshold=75)
# Save and run
python quickstart.py
```

### Recipe 3: "Find Best Settings"
```bash
python main.py
# Choose option 3: Parameter optimization
```

### Recipe 4: "Compare All Strategies"
```bash
python main.py
# Choose option 2: Compare multiple strategies
```

### Recipe 5: "Build My Own"
```python
# Copy examples/moving_average_strategy.py
# Modify generate_signals() with your logic
# Run it!
```

---

## 🔥 Most Common Code Patterns

### Pattern 1: Basic Backtest
```python
from data_handlers.loader import DataLoader
from engine.backtest import Backtester
from examples.moving_average_strategy import MovingAverageCrossover

data = DataLoader().load_data(exchange='Combined_Index', start_date='2023-01-01')
strategy = MovingAverageCrossover(10, 30)
results = Backtester(strategy, 10000).run(data)
print(f"Return: {results['total_return']:.2f}%")
```

### Pattern 2: With Report
```python
# Add these lines after running backtest:
from analytics.reports import ReportGenerator
ReportGenerator().generate_full_report(results, save_charts=True)
```

### Pattern 3: Parameter Loop
```python
for fast in [5, 10, 15]:
    for slow in [20, 30, 40]:
        strategy = MovingAverageCrossover(fast, slow)
        results = Backtester(strategy, 10000).run(data)
        print(f"Fast={fast}, Slow={slow}: {results['total_return']:.2f}%")
```

---

## ✅ Checklist for New Users

- [ ] Run `python verify_setup.py` - Everything working?
- [ ] Run `python quickstart.py` - See first results?
- [ ] Open `output/RSI_Strategy_report/` - Check charts?
- [ ] Run `python examples/usage_examples.py` - Try example 1?
- [ ] Modify `quickstart.py` parameters - Test different settings?
- [ ] Create your first custom strategy - Follow example 3?
- [ ] Run parameter optimization - Find best settings?
- [ ] Compare strategies - Which works best?

---

## 🆘 Common Questions

**Q: How do I make it faster?**
A: Use `resample_data(data, '1H')` for hourly instead of minute data

**Q: How do I test different exchanges?**
A: Change `exchange='Combined_Index'` to `exchange='Binance'` etc.

**Q: How do I save results?**
A: Use `ReportGenerator().generate_full_report(results)`

**Q: How do I create my own strategy?**
A: See example 3 in `examples/usage_examples.py`

**Q: Where are the charts saved?**
A: In `output/[StrategyName]_report/` folder

**Q: Can I test on multiple assets?**
A: Currently ETH/USD only, but framework supports adding more

**Q: How do I optimize parameters?**
A: Run `python main.py` and choose option 3

---

## 🎉 You're Ready!

**Start with:** `python quickstart.py`

**Then explore:** `python examples/usage_examples.py`

**Build your own:** Copy any example and modify!

**Need help?** Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for code snippets

---

**Happy Backtesting! 🚀📈**
