"""
Production Logging System
==========================

Comprehensive logging system for production backtesting engine.

Features:
- Structured logging with multiple handlers
- Rotating file logs (prevents disk overflow)
- Different log levels for console and file
- Performance logging
- Error tracking
- Context managers for timing

Usage:
    from utils.logger import get_logger, log_performance

    logger = get_logger(__name__)
    logger.info("Backtest started")

    with log_performance("Loading data"):
        data = load_data()
"""

import logging
import sys
import time
import functools
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from contextlib import contextmanager
from typing import Optional
from datetime import datetime


# ============================================================================
# Logger Configuration
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colored output for console.
    """
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logger(
    name: str = 'backtest',
    log_dir: str = 'logs',
    level: int = logging.INFO,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup production logger with console and file handlers.

    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Overall logging level
        console_level: Console output level
        file_level: File output level
        max_bytes: Max size of each log file
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Console Handler - Human-readable with colors
    # ========================================================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)

    console_formatter = ColoredFormatter(
        fmt='%(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # ========================================================================
    # File Handler - Detailed with rotation
    # ========================================================================
    log_file = Path(log_dir) / f'{name}.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(file_level)

    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # ========================================================================
    # Error File Handler - Errors only
    # ========================================================================
    error_log_file = Path(log_dir) / f'{name}_errors.log'
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)

    # ========================================================================
    # Daily File Handler - One file per day
    # ========================================================================
    daily_log_file = Path(log_dir) / f'{name}_daily.log'
    daily_handler = TimedRotatingFileHandler(
        daily_log_file,
        when='midnight',
        interval=1,
        backupCount=30  # Keep 30 days
    )
    daily_handler.setLevel(file_level)
    daily_handler.setFormatter(file_formatter)
    logger.addHandler(daily_handler)

    return logger


def get_logger(name: str = 'backtest') -> logging.Logger:
    """
    Get or create logger instance.

    Usage:
        logger = get_logger(__name__)
        logger.info("Message")

    Args:
        name: Logger name (use __name__ for module-specific logger)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If not configured, set up with defaults
    if not logger.handlers:
        setup_logger(name)

    return logger


# ============================================================================
# Performance Logging
# ============================================================================

@contextmanager
def log_performance(operation: str, logger: Optional[logging.Logger] = None, level: int = logging.INFO):
    """
    Context manager for logging operation performance.

    Usage:
        with log_performance("Loading data"):
            data = load_data()

    Args:
        operation: Operation description
        logger: Logger instance (creates default if None)
        level: Log level for the message
    """
    if logger is None:
        logger = get_logger()

    start_time = time.time()
    logger.log(level, f"Starting: {operation}")

    try:
        yield
        elapsed = time.time() - start_time
        logger.log(level, f"Completed: {operation} in {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Failed: {operation} after {elapsed:.2f}s - {str(e)}")
        raise


