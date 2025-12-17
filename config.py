"""
Configuration file for backtesting engine.
"""

from pathlib import Path

# Directories
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'csv_data'
OUTPUT_DIR = PROJECT_ROOT / 'output'

# Backtest Settings
DEFAULT_INITIAL_CAPITAL = 10000.0
DEFAULT_COMMISSION_RATE = 0.001  # 0.1%
DEFAULT_POSITION_SIZE = 1.0  # 100% of capital
DEFAULT_SLIPPAGE = 0.0005  # 0.05%

# Data Settings
DEFAULT_EXCHANGE = 'Combined_Index'
DEFAULT_SYMBOL = 'ETHUSD'

# Available exchanges
EXCHANGES = [
    'Binance',
    'BitMEX',
    'Bitfinex',
    'Bitstamp',
    'Coinbase',
    'Combined_Index',
    'KuCoin',
    'OKX'
]

# Risk-Free Rate (annual)
RISK_FREE_RATE = 0.0  # 0% for crypto

# Charting
CHART_STYLE = 'darkgrid'
CHART_DPI = 300
