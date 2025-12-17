"""
Fast Technical Indicators Using Numba JIT Compilation
======================================================

This module provides optimized versions of technical indicators using Numba JIT compilation.
Expected speedup: 10-50x compared to pandas rolling operations.

Usage:
    from utils.indicators_fast import calculate_sma_fast, calculate_ema_fast

    sma = calculate_sma_fast(prices, period=20)
    ema = calculate_ema_fast(prices, period=20)
"""

import numpy as np
from numba import jit, prange
import pandas as pd


# ============================================================================
# Simple Moving Average (SMA) - Optimized with Numba
# ============================================================================

@jit(nopython=True, cache=True)
def calculate_sma_fast(prices: np.ndarray, period: int) -> np.ndarray:
    """
    Calculate Simple Moving Average using Numba JIT compilation.

    Expected speedup: 10-20x compared to pandas rolling().mean()

    Args:
        prices: Array of prices
        period: Moving average period

    Returns:
        Array of SMA values (NaN for first period-1 values)
    """
    n = len(prices)
    result = np.empty(n)
    result[:period-1] = np.nan

    # Calculate first SMA
    result[period-1] = np.mean(prices[:period])

    # Use sliding window for efficiency
    for i in range(period, n):
        result[i] = result[i-1] + (prices[i] - prices[i-period]) / period

    return result


# ============================================================================
# Exponential Moving Average (EMA) - Optimized with Numba
# ============================================================================

@jit(nopython=True, cache=True)
def calculate_ema_fast(prices: np.ndarray, period: int) -> np.ndarray:
    """
    Calculate Exponential Moving Average using Numba JIT compilation.

    Expected speedup: 15-30x compared to pandas ewm().mean()

    Args:
        prices: Array of prices
        period: EMA period

    Returns:
        Array of EMA values
    """
    n = len(prices)
    result = np.empty(n)
    alpha = 2.0 / (period + 1.0)

    # Initialize with first valid price
    result[0] = prices[0]

    # Calculate EMA iteratively
    for i in range(1, n):
        result[i] = alpha * prices[i] + (1 - alpha) * result[i-1]

    return result


# ============================================================================
# RSI (Relative Strength Index) - Optimized with Numba
# ============================================================================