def log_execution_time(func):
    """
    Decorator for logging function execution time.

    Usage:
        @log_execution_time
        def my_function():
            pass

    Args:
        func: Function to decorate

    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        logger.debug(f"Calling: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"Completed: {func.__name__} in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed: {func.__name__} after {elapsed:.3f}s - {str(e)}")
            raise

    return wrapper


# ============================================================================
# Specialized Loggers
# ============================================================================

class BacktestLogger:
    """
    Specialized logger for backtesting operations.
    """

    def __init__(self, name: str = 'backtest'):
        self.logger = get_logger(name)

    def log_backtest_start(self, strategy_name: str, initial_capital: float, date_range: tuple):
        """Log backtest initialization."""
        self.logger.info("=" * 60)
        self.logger.info("BACKTEST STARTED")
        self.logger.info("=" * 60)
        self.logger.info(f"Strategy: {strategy_name}")
        self.logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        self.logger.info(f"Date Range: {date_range[0]} to {date_range[1]}")

    def log_backtest_end(self, results: dict):
        """Log backtest completion."""
        self.logger.info("=" * 60)
        self.logger.info("BACKTEST COMPLETED")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Return: {results.get('total_return', 0):.2f}%")
        self.logger.info(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        self.logger.info(f"Max Drawdown: {results.get('max_drawdown', 0):.2f}%")
        self.logger.info(f"Total Trades: {results.get('total_trades', 0)}")
        self.logger.info(f"Win Rate: {results.get('win_rate', 0):.2f}%")

    def log_trade(self, trade_type: str, price: float, quantity: float, value: float):
        """Log individual trade."""
        self.logger.debug(
            f"TRADE: {trade_type} | Price: ${price:.2f} | "
            f"Quantity: {quantity:.4f} | Value: ${value:.2f}"
        )

    def log_signal(self, timestamp, signal_type: str, indicators: dict):
        """Log trading signal."""
        indicator_str = ", ".join([f"{k}={v:.2f}" for k, v in indicators.items()])
        self.logger.debug(f"SIGNAL: {timestamp} | {signal_type} | {indicator_str}")

    def log_error(self, error_type: str, message: str, context: dict = None):
        """Log error with context."""
        self.logger.error(f"ERROR: {error_type} | {message}")
        if context:
            for key, value in context.items():
                self.logger.error(f"  {key}: {value}")


class PerformanceLogger:
    """
    Logger for performance metrics and benchmarking.
    """

    def __init__(self, name: str = 'performance'):
        self.logger = get_logger(name)
        self.timings = {}

    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.timings[operation] = time.time()
        self.logger.debug(f"Timer started: {operation}")

    def stop_timer(self, operation: str):
        """Stop timing and log result."""
        if operation not in self.timings:
            self.logger.warning(f"No timer found for: {operation}")
            return 0

        elapsed = time.time() - self.timings[operation]
        del self.timings[operation]
        self.logger.info(f"⏱️  {operation}: {elapsed:.3f}s")
        return elapsed

    def log_memory_usage(self, context: str = ""):
        """Log current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.logger.info(f"💾 Memory usage{f' ({context})' if context else ''}: {memory_mb:.1f} MB")
        except ImportError:
            self.logger.warning("psutil not installed - cannot log memory usage")


# ============================================================================
# Utility Functions
# ============================================================================

def log_system_info():
    """Log system information."""
    import platform
    logger = get_logger('system')

    logger.info("=" * 60)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 60)
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Processor: {platform.processor()}")

    try:
        import psutil
        logger.info(f"CPU Cores: {psutil.cpu_count()}")
        logger.info(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    except ImportError:
        logger.warning("psutil not installed - cannot log detailed system info")


def log_data_info(data, name: str = "Dataset"):
    """Log dataset information."""
    logger = get_logger('data')

    logger.info(f"\n{name} Information:")
    logger.info(f"  Rows: {len(data):,}")
    logger.info(f"  Columns: {list(data.columns)}")
    logger.info(f"  Date range: {data.index[0]} to {data.index[-1]}")
    logger.info(f"  Memory: {data.memory_usage(deep=True).sum() / (1024**2):.1f} MB")


# ============================================================================
# Main - Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Logger Demo")
    print("=" * 60)

    # Setup logger
    logger = setup_logger('demo', log_dir='logs')

    # Test different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")

    # Test performance logging
    with log_performance("Sample operation", logger):
        time.sleep(1)

    # Test BacktestLogger
    bt_logger = BacktestLogger()
    bt_logger.log_backtest_start("MA Crossover", 10000, ("2023-01-01", "2023-12-31"))

    # Test PerformanceLogger
    perf_logger = PerformanceLogger()
    perf_logger.start_timer("data_loading")
    time.sleep(0.5)
    perf_logger.stop_timer("data_loading")

    # Log system info
    log_system_info()

    print("\n✅ Logs saved to: logs/")
    print("   - demo.log (all logs)")
    print("   - demo_errors.log (errors only)")
    print("   - demo_daily.log (daily rotation)")
