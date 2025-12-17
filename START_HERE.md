# 👋 START HERE - Your Backtesting Engine

## ⚡ Get Started in 30 Seconds

```bash
# For absolute beginners (step-by-step explanations)
python simple_demo.py

# OR for quick results
python quickstart.py
```

That's it! 🎉

---

## 📚 Documentation Guide

**Choose based on your needs:**

| If you want to... | Read this file | Time |
|-------------------|----------------|------|
| 🚀 **See it work NOW** | Run: `python quickstart.py` | 30 sec |
| 📖 **Quick code examples** | [CHEAT_SHEET.md](CHEAT_SHEET.md) | 2 min |
| 🎯 **Understand basics** | [USAGE_SUMMARY.md](USAGE_SUMMARY.md) | 5 min |
| 💻 **Copy-paste code** | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 10 min |
| 📘 **Complete guide** | [GETTING_STARTED.md](GETTING_STARTED.md) | 20 min |
| 🏗️ **Full documentation** | [README.md](README.md) | 30 min |
| 🔧 **Technical details** | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 15 min |
| 🎓 **Learn by doing** | [examples/usage_examples.py](examples/usage_examples.py) | 1 hour |

---

## 🎯 Three Ways to Use

### Option 1: Beginner Mode (Easiest - with explanations)
```bash
python simple_demo.py
```

### Option 2: Quick Demo (Fast results)
```bash
python quickstart.py
```

### Option 3: Interactive Menu
```bash
python main.py
# Choose: 1=Single test, 2=Compare, 3=Optimize
```

### Option 4: Write Code (Most Flexible)
```python
from data_handlers.loader import DataLoader
from engine.backtest import Backtester
from examples.moving_average_strategy import MovingAverageCrossover

data = DataLoader().load_data(exchange='Combined_Index', start_date='2023-01-01')
strategy = MovingAverageCrossover(10, 30)
results = Backtester(strategy, 10000).run(data)
print(f"Return: {results['total_return']:.2f}%")
```

---

## 📊 What You Have

✅ **2.4GB of ETH/USD data** from 8 exchanges (2016-2024)  
✅ **4 working strategies** (MA, RSI, Bollinger, MACD)  
✅ **20+ performance metrics** (Sharpe, Drawdown, Win Rate, etc.)  
✅ **5 chart types** per backtest (auto-generated)  
✅ **Complete examples** showing everything  
✅ **Docker support** for easy deployment  

---

## 🎓 Learning Path

1. **Day 1:** Run `python quickstart.py` - See it work
2. **Day 2:** Run `python examples/usage_examples.py` - Try examples 1-3
3. **Day 3:** Modify `quickstart.py` - Change parameters
4. **Day 4:** Copy example strategy - Make your own
5. **Day 5:** Run parameter optimization - Find best settings

---

## 🔥 Most Useful Files

```
backtest/
├── simple_demo.py             🎓 Run this FIRST (for beginners!)
├── quickstart.py              ⚡ Quick results
├── main.py                    🎯 Interactive app
├── examples/usage_examples.py 📖 9 complete examples
│
├── START_HERE.md             👈 You are here
├── CHEAT_SHEET.md            📝 Quick code snippets
├── USAGE_SUMMARY.md          📊 Usage overview
├── QUICK_REFERENCE.md        💻 Detailed code
├── GETTING_STARTED.md        📘 Complete guide
└── README.md                 📚 Full docs
```

---

## ✨ Quick Win

**For beginners - run this:**
```bash
python simple_demo.py
```

**For quick results - run this:**
```bash
python quickstart.py
```

**You just ran your first backtest!** 🎉

---

## 🆘 Need Help?

**Quick questions:** Check [CHEAT_SHEET.md](CHEAT_SHEET.md)  
**How to use:** Check [USAGE_SUMMARY.md](USAGE_SUMMARY.md)  
**Code examples:** Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)  
**Full guide:** Check [GETTING_STARTED.md](GETTING_STARTED.md)  

---

## 📈 What You'll See

After running `python quickstart.py`:

```
💰 Initial Capital:  $   10,000.00
💵 Final Equity:     $   10,159.10
📈 Total Return:             1.59%
📊 Total Trades:                1
✅ Winning Trades:              1
🎯 Win Rate:               100.00%
💎 Profit Factor:             inf
📉 Max Drawdown:             1.97%
📊 Sharpe Ratio:             7.13
```

Plus 5 beautiful charts! 📊

---

**Ready? Run:** `python quickstart.py` 🚀
