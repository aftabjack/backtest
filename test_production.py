"""
Production Testing Suite
========================

Comprehensive tests for production scenarios including:
- Different date ranges
- All exchanges
- Edge cases
- Error handling
- Validation
- Performance
"""

import sys
import traceback
from datetime import datetime
from backtest_engine import BacktestEngine
from examples.moving_average_strategy import MovingAverageCrossover
from examples.rsi_strategy import RSIStrategy
from examples.bollinger_bands_strategy import BollingerBandsStrategy
from examples.macd_strategy import MACDStrategy

# Test results
tests_passed = 0
tests_failed = 0
test_results = []


def log_test(test_name, passed, error=None):
    """Log test result."""
    global tests_passed, tests_failed

    if passed:
        tests_passed += 1
        print(f"✅ PASS: {test_name}")
        test_results.append((test_name, "PASS", None))
    else:
        tests_failed += 1
        print(f"❌ FAIL: {test_name}")
        if error:
            print(f"   Error: {error}")
        test_results.append((test_name, "FAIL", error))


def test_date_ranges():
    """Test different date ranges."""
    print("\n" + "="*80)
    print("TEST SUITE 1: Date Ranges")
    print("="*80)

    test_cases = [
        ("1 month", "2023-01-01", "2023-01-31"),
        ("3 months", "2023-01-01", "2023-03-31"),
        ("6 months", "2023-01-01", "2023-06-30"),
        ("1 year", "2023-01-01", "2023-12-31"),
        ("Recent data", "2024-01-01", "2024-03-31"),
    ]

    for name, start, end in test_cases:
        try:
            engine = BacktestEngine()
            strategy = MovingAverageCrossover(10, 30)
            results = engine.backtest(
                strategy=strategy,
                start_date=start,
                end_date=end,
                initial_capital=10000
            )

            # Verify results
            assert results is not None, "No results returned"
            assert 'total_return' in results, "Missing total_return"
            assert 'total_trades' in results, "Missing total_trades"

            log_test(f"Date range: {name} ({start} to {end})", True)
            print(f"   Return: {results['total_return']:.2f}%, Trades: {results['total_trades']}")

        except Exception as e:
            log_test(f"Date range: {name} ({start} to {end})", False, str(e))


def test_all_exchanges():
    """Test all available exchanges."""
    print("\n" + "="*80)
    print("TEST SUITE 2: All Exchanges")
    print("="*80)

    exchanges = [
        'Combined_Index',
        'Binance',
        'Coinbase',
        'BitMEX',
        'Bitfinex',
        'Bitstamp',
        'KuCoin',
        'OKX'
    ]

    for exchange in exchanges:
        try:
            engine = BacktestEngine()
            strategy = MovingAverageCrossover(10, 30)
            results = engine.backtest(
                strategy=strategy,
                exchange=exchange,
                start_date='2023-01-01',
                end_date='2023-03-31',
                initial_capital=10000
            )

            assert results is not None, "No results returned"
            log_test(f"Exchange: {exchange}", True)
            print(f"   Return: {results['total_return']:.2f}%, Trades: {results['total_trades']}")

        except Exception as e:
            log_test(f"Exchange: {exchange}", False, str(e))


def test_all_strategies():
    """Test all built-in strategies."""
    print("\n" + "="*80)
    print("TEST SUITE 3: All Strategies")
    print("="*80)

    strategies = [
        ("MA Crossover", MovingAverageCrossover(10, 30)),
        ("RSI", RSIStrategy(rsi_period=14)),
        ("Bollinger Bands", BollingerBandsStrategy(period=20)),
        ("MACD", MACDStrategy()),
    ]

    for name, strategy in strategies:
        try:
            engine = BacktestEngine()
            results = engine.backtest(
                strategy=strategy,
                start_date='2023-01-01',
                end_date='2023-03-31',
                initial_capital=10000
            )

            assert results is not None, "No results returned"
            log_test(f"Strategy: {name}", True)
            print(f"   Return: {results['total_return']:.2f}%, Trades: {results['total_trades']}")

        except Exception as e:
            log_test(f"Strategy: {name}", False, str(e))


