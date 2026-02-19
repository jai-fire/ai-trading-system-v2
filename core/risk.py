# core/risk.py
import pandas as pd
from typing import Dict, Optional
from core.config import config
from core.logger import logger

class RiskManager:
    """Enforce risk rules: position sizing, stop-loss, take-profit, daily limits."""
    
    def __init__(self, capital: float = None):
        self.capital = capital or config.CAPITAL
        self.daily_pnl = 0.0
        self.open_positions: Dict[str, dict] = {}
        logger.info(f"RiskManager initialized with capital: ${self.capital}")
    
    def calculate_position_size(self, symbol: str, price: float, confidence: float = 1.0) -> float:
        """Calculate position size based on risk percentage and confidence."""
        risk_amount = self.capital * config.MAX_POSITION_SIZE * confidence
        position_size = risk_amount / price
        logger.debug(f"Position size for {symbol}: {position_size:.4f} @ ${price}")
        return position_size
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """Check if stop-loss is triggered."""
        if symbol not in self.open_positions:
            return False
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        stop_loss = entry_price * (1 - config.STOP_LOSS_PCT)
        
        if current_price <= stop_loss:
            logger.warning(f"Stop-loss triggered for {symbol}: ${current_price} <= ${stop_loss}")
            return True
        return False
    
    def check_take_profit(self, symbol: str, current_price: float) -> bool:
        """Check if take-profit is triggered."""
        if symbol not in self.open_positions:
            return False
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        take_profit = entry_price * (1 + config.TAKE_PROFIT_PCT)
        
        if current_price >= take_profit:
            logger.info(f"Take-profit triggered for {symbol}: ${current_price} >= ${take_profit}")
            return True
        return False
    
    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit is exceeded."""
        daily_loss_limit = -1 * self.capital * config.MAX_DAILY_LOSS
        if self.daily_pnl <= daily_loss_limit:
            logger.error(f"Daily loss limit exceeded: ${self.daily_pnl} <= ${daily_loss_limit}")
            return True
        return False
    
    def open_position(self, symbol: str, entry_price: float, size: float, direction: str = 'long'):
        """Record opened position."""
        self.open_positions[symbol] = {
            'entry_price': entry_price,
            'size': size,
            'direction': direction,
            'value': entry_price * size
        }
        logger.info(f"Opened {direction} position: {symbol} {size:.4f} @ ${entry_price}")
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[float]:
        """Close position and calculate P&L."""
        if symbol not in self.open_positions:
            logger.warning(f"No open position for {symbol}")
            return None
        
        position = self.open_positions.pop(symbol)
        entry_price = position['entry_price']
        size = position['size']
        direction = position['direction']
        
        pnl = (exit_price - entry_price) * size
        if direction == 'short':
            pnl = -pnl
        
        self.daily_pnl += pnl
        self.capital += pnl
        
        logger.info(f"Closed {direction} position: {symbol} {size:.4f} @ ${exit_price} | P&L: ${pnl:.2f}")
        return pnl
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value."""
        total_value = self.capital
        for symbol, position in self.open_positions.items():
            if symbol in current_prices:
                current_value = current_prices[symbol] * position['size']
                total_value += (current_value - position['value'])
        return total_value
    
    def reset_daily_pnl(self):
        """Reset daily P&L counter (call at start of day)."""
        logger.info(f"Resetting daily P&L: ${self.daily_pnl}")
        self.daily_pnl = 0.0
