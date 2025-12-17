"""
Bollinger Bands Strategy.
Generates buy signal when price touches lower band.
Generates sell signal when price touches upper band.
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, SignalType, IndicatorMixin


class BollingerBandsStrategy(BaseStrategy, IndicatorMixin):
    """
    Bollinger Bands Mean Reversion Strategy.

    Parameters:
        period: Bollinger Bands period (default: 20)
        std_dev: Number of standard deviations (default: 2.0)
    """

    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0
    ):
        """Initialize Bollinger Bands strategy."""
        params = {
            'period': period,
            'std_dev': std_dev
        }
        super().__init__(name='Bollinger Bands', params=params)

        self.period = period
        self.std_dev = std_dev

    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        upper, middle, lower = self.calculate_bollinger_bands(
            self.data['close'],
            self.period,
            self.std_dev
        )

        self.data['bb_upper'] = upper
        self.data['bb_middle'] = middle
        self.data['bb_lower'] = lower

        # Calculate bandwidth
        self.data['bb_width'] = (upper - lower) / middle * 100

        return self.data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on Bollinger Bands."""
        df = data.copy()

        # Initialize signal column
        df['signal'] = SignalType.HOLD.value

        # Track position state
        in_position = False

        for i in range(1, len(df)):
            close = df['close'].iloc[i]
            lower = df['bb_lower'].iloc[i]
            upper = df['bb_upper'].iloc[i]
            middle = df['bb_middle'].iloc[i]

            # Buy signal: price touches or crosses below lower band
            if not in_position and close <= lower:
                df.iloc[i, df.columns.get_loc('signal')] = SignalType.BUY.value
                in_position = True

            # Sell signal: price touches or crosses above upper band
            elif in_position and close >= upper:
                df.iloc[i, df.columns.get_loc('signal')] = SignalType.SELL.value
                in_position = False

            # Alternative exit: price crosses middle band
            # Uncomment if you want to exit at middle band
            # elif in_position and close >= middle:
            #     df.iloc[i, df.columns.get_loc('signal')] = SignalType.SELL.value
            #     in_position = False

        return df

    def get_parameters(self) -> dict:
        """Return strategy parameters."""
        return self.params

    def validate_parameters(self) -> bool:
        """Validate parameters."""
        if self.period <= 0:
            raise ValueError("Period must be positive")

        if self.std_dev <= 0:
            raise ValueError("Standard deviation must be positive")

        return True
