#!/bin/bash

echo "AI Trading System V2 - Setup Script"
echo "====================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/raw data/processed
mkdir -p logs
mkdir -p models/saved
mkdir -p core/data core/features core/models core/llm core/backtest core/risk

# Create empty __init__.py files
touch core/__init__.py
touch core/data/__init__.py
touch core/features/__init__.py
touch core/models/__init__.py
touch core/llm/__init__.py
touch core/backtest/__init__.py
touch core/risk/__init__.py

# Copy example config if doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
LLM_API_KEY=your_llm_api_key_here
LLM_PROVIDER=openai
EOF
    echo ".env file created. Please update with your API keys."
fi

# Set permissions
chmod +x cli.py

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Update config.yaml with your preferences"
echo "3. Run: source venv/bin/activate"
echo "4. Run: ./cli.py --help"
echo ""
echo "For Docker:"
echo "  docker-compose up -d"
echo ""