@jit(nopython=True, cache=True)
def calculate_rsi_fast(prices: np.ndarray, period: int = 14) -> np.ndarray:
    """
    Calculate RSI using Numba JIT compilation.

    Expected speedup: 20-40x compared to pandas implementation

    Args:
        prices: Array of prices
        period: RSI period (default 14)

    Returns:
        Array of RSI values (0-100)
    """
    n = len(prices)
    result = np.empty(n)
    result[:period] = np.nan

    # Calculate price changes
    deltas = np.diff(prices)

    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    # Calculate initial average gain and loss
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    # Calculate first RSI
    if avg_loss == 0:
        result[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        result[period] = 100.0 - (100.0 / (1.0 + rs))

    # Calculate subsequent RSI values using smoothed averages
    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period

        if avg_loss == 0:
            result[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i] = 100.0 - (100.0 / (1.0 + rs))

    return result


# ============================================================================
# MACD - Optimized with Numba
# ============================================================================

@jit(nopython=True, cache=True)
def calculate_macd_fast(prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    Calculate MACD using Numba JIT compilation.

    Expected speedup: 15-25x compared to pandas implementation

    Args:
        prices: Array of prices
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line period (default 9)

    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    # Calculate fast and slow EMAs
    ema_fast = calculate_ema_fast(prices, fast)
    ema_slow = calculate_ema_fast(prices, slow)

    # MACD line
    macd_line = ema_fast - ema_slow

    # Signal line (EMA of MACD)
    signal_line = calculate_ema_fast(macd_line, signal)

    # Histogram
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


# ============================================================================
# Bollinger Bands - Optimized with Numba
# ============================================================================

@jit(nopython=True, cache=True)
def calculate_bollinger_bands_fast(prices: np.ndarray, period: int = 20, std_dev: float = 2.0):
    """
    Calculate Bollinger Bands using Numba JIT compilation.

    Expected speedup: 10-20x compared to pandas implementation

    Args:
        prices: Array of prices
        period: Moving average period (default 20)
        std_dev: Number of standard deviations (default 2.0)

    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    n = len(prices)
    middle_band = calculate_sma_fast(prices, period)

    upper_band = np.empty(n)
    lower_band = np.empty(n)
    upper_band[:period-1] = np.nan
    lower_band[:period-1] = np.nan

    # Calculate rolling standard deviation
    for i in range(period-1, n):
        window = prices[i-period+1:i+1]
        std = np.std(window)
        upper_band[i] = middle_band[i] + (std_dev * std)
        lower_band[i] = middle_band[i] - (std_dev * std)

    return upper_band, middle_band, lower_band


# ============================================================================
# ATR (Average True Range) - Optimized with Numba
# ============================================================================

@jit(nopython=True, cache=True)
def calculate_atr_fast(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    """
    Calculate ATR using Numba JIT compilation.

    Expected speedup: 15-30x compared to pandas implementation

    Args:
        high: Array of high prices
        low: Array of low prices
        close: Array of close prices
        period: ATR period (default 14)

    Returns:
        Array of ATR values
    """
    n = len(close)
    tr = np.empty(n)
    atr = np.empty(n)

    # First TR is just high - low
    tr[0] = high[0] - low[0]
    atr[:period-1] = np.nan

    # Calculate True Range for each bar
    for i in range(1, n):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i-1])
        lc = abs(low[i] - close[i-1])
        tr[i] = max(hl, hc, lc)

    # Calculate initial ATR (simple average)
    atr[period-1] = np.mean(tr[:period])

    # Calculate subsequent ATR values (smoothed)
    for i in range(period, n):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period

    return atr


# ============================================================================
# Vectorized Signal Generation - Parallel Processing
# ============================================================================

@jit(nopython=True, parallel=True, cache=True)
def generate_crossover_signals_fast(fast_ma: np.ndarray, slow_ma: np.ndarray) -> np.ndarray:
    """
    Generate crossover signals using parallel processing.

    Expected speedup: 5-10x for large datasets

    Args:
        fast_ma: Fast moving average array
        slow_ma: Slow moving average array

    Returns:
        Array of signals: 1 (buy), -1 (sell), 0 (hold)
    """
    n = len(fast_ma)
    signals = np.zeros(n)

    for i in prange(1, n):
        if not (np.isnan(fast_ma[i]) or np.isnan(slow_ma[i]) or
                np.isnan(fast_ma[i-1]) or np.isnan(slow_ma[i-1])):
            # Bullish crossover
            if fast_ma[i] > slow_ma[i] and fast_ma[i-1] <= slow_ma[i-1]:
                signals[i] = 1.0
            # Bearish crossover
            elif fast_ma[i] < slow_ma[i] and fast_ma[i-1] >= slow_ma[i-1]:
                signals[i] = -1.0

    return signals


@jit(nopython=True, parallel=True, cache=True)
def generate_rsi_signals_fast(rsi: np.ndarray, oversold: float = 30.0, overbought: float = 70.0) -> np.ndarray:
    """
    Generate RSI signals using parallel processing.

    Args:
        rsi: RSI array
        oversold: Oversold threshold (default 30)
        overbought: Overbought threshold (default 70)

    Returns:
        Array of signals: 1 (buy), -1 (sell), 0 (hold)
    """
    n = len(rsi)
    signals = np.zeros(n)

    for i in prange(1, n):
        if not (np.isnan(rsi[i]) or np.isnan(rsi[i-1])):
            # Buy signal: RSI crosses above oversold
            if rsi[i] > oversold and rsi[i-1] <= oversold:
                signals[i] = 1.0
            # Sell signal: RSI crosses below overbought
            elif rsi[i] < overbought and rsi[i-1] >= overbought:
                signals[i] = -1.0

    return signals


# ============================================================================
# Helper Functions - Pandas Integration
# ============================================================================

def calculate_sma_pandas(series: pd.Series, period: int) -> pd.Series:
    """
    Pandas wrapper for Numba-optimized SMA.

    Usage:
        df['sma'] = calculate_sma_pandas(df['close'], 20)
    """
    values = series.values.astype(np.float64)
    result = calculate_sma_fast(values, period)
    return pd.Series(result, index=series.index)


def calculate_ema_pandas(series: pd.Series, period: int) -> pd.Series:
    """
    Pandas wrapper for Numba-optimized EMA.

    Usage:
        df['ema'] = calculate_ema_pandas(df['close'], 20)
    """
    values = series.values.astype(np.float64)
    result = calculate_ema_fast(values, period)
    return pd.Series(result, index=series.index)


def calculate_rsi_pandas(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Pandas wrapper for Numba-optimized RSI.

    Usage:
        df['rsi'] = calculate_rsi_pandas(df['close'], 14)
    """
    values = series.values.astype(np.float64)
    result = calculate_rsi_fast(values, period)
    return pd.Series(result, index=series.index)


def calculate_macd_pandas(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    Pandas wrapper for Numba-optimized MACD.

    Usage:
        macd, signal_line, histogram = calculate_macd_pandas(df['close'], 12, 26, 9)
    """
    values = series.values.astype(np.float64)
    macd_line, signal_line, histogram = calculate_macd_fast(values, fast, slow, signal)

    return (
        pd.Series(macd_line, index=series.index),
        pd.Series(signal_line, index=series.index),
        pd.Series(histogram, index=series.index)
    )


def calculate_bollinger_bands_pandas(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    """
    Pandas wrapper for Numba-optimized Bollinger Bands.

    Usage:
        upper, middle, lower = calculate_bollinger_bands_pandas(df['close'], 20, 2.0)
    """
    values = series.values.astype(np.float64)
    upper, middle, lower = calculate_bollinger_bands_fast(values, period, std_dev)

    return (
        pd.Series(upper, index=series.index),
        pd.Series(middle, index=series.index),
        pd.Series(lower, index=series.index)
    )


def calculate_atr_pandas(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Pandas wrapper for Numba-optimized ATR.

    Usage:
        df['atr'] = calculate_atr_pandas(df, 14)
    """
    high = df['high'].values.astype(np.float64)
    low = df['low'].values.astype(np.float64)
    close = df['close'].values.astype(np.float64)

    result = calculate_atr_fast(high, low, close, period)
    return pd.Series(result, index=df.index)


# ============================================================================
# Performance Benchmarking
# ============================================================================

if __name__ == "__main__":
    import time

    print("=" * 60)
    print("Numba JIT Performance Benchmark")
    print("=" * 60)

    # Generate test data
    np.random.seed(42)
    n = 100000
    prices = np.cumsum(np.random.randn(n)) + 100

    print(f"\nTest data: {n:,} price points")

    # Benchmark SMA
    print("\n1. Simple Moving Average (period=20)")
    start = time.time()
    sma = calculate_sma_fast(prices, 20)
    numba_time = time.time() - start
    print(f"   Numba JIT: {numba_time:.4f} seconds")

    # Pandas comparison
    start = time.time()
    sma_pandas = pd.Series(prices).rolling(20).mean().values
    pandas_time = time.time() - start
    print(f"   Pandas:    {pandas_time:.4f} seconds")
    print(f"   Speedup:   {pandas_time / numba_time:.1f}x faster")

    # Benchmark EMA
    print("\n2. Exponential Moving Average (period=20)")
    start = time.time()
    ema = calculate_ema_fast(prices, 20)
    numba_time = time.time() - start
    print(f"   Numba JIT: {numba_time:.4f} seconds")

    start = time.time()
    ema_pandas = pd.Series(prices).ewm(span=20).mean().values
    pandas_time = time.time() - start
    print(f"   Pandas:    {pandas_time:.4f} seconds")
    print(f"   Speedup:   {pandas_time / numba_time:.1f}x faster")

    # Benchmark RSI
    print("\n3. RSI (period=14)")
    start = time.time()
    rsi = calculate_rsi_fast(prices, 14)
    numba_time = time.time() - start
    print(f"   Numba JIT: {numba_time:.4f} seconds")
    print(f"   (No pandas comparison - custom implementation)")

    print("\n" + "=" * 60)
    print("✅ Benchmarking complete!")
    print("=" * 60)
