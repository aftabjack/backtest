"""
Data loader for historical market data.
Supports loading ETH/USD data from multiple exchanges.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Union, List
from datetime import datetime


class DataLoader:
    """Load and prepare market data for backtesting."""

    SUPPORTED_EXCHANGES = [
        'Binance', 'BitMEX', 'Bitfinex', 'Bitstamp',
        'Coinbase', 'Combined_Index', 'KuCoin', 'OKX'
    ]

    def __init__(self, data_dir: str = 'csv_data', file_format: str = 'csv'):
        """
        Initialize DataLoader.

        Args:
            data_dir: Directory containing data files
            file_format: File format ('csv' or 'parquet')
        """
        self.data_dir = Path(data_dir)
        self.file_format = file_format.lower()

        if self.file_format not in ['csv', 'parquet']:
            raise ValueError(f"Unsupported file format: {file_format}. Use 'csv' or 'parquet'")

        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

    def load_data(
        self,
        exchange: str = 'Combined_Index',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        symbol: str = 'ETHUSD'
    ) -> pd.DataFrame:
        """
        Load market data from CSV file.

        Args:
            exchange: Exchange name (default: Combined_Index)
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            symbol: Trading pair symbol

        Returns:
            DataFrame with OHLCV data
        """
        if exchange not in self.SUPPORTED_EXCHANGES:
            raise ValueError(
                f"Exchange {exchange} not supported. "
                f"Choose from: {', '.join(self.SUPPORTED_EXCHANGES)}"
            )

        # Construct filename based on format
        file_extension = '.parquet' if self.file_format == 'parquet' else '.csv'
        filename = f"{symbol}_1m_{exchange}{file_extension}"
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")

        # Load data based on format
        if self.file_format == 'parquet':
            df = pd.read_parquet(filepath)
        else:
            df = pd.read_csv(filepath)
            # Standardize column names for CSV
            df = self._standardize_columns(df)
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Set index if not already set
        if 'timestamp' in df.columns:
            df.set_index('timestamp', inplace=True)
        elif not isinstance(df.index, pd.DatetimeIndex):
            # Ensure index is datetime
            df.index = pd.to_datetime(df.index)

        # Filter by date range
        if start_date:
            df = df[df.index >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df.index <= pd.to_datetime(end_date)]

        # Validate data
        df = self._validate_data(df)

        return df

    def load_multiple_exchanges(
        self,
        exchanges: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        symbol: str = 'ETHUSD'
    ) -> dict:
        """
        Load data from multiple exchanges.

        Args:
            exchanges: List of exchange names
            start_date: Start date
            end_date: End date
            symbol: Trading pair symbol

        Returns:
            Dictionary mapping exchange names to DataFrames
        """
        data = {}
        for exchange in exchanges:
            try:
                data[exchange] = self.load_data(
                    exchange=exchange,
                    start_date=start_date,
                    end_date=end_date,
                    symbol=symbol
                )
                print(f"✓ Loaded {exchange}: {len(data[exchange])} rows")
            except Exception as e:
                print(f"✗ Failed to load {exchange}: {e}")

        return data

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names."""
        column_mapping = {
            'Open time': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }

        df.rename(columns=column_mapping, inplace=True)

        # Ensure required columns exist
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        return df[required_cols]

    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean data."""
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]

        # Remove rows with NaN values
        initial_len = len(df)
        df = df.dropna()
        dropped = initial_len - len(df)

        if dropped > 0:
            print(f"Warning: Dropped {dropped} rows with NaN values")

        # Ensure positive prices and volume
        df = df[
            (df['open'] > 0) &
            (df['high'] > 0) &
            (df['low'] > 0) &
            (df['close'] > 0) &
            (df['volume'] >= 0)
        ]

        # Validate OHLC relationships
        invalid_ohlc = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )

        if invalid_ohlc.any():
            print(f"Warning: Found {invalid_ohlc.sum()} rows with invalid OHLC relationships")
            df = df[~invalid_ohlc]

        # Sort by timestamp
        df = df.sort_index()

        return df

    def get_data_info(self, exchange: str = 'Combined_Index', symbol: str = 'ETHUSD') -> dict:
        """
        Get information about the dataset.

        Args:
            exchange: Exchange name
            symbol: Trading pair symbol

        Returns:
            Dictionary with dataset information
        """
        df = self.load_data(exchange=exchange, symbol=symbol)

        info = {
            'exchange': exchange,
            'symbol': symbol,
            'rows': len(df),
            'start_date': df.index.min().strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': df.index.max().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_days': (df.index.max() - df.index.min()).days,
            'price_range': {
                'min': df['low'].min(),
                'max': df['high'].max(),
                'mean': df['close'].mean()
            },
            'volume_stats': {
                'total': df['volume'].sum(),
                'mean': df['volume'].mean(),
                'max': df['volume'].max()
            }
        }

        return info


def resample_data(
    df: pd.DataFrame,
    timeframe: str = '5T'
) -> pd.DataFrame:
    """
    Resample 1-minute data to different timeframes.

    Args:
        df: DataFrame with 1-minute OHLCV data
        timeframe: Timeframe (e.g., '5T' for 5 minutes, '1H' for 1 hour, '1D' for 1 day)

    Returns:
        Resampled DataFrame
    """
    resampled = df.resample(timeframe).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    return resampled
