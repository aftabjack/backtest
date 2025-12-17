"""
Base strategy class for implementing trading strategies.
All custom strategies should inherit from this base class.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
from enum import Enum


class SignalType(Enum):
    """Trading signal types."""
    BUY = 1
    SELL = -1
    HOLD = 0


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.

    Custom strategies must implement:
    - generate_signals(): Generate buy/sell signals
    - get_parameters(): Return strategy parameters
    """

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize strategy.

        Args:
            name: Strategy name
            params: Strategy parameters dictionary
        """
        self.name = name
        self.params = params or {}
        self.data = None
        self.signals = None

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on strategy logic.

        Args:
            data: OHLCV DataFrame with price data

        Returns:
            DataFrame with 'signal' column (1=BUY, -1=SELL, 0=HOLD)
        """
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters.

        Returns:
            Dictionary of parameter names and values
        """
        pass

    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare and validate input data.

        Args:
            data: Raw OHLCV data

        Returns:
            Prepared DataFrame
        """
        self.data = data.copy()

        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in self.data.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        return self.data

    def calculate_indicators(self) -> pd.DataFrame:
        """
        Calculate technical indicators.
        Override in child classes to add custom indicators.

        Returns:
            DataFrame with indicators
        """
        return self.data

    def backtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Run the strategy on historical data.

        Args:
            data: OHLCV DataFrame

        Returns:
            DataFrame with signals and indicators
        """
        self.prepare_data(data)
        self.calculate_indicators()
        self.signals = self.generate_signals(self.data)

        return self.signals

    def get_name(self) -> str:
        """Get strategy name."""
        return self.name

    def get_signal_counts(self) -> Dict[str, int]:
        """
        Get count of each signal type.

        Returns:
            Dictionary with signal counts
        """
        if self.signals is None or 'signal' not in self.signals.columns:
            return {'buy': 0, 'sell': 0, 'hold': 0}

        signals = self.signals['signal']
        return {
            'buy': (signals == SignalType.BUY.value).sum(),
            'sell': (signals == SignalType.SELL.value).sum(),
            'hold': (signals == SignalType.HOLD.value).sum()
        }

    def validate_parameters(self) -> bool:
        """
        Validate strategy parameters.
        Override in child classes for custom validation.

        Returns:
            True if parameters are valid
        """
        return True

    def __str__(self) -> str:
        """String representation of strategy."""
        params_str = ', '.join([f"{k}={v}" for k, v in self.params.items()])
        return f"{self.name}({params_str})"

    def __repr__(self) -> str:
        """Representation of strategy."""
        return self.__str__()


class IndicatorMixin:
    """Mixin class providing common technical indicators."""

    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            data: Price series
            period: RSI period (default: 14)

        Returns:
            RSI series
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> tuple:
        """
        Calculate Bollinger Bands.

        Args:
            data: Price series
            period: Moving average period
            std_dev: Number of standard deviations

        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band, middle_band, lower_band

    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: Price series
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period

        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        fast_ema = data.ewm(span=fast_period, adjust=False).mean()
        slow_ema = data.ewm(span=slow_period, adjust=False).mean()

        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period

        Returns:
            ATR series
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr
