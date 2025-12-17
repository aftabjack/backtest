"""
Verify that the backtesting engine is set up correctly.
Run this script to check dependencies and data availability.
"""

import sys
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking dependencies...")
    missing = []

    dependencies = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
        'scipy', 'sklearn'
    ]

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (missing)")
            missing.append(dep)

    # Check optional dependencies
    print("\nOptional dependencies:")
    optional = ['talib', 'pandas_ta']

    for dep in optional:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  - {dep} (not installed, but optional)")

    return len(missing) == 0


def check_data():
    """Check if data files are available."""
    print("\nChecking data availability...")
    data_dir = Path('csv_data')

    if not data_dir.exists():
        print(f"  ✗ Data directory not found: {data_dir}")
        return False

    csv_files = list(data_dir.glob('*.csv'))

    if not csv_files:
        print(f"  ✗ No CSV files found in {data_dir}")
        return False

    print(f"  ✓ Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        print(f"    - {csv_file.name} ({size_mb:.1f} MB)")

    return True


def check_structure():
    """Check if project structure is correct."""
    print("\nChecking project structure...")

    required_dirs = [
        'strategies', 'engine', 'analytics',
        'data_handlers', 'examples', 'output'
    ]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_exist = False

    return all_exist


def check_imports():
    """Check if custom modules can be imported."""
    print("\nChecking custom modules...")

    modules = [
        ('data_handlers.loader', 'DataLoader'),
        ('engine.backtest', 'Backtester'),
        ('engine.portfolio', 'Portfolio'),
        ('strategies.base_strategy', 'BaseStrategy'),
        ('analytics.metrics', 'PerformanceMetrics'),
        ('analytics.reports', 'ReportGenerator'),
    ]

    all_ok = True
    for module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✓ {module_path}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_path}.{class_name} - {e}")
            all_ok = False

    return all_ok


def main():
    """Run all verification checks."""
    print("="*80)
    print("BACKTESTING ENGINE SETUP VERIFICATION")
    print("="*80 + "\n")

    checks = {
        'Dependencies': check_dependencies(),
        'Project Structure': check_structure(),
        'Data Files': check_data(),
        'Module Imports': check_imports()
    }

    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80 + "\n")

    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*80)

    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Run: python quickstart.py")
        print("  2. Or run: python main.py")
        print("  3. Check the README.md for detailed documentation")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Download data to csv_data/ directory")
        print("  • Make sure you're in the project root directory")

    print("="*80 + "\n")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