def test_different_parameters():
    """Test different configuration parameters."""
    print("\n" + "="*80)
    print("TEST SUITE 4: Different Parameters")
    print("="*80)

    test_cases = [
        ("Low capital", 1000, 0.001, 1.0),
        ("High capital", 100000, 0.001, 1.0),
        ("High commission", 10000, 0.01, 1.0),  # 1%
        ("Low commission", 10000, 0.0001, 1.0),  # 0.01%
        ("50% position", 10000, 0.001, 0.5),
        ("25% position", 10000, 0.001, 0.25),
    ]

    for name, capital, commission, position_size in test_cases:
        try:
            engine = BacktestEngine()
            strategy = MovingAverageCrossover(10, 30)
            results = engine.backtest(
                strategy=strategy,
                start_date='2023-01-01',
                end_date='2023-03-31',
                initial_capital=capital,
                commission_rate=commission,
                position_size=position_size
            )

            assert results is not None, "No results returned"
            log_test(f"Parameters: {name}", True)
            print(f"   Return: {results['total_return']:.2f}%, Trades: {results['total_trades']}")

        except Exception as e:
            log_test(f"Parameters: {name}", False, str(e))


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*80)
    print("TEST SUITE 5: Edge Cases & Error Handling")
    print("="*80)

    # Test 1: Invalid exchange
    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            exchange='InvalidExchange',
            start_date='2023-01-01',
            end_date='2023-03-31'
        )
        log_test("Invalid exchange (should fail)", False, "Should have raised error")
    except Exception as e:
        log_test("Invalid exchange (should fail)", True)
        print(f"   Expected error: {type(e).__name__}")

    # Test 2: Invalid date format
    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            start_date='2023/01/01',  # Wrong format
            end_date='2023-03-31'
        )
        log_test("Invalid date format (should fail)", False, "Should have raised error")
    except Exception as e:
        log_test("Invalid date format (should fail)", True)
        print(f"   Expected error: {type(e).__name__}")

    # Test 3: Start date after end date
    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            start_date='2023-12-31',
            end_date='2023-01-01'
        )
        log_test("Start > End date (should fail)", False, "Should have raised error")
    except Exception as e:
        log_test("Start > End date (should fail)", True)
        print(f"   Expected error: {type(e).__name__}")

    # Test 4: Negative capital
    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            initial_capital=-1000,
            start_date='2023-01-01',
            end_date='2023-03-31'
        )
        log_test("Negative capital (should fail)", False, "Should have raised error")
    except Exception as e:
        log_test("Negative capital (should fail)", True)
        print(f"   Expected error: {type(e).__name__}")

    # Test 5: Invalid commission rate
    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            commission_rate=1.5,  # 150% - invalid
            start_date='2023-01-01',
            end_date='2023-03-31'
        )
        log_test("Invalid commission rate (should fail)", False, "Should have raised error")
    except Exception as e:
        log_test("Invalid commission rate (should fail)", True)
        print(f"   Expected error: {type(e).__name__}")

    # Test 6: Invalid position size
    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            position_size=2.0,  # 200% - invalid
            start_date='2023-01-01',
            end_date='2023-03-31'
        )
        log_test("Invalid position size (should fail)", False, "Should have raised error")
    except Exception as e:
        log_test("Invalid position size (should fail)", True)
        print(f"   Expected error: {type(e).__name__}")

    # Test 7: Very short date range (might have insufficient data)
    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            start_date='2023-01-01',
            end_date='2023-01-02',  # Only 1 day
            validate=False  # Skip validation
        )
        log_test("Very short date range (1 day)", True)
        print(f"   Return: {results['total_return']:.2f}%, Trades: {results['total_trades']}")
    except Exception as e:
        log_test("Very short date range (1 day)", False, str(e))


