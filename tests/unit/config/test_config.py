"""Tests for config module."""

import pytest
import os
import tempfile
from unittest.mock import patch, mock_open
from pathlib import Path
import socket

from src.config.config import Config, load_env_file, is_running_in_docker


class TestLoadEnvFile:
    """Test environment file loading functionality."""
    
    def test_load_env_file_success(self, tmp_path):
        """Test successful loading of environment file."""
        env_file = tmp_path / "test.env"
        env_file.write_text("""
# Comment line
TEST_VAR=test_value
ANOTHER_VAR=another_value
COMPLEX_VAR=value with spaces
""")
        
        # Clear any existing env vars
        for var in ['TEST_VAR', 'ANOTHER_VAR', 'COMPLEX_VAR']:
            if var in os.environ:
                del os.environ[var]
        
        load_env_file(str(env_file))
        
        assert os.getenv('TEST_VAR') == 'test_value'
        assert os.getenv('ANOTHER_VAR') == 'another_value'
        assert os.getenv('COMPLEX_VAR') == 'value with spaces'
    
    def test_load_env_file_nonexistent(self):
        """Test loading non-existent file doesn't crash."""
        load_env_file('/nonexistent/file.env')  # Should not raise exception
    
    def test_load_env_file_no_override(self, tmp_path):
        """Test that existing environment variables are not overridden."""
        env_file = tmp_path / "test.env"
        env_file.write_text("EXISTING_VAR=new_value")
        
        os.environ['EXISTING_VAR'] = 'original_value'
        load_env_file(str(env_file))
        
        assert os.getenv('EXISTING_VAR') == 'original_value'
    
    def test_load_env_file_malformed_lines(self, tmp_path):
        """Test handling of malformed lines in env file."""
        env_file = tmp_path / "test.env"
        env_file.write_text("VALID_VAR=valid_value\ninvalid_line_without_equals\nANOTHER_VALID=value\n")
        
        # Clear existing vars
        for var in ['VALID_VAR', 'ANOTHER_VALID']:
            if var in os.environ:
                del os.environ[var]
        
        load_env_file(str(env_file))
        
        assert os.getenv('VALID_VAR') == 'valid_value'
        assert os.getenv('ANOTHER_VALID') == 'value'


