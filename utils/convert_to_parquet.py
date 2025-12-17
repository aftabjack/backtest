"""
CSV to Parquet Conversion Script
=================================

This script converts all CSV files in csv_data/ to optimized Parquet format.

Benefits:
- 10x faster loading speed
- 50-70% smaller file size
- Column-oriented storage (better for analytics)
- Built-in compression

Usage:
    python utils/convert_to_parquet.py
"""

import os
import pandas as pd
import time
from pathlib import Path


def convert_csv_to_parquet(csv_path: str, parquet_path: str):
    """
    Convert a single CSV file to Parquet format.

    Args:
        csv_path: Path to input CSV file
        parquet_path: Path to output Parquet file
    """
    print(f"\nConverting: {os.path.basename(csv_path)}")
    start_time = time.time()

    # Read CSV
    df = pd.read_csv(csv_path)

    # Standardize column names - handle multiple formats
    column_mapping = {
        'Timestamp': 'timestamp',
        'Open time': 'timestamp',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }

    # Apply column renaming
    df.rename(columns=column_mapping, inplace=True)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Get file sizes
    csv_size = os.path.getsize(csv_path) / (1024 * 1024)  # MB

    # Write Parquet with optimal settings
    df.to_parquet(
        parquet_path,
        engine='pyarrow',
        compression='snappy',  # Fast compression
        index=False
    )

    parquet_size = os.path.getsize(parquet_path) / (1024 * 1024)  # MB
    elapsed = time.time() - start_time

    print(f"  CSV size:     {csv_size:.2f} MB")
    print(f"  Parquet size: {parquet_size:.2f} MB")
    print(f"  Compression:  {(1 - parquet_size/csv_size) * 100:.1f}% smaller")
    print(f"  Time:         {elapsed:.2f} seconds")
    print(f"  Rows:         {len(df):,}")


def convert_all_csv_files(csv_dir: str = 'csv_data', parquet_dir: str = 'parquet_data'):
    """
    Convert all CSV files in a directory to Parquet format.

    Args:
        csv_dir: Directory containing CSV files
        parquet_dir: Output directory for Parquet files
    """
    print("=" * 60)
    print("CSV to Parquet Conversion")
    print("=" * 60)

    # Create output directory
    os.makedirs(parquet_dir, exist_ok=True)

    # Find all CSV files
    csv_files = list(Path(csv_dir).glob('*.csv'))

    if not csv_files:
        print(f"\n❌ No CSV files found in {csv_dir}/")
        return

    print(f"\nFound {len(csv_files)} CSV files")

    total_csv_size = 0
    total_parquet_size = 0
    total_start = time.time()

    # Convert each file
    for csv_file in csv_files:
        csv_path = str(csv_file)
        parquet_path = os.path.join(
            parquet_dir,
            csv_file.stem + '.parquet'
        )

        try:
            convert_csv_to_parquet(csv_path, parquet_path)
            total_csv_size += os.path.getsize(csv_path)
            total_parquet_size += os.path.getsize(parquet_path)
        except Exception as e:
            print(f"  ❌ Error: {e}")

    total_elapsed = time.time() - total_start

    # Print summary
    print("\n" + "=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"Files converted:    {len(csv_files)}")
    print(f"Total CSV size:     {total_csv_size / (1024**2):.2f} MB")
    print(f"Total Parquet size: {total_parquet_size / (1024**2):.2f} MB")
    print(f"Space saved:        {(total_csv_size - total_parquet_size) / (1024**2):.2f} MB")
    print(f"Compression ratio:  {(1 - total_parquet_size/total_csv_size) * 100:.1f}%")
    print(f"Total time:         {total_elapsed:.2f} seconds")
    print("\n✅ Conversion complete!")
    print(f"Parquet files saved to: {parquet_dir}/")


def benchmark_loading_speed(csv_path: str, parquet_path: str):
    """
    Benchmark loading speed comparison between CSV and Parquet.

    Args:
        csv_path: Path to CSV file
        parquet_path: Path to Parquet file
    """
    print("\n" + "=" * 60)
    print("Loading Speed Benchmark")
    print("=" * 60)
    print(f"File: {os.path.basename(csv_path)}")

    # Benchmark CSV loading
    print("\nLoading CSV...")
    start = time.time()
    df_csv = pd.read_csv(csv_path)
    csv_time = time.time() - start
    print(f"  Time: {csv_time:.4f} seconds")

    # Benchmark Parquet loading
    print("\nLoading Parquet...")
    start = time.time()
    df_parquet = pd.read_parquet(parquet_path)
    parquet_time = time.time() - start
    print(f"  Time: {parquet_time:.4f} seconds")

    # Results
    speedup = csv_time / parquet_time
    print("\n" + "=" * 60)
    print(f"Speedup: {speedup:.1f}x faster")
    print("=" * 60)

    return speedup


if __name__ == "__main__":
    # Convert all CSV files
    convert_all_csv_files()

    # Benchmark loading speed on one file
    csv_file = 'csv_data/Combined_Index.csv'
    parquet_file = 'parquet_data/Combined_Index.parquet'

    if os.path.exists(csv_file) and os.path.exists(parquet_file):
        benchmark_loading_speed(csv_file, parquet_file)
    else:
        print("\n💡 Tip: Run this script to convert CSV files first!")