def test_csv_fallback():
    """Test CSV fallback when Parquet not available."""
    print("\n" + "="*80)
    print("TEST SUITE 6: CSV Fallback")
    print("="*80)

    try:
        # Force CSV usage
        engine = BacktestEngine(use_parquet=False)
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            start_date='2023-01-01',
            end_date='2023-01-31',
            initial_capital=10000
        )

        assert results is not None, "No results returned"
        log_test("CSV fallback", True)
        print(f"   Return: {results['total_return']:.2f}%, Trades: {results['total_trades']}")

    except Exception as e:
        log_test("CSV fallback", False, str(e))


def test_validation_disabled():
    """Test with validation disabled."""
    print("\n" + "="*80)
    print("TEST SUITE 7: Validation Disabled")
    print("="*80)

    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            start_date='2023-01-01',
            end_date='2023-03-31',
            initial_capital=10000,
            validate=False  # Disable validation
        )

        assert results is not None, "No results returned"
        log_test("Validation disabled", True)
        print(f"   Return: {results['total_return']:.2f}%, Trades: {results['total_trades']}")

    except Exception as e:
        log_test("Validation disabled", False, str(e))


def test_report_generation():
    """Test report generation."""
    print("\n" + "="*80)
    print("TEST SUITE 8: Report Generation")
    print("="*80)

    try:
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(10, 30)
        results = engine.backtest(
            strategy=strategy,
            start_date='2023-01-01',
            end_date='2023-03-31',
            initial_capital=10000
        )

        # Generate report
        report_path = engine.generate_report(save_charts=True)

        assert report_path is not None, "No report path returned"
        log_test("Report generation", True)
        print(f"   Report path: {report_path}")

    except Exception as e:
        log_test("Report generation", False, str(e))


def test_multiple_runs():
    """Test multiple consecutive runs."""
    print("\n" + "="*80)
    print("TEST SUITE 9: Multiple Consecutive Runs")
    print("="*80)

    try:
        engine = BacktestEngine()

        for i in range(3):
            strategy = MovingAverageCrossover(10, 30)
            results = engine.backtest(
                strategy=strategy,
                start_date='2023-01-01',
                end_date='2023-03-31',
                initial_capital=10000
            )

            assert results is not None, f"No results returned for run {i+1}"

        log_test("Multiple consecutive runs (3x)", True)

    except Exception as e:
        log_test("Multiple consecutive runs (3x)", False, str(e))


def print_summary():
    """Print test summary."""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total_tests = tests_passed + tests_failed
    pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed:      {tests_passed} ✅")
    print(f"Failed:      {tests_failed} ❌")
    print(f"Pass Rate:   {pass_rate:.1f}%")

    if tests_failed > 0:
        print("\n" + "="*80)
        print("FAILED TESTS:")
        print("="*80)
        for name, status, error in test_results:
            if status == "FAIL":
                print(f"\n❌ {name}")
                if error:
                    print(f"   Error: {error}")

    print("\n" + "="*80)
    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED! Production ready!")
    else:
        print("⚠️  Some tests failed. Review errors above.")
    print("="*80)


def main():
    """Run all test suites."""
    print("="*80)
    print("PRODUCTION TESTING SUITE")
    print("="*80)
    print("\nTesting production scenarios for bugs and errors...")
    print("This may take a few minutes...\n")

    try:
        # Run all test suites
        test_date_ranges()
        test_all_exchanges()
        test_all_strategies()
        test_different_parameters()
        test_edge_cases()
        test_csv_fallback()
        test_validation_disabled()
        test_report_generation()
        test_multiple_runs()

    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Critical error during testing: {e}")
        traceback.print_exc()
    finally:
        # Always print summary
        print_summary()


if __name__ == "__main__":
    main()
