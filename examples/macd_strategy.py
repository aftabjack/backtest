"""
MACD (Moving Average Convergence Divergence) Strategy.
Generates buy signal when MACD line crosses above signal line.
Generates sell signal when MACD line crosses below signal line.
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, SignalType, IndicatorMixin


class MACDStrategy(BaseStrategy, IndicatorMixin):
    """
    MACD Crossover Strategy.

    Parameters:
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ):
        """Initialize MACD strategy."""
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period
        }
        super().__init__(name='MACD Strategy', params=params)

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate MACD indicators."""
        macd_line, signal_line, histogram = self.calculate_macd(
            self.data['close'],
            self.fast_period,
            self.slow_period,
            self.signal_period
        )

        self.data['macd'] = macd_line
        self.data['macd_signal'] = signal_line
        self.data['macd_histogram'] = histogram

        return self.data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MACD crossover."""
        df = data.copy()

        # Initialize signal column
        df['signal'] = SignalType.HOLD.value

        # Calculate crossovers
        df['macd_above_signal'] = df['macd'] > df['macd_signal']
        df['crossover'] = df['macd_above_signal'].diff()

        # Buy signal: MACD crosses above signal line
        df.loc[df['crossover'] == 1, 'signal'] = SignalType.BUY.value

        # Sell signal: MACD crosses below signal line
        df.loc[df['crossover'] == -1, 'signal'] = SignalType.SELL.value

        # Clean up temporary columns
        df.drop(['macd_above_signal', 'crossover'], axis=1, inplace=True)

        return df

    def get_parameters(self) -> dict:
        """Return strategy parameters."""
        return self.params

    def validate_parameters(self) -> bool:
        """Validate parameters."""
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")

        if self.fast_period <= 0 or self.slow_period <= 0 or self.signal_period <= 0:
            raise ValueError("All periods must be positive")

        return True
