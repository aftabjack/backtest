"""
Visualization and reporting module.
Generate charts and export reports.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional
from pathlib import Path
import json


class ReportGenerator:
    """Generate backtest reports in various formats."""

    def __init__(self, output_dir: str = 'output'):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set style
        sns.set_style('darkgrid')
        plt.rcParams['figure.figsize'] = (12, 6)

    def generate_full_report(
        self,
        results: Dict[str, Any],
        save_charts: bool = True,
        show_charts: bool = False
    ) -> str:
        """
        Generate comprehensive backtest report.

        Args:
            results: Backtest results dictionary
            save_charts: Whether to save chart files
            show_charts: Whether to display charts

        Returns:
            Path to report directory
        """
        strategy_name = results['strategy'].replace(' ', '_')
        report_dir = self.output_dir / f"{strategy_name}_report"
        report_dir.mkdir(exist_ok=True)

        print(f"Generating report for {results['strategy']}...")

        # Export results to JSON
        self._export_json(results, report_dir / 'results.json')

        # Export trades to CSV
        if 'trades' in results and not results['trades'].empty:
            results['trades'].to_csv(report_dir / 'trades.csv', index=False)
            print(f"✓ Exported trades to CSV")

        # Export equity curve to CSV
        if 'equity_curve' in results and not results['equity_curve'].empty:
            results['equity_curve'].to_csv(report_dir / 'equity_curve.csv')
            print(f"✓ Exported equity curve to CSV")

        # Generate charts
        if save_charts or show_charts:
            self._generate_charts(results, report_dir, save_charts, show_charts)

        # Generate text report
        self._generate_text_report(results, report_dir / 'report.txt')

        print(f"\n✓ Report generated successfully!")
        print(f"Report location: {report_dir}")

        return str(report_dir)

    def _export_json(self, results: Dict[str, Any], filepath: Path):
        """Export results to JSON (excluding DataFrames)."""
        json_results = {}

        for key, value in results.items():
            if isinstance(value, pd.DataFrame):
                continue
            elif isinstance(value, (np.integer, np.floating)):
                json_results[key] = float(value)
            elif isinstance(value, (int, float, str, bool, list, dict)) or value is None:
                json_results[key] = value

        with open(filepath, 'w') as f:
            json.dump(json_results, f, indent=2)

        print(f"✓ Exported results to JSON")

    def _generate_charts(
        self,
        results: Dict[str, Any],
        report_dir: Path,
        save: bool = True,
        show: bool = False
    ):
        """Generate all charts."""
        print("\nGenerating charts...")

        # 1. Equity curve
        self._plot_equity_curve(results, report_dir, save, show)

        # 2. Drawdown chart
        self._plot_drawdown(results, report_dir, save, show)

        # 3. Trade distribution
        if 'trades' in results and not results['trades'].empty:
            self._plot_trade_distribution(results, report_dir, save, show)

        # 4. Monthly returns heatmap
        self._plot_monthly_returns(results, report_dir, save, show)

        # 5. Cumulative returns comparison
        self._plot_returns_comparison(results, report_dir, save, show)

        print("✓ All charts generated")

    def _plot_equity_curve(
        self,
        results: Dict[str, Any],
        report_dir: Path,
        save: bool,
        show: bool
    ):
        """Plot equity curve."""
        if 'equity_curve' not in results or results['equity_curve'].empty:
            return

        fig, ax = plt.subplots(figsize=(14, 7))

        equity_curve = results['equity_curve']
        ax.plot(equity_curve.index, equity_curve['equity'], linewidth=2, color='#2E86AB')
        ax.axhline(y=results['initial_capital'], color='gray', linestyle='--', alpha=0.5, label='Initial Capital')

        ax.set_title(f"Equity Curve - {results['strategy']}", fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Equity ($)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add annotations
        final_equity = equity_curve['equity'].iloc[-1]
        initial_capital = results['initial_capital']
        total_return = ((final_equity - initial_capital) / initial_capital) * 100

        textstr = f'Final Equity: ${final_equity:,.2f}\nTotal Return: {total_return:.2f}%'
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save:
            plt.savefig(report_dir / 'equity_curve.png', dpi=300, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def _plot_drawdown(
        self,
        results: Dict[str, Any],
        report_dir: Path,
        save: bool,
        show: bool
    ):
        """Plot drawdown chart."""
        if 'equity_curve' not in results or results['equity_curve'].empty:
            return

        fig, ax = plt.subplots(figsize=(14, 7))

        equity = results['equity_curve']['equity']
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100

        ax.fill_between(drawdown.index, drawdown, 0, color='#E63946', alpha=0.7)
        ax.plot(drawdown.index, drawdown, linewidth=1, color='#C1121F')

        ax.set_title(f"Drawdown - {results['strategy']}", fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.grid(True, alpha=0.3)

        # Add max drawdown annotation
        max_dd = results.get('max_drawdown', 0)
        textstr = f'Max Drawdown: {max_dd:.2f}%'
        ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=11,
                verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save:
            plt.savefig(report_dir / 'drawdown.png', dpi=300, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def _plot_trade_distribution(
        self,
        results: Dict[str, Any],
        report_dir: Path,
        save: bool,
        show: bool
    ):
        """Plot trade P&L distribution."""
        trades_df = results['trades']
        closed_trades = trades_df[trades_df['status'] == 'CLOSED']

        if closed_trades.empty:
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Histogram of P&L
        pnl = closed_trades['pnl']
        ax1.hist(pnl, bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax1.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('P&L ($)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.grid(True, alpha=0.3)

        # Win/Loss pie chart
        wins = len(closed_trades[closed_trades['pnl'] > 0])
        losses = len(closed_trades[closed_trades['pnl'] <= 0])

        ax2.pie([wins, losses], labels=['Wins', 'Losses'], autopct='%1.1f%%',
                colors=['#06A77D', '#E63946'], startangle=90)
        ax2.set_title('Win/Loss Ratio', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save:
            plt.savefig(report_dir / 'trade_distribution.png', dpi=300, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def _plot_monthly_returns(
        self,
        results: Dict[str, Any],
        report_dir: Path,
        save: bool,
        show: bool
    ):
        """Plot monthly returns heatmap."""
        if 'equity_curve' not in results or results['equity_curve'].empty:
            return

        equity_curve = results['equity_curve'].copy()

        # Calculate monthly returns
        equity_curve['month'] = equity_curve.index.month
        equity_curve['year'] = equity_curve.index.year

        monthly_equity = equity_curve.groupby(['year', 'month'])['equity'].last()

        if len(monthly_equity) < 2:
            return

        monthly_returns = monthly_equity.pct_change() * 100
        monthly_returns = monthly_returns.reset_index()

        # Create pivot table
        pivot = monthly_returns.pivot(index='year', columns='month', values='equity')

        if pivot.empty or pivot.shape[0] == 0:
            return

        fig, ax = plt.subplots(figsize=(12, max(6, pivot.shape[0] * 0.5)))

        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
                    cbar_kws={'label': 'Return (%)'}, ax=ax, linewidths=0.5)

        ax.set_title(f"Monthly Returns (%) - {results['strategy']}", fontsize=16, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Year', fontsize=12)

        plt.tight_layout()

        if save:
            plt.savefig(report_dir / 'monthly_returns.png', dpi=300, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def _plot_returns_comparison(
        self,
        results: Dict[str, Any],
        report_dir: Path,
        save: bool,
        show: bool
    ):
        """Plot cumulative returns vs buy-and-hold."""
        if 'equity_curve' not in results or results['equity_curve'].empty:
            return

        if 'signals' not in results or results['signals'].empty:
            return

        fig, ax = plt.subplots(figsize=(14, 7))

        # Strategy returns
        equity_curve = results['equity_curve']
        strategy_returns = (equity_curve['equity'] / results['initial_capital'] - 1) * 100

        # Buy-and-hold returns
        signals = results['signals']
        first_price = signals['close'].iloc[0]
        bh_returns = (signals['close'] / first_price - 1) * 100

        # Align indices
        common_index = strategy_returns.index.intersection(bh_returns.index)

        ax.plot(common_index, strategy_returns.loc[common_index], linewidth=2,
                color='#2E86AB', label='Strategy')
        ax.plot(common_index, bh_returns.loc[common_index], linewidth=2,
                color='#F77F00', label='Buy & Hold', linestyle='--')

        ax.set_title(f"Cumulative Returns Comparison - {results['strategy']}",
                     fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cumulative Return (%)', fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)

        plt.tight_layout()

        if save:
            plt.savefig(report_dir / 'returns_comparison.png', dpi=300, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def _generate_text_report(self, results: Dict[str, Any], filepath: Path):
        """Generate text report file."""
        with open(filepath, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"BACKTEST REPORT: {results['strategy']}\n")
            f.write("="*80 + "\n\n")

            f.write("STRATEGY PARAMETERS\n")
            f.write("-"*80 + "\n")
            for key, value in results.get('parameters', {}).items():
                f.write(f"{key}: {value}\n")

            f.write("\n" + "="*80 + "\n")
            f.write("PERFORMANCE SUMMARY\n")
            f.write("="*80 + "\n\n")

            metrics = [
                ('Initial Capital', f"${results['initial_capital']:,.2f}"),
                ('Final Equity', f"${results['final_equity']:,.2f}"),
                ('Total P&L', f"${results['total_pnl']:,.2f}"),
                ('Total Return', f"{results['total_return']:.2f}%"),
                ('', ''),
                ('Total Trades', results['total_trades']),
                ('Winning Trades', results['winning_trades']),
                ('Losing Trades', results['losing_trades']),
                ('Win Rate', f"{results['win_rate']:.2f}%"),
                ('', ''),
                ('Average Win', f"${results['average_win']:,.2f}"),
                ('Average Loss', f"${results['average_loss']:,.2f}"),
                ('Profit Factor', f"{results['profit_factor']:.2f}"),
                ('', ''),
                ('Max Drawdown', f"{results['max_drawdown']:.2f}%"),
                ('Sharpe Ratio', f"{results['sharpe_ratio']:.2f}"),
                ('Sortino Ratio', f"{results['sortino_ratio']:.2f}"),
            ]

            for label, value in metrics:
                if label:
                    f.write(f"{label:<25} {str(value):>20}\n")
                else:
                    f.write("\n")

            f.write("\n" + "="*80 + "\n")

        print(f"✓ Generated text report")
