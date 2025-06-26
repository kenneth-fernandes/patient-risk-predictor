"""Global test configuration and fixtures."""

import os
import shutil
import tempfile
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["MLFLOW_TRACKING_URI"] = "file:///tmp/test_mlruns"
os.environ["CI"] = os.getenv("CI", "false")


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line("markers", "ci: mark test to run in CI environment")
    config.addinivalue_line("markers", "local: mark test to run only locally")
    config.addinivalue_line("markers", "slow: mark test as slow running")

    # Create test directories
    os.makedirs("/tmp/test_mlruns", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment."""
    ci_env = os.getenv("CI", "false").lower() == "true"

    if ci_env:
        # In CI, skip tests marked as 'local'
        skip_local = pytest.mark.skip(reason="Skipped in CI environment")
        for item in items:
            if "local" in item.keywords:
                item.add_marker(skip_local)
    else:
        # Locally, we can run all tests
        pass


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment for the entire test session."""
    # Ensure test directories exist
    test_dirs = ["/tmp/test_mlruns", "logs", "htmlcov"]

    for directory in test_dirs:
        os.makedirs(directory, exist_ok=True)

    yield

    # Cleanup after all tests
    if os.getenv("CI") == "true":
        # In CI, clean up test artifacts
        import shutil

        for directory in ["/tmp/test_mlruns"]:
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=True)


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "age": 63.0,
        "sex": 1.0,
        "cp": 3.0,
        "trestbps": 145.0,
        "chol": 233.0,
        "fbs": 1.0,
        "restecg": 0.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 2.3,
        "slope": 0.0,
        "ca": 0.0,
        "thal": 1.0,
    }


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing model functions."""
    data = {
        "age": [63, 37, 41, 56, 57],
        "sex": [1, 1, 0, 1, 0],
        "cp": [3, 2, 1, 1, 0],
        "trestbps": [145, 130, 130, 120, 120],
        "chol": [233, 250, 204, 236, 354],
        "fbs": [1, 0, 0, 0, 0],
        "restecg": [0, 1, 0, 1, 1],
        "thalach": [150, 187, 172, 178, 163],
        "exang": [0, 0, 0, 0, 1],
        "oldpeak": [2.3, 3.5, 1.4, 0.8, 0.6],
        "slope": [0, 0, 2, 2, 2],
        "ca": [0, 0, 0, 0, 0],
        "thal": [1, 2, 2, 2, 2],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_targets():
    """Sample target values for testing."""
    return np.array([1, 1, 1, 1, 0])


@pytest.fixture
def mock_model():
    """Mock ML model for testing."""
    model = Mock()
    model.predict.return_value = np.array([1])
    model.predict_proba.return_value = np.array([[0.3, 0.7]])
    return model


@pytest.fixture
def temp_mlflow_dir():
    """Temporary MLflow directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(
        os.environ,
        {
            "HOST": "127.0.0.1",
            "PORT": "8000",
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "debug",
            "WORKERS": "1",
        },
    ):
        yield


@pytest.fixture
def mock_docker_env():
    """Mock Docker environment detection."""
    with patch("src.config.config.is_running_in_docker", return_value=True):
        yield


@pytest.fixture
def mock_local_env():
    """Mock local environment detection."""
    with patch("src.config.config.is_running_in_docker", return_value=False):
        yield


@pytest.fixture
def test_config_files(tmp_path):
    """Create temporary config files for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create test local.env
    local_env = config_dir / "local.env"
    local_env.write_text(
        """
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=info
WORKERS=1
MLFLOW_TRACKING_URI=file:///tmp/mlruns
"""
    )

    # Create test docker.env
    docker_env = config_dir / "docker.env"
    docker_env.write_text(
        """
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
WORKERS=2
MLFLOW_TRACKING_URI=http://mlflow:5000
"""
    )

    return config_dir
