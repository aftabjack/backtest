"""
Simplified Backtest Engine Wrapper
===================================

Easy-to-use interface for the backtesting engine with all production features.

Usage:
    from backtest_engine import BacktestEngine, Strategy

    # Create strategy
    class MyStrategy(Strategy):
        def generate_signals(self, data):
            # Your strategy logic
            return signals

    # Run backtest
    engine = BacktestEngine()
    results = engine.backtest(
        strategy=MyStrategy(),
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-12-31',
        initial_capital=10000
    )

    # View results
    engine.print_results()
    engine.generate_report()
"""

from typing import Optional, Dict, Any
from data_handlers.loader import DataLoader
from engine.backtest import Backtester
from strategies.base_strategy import BaseStrategy
from analytics.reports import ReportGenerator
from utils.logger import get_logger, BacktestLogger, log_performance
from utils.validators import BacktestConfig, DataLoadConfig, validate_dataframe
import pandas as pd


class BacktestEngine:
    """
    Simplified wrapper for backtesting engine with production features.

    Includes:
    - Automatic Parquet loading (12x faster)
    - Production logging
    - Input validation
    - Report generation
    """

    def __init__(
        self,
        use_parquet: bool = True,
        log_level: str = 'INFO',
        data_dir: Optional[str] = None
    ):
        """
        Initialize BacktestEngine.

        Args:
            use_parquet: Use Parquet format for 12x faster loading (default: True)
            log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
            data_dir: Custom data directory (auto-detects if None)
        """
        self.use_parquet = use_parquet
        self.logger = get_logger('backtest_engine')
        self.bt_logger = BacktestLogger()

        # Auto-detect data directory
        if data_dir is None:
            if use_parquet:
                import os
                data_dir = 'parquet_data' if os.path.exists('parquet_data') else 'csv_data'
                self.use_parquet = (data_dir == 'parquet_data')
            else:
                data_dir = 'csv_data'

        # Initialize data loader
        file_format = 'parquet' if self.use_parquet else 'csv'
        self.loader = DataLoader(data_dir=data_dir, file_format=file_format)

        self.logger.info(f"BacktestEngine initialized (format: {file_format})")

        # Store results
        self.results = None
        self.backtester = None
        self.data = None

    def backtest(
        self,
        strategy: BaseStrategy,
        exchange: str = 'Combined_Index',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,
        position_size: float = 1.0,
        slippage: float = 0.0,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Run backtest with automatic validation and logging.

        Args:
            strategy: Trading strategy (must inherit from BaseStrategy)
            exchange: Exchange name (default: Combined_Index)
            start_date: Start date YYYY-MM-DD (default: all data)
            end_date: End date YYYY-MM-DD (default: all data)
            initial_capital: Starting capital (default: 10000)
            commission_rate: Commission rate as decimal (default: 0.001 = 0.1%)
            position_size: Position size as fraction (default: 1.0 = 100%)
            slippage: Slippage as decimal (default: 0.0)
            validate: Validate inputs (default: True)

        Returns:
            Dictionary with backtest results
        """
        # Step 1: Validate configuration
        if validate:
            self.logger.info("Validating configuration...")
            try:
                config = BacktestConfig(
                    initial_capital=initial_capital,
                    commission_rate=commission_rate,
                    position_size=position_size,
                    slippage=slippage
                )
                data_config = DataLoadConfig(
                    exchange=exchange,
                    start_date=start_date,
                    end_date=end_date
                )
                self.logger.info("✅ Configuration validated")
            except Exception as e:
                self.logger.error(f"❌ Configuration validation failed: {e}")
                raise

        # Step 2: Load data
        self.logger.info(f"Loading data from {exchange}...")
        with log_performance("Data loading", self.logger):
            self.data = self.loader.load_data(
                exchange=exchange,
                start_date=start_date,
                end_date=end_date
            )

        self.logger.info(f"Loaded {len(self.data):,} rows")

        # Validate data
        if validate:
            try:
                validate_dataframe(self.data, check_ohlc=True, min_rows=100)
                self.logger.info("✅ Data validated")
            except Exception as e:
                self.logger.error(f"❌ Data validation failed: {e}")
                raise

        # Step 3: Log backtest start
        self.bt_logger.log_backtest_start(
            strategy_name=strategy.get_name(),
            initial_capital=initial_capital,
            date_range=(
                str(self.data.index[0].date()),
                str(self.data.index[-1].date())
            )
        )

        # Step 4: Run backtest
        self.logger.info("Running backtest...")
        self.backtester = Backtester(
            strategy=strategy,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            position_size=position_size,
            slippage=slippage
        )

        with log_performance("Backtest execution", self.logger):
            self.results = self.backtester.run(self.data)

        # Step 5: Log completion
        self.bt_logger.log_backtest_end(self.results)

        return self.results

    def print_results(self):
        """Print backtest results to console."""
        if self.backtester is None:
            raise ValueError("No backtest results available. Run backtest() first.")

        self.backtester.print_results()

    def generate_report(self, save_charts: bool = True) -> str:
        """
        Generate comprehensive report with charts.

        Args:
            save_charts: Save charts to files (default: True)

        Returns:
            Path to report directory
        """
        if self.results is None:
            raise ValueError("No backtest results available. Run backtest() first.")

        self.logger.info("Generating report...")
        report_gen = ReportGenerator()

        with log_performance("Report generation", self.logger):
            report_path = report_gen.generate_full_report(
                self.results,
                save_charts=save_charts
            )

        self.logger.info(f"Report saved to: {report_path}")
        return report_path

    def get_results(self) -> Dict[str, Any]:
        """Get backtest results dictionary."""
        if self.results is None:
            raise ValueError("No backtest results available. Run backtest() first.")
        return self.results

    def get_equity_curve(self) -> pd.Series:
        """Get equity curve as pandas Series."""
        if self.results is None:
            raise ValueError("No backtest results available. Run backtest() first.")
        return self.results['equity_curve']

    def get_trades(self) -> pd.DataFrame:
        """Get trades as pandas DataFrame."""
        if self.results is None:
            raise ValueError("No backtest results available. Run backtest() first.")
        return self.results['trades']


# Re-export Strategy base class for convenience
Strategy = BaseStrategy


# Example usage
if __name__ == "__main__":
    from examples.moving_average_strategy import MovingAverageCrossover

    print("=" * 80)
    print("Backtest Engine - Quick Example")
    print("=" * 80)

    # Create engine (auto-detects Parquet or CSV)
    engine = BacktestEngine()

    # Create strategy
    strategy = MovingAverageCrossover(
        fast_period=10,
        slow_period=30,
        ma_type='EMA'
    )

    # Run backtest (with validation and logging)
    results = engine.backtest(
        strategy=strategy,
        exchange='Combined_Index',
        start_date='2023-01-01',
        end_date='2023-03-31',
        initial_capital=10000,
        commission_rate=0.001
    )

    # Print results
    print("\n")
    engine.print_results()

    # Generate report
    report_path = engine.generate_report()
    print(f"\n📊 Report: {report_path}")

    print("\n" + "=" * 80)
    print("✅ Backtest complete!")
    print("=" * 80)
