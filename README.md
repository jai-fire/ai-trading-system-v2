# AI Trading System V2 - Production-Ready Edition

**Advanced AI Cryptocurrency Trading Platform with REST API, Real-World Error Handling, and Enterprise Features**

## 🎯 What's New in V2?

### ✨ Major Improvements Over V1

**Performance & Scalability:**
- ✅ Async/await support for concurrent operations
- ✅ Connection pooling for database efficiency
- ✅ Redis caching for market data
- ✅ Message queue for event processing
- ✅ Rate limiting & throttling

**Production Features:**
- ✅ REST API with FastAPI (async framework)
- ✅ Comprehensive error handling & validation
- ✅ Request/Response logging & monitoring
- ✅ Health checks & system diagnostics
- ✅ Metrics collection (Prometheus)
- ✅ Database migrations with Alembic

**Security & Reliability:**
- ✅ Input validation & sanitization
- ✅ SQL injection protection (ORM + parameterized queries)
- ✅ API authentication (API keys, JWT tokens)
- ✅ Rate limiting per API key
- ✅ Encrypted credential storage
- ✅ Audit logging for all transactions

**Developer Experience:**
- ✅ Comprehensive unit tests
- ✅ Integration tests
- ✅ API documentation (OpenAPI/Swagger)
- ✅ Development vs Production config separation
- ✅ Logging with rotating file handlers
- ✅ Debug mode with enhanced error messages

**Deployment & Operations:**
- ✅ Kubernetes manifests
- ✅ Health check endpoints
- ✅ Graceful shutdown
- ✅ Environment-based configuration
- ✅ Database backup automation
- ✅ Alert system integration ready

## 📦 System Architecture

```
ai-trading-system-v2/
├── src/
│   ├── api/                    # REST API endpoints
│   │   ├── routes/             # Endpoint definitions
│   │   ├── models/             # Pydantic request/response models
│   │   └── middleware/         # Auth, logging, error handling
│   ├── core/                   # Core business logic
│   │   ├── trading.py          # Trading engine
│   │   ├── ml_models.py        # ML model management
│   │   └── strategies.py       # Trading strategies
│   ├── data/                   # Data layer
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── database.py         # Database connections
│   │   └── cache.py            # Redis cache
│   ├── indicators/             # Technical analysis
│   ├── utils/                  # Utilities & helpers
│   ├── config.py               # Configuration management
│   └── main.py                 # FastAPI app initialization
├── tests/                      # Comprehensive test suite
├── migrations/                 # Database migrations
├── kubernetes/                 # K8s manifests
├── docker-compose.yml          # Local development
├── Dockerfile                  # Production image
└── requirements.txt            # Dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 13+ (if not using Docker)
- Redis 6+ (if not using Docker)

### Installation

```bash
# Clone repository
git clone https://github.com/jai-fire/ai-trading-system-v2.git
cd ai-trading-system-v2

# Option 1: Docker (Recommended)
docker-compose up -d

# Option 2: Local setup
pip install -r requirements.txt
export DATABASE_URL=postgresql://user:pass@localhost:5432/trading
export REDIS_URL=redis://localhost:6379
python -m src.main
```

### Access Services

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Dashboard:** http://localhost:8050
- **Metrics:** http://localhost:9090

## 🔑 API Endpoints

### Authentication
```bash
POST /api/v1/auth/login
POST /api/v1/auth/refresh
```

### Trading
```bash
GET  /api/v1/trading/status
POST /api/v1/trading/start
POST /api/v1/trading/stop
GET  /api/v1/trades/history
```

### Market Data
```bash
GET /api/v1/market/price/{symbol}
GET /api/v1/market/indicators/{symbol}
GET /api/v1/market/candles/{symbol}
```

### Account
```bash
GET /api/v1/account/balance
GET /api/v1/account/portfolio
GET /api/v1/account/performance
```

## 📊 Database Schema

**Improvements:**
- Proper indexing for query performance
- Foreign key constraints
- Data validation at DB level
- Audit timestamps (created_at, updated_at)
- Soft deletes where applicable
- Partitioning support for large tables

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_trading.py -v

# Integration tests
pytest tests/integration/ -v
```

## 🔐 Security

- ✅ API key rotation support
- ✅ Rate limiting (100 requests/minute)
- ✅ CORS configuration
- ✅ HTTPS in production
- ✅ Secrets management (environment variables)
- ✅ Dependency scanning
- ✅ Security headers

## 📈 Monitoring & Logging

- Prometheus metrics
- ELK stack integration ready
- Structured logging (JSON)
- Request tracing (correlation IDs)
- Performance monitoring
- Alert thresholds

## 🐳 Docker Deployment

```bash
# Build image
docker build -t ai-trading-v2:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale worker=3
```

## ☸️ Kubernetes

```bash
# Deploy to K8s
kubectl apply -f kubernetes/

# Check pods
kubectl get pods

# View logs
kubectl logs -f deployment/trading-api
```

## 📝 Configuration

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@db:5432/trading

# Redis
REDIS_URL=redis://cache:6379

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Trading
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
OPENAI_API_KEY=your_key

# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/name`
5. Submit pull request

## 📄 License

MIT License - See LICENSE file

## ⚠️ Disclaimer

This software is provided AS-IS for educational purposes. Cryptocurrency trading involves risk. Always:
- Test thoroughly with small amounts first
- Use stop losses
- Monitor your trades
- Never risk money you can't afford to lose

## 📞 Support & Documentation

- **API Docs:** http://localhost:8000/docs
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Documentation:** /docs folder
