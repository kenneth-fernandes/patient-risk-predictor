# ❤️ Patient Risk Predictor

[![CI](https://github.com/kenneth-fernandes/patient-risk-predictor/actions/workflows/ci.yml/badge.svg)](https://github.com/kenneth-fernandes/patient-risk-predictor/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/kenneth-fernandes/patient-risk-predictor/branch/main/graph/badge.svg)](https://codecov.io/gh/kenneth-fernandes/patient-risk-predictor)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A machine learning application for predicting heart disease risk using the UCI Heart Disease dataset. Built with FastAPI, MLflow, and scikit-learn for production-ready deployment.

## ✨ Features

- 🤖 **Machine Learning Model**: Random Forest classifier trained on UCI Heart Disease dataset
- 🚀 **FastAPI REST API**: High-performance asynchronous API server
- 📊 **MLflow Integration**: Experiment tracking and model versioning
- 🐳 **Docker Support**: Full containerization with Docker Compose
- 🔧 **Local Development**: Comprehensive local setup script
- 🏥 **Health Monitoring**: Built-in health checks and monitoring
- 📈 **Model Metrics**: Accuracy tracking and performance monitoring

## 📋 Prerequisites

- **Python 3.11+** 🐍
- **Docker & Docker Compose** 🐳 (for containerized deployment)
- **Git** 📝

## 🚀 Quick Start

### Option 1: Fully Local Deployment (Recommended for Development)

The easiest way to get started! Uses the comprehensive `run_local.sh` script:

```bash
# Clone the repository
git clone <your-repo-url>
cd patient-risk-predictor

# Install Python dependencies
pip install -r requirements.txt

# Run the full workflow (train model + start API)
./scripts/run_local.sh

# Or use specific commands:
./scripts/run_local.sh train           # Train model only
./scripts/run_local.sh api             # Run API only
./scripts/run_local.sh flush           # Clear environment variables
./scripts/run_local.sh cleanup         # Clean corrupted MLflow files
```

#### 🎯 Advanced Local Options

```bash
# Run with MLflow UI server (includes web interface)
./scripts/run_local.sh full --server

# Run with simple file-based MLflow (default)
./scripts/run_local.sh full --simple

# Custom API configuration
./scripts/run_local.sh api-custom

# Get help
./scripts/run_local.sh --help
```

### Option 2: Fully Dockerized Deployment (Production-Ready)

Perfect for production environments with full container orchestration:

```bash
# Clone the repository
git clone <your-repo-url>
cd patient-risk-predictor

# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# Train the model (one-time setup)
docker-compose --profile training up trainer

# View logs
docker-compose logs -f api
docker-compose logs -f mlflow
```

#### 🐳 Docker Architecture

The Docker setup includes:
- **PostgreSQL**: Database for MLflow tracking
- **MLflow Server**: Experiment tracking with web UI
- **API Service**: FastAPI application
- **Trainer Service**: On-demand model training

## 📡 API Endpoints

Once running, your API will be available at `http://localhost:8000`

### Health Check
```bash
curl http://localhost:8000/
```

### Make Predictions
```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }'
```

**Response:**
```json
{
  "risk": 0
}
```

## 📊 MLflow Tracking

### Local Deployment
- **File-based tracking**: Models saved to `./mlruns/`
- **With server**: MLflow UI at `http://localhost:5001`

### Docker Deployment
- **MLflow UI**: `http://localhost:5001`
- **PostgreSQL backend**: Persistent experiment tracking
- **Shared volumes**: Data persistence across container restarts

## 🔧 Development

### Project Structure
```
patient-risk-predictor/
├── 🐳 docker-compose.yml          # Docker orchestration
├── 🐳 Dockerfile                  # Container definition
├── 📝 main.py                     # Application entry point
├── 📦 requirements.txt            # Python dependencies
├── 🔧 scripts/
│   └── run_local.sh               # Local deployment script
├── ⚙️ config/
│   ├── docker.env                 # Docker environment variables
│   └── local.env                  # Local environment variables
└── 📁 src/
    ├── 🌐 api/
    │   ├── app.py                 # FastAPI application
    │   ├── ml_utils.py            # ML utilities
    │   └── schemas.py             # Pydantic models
    ├── ⚙️ config/
    │   └── config.py              # Configuration management
    └── 🤖 model/
        └── train.py               # Model training logic
```

### Environment Variables

**Local Development** (loaded from `config/local.env`):
```bash
ENVIRONMENT=development
MLFLOW_TRACKING_URI=file:///app/mlruns  # or http://localhost:5001
HOST=127.0.0.1
PORT=8000
```

**Docker Deployment** (loaded from `config/docker.env`):
```bash
ENVIRONMENT=production
MLFLOW_TRACKING_URI=http://mlflow:5000
HOST=0.0.0.0
PORT=8000
```

## 🧪 Testing

This project includes comprehensive test coverage with unit tests, integration tests, and CI/CD automation.

### Running Tests Locally

```bash
# Install all dependencies (includes testing tools)
pip install -r requirements.txt

# Run all tests with coverage (default)
./scripts/test.sh
./scripts/test.sh all

# Run only unit tests
./scripts/test.sh unit

# Run only integration tests
./scripts/test.sh integration

# Run tests in parallel (faster if pytest-xdist available)
./scripts/test.sh parallel

# Quick test run (no coverage, faster)
./scripts/test.sh quick

# Generate detailed coverage report
./scripts/test.sh coverage

# Run complete CI test suite
./scripts/test.sh ci

# Get help with test options
./scripts/test.sh help
```

**Test Output Files:**
- **Coverage Reports**: `reports/coverage/htmlcov/index.html` (HTML), `reports/coverage/coverage.xml` (XML)
- **Test Results**: `reports/tests/test-results.xml` (JUnit format)
- **Unit Test Results**: `reports/tests/test-results-unit.xml`
- **Integration Test Results**: `reports/tests/test-results-integration.xml`

### 🔍 Code Quality & Security Checks

```bash
# Run all quality checks (linting, formatting, type checking, security)
./scripts/quality.sh

# Individual quality checks
./scripts/quality.sh lint         # Linting with flake8
./scripts/quality.sh format       # Auto-format code with black + isort
./scripts/quality.sh format-check # Check formatting without fixing
./scripts/quality.sh type-check   # Type checking with mypy
./scripts/quality.sh security     # Security scans (safety + bandit)

# Get help with quality options
./scripts/quality.sh help
```

**Quality Tools Configuration:**
- **flake8**: Max line length 100, ignores E203 (whitespace before ':'), W503 (line break before binary operator)
- **black**: Line length 100, automatic code formatting
- **isort**: Import sorting with black profile compatibility
- **mypy**: Type checking with missing imports ignored for flexibility
- **safety**: Scans for known security vulnerabilities in dependencies
- **bandit**: Static security analysis for common Python security issues

**Quality Reports:**
- **Security Issues**: `reports/security/bandit-report.json` (generated only if issues found)

### 🐍 Dependency Compatibility Testing

**Test dependencies before committing changes:**

```bash
# Quick dependency test (current Python version)
./scripts/test_deps.sh

# Multi-version testing (if multiple Python versions installed)
./scripts/test_deps_multi.sh

# Get help installing multiple Python versions
./scripts/install_python_versions.sh
```

**Benefits:**
- ✅ **Catch conflicts early**: Find dependency issues before CI/CD
- ✅ **Multi-Python support**: Test compatibility across Python 3.11, 3.12
- ✅ **No installations**: Uses `--dry-run` flag to test without installing
- ✅ **Fast feedback**: Get results in seconds instead of waiting for CI

### Test Coverage

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows end-to-end
- **API Tests**: Test FastAPI endpoints and data validation
- **Model Tests**: Test ML model training and prediction
- **Config Tests**: Test configuration management

### GitHub Actions CI/CD

The project includes automated testing on every push and pull request:

- ✅ **Code Quality**: Linting, formatting, type checking
- ✅ **Security Scanning**: Safety and Bandit security checks
- ✅ **Multi-Python Testing**: Tests on Python 3.11, 3.12
- ✅ **Docker Testing**: Container build and functionality tests
<!-- - ✅ **Performance Testing**: Load testing with Locust -->
- ✅ **Coverage Reporting**: Automated coverage tracking

### Test the API
```bash
# Health check
curl http://localhost:8000/

# Sample prediction
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "age": 45,
    "sex": 0,
    "cp": 2,
    "trestbps": 130,
    "chol": 200,
    "fbs": 0,
    "restecg": 1,
    "thalach": 175,
    "exang": 0,
    "oldpeak": 1.0,
    "slope": 1,
    "ca": 0,
    "thal": 2
  }'
```

### Model Parameters
| Parameter | Description | Range |
|-----------|-------------|-------|
| `age` | Age in years | 29-77 |
| `sex` | Sex (1=male, 0=female) | 0-1 |
| `cp` | Chest pain type | 0-3 |
| `trestbps` | Resting blood pressure | 94-200 |
| `chol` | Serum cholesterol | 126-564 |
| `fbs` | Fasting blood sugar > 120 | 0-1 |
| `restecg` | Resting ECG results | 0-2 |
| `thalach` | Max heart rate achieved | 71-202 |
| `exang` | Exercise induced angina | 0-1 |
| `oldpeak` | ST depression | 0.0-6.2 |
| `slope` | Slope of peak exercise ST | 0-2 |
| `ca` | Number of major vessels | 0-4 |
| `thal` | Thalassemia | 0-3 |

## 🚀 Development Scripts

All development commands are organized in shell scripts for easy use:

### **⚡ Quick Reference - Most Common Commands**

**🧪 Before Committing:**
```bash
./scripts/test_deps.sh       # Test dependencies (30 seconds)
./scripts/test.sh quick      # Quick tests (2-3 minutes)
./scripts/quality.sh         # Code quality & security (1-2 minutes)
./scripts/test.sh all        # Full tests with coverage (5-10 minutes)
```

**🛠️ Development:**
```bash
./scripts/commands.sh        # Show all available commands
./scripts/run_local.sh       # Start the application
./scripts/setup.sh dev-setup # Setup development environment
```

**⚡ Quick Start:**
```bash
# 1. Setup
pip install -r requirements.txt
./scripts/setup.sh dev-setup

# 2. Test everything works
./scripts/test_deps.sh
./scripts/test.sh quick

# 3. Run the application
./scripts/run_local.sh
```

### **🎯 All Commands**

### **🛠️ Setup & Installation**
```bash
./scripts/setup.sh install      # Install production dependencies
./scripts/setup.sh install-dev  # Install development dependencies  
./scripts/setup.sh dev-setup    # Complete development environment
```

### **🧪 Testing Options**
```bash
./scripts/test.sh              # Run all tests with coverage (default)
./scripts/test.sh all          # Run all tests with coverage
./scripts/test.sh unit         # Run unit tests only
./scripts/test.sh integration  # Run integration tests only
./scripts/test.sh quick        # Run tests without coverage (faster)
./scripts/test.sh parallel     # Run tests in parallel (if pytest-xdist available)
./scripts/test.sh coverage     # Generate detailed coverage report
./scripts/test.sh ci           # Run complete CI test suite
./scripts/test.sh help         # Show test command help
```

### **🐍 Dependency Testing**
```bash
./scripts/test_deps.sh         # Test dependency compatibility (current Python)
./scripts/test_deps_multi.sh   # Test with multiple Python versions (if available)
./scripts/install_python_versions.sh  # Get instructions for installing multiple Python versions
```

**Why test dependencies?**
- ✅ Catch version conflicts before committing
- ✅ Ensure compatibility across Python 3.11, 3.12
- ✅ Avoid CI/CD failures from dependency issues
- ✅ Test locally without installing packages

**Example workflow:**
```bash
# Before committing dependency changes
./scripts/test_deps.sh          # Quick check with current Python

# For comprehensive testing (optional)
./scripts/test_deps_multi.sh    # Test with multiple Python versions
```

### **🔍 Code Quality & Security**
```bash
./scripts/quality.sh              # Run all quality checks (default)
./scripts/quality.sh all          # Run all quality checks
./scripts/quality.sh lint         # Run linting with flake8
./scripts/quality.sh format       # Format code with black and isort
./scripts/quality.sh format-check # Check code formatting without fixing
./scripts/quality.sh type-check   # Run type checking with mypy
./scripts/quality.sh security     # Run security checks (safety + bandit)
./scripts/quality.sh help         # Show quality command help
```

**Quality Check Tools:**
- **Linting**: flake8 with max line length 100, ignoring E203,W503
- **Formatting**: black (line length 100) + isort (black profile)
- **Type Checking**: mypy with missing imports ignored
- **Security**: safety (vulnerability scanning) + bandit (security linting)

**Quality Reports Generated:**
- **Security Reports**: `reports/security/bandit-report.json` (if issues found)

### **🐳 Docker Utilities**
```bash
./scripts/docker.sh build      # Build Docker image
./scripts/docker.sh run        # Run container
./scripts/docker.sh test       # Test container functionality
./scripts/docker.sh clean      # Clean up Docker resources
```

### **🧹 Maintenance**
```bash
./scripts/clean.sh            # Clean temporary files
./scripts/clean.sh coverage   # Clean coverage reports
./scripts/clean.sh all        # Clean everything
```

## 📁 Project Structure

```
patient-risk-predictor/
├── 📁 config/                 # Configuration files
│   ├── 📁 testing/            # Test configurations (pytest.ini, .safety-project.ini)
│   ├── docker.env             # Docker environment variables
│   └── local.env              # Local development environment variables
├── 📁 reports/                # Generated reports (gitignored)
│   ├── 📁 coverage/           # Coverage reports (XML, HTML, .coverage)
│   ├── 📁 security/           # Security scan results
│   └── 📁 tests/              # Test result files (JUnit XML)
├── 📁 scripts/                # Development utility scripts
├── 📁 src/                    # Source code
│   ├── 📁 api/                # FastAPI application
│   ├── 📁 config/             # Configuration management
│   └── 📁 model/              # ML model training
├── 📁 tests/                  # Comprehensive test suite
│   ├── 📁 unit/               # Unit tests
│   └── 📁 integration/        # Integration tests
├── 📄 main.py                 # Application entry point
├── 📄 requirements.txt        # Python dependencies
└── 📄 docker-compose.yml      # Multi-container orchestration
```

## 🛠️ Troubleshooting

### Common Issues

**🚨 Emergency Commands:**
```bash
./scripts/clean.sh all       # Clean everything
./scripts/docker.sh down     # Stop Docker services
docker system prune -f       # Clean Docker completely
```

**Dependency conflicts:**
```bash
# Test dependencies before making changes
./scripts/test_deps.sh

# If conflicts found, check specific errors
pip install -r requirements.txt --dry-run

# Install specific Python versions for testing
./scripts/install_python_versions.sh
```

**Port conflicts:**
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :5001

# Kill conflicting processes
kill -9 <PID>
```

**MLflow corruption:**
```bash
# Clean up corrupted MLflow directories
./scripts/run_local.sh cleanup
```

**Docker issues:**
```bash
# Clean up Docker resources
docker-compose down -v
docker system prune -f

# Rebuild from scratch
docker-compose up --build --force-recreate
```

**Model not loading:**
```bash
# Retrain the model
./scripts/run_local.sh train

# Or with Docker
docker-compose --profile training up trainer
```

### Logs and Debugging

**Local deployment:**
```bash
# Check MLflow experiments
ls -la mlruns/

# View application logs
tail -f logs/app.log
```

**Docker deployment:**
```bash
# View service logs
docker-compose logs -f api
docker-compose logs -f mlflow
docker-compose logs -f postgres

# Check service health
docker-compose ps
```

## 🛠️ Development Challenges & Solutions

This section documents the key challenges encountered during development and their solutions, providing insights for future maintenance and similar projects.

### Python Version Compatibility Issues

**Challenge**: Supporting multiple Python versions (3.9-3.12) caused numerous dependency conflicts and compatibility issues.

**Issues Encountered**:
- MLflow dependencies conflicted with newer Python versions
- Test mocking patterns broke on Python 3.10+ due to pathlib changes
- Package version conflicts between FastAPI, MLflow, and development tools
- Different behavior in package resolution across Python versions

**Solutions Implemented**:
- **Standardized on Python 3.11+**: Removed support for 3.9 and 3.10 to eliminate compatibility matrix complexity
- **Flexible dependency ranges**: Changed from pinned versions (`==`) to flexible ranges (`>=`) in requirements.txt
- **Fixed test patterns**: Updated mocking to use specific module paths instead of global patches
- **Multi-version testing**: Created scripts to validate dependency compatibility across supported versions

### Dependency Management Complexity

**Challenge**: Complex dependency tree with MLflow, FastAPI, and scientific packages causing conflicts.

**Specific Conflicts Resolved**:
- `packaging` version conflicts between MLflow and other packages
- `pytz` timezone library version mismatches
- `anyio` async library conflicts with FastAPI
- Development tool dependencies interfering with production packages

**Solutions**:
- **Separated concerns**: Created `requirements-prod.txt` for production-only dependencies
- **Dependency testing scripts**: Built automated tools to test compatibility before deployment
- **Version range optimization**: Carefully balanced flexibility with stability in version specifications

### CI/CD Pipeline Reliability

**Challenge**: GitHub Actions workflow failures due to timing issues, resource constraints, and environment inconsistencies.

**Issues Faced**:
- Docker containers failing to start in CI due to insufficient wait times
- Connection resets during health checks in containerized environments
- Memory and resource limitations causing random test failures
- Inconsistent behavior between local and CI environments

**Solutions Developed**:
- **Robust health checking**: Implemented retry loops with proper timeouts for container startup
- **Environment detection**: Added automatic Docker vs local environment detection
- **Enhanced error reporting**: Added comprehensive logging and container inspection in CI
- **Resource optimization**: Disabled performance testing to reduce CI resource usage
- **Proper test isolation**: Used test environment variables to avoid model loading requirements

### Code Quality and Security Standards

**Challenge**: Establishing and maintaining consistent code quality across a growing codebase.

**Quality Issues Addressed**:
- Inconsistent code formatting and import organization
- Missing type annotations causing mypy failures
- Security vulnerabilities in dependencies (17 found during scanning)
- Unused imports and variables cluttering the codebase

**Quality Solutions**:
- **Automated formatting**: Implemented black + isort with consistent configuration
- **Type safety**: Added mypy checking with proper type annotations
- **Security scanning**: Integrated Safety and Bandit for vulnerability detection
- **Lint enforcement**: Configured flake8 with project-specific rules
- **Pre-commit workflow**: Created comprehensive quality check scripts

### Docker Deployment Challenges

**Challenge**: Creating reliable Docker deployments that work consistently across environments.

**Docker Issues Resolved**:
- Model loading failures in production containers
- Port binding and networking configuration problems
- Health check timeouts and startup reliability
- Volume persistence for MLflow data

**Docker Solutions**:
- **Environment-specific configuration**: Automatic detection of Docker vs local environments
- **Proper health checks**: Implemented Docker native health checks with appropriate timeouts
- **Model training workflow**: Created separate training and API containers with shared volumes
- **Security hardening**: Used non-root user and minimal base images

### Testing Infrastructure Complexity

**Challenge**: Building comprehensive test coverage while maintaining fast execution and reliability.

**Testing Challenges**:
- Mock setup complexity for MLflow and FastAPI components
- Test isolation between unit and integration tests
- Database and external service mocking
- Coverage measurement across different test types

**Testing Solutions**:
- **Comprehensive fixtures**: Built reusable test fixtures for common scenarios
- **Proper mocking strategies**: Isolated external dependencies with strategic mocking
- **Separate test configurations**: Different pytest configurations for unit vs integration tests
- **Coverage optimization**: Achieved 94% coverage with focused testing strategies

### Documentation and Developer Experience

**Challenge**: Creating comprehensive documentation that remains current and useful.

**Documentation Challenges**:
- Keeping README synchronized with actual functionality
- Providing clear setup instructions for different environments
- Documenting complex workflows and troubleshooting procedures

**Documentation Solutions**:
- **Comprehensive README**: Detailed setup, usage, and troubleshooting instructions
- **Command reference**: Complete documentation of all development scripts
- **Workflow examples**: Step-by-step examples for common development tasks
- **Troubleshooting guides**: Solutions for common issues and debugging procedures

### Lessons Learned

1. **Start with fewer Python versions**: Supporting a wide range increases complexity exponentially
2. **Invest early in automation**: Quality checks and testing automation save significant time
3. **Environment consistency is critical**: Docker and proper configuration management prevent many issues
4. **Comprehensive logging helps debugging**: Detailed logs and error reporting speed up issue resolution
5. **Documentation pays dividends**: Good documentation reduces support burden and improves adoption

## 🙏 Acknowledgments

- **UCI Machine Learning Repository** for the Heart Disease dataset
- **FastAPI** for the excellent web framework
- **MLflow** for experiment tracking and model management
- **scikit-learn** for machine learning capabilities

---

Made with ❤️ for healthcare innovation 🏥