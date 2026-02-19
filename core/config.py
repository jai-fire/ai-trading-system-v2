# core/config.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseSettings, validator

class Config(BaseSettings):
    """Central configuration manager using environment variables + YAML."""
    
    # Data Settings
    SYMBOLS: list = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    TIMEFRAMES: list = ["1h", "4h", "1d"]
    EXCHANGE: str = "binance"
    DATA_DIR: Path = Path("data/")
    
    # Model Settings
    LSTM_LOOKBACK: int = 60
    LSTM_EPOCHS: int = 100
    LSTM_BATCH_SIZE: int = 32
    GBM_ESTIMATORS: int = 200
    ENSEMBLE_WEIGHTS: Dict[str, float] = {"lstm": 0.5, "gbm": 0.5}
    
    # Risk Management
    MAX_POSITION_SIZE: float = 0.02  # 2% of portfolio
    STOP_LOSS_PCT: float = 0.02
    TAKE_PROFIT_PCT: float = 0.05
    MAX_DAILY_LOSS: float = 0.05  # 5% max daily loss
    
    # Trading Settings
    CAPITAL: float = 10000.0
    TRADING_MODE: str = "paper"  # paper or live
    LOOKBACK_DAYS: int = 365
    
    # LLM Settings
    LLM_MODEL: str = "llama-3.2-1b"  # or any offline model
    LLM_MAX_TOKENS: int = 500
    LLM_TEMP: float = 0.7
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # API Keys (optional for live trading)
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs/")
    
    # S3 Settings (optional)
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator('DATA_DIR', 'LOG_DIR', pre=True)
    def ensure_path(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def load_from_yaml(cls, yaml_path: str = "config.yaml"):
        """Load configuration from YAML file."""
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        return cls()
    
    def save_to_yaml(self, yaml_path: str = "config.yaml"):
        """Save current configuration to YAML file."""
        config_dict = self.dict()
        # Convert Path objects to strings
        for key, value in config_dict.items():
            if isinstance(value, Path):
                config_dict[key] = str(value)
        with open(yaml_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)

# Global config instance
config = Config.load_from_yaml()
