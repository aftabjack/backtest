"""
Portfolio and position management for backtesting.
Tracks trades, positions, and account balance.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PositionType(Enum):
    """Position types."""
    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(Enum):
    """Order types."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


@dataclass
class Trade:
    """Represents a single trade."""
    entry_time: datetime
    exit_time: Optional[datetime] = None
    position_type: PositionType = PositionType.LONG
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: float = 0.0
    commission: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0
    status: str = "OPEN"  # OPEN, CLOSED

    def close_trade(self, exit_time: datetime, exit_price: float, commission: float = 0.0):
        """Close the trade and calculate P&L."""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.status = "CLOSED"

        if self.position_type == PositionType.LONG:
            self.pnl = (exit_price - self.entry_price) * self.quantity - self.commission - commission
        else:  # SHORT
            self.pnl = (self.entry_price - exit_price) * self.quantity - self.commission - commission

        self.commission += commission

        if self.entry_price > 0:
            if self.position_type == PositionType.LONG:
                self.pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100
            else:
                self.pnl_percent = ((self.entry_price - exit_price) / self.entry_price) * 100

    def is_winner(self) -> bool:
        """Check if trade is profitable."""
        return self.pnl > 0

    def to_dict(self) -> dict:
        """Convert trade to dictionary."""
        return {
            'entry_time': self.entry_time,
            'exit_time': self.exit_time,
            'position_type': self.position_type.value,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'commission': self.commission,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'status': self.status
        }


@dataclass
class Position:
    """Represents current position."""
    position_type: PositionType
    entry_time: datetime
    entry_price: float
    quantity: float
    current_price: float = 0.0

    def update_price(self, price: float):
        """Update current price."""
        self.current_price = price

    def unrealized_pnl(self) -> float:
        """Calculate unrealized P&L."""
        if self.position_type == PositionType.LONG:
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity

    def unrealized_pnl_percent(self) -> float:
        """Calculate unrealized P&L percentage."""
        if self.entry_price == 0:
            return 0.0

        if self.position_type == PositionType.LONG:
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.current_price) / self.entry_price) * 100


