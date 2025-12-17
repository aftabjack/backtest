"""
Core backtesting engine.
Executes trading strategies on historical data and tracks performance.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime

from strategies.base_strategy import BaseStrategy, SignalType
from engine.portfolio import Portfolio, PositionType


class Backtester:
    """
    Main backtesting engine.
    Runs strategies on historical data and generates performance reports.
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,
        position_size: float = 1.0,
        allow_short: bool = False,
        slippage: float = 0.0
    ):
        """
        Initialize backtester.

        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital
            commission_rate: Commission rate (e.g., 0.001 = 0.1%)
            position_size: Position size as fraction of capital
            allow_short: Allow short positions
            slippage: Slippage as percentage (e.g., 0.001 = 0.1%)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.position_size = position_size
        self.allow_short = allow_short
        self.slippage = slippage

        # Portfolio
        self.portfolio = Portfolio(
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            position_size=position_size,
            allow_short=allow_short
        )

        # Results
        self.results = None
        self.data_with_signals = None

    def run(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run backtest on historical data.

        Args:
            data: OHLCV DataFrame

        Returns:
            Dictionary with backtest results
        """
        print(f"\n{'='*60}")
        print(f"Running Backtest: {self.strategy.get_name()}")
        print(f"{'='*60}")
        print(f"Data period: {data.index[0]} to {data.index[-1]}")
        print(f"Total bars: {len(data)}")
        print(f"Initial capital: ${self.initial_capital:,.2f}")
        print(f"Commission rate: {self.commission_rate*100:.3f}%")
        print(f"Position size: {self.position_size*100:.1f}%")
        print(f"{'='*60}\n")

        # Reset portfolio
        self.portfolio.reset()

        # Generate signals
        print("Generating signals...")
        signals_df = self.strategy.backtest(data)
        self.data_with_signals = signals_df.copy()

        # Execute trades based on signals
        print("Executing trades...")
        self._execute_trades(signals_df)

        # Generate results
        print("Calculating performance metrics...")
        self.results = self._generate_results()

        print(f"\n{'='*60}")
        print("Backtest Complete!")
        print(f"{'='*60}\n")

        return self.results

    def _execute_trades(self, signals_df: pd.DataFrame):
        """
        Execute trades based on signals.

        Args:
            signals_df: DataFrame with signals
        """
        for timestamp, row in signals_df.iterrows():
            signal = row.get('signal', SignalType.HOLD.value)
            close_price = row['close']

            # Apply slippage
            if signal == SignalType.BUY.value:
                execution_price = close_price * (1 + self.slippage)
            elif signal == SignalType.SELL.value:
                execution_price = close_price * (1 - self.slippage)
            else:
                execution_price = close_price

            # Process signal
            if signal == SignalType.BUY.value:
                # Close short position if exists
                if self.portfolio.current_position and \
                   self.portfolio.current_position.position_type == PositionType.SHORT:
                    self.portfolio.close_position(timestamp, execution_price)

                # Open long position
                if self.portfolio.current_position is None:
                    self.portfolio.open_position(
                        timestamp=timestamp,
                        price=execution_price,
                        position_type=PositionType.LONG
                    )

            elif signal == SignalType.SELL.value:
                # Close long position if exists
                if self.portfolio.current_position and \
                   self.portfolio.current_position.position_type == PositionType.LONG:
                    self.portfolio.close_position(timestamp, execution_price)

                # Open short position (if allowed)
                if self.portfolio.current_position is None and self.allow_short:
                    self.portfolio.open_position(
                        timestamp=timestamp,
                        price=execution_price,
                        position_type=PositionType.SHORT
                    )

            # Update portfolio with current price
            self.portfolio.update(timestamp, close_price)

        # Close any remaining positions at the end
        if self.portfolio.current_position is not None:
            last_timestamp = signals_df.index[-1]
            last_price = signals_df.iloc[-1]['close']
            self.portfolio.close_position(last_timestamp, last_price)

    def _generate_results(self) -> Dict[str, Any]:
        """
        Generate comprehensive backtest results.

        Returns:
            Dictionary with results
        """
        equity_curve = self.portfolio.get_equity_curve()
        trades_df = self.portfolio.get_trades_df()

        # Basic metrics
        results = {
            'strategy': self.strategy.get_name(),
            'parameters': self.strategy.get_parameters(),
            'initial_capital': self.initial_capital,
            'final_equity': self.portfolio.equity,
            'total_return': self.portfolio.total_return(),
            'total_pnl': self.portfolio.total_pnl(),

            # Trade statistics
            'total_trades': self.portfolio.total_trades(),
            'winning_trades': self.portfolio.winning_trades(),
            'losing_trades': self.portfolio.losing_trades(),
            'win_rate': self.portfolio.win_rate(),

            # P&L statistics
            'average_win': self.portfolio.average_win(),
            'average_loss': self.portfolio.average_loss(),
            'profit_factor': self.portfolio.profit_factor(),

            # Risk metrics
            'max_drawdown': self._calculate_max_drawdown(equity_curve),
            'sharpe_ratio': self._calculate_sharpe_ratio(equity_curve),
            'sortino_ratio': self._calculate_sortino_ratio(equity_curve),

            # DataFrames
            'equity_curve': equity_curve,
            'trades': trades_df,
            'signals': self.data_with_signals
        }

        # Calculate additional metrics if trades exist
        if not trades_df.empty:
            results['largest_win'] = trades_df['pnl'].max()
            results['largest_loss'] = trades_df['pnl'].min()
            results['average_trade_duration'] = self._calculate_avg_trade_duration(trades_df)

        return results

    def _calculate_max_drawdown(self, equity_curve: pd.DataFrame) -> float:
        """
        Calculate maximum drawdown.

        Args:
            equity_curve: DataFrame with equity values

        Returns:
            Maximum drawdown as percentage
        """
        if equity_curve.empty:
            return 0.0

        equity = equity_curve['equity']
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100

        return abs(drawdown.min())

    def _calculate_sharpe_ratio(
        self,
        equity_curve: pd.DataFrame,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 525600  # Minutes in a year
    ) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            equity_curve: DataFrame with equity values
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods per year

        Returns:
            Sharpe ratio
        """
        if equity_curve.empty or len(equity_curve) < 2:
            return 0.0

        returns = equity_curve['equity'].pct_change().dropna()

        if returns.std() == 0:
            return 0.0

        excess_returns = returns - (risk_free_rate / periods_per_year)
        sharpe = np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()

        return sharpe

    def _calculate_sortino_ratio(
        self,
        equity_curve: pd.DataFrame,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 525600
    ) -> float:
        """
        Calculate Sortino ratio (uses only downside deviation).

        Args:
            equity_curve: DataFrame with equity values
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods per year

        Returns:
            Sortino ratio
        """
        if equity_curve.empty or len(equity_curve) < 2:
            return 0.0

        returns = equity_curve['equity'].pct_change().dropna()
        excess_returns = returns - (risk_free_rate / periods_per_year)

        # Calculate downside deviation
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std()

        return sortino

    def _calculate_avg_trade_duration(self, trades_df: pd.DataFrame) -> str:
        """
        Calculate average trade duration.

        Args:
            trades_df: DataFrame with trades

        Returns:
            Average duration as string
        """
        if trades_df.empty:
            return "N/A"

        closed_trades = trades_df[trades_df['status'] == 'CLOSED'].copy()

        if closed_trades.empty:
            return "N/A"

        # Convert to datetime if not already
        closed_trades['entry_time'] = pd.to_datetime(closed_trades['entry_time'])
        closed_trades['exit_time'] = pd.to_datetime(closed_trades['exit_time'])

        durations = closed_trades['exit_time'] - closed_trades['entry_time']
        avg_duration = durations.mean()

        # Format duration
        days = avg_duration.days
        hours = avg_duration.seconds // 3600
        minutes = (avg_duration.seconds % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def print_results(self):
        """Print formatted backtest results."""
        if self.results is None:
            print("No results available. Run backtest first.")
            return

        r = self.results

        print(f"\n{'='*60}")
        print(f"BACKTEST RESULTS: {r['strategy']}")
        print(f"{'='*60}")

        print(f"\nStrategy Parameters:")
        for key, value in r['parameters'].items():
            print(f"  {key}: {value}")

        print(f"\n{'-'*60}")
        print("PERFORMANCE SUMMARY")
        print(f"{'-'*60}")
        print(f"Initial Capital:     ${r['initial_capital']:>15,.2f}")
        print(f"Final Equity:        ${r['final_equity']:>15,.2f}")
        print(f"Total P&L:           ${r['total_pnl']:>15,.2f}")
        print(f"Total Return:        {r['total_return']:>15,.2f}%")

        print(f"\n{'-'*60}")
        print("TRADE STATISTICS")
        print(f"{'-'*60}")
        print(f"Total Trades:        {r['total_trades']:>15}")
        print(f"Winning Trades:      {r['winning_trades']:>15}")
        print(f"Losing Trades:       {r['losing_trades']:>15}")
        print(f"Win Rate:            {r['win_rate']:>15,.2f}%")

        print(f"\n{'-'*60}")
        print("P&L ANALYSIS")
        print(f"{'-'*60}")
        print(f"Average Win:         ${r['average_win']:>15,.2f}")
        print(f"Average Loss:        ${r['average_loss']:>15,.2f}")
        print(f"Profit Factor:       {r['profit_factor']:>15,.2f}")

        if 'largest_win' in r:
            print(f"Largest Win:         ${r['largest_win']:>15,.2f}")
            print(f"Largest Loss:        ${r['largest_loss']:>15,.2f}")

        print(f"\n{'-'*60}")
        print("RISK METRICS")
        print(f"{'-'*60}")
        print(f"Max Drawdown:        {r['max_drawdown']:>15,.2f}%")
        print(f"Sharpe Ratio:        {r['sharpe_ratio']:>15,.2f}")
        print(f"Sortino Ratio:       {r['sortino_ratio']:>15,.2f}")

        if 'average_trade_duration' in r:
            print(f"Avg Trade Duration:  {r['average_trade_duration']:>15}")

        print(f"\n{'='*60}\n")

    def get_results(self) -> Optional[Dict[str, Any]]:
        """Get backtest results."""
        return self.results

    def get_equity_curve(self) -> Optional[pd.DataFrame]:
        """Get equity curve."""
        return self.results['equity_curve'] if self.results else None

    def get_trades(self) -> Optional[pd.DataFrame]:
        """Get trades DataFrame."""
        return self.results['trades'] if self.results else None