class TestIsRunningInDocker:
    """Test Docker environment detection."""
    
    def test_docker_env_file_exists(self):
        """Test detection via .dockerenv file."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            assert is_running_in_docker() is True
    
    def test_docker_container_env_var(self):
        """Test detection via DOCKER_CONTAINER environment variable."""
        with patch.dict(os.environ, {'DOCKER_CONTAINER': 'true'}):
            assert is_running_in_docker() is True
    
    def test_docker_working_directory(self):
        """Test detection via working directory."""
        with patch('os.getcwd', return_value='/app'):
            assert is_running_in_docker() is True
    
    def test_docker_mlflow_hostname_resolution(self):
        """Test detection via MLflow hostname resolution."""
        with patch.dict(os.environ, {'MLFLOW_TRACKING_URI': 'http://mlflow:5000'}):
            with patch('socket.gethostbyname', return_value='172.17.0.2'):
                assert is_running_in_docker() is True
    
    def test_docker_mlflow_hostname_resolution_fails(self):
        """Test when MLflow hostname resolution fails."""
        with patch.dict(os.environ, {'MLFLOW_TRACKING_URI': 'http://mlflow:5000'}):
            with patch('socket.gethostbyname', side_effect=socket.gaierror):
                with patch('os.path.exists', return_value=False):
                    with patch('os.getcwd', return_value='/home/user'):
                        assert is_running_in_docker() is False
    
    def test_not_in_docker(self):
        """Test when not running in Docker."""
        with patch('os.path.exists', return_value=False):
            with patch('os.getcwd', return_value='/home/user/project'):
                with patch.dict(os.environ, {}, clear=True):
                    assert is_running_in_docker() is False
    
    def test_docker_detection_exception(self):
        """Test exception handling in Docker detection."""
        with patch('os.path.exists', side_effect=Exception("Test error")):
            assert is_running_in_docker() is False


class TestConfig:
    """Test Config class functionality."""
    
    def test_config_init_local_environment(self, mock_local_env):
        """Test config initialization in local environment."""
        with patch('src.config.config.load_env_file') as mock_load:
            config = Config()
            assert config.is_docker is False
            mock_load.assert_called_once()
    
    def test_config_init_docker_environment(self, mock_docker_env):
        """Test config initialization in Docker environment."""
        with patch('src.config.config.load_env_file') as mock_load:
            config = Config()
            assert config.is_docker is True
            mock_load.assert_called_once()
    
    def test_mlflow_tracking_uri_from_env(self):
        """Test MLflow URI from environment variable."""
        with patch.dict(os.environ, {'MLFLOW_TRACKING_URI': 'http://test:5000'}):
            config = Config()
            assert config.mlflow_tracking_uri == 'http://test:5000'
    
    def test_mlflow_tracking_uri_docker_default(self, mock_docker_env):
        """Test MLflow URI default for Docker."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                config = Config()
                assert config.mlflow_tracking_uri == 'http://mlflow:5000'
    
    def test_mlflow_tracking_uri_local_default(self, mock_local_env):
        """Test MLflow URI default for local environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                with patch('os.getcwd', return_value='/test/dir'):
                    config = Config()
                    assert config.mlflow_tracking_uri == 'file:///test/dir/mlruns'
    
    def test_api_host_docker(self, mock_docker_env):
        """Test API host in Docker environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                config = Config()
                assert config.api_host == '0.0.0.0'
    
    def test_api_host_local(self, mock_local_env):
        """Test API host in local environment."""
        config = Config()
        assert config.api_host == '127.0.0.1'
    
    def test_api_host_from_env(self):
        """Test API host from environment variable."""
        with patch.dict(os.environ, {'HOST': '192.168.1.100'}):
            config = Config()
            assert config.api_host == '192.168.1.100'
    
    def test_api_port_default(self):
        """Test default API port."""
        config = Config()
        assert config.api_port == 8000
    
    def test_api_port_from_env(self):
        """Test API port from environment variable."""
        with patch.dict(os.environ, {'PORT': '9000'}):
            config = Config()
            assert config.api_port == 9000
    
    def test_environment_docker(self, mock_docker_env):
        """Test environment string in Docker."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                config = Config()
                assert config.environment == 'docker'
    
    def test_environment_local(self, mock_local_env):
        """Test environment string in local."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                config = Config()
                assert config.environment == 'local'
    
    def test_environment_from_env(self):
        """Test environment from environment variable."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'staging'}):
            config = Config()
            assert config.environment == 'staging'
    
    def test_log_level_default(self, mock_local_env):
        """Test default log level."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                config = Config()
                assert config.log_level == 'info'
    
    def test_log_level_from_env(self):
        """Test log level from environment variable."""
        with patch.dict(os.environ, {'LOG_LEVEL': 'debug'}):
            config = Config()
            assert config.log_level == 'debug'
    
    def test_workers_docker(self, mock_docker_env):
        """Test workers count in Docker."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                config = Config()
                assert config.workers == 2
    
    def test_workers_local(self, mock_local_env):
        """Test workers count in local environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.config.load_env_file'):
                config = Config()
                assert config.workers == 1
    
    def test_workers_from_env(self):
        """Test workers from environment variable."""
        with patch.dict(os.environ, {'WORKERS': '4'}):
            config = Config()
            assert config.workers == 4
    
    def test_experiment_name(self):
        """Test MLflow experiment name."""
        config = Config()
        assert config.experiment_name == 'patient_risk_prediction'
    
    def test_model_name(self):
        """Test model artifact name."""
        config = Config()
        assert config.model_name == 'random_forest_model'
    
    def test_mlflow_uri_caching(self):
        """Test that MLflow URI is cached after first access."""
        config = Config()
        first_uri = config.mlflow_tracking_uri
        second_uri = config.mlflow_tracking_uri
        assert first_uri == second_uri
        assert config._mlflow_uri is not None


class TestConfigIntegration:
    """Integration tests for config functionality."""
    
    def test_full_config_load_local(self, test_config_files, mock_local_env):
        """Test full config loading in local environment."""
        with patch('src.config.config.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = test_config_files.parent
            
            config = Config()
            
            # Check that environment was detected as local
            assert config.is_docker is False
            
            # Check that values can be retrieved
            assert isinstance(config.api_port, int)
            assert isinstance(config.api_host, str)
            assert isinstance(config.mlflow_tracking_uri, str)
    
    def test_full_config_load_docker(self, test_config_files, mock_docker_env):
        """Test full config loading in Docker environment."""
        with patch('src.config.config.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = test_config_files.parent
            
            config = Config()
            
            # Check that environment was detected as Docker
            assert config.is_docker is True
            
            # Check that values can be retrieved
            assert isinstance(config.api_port, int)
            assert isinstance(config.api_host, str)
            assert isinstance(config.mlflow_tracking_uri, str)