class Portfolio:
    """
    Portfolio manager for backtesting.
    Tracks balance, positions, and trades.
    """

    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,  # 0.1%
        position_size: float = 1.0,  # Fraction of capital per trade
        allow_short: bool = False
    ):
        """
        Initialize portfolio.

        Args:
            initial_capital: Starting capital
            commission_rate: Commission rate (default: 0.1%)
            position_size: Position size as fraction of capital (default: 1.0 = 100%)
            allow_short: Allow short positions
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.position_size = position_size
        self.allow_short = allow_short

        # Portfolio state
        self.cash = initial_capital
        self.equity = initial_capital
        self.current_position: Optional[Position] = None
        self.trades: List[Trade] = []

        # Tracking
        self.equity_curve = []
        self.timestamps = []

    def open_position(
        self,
        timestamp: datetime,
        price: float,
        position_type: PositionType = PositionType.LONG,
        quantity: Optional[float] = None
    ) -> bool:
        """
        Open a new position.

        Args:
            timestamp: Entry timestamp
            price: Entry price
            position_type: LONG or SHORT
            quantity: Position quantity (if None, calculated from position_size)

        Returns:
            True if position opened successfully
        """
        if self.current_position is not None:
            return False

        if position_type == PositionType.SHORT and not self.allow_short:
            return False

        # Calculate quantity (accounting for commission)
        if quantity is None:
            # Calculate max position value including commission
            # position_value * (1 + commission_rate) = cash * position_size
            # position_value = (cash * position_size) / (1 + commission_rate)
            available_for_position = self.cash * self.position_size
            position_value = available_for_position / (1 + self.commission_rate)
            quantity = position_value / price

        # Calculate commission
        commission = quantity * price * self.commission_rate

        # Check if sufficient funds
        required_capital = quantity * price + commission
        if required_capital > self.cash:
            return False

        # Open position
        self.current_position = Position(
            position_type=position_type,
            entry_time=timestamp,
            entry_price=price,
            quantity=quantity,
            current_price=price
        )

        # Update cash
        self.cash -= required_capital

        # Create trade
        trade = Trade(
            entry_time=timestamp,
            position_type=position_type,
            entry_price=price,
            quantity=quantity,
            commission=commission,
            status="OPEN"
        )
        self.trades.append(trade)

        return True

    def close_position(self, timestamp: datetime, price: float) -> bool:
        """
        Close current position.

        Args:
            timestamp: Exit timestamp
            price: Exit price

        Returns:
            True if position closed successfully
        """
        if self.current_position is None:
            return False

        # Calculate commission
        commission = self.current_position.quantity * price * self.commission_rate

        # Close trade
        if self.trades and self.trades[-1].status == "OPEN":
            self.trades[-1].close_trade(timestamp, price, commission)

            # Update cash
            if self.current_position.position_type == PositionType.LONG:
                self.cash += self.current_position.quantity * price - commission
            else:  # SHORT
                pnl = (self.current_position.entry_price - price) * self.current_position.quantity
                self.cash += self.current_position.quantity * self.current_position.entry_price + pnl - commission

        # Clear position
        self.current_position = None

        return True

    def update(self, timestamp: datetime, price: float):
        """
        Update portfolio with current market price.

        Args:
            timestamp: Current timestamp
            price: Current market price
        """
        # Update position price
        if self.current_position is not None:
            self.current_position.update_price(price)
            unrealized_pnl = self.current_position.unrealized_pnl()
            self.equity = self.cash + unrealized_pnl + (self.current_position.quantity * price)
        else:
            self.equity = self.cash

        # Record equity curve
        self.equity_curve.append(self.equity)
        self.timestamps.append(timestamp)

    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get equity curve as DataFrame.

        Returns:
            DataFrame with timestamp and equity
        """
        return pd.DataFrame({
            'timestamp': self.timestamps,
            'equity': self.equity_curve
        }).set_index('timestamp')

    def get_trades_df(self) -> pd.DataFrame:
        """
        Get all trades as DataFrame.

        Returns:
            DataFrame with trade history
        """
        if not self.trades:
            return pd.DataFrame()

        return pd.DataFrame([trade.to_dict() for trade in self.trades])

    def get_closed_trades(self) -> List[Trade]:
        """Get list of closed trades."""
        return [t for t in self.trades if t.status == "CLOSED"]

    def get_open_trades(self) -> List[Trade]:
        """Get list of open trades."""
        return [t for t in self.trades if t.status == "OPEN"]

    def total_trades(self) -> int:
        """Get total number of trades."""
        return len(self.get_closed_trades())

    def winning_trades(self) -> int:
        """Get number of winning trades."""
        return sum(1 for t in self.get_closed_trades() if t.is_winner())

    def losing_trades(self) -> int:
        """Get number of losing trades."""
        return sum(1 for t in self.get_closed_trades() if not t.is_winner())

    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        total = self.total_trades()
        if total == 0:
            return 0.0
        return (self.winning_trades() / total) * 100

    def total_pnl(self) -> float:
        """Calculate total profit/loss."""
        return sum(t.pnl for t in self.get_closed_trades())

    def total_return(self) -> float:
        """Calculate total return percentage."""
        if self.initial_capital == 0:
            return 0.0
        return ((self.equity - self.initial_capital) / self.initial_capital) * 100

    def average_win(self) -> float:
        """Calculate average winning trade."""
        winners = [t.pnl for t in self.get_closed_trades() if t.is_winner()]
        return np.mean(winners) if winners else 0.0

    def average_loss(self) -> float:
        """Calculate average losing trade."""
        losers = [t.pnl for t in self.get_closed_trades() if not t.is_winner()]
        return np.mean(losers) if losers else 0.0

    def profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum(t.pnl for t in self.get_closed_trades() if t.is_winner())
        gross_loss = abs(sum(t.pnl for t in self.get_closed_trades() if not t.is_winner()))

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def reset(self):
        """Reset portfolio to initial state."""
        self.cash = self.initial_capital
        self.equity = self.initial_capital
        self.current_position = None
        self.trades = []
        self.equity_curve = []
        self.timestamps = []
