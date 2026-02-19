# core/signal_engine.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from core.config import config
from core.logger import logger
from core.risk import RiskManager

class SignalEngine:
    """Generate trading signals from model predictions + risk management."""
    
    def __init__(self, risk_manager: RiskManager = None):
        self.risk_manager = risk_manager or RiskManager()
        logger.info("SignalEngine initialized")
    
    def generate_signals(self, predictions: Dict[str, Dict[str, float]], 
                        current_prices: Dict[str, float],
                        market_data: Dict[str, pd.DataFrame] = None) -> Dict[str, dict]:
        """
        Generate trading signals from ensemble predictions.
        
        Args:
            predictions: {symbol: {model_name: prediction_value}}
            current_prices: {symbol: current_price}
            market_data: Optional market context for filtering
        
        Returns:
            {symbol: {action: 'buy'/'sell'/'hold', confidence: float, size: float}}
        """
        signals = {}
        
        # Check if daily loss limit exceeded
        if self.risk_manager.check_daily_loss_limit():
            logger.warning("Daily loss limit exceeded - no new signals")
            return {symbol: {'action': 'hold', 'confidence': 0.0} for symbol in predictions}
        
        for symbol, model_preds in predictions.items():
            if symbol not in current_prices:
                continue
            
            # Aggregate predictions
            avg_pred = np.mean(list(model_preds.values()))
            confidence = self._calculate_confidence(model_preds)
            
            # Check risk management rules
            current_price = current_prices[symbol]
            
            # Check stop-loss
            if self.risk_manager.check_stop_loss(symbol, current_price):
                signals[symbol] = {
                    'action': 'sell',
                    'reason': 'stop_loss',
                    'confidence': 1.0,
                    'price': current_price
                }
                continue
            
            # Check take-profit
            if self.risk_manager.check_take_profit(symbol, current_price):
                signals[symbol] = {
                    'action': 'sell',
                    'reason': 'take_profit',
                    'confidence': 1.0,
                    'price': current_price
                }
                continue
            
            # Generate signal based on prediction
            action = self._determine_action(avg_pred, confidence)
            position_size = 0.0
            
            if action == 'buy':
                position_size = self.risk_manager.calculate_position_size(
                    symbol, current_price, confidence
                )
            
            signals[symbol] = {
                'action': action,
                'confidence': confidence,
                'prediction': avg_pred,
                'price': current_price,
                'size': position_size
            }
            
            logger.debug(f"Signal for {symbol}: {action} | Confidence: {confidence:.2f}")
        
        return signals
    
    def _calculate_confidence(self, model_preds: Dict[str, float]) -> float:
        """Calculate confidence score from model agreement."""
        if not model_preds:
            return 0.0
        
        # Confidence = 1 - std_dev of predictions
        predictions = list(model_preds.values())
        if len(predictions) == 1:
            return abs(predictions[0])
        
        std_dev = np.std(predictions)
        avg = np.mean(predictions)
        confidence = min(abs(avg) * (1 - std_dev), 1.0)
        return max(confidence, 0.0)
    
    def _determine_action(self, prediction: float, confidence: float, 
                         threshold: float = 0.02) -> str:
        """Determine trading action based on prediction and confidence."""
        # Only act if confidence is above minimum threshold
        if confidence < 0.5:
            return 'hold'
        
        # Prediction > threshold = buy signal
        if prediction > threshold:
            return 'buy'
        # Prediction < -threshold = sell signal
        elif prediction < -threshold:
            return 'sell'
        else:
            return 'hold'
    
    def execute_signals(self, signals: Dict[str, dict]) -> List[dict]:
        """Execute trading signals (paper or live)."""
        executions = []
        
        for symbol, signal in signals.items():
            action = signal['action']
            price = signal['price']
            
            if action == 'buy' and signal.get('size', 0) > 0:
                self.risk_manager.open_position(
                    symbol, price, signal['size'], direction='long'
                )
                executions.append({
                    'symbol': symbol,
                    'action': action,
                    'price': price,
                    'size': signal['size'],
                    'status': 'executed'
                })
                logger.info(f"Executed BUY: {symbol} {signal['size']:.4f} @ ${price}")
            
            elif action == 'sell' and symbol in self.risk_manager.open_positions:
                pnl = self.risk_manager.close_position(symbol, price)
                executions.append({
                    'symbol': symbol,
                    'action': action,
                    'price': price,
                    'pnl': pnl,
                    'status': 'executed'
                })
                logger.info(f"Executed SELL: {symbol} @ ${price} | P&L: ${pnl:.2f}")
        
        return executions
