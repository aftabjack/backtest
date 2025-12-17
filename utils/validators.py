"""
Input Validation System Using Pydantic
=======================================

Robust input validation for production backtesting engine.

Features:
- Type validation with Pydantic
- Range validation
- Data integrity checks
- Clear error messages
- Custom validators

Usage:
    from utils.validators import BacktestConfig, validate_dataframe

    # Validate configuration
    config = BacktestConfig(
        initial_capital=10000,
        commission_rate=0.001,
        position_size=1.0
    )

    # Validate data
    validate_dataframe(df, check_ohlc=True)
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ExchangeEnum(str, Enum):
    """Supported exchanges."""
    COMBINED_INDEX = "Combined_Index"
    BINANCE = "Binance"
    COINBASE = "Coinbase"
    OKX = "OKX"
    BITMEX = "BitMEX"
    BITFINEX = "Bitfinex"
    BITSTAMP = "Bitstamp"
    KUCOIN = "KuCoin"


class TimeframeEnum(str, Enum):
    """Supported timeframes."""
    ONE_MIN = "1T"
    FIVE_MIN = "5T"
    FIFTEEN_MIN = "15T"
    THIRTY_MIN = "30T"
    ONE_HOUR = "1H"
    FOUR_HOUR = "4H"
    ONE_DAY = "1D"


class MATypeEnum(str, Enum):
    """Moving average types."""
    SMA = "SMA"
    EMA = "EMA"


# ============================================================================
# Backtester Configuration Validation
# ============================================================================

class BacktestConfig(BaseModel):
    """
    Validated configuration for Backtester.

    All parameters are validated for type, range, and logical consistency.
    """
    initial_capital: float = Field(
        ...,
        gt=0,
        description="Starting capital (must be > 0)"
    )

    commission_rate: float = Field(
        default=0.001,
        ge=0,
        le=0.1,
        description="Commission rate (0-10%)"
    )

    position_size: float = Field(
        default=1.0,
        gt=0,
        le=1.0,
        description="Position size as fraction of capital (0-1)"
    )

    allow_short: bool = Field(
        default=False,
        description="Allow short selling"
    )

    slippage: float = Field(
        default=0.0,
        ge=0,
        le=0.01,
        description="Slippage (0-1%)"
    )

    max_position_size: Optional[float] = Field(
        default=None,
        gt=0,
        description="Maximum position size (optional)"
    )

    @field_validator('commission_rate')
    @classmethod
    def validate_commission(cls, v):
        """Validate commission rate is reasonable."""
        if v > 0.05:  # 5%
            raise ValueError(
                f"Commission rate {v*100:.2f}% is unusually high. "
                "Typical rates are 0.1-0.5%. Use at your own risk."
            )
        return v

    @field_validator('slippage')
    @classmethod
    def validate_slippage(cls, v):
        """Validate slippage is reasonable."""
        if v > 0.005:  # 0.5%
            raise ValueError(
                f"Slippage {v*100:.2f}% is unusually high. "
                "Typical slippage is 0.05-0.1%."
            )
        return v

    @model_validator(mode='after')
    def validate_position_constraints(self):
        """Validate position sizing constraints."""
        if self.max_position_size is not None and self.max_position_size < self.position_size:
            raise ValueError(
                f"max_position_size ({self.max_position_size}) cannot be less than "
                f"position_size ({self.position_size})"
            )
        return self

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


# ============================================================================
# Strategy Configuration Validation
# ============================================================================

class MAStrategyConfig(BaseModel):
    """Validation for Moving Average strategy parameters."""
    fast_period: int = Field(
        ...,
        gt=1,
        lt=200,
        description="Fast MA period (2-199)"
    )

    slow_period: int = Field(
        ...,
        gt=1,
        lt=500,
        description="Slow MA period (2-499)"
    )

    ma_type: MATypeEnum = Field(
        default=MATypeEnum.SMA,
        description="Moving average type (SMA or EMA)"
    )

    @model_validator(mode='after')
    def validate_periods(self):
        """Validate fast period is less than slow period."""
        if self.fast_period >= self.slow_period:
            raise ValueError(
                f"fast_period ({self.fast_period}) must be less than slow_period ({self.slow_period})"
            )

        if self.slow_period / self.fast_period < 2:
            raise ValueError(
                f"slow_period ({self.slow_period}) should be at least 2x fast_period ({self.fast_period}) "
                "for meaningful crossovers"
            )

        return self


class RSIStrategyConfig(BaseModel):
    """Validation for RSI strategy parameters."""
    rsi_period: int = Field(
        ...,
        gt=2,
        lt=100,
        description="RSI period (3-99)"
    )

    oversold_threshold: float = Field(
        ...,
        gt=0,
        lt=50,
        description="Oversold threshold (0-50)"
    )

    overbought_threshold: float = Field(
        ...,
        gt=50,
        lt=100,
        description="Overbought threshold (50-100)"
    )

    @model_validator(mode='after')
    def validate_thresholds(self):
        """Validate RSI thresholds."""
        if self.overbought_threshold - self.oversold_threshold < 20:
            raise ValueError(
                f"Gap between thresholds ({self.overbought_threshold - self.oversold_threshold:.1f}) should be "
                "at least 20 points for meaningful signals"
            )

        return self


class BollingerBandsConfig(BaseModel):
    """Validation for Bollinger Bands strategy parameters."""
    period: int = Field(
        ...,
        gt=2,
        lt=200,
        description="BB period (3-199)"
    )

    std_dev: float = Field(
        ...,
        gt=0.5,
        lt=5.0,
        description="Standard deviation multiplier (0.5-5.0)"
    )

    @field_validator('std_dev')
    @classmethod
    def validate_std_dev(cls, v):
        """Validate standard deviation is reasonable."""
        if v < 1.5 or v > 3.0:
            raise ValueError(
                f"std_dev {v} is unusual. Typical values are 2.0-2.5."
            )
        return v


class MACDStrategyConfig(BaseModel):
    """Validation for MACD strategy parameters."""
    fast_period: int = Field(
        ...,
        gt=2,
        lt=50,
        description="MACD fast period (3-49)"
    )

    slow_period: int = Field(
        ...,
        gt=10,
        lt=100,
        description="MACD slow period (11-99)"
    )

    signal_period: int = Field(
        ...,
        gt=2,
        lt=50,
        description="MACD signal period (3-49)"
    )

    @model_validator(mode='after')
    def validate_macd_periods(self):
        """Validate MACD periods."""
        if self.fast_period >= self.slow_period:
            raise ValueError(
                f"fast_period ({self.fast_period}) must be less than slow_period ({self.slow_period})"
            )

        if self.signal_period >= self.fast_period:
            raise ValueError(
                f"signal_period ({self.signal_period}) should be less than fast_period ({self.fast_period})"
            )

        return self


# ============================================================================
# Data Loading Validation
# ============================================================================

class DataLoadConfig(BaseModel):
    """Validation for data loading parameters."""
    exchange: ExchangeEnum = Field(
        default=ExchangeEnum.COMBINED_INDEX,
        description="Exchange name"
    )

    start_date: Optional[str] = Field(
        default=None,
        description="Start date (YYYY-MM-DD)"
    )

    end_date: Optional[str] = Field(
        default=None,
        description="End date (YYYY-MM-DD)"
    )

    timeframe: Optional[TimeframeEnum] = Field(
        default=None,
        description="Timeframe for resampling"
    )

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format."""
        if v is None:
            return v

        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError(
                f"Invalid date format: {v}. Use YYYY-MM-DD (e.g., 2023-01-01)"
            )

        return v

    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate date range."""
        if self.start_date and self.end_date:
            start_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(self.end_date, '%Y-%m-%d')

            if start_dt >= end_dt:
                raise ValueError(
                    f"start_date ({self.start_date}) must be before end_date ({self.end_date})"
                )

            # Check for reasonable date range
            days = (end_dt - start_dt).days
            if days > 3650:  # 10 years
                raise ValueError(
                    f"Date range ({days} days) exceeds 10 years. "
                    "Consider using a shorter range for better performance."
                )

        return self


# ============================================================================
# DataFrame Validation
# ============================================================================

class DataFrameValidationError(Exception):
    """Custom exception for DataFrame validation errors."""
    pass


def validate_dataframe(
    df: pd.DataFrame,
    check_ohlc: bool = True,
    check_volume: bool = False,
    check_sorted: bool = True,
    check_duplicates: bool = True,
    check_missing: bool = True,
    min_rows: int = 100
) -> bool:
    """
    Validate DataFrame for backtesting.

    Args:
        df: DataFrame to validate
        check_ohlc: Check for OHLC columns
        check_volume: Check for volume column
        check_sorted: Check if index is sorted
        check_duplicates: Check for duplicate timestamps
        check_missing: Check for missing values
        min_rows: Minimum required rows

    Returns:
        True if valid

    Raises:
        DataFrameValidationError: If validation fails
    """
    # Check if DataFrame is empty
    if df is None or len(df) == 0:
        raise DataFrameValidationError("DataFrame is empty")

    # Check minimum rows
    if len(df) < min_rows:
        raise DataFrameValidationError(
            f"DataFrame has only {len(df)} rows, minimum is {min_rows}"
        )

    # Check for required columns
    required_columns = []
    if check_ohlc:
        required_columns.extend(['open', 'high', 'low', 'close'])
    if check_volume:
        required_columns.append('volume')

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise DataFrameValidationError(
            f"Missing required columns: {missing_columns}"
        )

    # Check if index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        raise DataFrameValidationError(
            "Index must be DatetimeIndex (use df.set_index('timestamp'))"
        )

    # Check if sorted
    if check_sorted and not df.index.is_monotonic_increasing:
        raise DataFrameValidationError(
            "Index must be sorted in ascending order"
        )

    # Check for duplicates
    if check_duplicates and df.index.duplicated().any():
        n_duplicates = df.index.duplicated().sum()
        raise DataFrameValidationError(
            f"Found {n_duplicates} duplicate timestamps"
        )

    # Check for missing values
    if check_missing:
        missing = df[required_columns].isnull().sum()
        if missing.any():
            raise DataFrameValidationError(
                f"Found missing values:\n{missing[missing > 0]}"
            )

    # Check OHLC relationships
    if check_ohlc:
        # High should be >= Low
        if (df['high'] < df['low']).any():
            n_invalid = (df['high'] < df['low']).sum()
            raise DataFrameValidationError(
                f"Found {n_invalid} rows where High < Low"
            )

        # High should be >= Open and Close
        if (df['high'] < df[['open', 'close']].max(axis=1)).any():
            raise DataFrameValidationError(
                "High price should be >= Open and Close"
            )

        # Low should be <= Open and Close
        if (df['low'] > df[['open', 'close']].min(axis=1)).any():
            raise DataFrameValidationError(
                "Low price should be <= Open and Close"
            )

        # Check for non-positive prices
        price_columns = ['open', 'high', 'low', 'close']
        if (df[price_columns] <= 0).any().any():
            raise DataFrameValidationError(
                "Found non-positive prices"
            )

    # Check for infinite values
    if np.isinf(df.select_dtypes(include=[np.number])).any().any():
        raise DataFrameValidationError(
            "Found infinite values in DataFrame"
        )

    return True


def validate_signals(signals: pd.DataFrame, data: pd.DataFrame) -> bool:
    """
    Validate trading signals DataFrame.

    Args:
        signals: Signals DataFrame
        data: Original data DataFrame

    Returns:
        True if valid

    Raises:
        DataFrameValidationError: If validation fails
    """
    # Check if signals exist
    if 'signal' not in signals.columns:
        raise DataFrameValidationError(
            "Signals DataFrame must have 'signal' column"
        )

    # Check signal values
    valid_signals = {-1, 0, 1}
    invalid_signals = set(signals['signal'].unique()) - valid_signals
    if invalid_signals:
        raise DataFrameValidationError(
            f"Invalid signal values: {invalid_signals}. Must be -1, 0, or 1"
        )

    # Check index alignment
    if not signals.index.equals(data.index):
        raise DataFrameValidationError(
            "Signals index must match data index"
        )

    return True


# ============================================================================
# Main - Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Validators Demo")
    print("=" * 60)

    # Test BacktestConfig
    print("\n1. Valid configuration:")
    try:
        config = BacktestConfig(
            initial_capital=10000,
            commission_rate=0.001,
            position_size=1.0
        )
        print(f"   ✅ Valid: {config.dict()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test invalid configuration
    print("\n2. Invalid configuration (commission too high):")
    try:
        config = BacktestConfig(
            initial_capital=10000,
            commission_rate=0.1,  # 10% - too high
            position_size=1.0
        )
        print(f"   ✅ Valid: {config.dict()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test MA strategy config
    print("\n3. Valid MA strategy:")
    try:
        strategy_config = MAStrategyConfig(
            fast_period=10,
            slow_period=30,
            ma_type="SMA"
        )
        print(f"   ✅ Valid: {strategy_config.dict()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test invalid MA strategy
    print("\n4. Invalid MA strategy (fast >= slow):")
    try:
        strategy_config = MAStrategyConfig(
            fast_period=30,
            slow_period=10,  # Invalid: should be > fast
            ma_type="SMA"
        )
        print(f"   ✅ Valid: {strategy_config.dict()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test DataFrame validation
    print("\n5. Valid DataFrame:")
    df = pd.DataFrame({
        'open': [100, 101, 102],
        'high': [105, 106, 107],
        'low': [99, 100, 101],
        'close': [104, 105, 106],
    }, index=pd.date_range('2023-01-01', periods=3, freq='1D'))

    try:
        validate_dataframe(df, min_rows=3)
        print("   ✅ DataFrame is valid")
    except DataFrameValidationError as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("✅ Validation demo complete!")
    print("=" * 60)
