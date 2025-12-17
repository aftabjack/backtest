"""
Moving Average Crossover Strategy.
Generates buy signal when fast MA crosses above slow MA.
Generates sell signal when fast MA crosses below slow MA.
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, SignalType, IndicatorMixin


class MovingAverageCrossover(BaseStrategy, IndicatorMixin):
    """
    Simple Moving Average Crossover Strategy.

    Parameters:
        fast_period: Fast MA period (default: 10)
        slow_period: Slow MA period (default: 30)
        ma_type: Type of moving average ('SMA' or 'EMA')
    """

    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 30,
        ma_type: str = 'SMA'
    ):
        """Initialize strategy with parameters."""
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'ma_type': ma_type
        }
        super().__init__(name='MA Crossover', params=params)

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.ma_type = ma_type.upper()

    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate moving averages."""
        close = self.data['close']

        if self.ma_type == 'SMA':
            self.data['fast_ma'] = self.calculate_sma(close, self.fast_period)
            self.data['slow_ma'] = self.calculate_sma(close, self.slow_period)
        else:  # EMA
            self.data['fast_ma'] = self.calculate_ema(close, self.fast_period)
            self.data['slow_ma'] = self.calculate_ema(close, self.slow_period)

        return self.data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MA crossover."""
        df = data.copy()

        # Initialize signal column
        df['signal'] = SignalType.HOLD.value

        # Calculate crossovers
        df['fast_above'] = df['fast_ma'] > df['slow_ma']
        df['crossover'] = df['fast_above'].diff()

        # Buy signal: fast MA crosses above slow MA
        df.loc[df['crossover'] == 1, 'signal'] = SignalType.BUY.value

        # Sell signal: fast MA crosses below slow MA
        df.loc[df['crossover'] == -1, 'signal'] = SignalType.SELL.value

        # Clean up temporary columns
        df.drop(['fast_above', 'crossover'], axis=1, inplace=True)

        return df

    def get_parameters(self) -> dict:
        """Return strategy parameters."""
        return self.params

    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")

        if self.fast_period <= 0 or self.slow_period <= 0:
            raise ValueError("Periods must be positive")

        if self.ma_type not in ['SMA', 'EMA']:
            raise ValueError("MA type must be 'SMA' or 'EMA'")

        return True
