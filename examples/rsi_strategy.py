"""
RSI (Relative Strength Index) Strategy.
Generates buy signal when RSI crosses below oversold threshold.
Generates sell signal when RSI crosses above overbought threshold.
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, SignalType, IndicatorMixin


class RSIStrategy(BaseStrategy, IndicatorMixin):
    """
    RSI Mean Reversion Strategy.

    Parameters:
        rsi_period: RSI calculation period (default: 14)
        oversold_threshold: Oversold level for buy signals (default: 30)
        overbought_threshold: Overbought level for sell signals (default: 70)
    """

    def __init__(
        self,
        rsi_period: int = 14,
        oversold_threshold: float = 30,
        overbought_threshold: float = 70
    ):
        """Initialize RSI strategy."""
        params = {
            'rsi_period': rsi_period,
            'oversold_threshold': oversold_threshold,
            'overbought_threshold': overbought_threshold
        }
        super().__init__(name='RSI Strategy', params=params)

        self.rsi_period = rsi_period
        self.oversold = oversold_threshold
        self.overbought = overbought_threshold

    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate RSI indicator."""
        self.data['rsi'] = self.calculate_rsi(self.data['close'], self.rsi_period)
        return self.data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on RSI levels."""
        df = data.copy()

        # Initialize signal column
        df['signal'] = SignalType.HOLD.value

        # Track position state
        in_position = False

        for i in range(1, len(df)):
            rsi_current = df['rsi'].iloc[i]
            rsi_previous = df['rsi'].iloc[i-1]

            # Buy signal: RSI crosses below oversold threshold
            if not in_position and rsi_previous >= self.oversold and rsi_current < self.oversold:
                df.iloc[i, df.columns.get_loc('signal')] = SignalType.BUY.value
                in_position = True

            # Sell signal: RSI crosses above overbought threshold
            elif in_position and rsi_previous <= self.overbought and rsi_current > self.overbought:
                df.iloc[i, df.columns.get_loc('signal')] = SignalType.SELL.value
                in_position = False

        return df

    def get_parameters(self) -> dict:
        """Return strategy parameters."""
        return self.params

    def validate_parameters(self) -> bool:
        """Validate parameters."""
        if self.rsi_period <= 0:
            raise ValueError("RSI period must be positive")

        if not (0 <= self.oversold < self.overbought <= 100):
            raise ValueError("Invalid oversold/overbought thresholds")

        return True
