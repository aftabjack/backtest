"""
Advanced performance metrics and analysis.
Provides detailed statistical analysis of backtest results.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy import stats


class PerformanceMetrics:
    """Calculate advanced performance metrics."""

    @staticmethod
    def calculate_all_metrics(
        equity_curve: pd.DataFrame,
        trades_df: pd.DataFrame,
        initial_capital: float,
        risk_free_rate: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.

        Args:
            equity_curve: DataFrame with equity values
            trades_df: DataFrame with trade history
            initial_capital: Starting capital
            risk_free_rate: Annual risk-free rate

        Returns:
            Dictionary with all metrics
        """
        metrics = {}

        # Returns metrics
        metrics.update(PerformanceMetrics._calculate_return_metrics(
            equity_curve, initial_capital
        ))

        # Risk metrics
        metrics.update(PerformanceMetrics._calculate_risk_metrics(
            equity_curve, risk_free_rate
        ))

        # Trade metrics
        if not trades_df.empty:
            metrics.update(PerformanceMetrics._calculate_trade_metrics(trades_df))

        # Drawdown metrics
        metrics.update(PerformanceMetrics._calculate_drawdown_metrics(equity_curve))

        return metrics

    @staticmethod
    def _calculate_return_metrics(
        equity_curve: pd.DataFrame,
        initial_capital: float
    ) -> Dict[str, float]:
        """Calculate return-based metrics."""
        if equity_curve.empty:
            return {}

        equity = equity_curve['equity']
        final_equity = equity.iloc[-1]

        total_return = ((final_equity - initial_capital) / initial_capital) * 100

        # Calculate returns
        returns = equity.pct_change().dropna()

        # Annualized return (assuming 1-minute data)
        periods_per_year = 525600  # Minutes in a year
        periods = len(equity)
        years = periods / periods_per_year

        if years > 0:
            cagr = (((final_equity / initial_capital) ** (1 / years)) - 1) * 100
        else:
            cagr = 0.0

        return {
            'total_return_pct': total_return,
            'cagr': cagr,
            'average_daily_return': returns.mean() * 1440,  # Convert to daily
            'return_volatility': returns.std() * np.sqrt(1440),  # Daily volatility
        }

    @staticmethod
    def _calculate_risk_metrics(
        equity_curve: pd.DataFrame,
        risk_free_rate: float = 0.0
    ) -> Dict[str, float]:
        """Calculate risk-based metrics."""
        if equity_curve.empty or len(equity_curve) < 2:
            return {}

        equity = equity_curve['equity']
        returns = equity.pct_change().dropna()

        # Sharpe Ratio
        periods_per_year = 525600
        excess_returns = returns - (risk_free_rate / periods_per_year)
        sharpe = np.sqrt(periods_per_year) * excess_returns.mean() / returns.std() if returns.std() > 0 else 0.0

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        sortino = np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std() if len(downside_returns) > 0 and downside_returns.std() > 0 else 0.0

        # Calmar Ratio
        max_dd = PerformanceMetrics._calculate_max_drawdown_value(equity_curve)
        years = len(equity) / periods_per_year
        cagr = (((equity.iloc[-1] / equity.iloc[0]) ** (1 / years)) - 1) * 100 if years > 0 else 0.0
        calmar = cagr / max_dd if max_dd > 0 else 0.0

        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5) * 100

        # Conditional Value at Risk (CVaR)
        cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100

        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'var_95': var_95,
            'cvar_95': cvar_95,
        }

    @staticmethod
    def _calculate_trade_metrics(trades_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trade-based metrics."""
        closed_trades = trades_df[trades_df['status'] == 'CLOSED'].copy()

        if closed_trades.empty:
            return {}

        wins = closed_trades[closed_trades['pnl'] > 0]
        losses = closed_trades[closed_trades['pnl'] <= 0]

        total_trades = len(closed_trades)
        winning_trades = len(wins)
        losing_trades = len(losses)

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        # Average metrics
        avg_win = wins['pnl'].mean() if not wins.empty else 0.0
        avg_loss = losses['pnl'].mean() if not losses.empty else 0.0

        # Profit factor
        gross_profit = wins['pnl'].sum() if not wins.empty else 0.0
        gross_loss = abs(losses['pnl'].sum()) if not losses.empty else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Expectancy
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * abs(avg_loss))

        # Consecutive wins/losses
        pnl_signs = np.sign(closed_trades['pnl'].values)
        max_consecutive_wins = PerformanceMetrics._max_consecutive(pnl_signs, 1)
        max_consecutive_losses = PerformanceMetrics._max_consecutive(pnl_signs, -1)

        # Best/Worst trades
        best_trade = closed_trades['pnl'].max()
        worst_trade = closed_trades['pnl'].min()

        # Average trade duration
        closed_trades['entry_time'] = pd.to_datetime(closed_trades['entry_time'])
        closed_trades['exit_time'] = pd.to_datetime(closed_trades['exit_time'])
        durations = (closed_trades['exit_time'] - closed_trades['entry_time']).dt.total_seconds() / 60
        avg_duration_minutes = durations.mean()

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'avg_trade_duration_minutes': avg_duration_minutes,
        }

    @staticmethod
    def _calculate_drawdown_metrics(equity_curve: pd.DataFrame) -> Dict[str, Any]:
        """Calculate drawdown-based metrics."""
        if equity_curve.empty:
            return {}

        equity = equity_curve['equity']

        # Calculate drawdown series
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100

        max_drawdown = abs(drawdown.min())

        # Drawdown duration
        is_drawdown = drawdown < 0
        drawdown_periods = is_drawdown.astype(int).groupby((~is_drawdown).cumsum()).sum()
        max_drawdown_duration = drawdown_periods.max() if not drawdown_periods.empty else 0

        # Current drawdown
        current_drawdown = abs(drawdown.iloc[-1])

        # Recovery factor
        total_return = ((equity.iloc[-1] - equity.iloc[0]) / equity.iloc[0]) * 100
        recovery_factor = total_return / max_drawdown if max_drawdown > 0 else 0.0

        return {
            'max_drawdown_pct': max_drawdown,
            'max_drawdown_duration_bars': max_drawdown_duration,
            'current_drawdown_pct': current_drawdown,
            'recovery_factor': recovery_factor,
        }

    @staticmethod
    def _calculate_max_drawdown_value(equity_curve: pd.DataFrame) -> float:
        """Calculate maximum drawdown percentage."""
        if equity_curve.empty:
            return 0.0

        equity = equity_curve['equity']
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100

        return abs(drawdown.min())

    @staticmethod
    def _max_consecutive(arr: np.ndarray, value: int) -> int:
        """Calculate maximum consecutive occurrences of a value."""
        if len(arr) == 0:
            return 0

        max_count = 0
        current_count = 0

        for v in arr:
            if v == value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0

        return max_count


class MonteCarloSimulation:
    """Monte Carlo simulation for strategy analysis."""

    @staticmethod
    def run_simulation(
        trades_df: pd.DataFrame,
        initial_capital: float,
        num_simulations: int = 1000
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation on trade sequence.

        Args:
            trades_df: DataFrame with trade history
            initial_capital: Starting capital
            num_simulations: Number of simulations to run

        Returns:
            Dictionary with simulation results
        """
        if trades_df.empty:
            return {}

        closed_trades = trades_df[trades_df['status'] == 'CLOSED'].copy()

        if closed_trades.empty:
            return {}

        pnl_list = closed_trades['pnl'].values
        num_trades = len(pnl_list)

        # Run simulations
        final_equities = []

        for _ in range(num_simulations):
            # Randomly shuffle trade order
            shuffled_pnl = np.random.choice(pnl_list, size=num_trades, replace=True)

            # Calculate equity curve
            equity = initial_capital + np.cumsum(shuffled_pnl)
            final_equities.append(equity[-1])

        final_equities = np.array(final_equities)

        # Calculate statistics
        mean_final_equity = final_equities.mean()
        median_final_equity = np.median(final_equities)
        std_final_equity = final_equities.std()

        # Percentiles
        percentile_5 = np.percentile(final_equities, 5)
        percentile_25 = np.percentile(final_equities, 25)
        percentile_75 = np.percentile(final_equities, 75)
        percentile_95 = np.percentile(final_equities, 95)

        # Probability of profit
        prob_profit = (final_equities > initial_capital).sum() / num_simulations * 100

        return {
            'num_simulations': num_simulations,
            'mean_final_equity': mean_final_equity,
            'median_final_equity': median_final_equity,
            'std_final_equity': std_final_equity,
            'percentile_5': percentile_5,
            'percentile_25': percentile_25,
            'percentile_75': percentile_75,
            'percentile_95': percentile_95,
            'probability_of_profit': prob_profit,
            'best_case': final_equities.max(),
            'worst_case': final_equities.min(),
        }


class StrategyComparison:
    """Compare multiple strategy results."""

    @staticmethod
    def compare_strategies(results_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Compare multiple strategy results.

        Args:
            results_list: List of result dictionaries from backtests

        Returns:
            DataFrame with comparison
        """
        comparison_data = []

        for result in results_list:
            comparison_data.append({
                'Strategy': result.get('strategy', 'Unknown'),
                'Total Return %': result.get('total_return', 0),
                'Win Rate %': result.get('win_rate', 0),
                'Profit Factor': result.get('profit_factor', 0),
                'Max Drawdown %': result.get('max_drawdown', 0),
                'Sharpe Ratio': result.get('sharpe_ratio', 0),
                'Total Trades': result.get('total_trades', 0),
                'Final Equity': result.get('final_equity', 0),
            })

        return pd.DataFrame(comparison_data)
