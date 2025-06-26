"""Tests for ML utilities module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.api.ml_utils import get_latest_model_path


class TestGetLatestModelPath:
    """Test ML utilities functionality."""

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_success(self, mock_config, mock_mlflow):
        """Test successful retrieval of latest model path."""
        # Setup config mocks
        mock_config.experiment_name = "test_experiment"
        mock_config.model_name = "test_model"
        mock_config.mlflow_tracking_uri = "file:///test/mlruns"
        mock_config.environment = "test"

        # Setup MLflow mocks
        mock_experiment = Mock()
        mock_experiment.experiment_id = "123"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        # Mock search_runs to return a DataFrame with runs
        mock_runs = pd.DataFrame(
            {"run_id": ["run_123", "run_456"], "start_time": ["2024-01-02", "2024-01-01"]}
        )
        mock_mlflow.search_runs.return_value = mock_runs

        # Call function
        result = get_latest_model_path()

        # Assertions
        expected_path = "runs:/run_123/test_model"
        assert result == expected_path

        # Verify MLflow calls
        mock_mlflow.set_tracking_uri.assert_called_once_with("file:///test/mlruns")
        mock_mlflow.get_experiment_by_name.assert_called_once_with("test_experiment")
        mock_mlflow.search_runs.assert_called_once_with(
            experiment_ids=["123"], order_by=["start_time DESC"], max_results=1
        )

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_with_custom_params(self, mock_config, mock_mlflow):
        """Test function with custom experiment and model names."""
        # Setup MLflow mocks
        mock_experiment = Mock()
        mock_experiment.experiment_id = "456"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        mock_runs = pd.DataFrame({"run_id": ["custom_run_789"], "start_time": ["2024-01-03"]})
        mock_mlflow.search_runs.return_value = mock_runs

        # Call function with custom parameters
        result = get_latest_model_path(
            experiment_name="custom_experiment", model_name="custom_model"
        )

        # Assertions
        expected_path = "runs:/custom_run_789/custom_model"
        assert result == expected_path

        # Verify correct experiment name was used
        mock_mlflow.get_experiment_by_name.assert_called_once_with("custom_experiment")

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_experiment_not_found(self, mock_config, mock_mlflow):
        """Test handling when experiment is not found."""
        # Setup config mocks
        mock_config.experiment_name = "nonexistent_experiment"
        mock_config.model_name = "test_model"

        # Mock experiment not found
        mock_mlflow.get_experiment_by_name.return_value = None

        # Should raise ValueError
        with pytest.raises(FileNotFoundError, match="Failed to get latest model"):
            get_latest_model_path()

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_no_runs(self, mock_config, mock_mlflow):
        """Test handling when no runs are found in experiment."""
        # Setup config mocks
        mock_config.experiment_name = "empty_experiment"
        mock_config.model_name = "test_model"

        # Setup MLflow mocks
        mock_experiment = Mock()
        mock_experiment.experiment_id = "789"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        # Mock empty search results
        mock_mlflow.search_runs.return_value = pd.DataFrame()

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Failed to get latest model"):
            get_latest_model_path()

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_mlflow_exception(self, mock_config, mock_mlflow):
        """Test handling of MLflow exceptions."""
        # Setup config mocks
        mock_config.experiment_name = "test_experiment"
        mock_config.model_name = "test_model"

        # Mock MLflow exception
        mock_mlflow.get_experiment_by_name.side_effect = Exception("MLflow connection error")

        # Should raise FileNotFoundError with wrapped exception
        with pytest.raises(FileNotFoundError, match="Failed to get latest model"):
            get_latest_model_path()

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_uses_config_defaults(self, mock_config, mock_mlflow):
        """Test that function uses config defaults when no parameters provided."""
        # Setup config mocks
        mock_config.experiment_name = "default_experiment"
        mock_config.model_name = "default_model"
        mock_config.mlflow_tracking_uri = "file:///default/mlruns"
        mock_config.environment = "default"

        # Setup MLflow mocks
        mock_experiment = Mock()
        mock_experiment.experiment_id = "default_123"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        mock_runs = pd.DataFrame({"run_id": ["default_run"], "start_time": ["2024-01-01"]})
        mock_mlflow.search_runs.return_value = mock_runs

        # Call function without parameters
        result = get_latest_model_path()

        # Verify config defaults were used
        mock_mlflow.get_experiment_by_name.assert_called_once_with("default_experiment")
        assert result == "runs:/default_run/default_model"

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_multiple_runs(self, mock_config, mock_mlflow):
        """Test that function returns the most recent run when multiple exist."""
        # Setup config mocks
        mock_config.experiment_name = "multi_run_experiment"
        mock_config.model_name = "test_model"

        # Setup MLflow mocks
        mock_experiment = Mock()
        mock_experiment.experiment_id = "multi_123"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        # Mock multiple runs (should return the first one due to DESC ordering)
        mock_runs = pd.DataFrame(
            {
                "run_id": ["newest_run", "older_run", "oldest_run"],
                "start_time": ["2024-01-03", "2024-01-02", "2024-01-01"],
            }
        )
        mock_mlflow.search_runs.return_value = mock_runs

        result = get_latest_model_path()

        # Should return the newest run (first in DESC order)
        assert result == "runs:/newest_run/test_model"

        # Verify search was limited to 1 result
        mock_mlflow.search_runs.assert_called_once_with(
            experiment_ids=["multi_123"], order_by=["start_time DESC"], max_results=1
        )

    @patch("src.api.ml_utils.mlflow")
    @patch("src.api.ml_utils.config")
    def test_get_latest_model_path_prints_debug_info(self, mock_config, mock_mlflow, capsys):
        """Test that function prints debug information."""
        # Setup config mocks
        mock_config.experiment_name = "debug_experiment"
        mock_config.model_name = "debug_model"
        mock_config.mlflow_tracking_uri = "file:///debug/mlruns"
        mock_config.environment = "debug"

        # Setup MLflow mocks
        mock_experiment = Mock()
        mock_experiment.experiment_id = "debug_123"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        mock_runs = pd.DataFrame({"run_id": ["debug_run"], "start_time": ["2024-01-01"]})
        mock_mlflow.search_runs.return_value = mock_runs

        # Call function
        get_latest_model_path()

        # Check that debug information was printed
        captured = capsys.readouterr()
        assert "Using MLflow URI: file:///debug/mlruns" in captured.out
        assert "environment: debug" in captured.out


class TestMLUtilsIntegration:
    """Integration tests for ML utilities."""

    @patch("src.api.ml_utils.mlflow")
    def test_full_workflow_simulation(self, mock_mlflow):
        """Test a complete workflow simulation."""
        # Mock a complete MLflow setup
        mock_experiment = Mock()
        mock_experiment.experiment_id = "workflow_123"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        # Mock recent runs with realistic data
        mock_runs = pd.DataFrame(
            {
                "run_id": ["workflow_run_latest"],
                "start_time": ["2024-01-15T10:30:00.000Z"],
                "metrics.accuracy": [0.85],
                "params.n_estimators": [100],
            }
        )
        mock_mlflow.search_runs.return_value = mock_runs

        with patch("src.api.ml_utils.config") as mock_config:
            mock_config.experiment_name = "patient_risk_prediction"
            mock_config.model_name = "random_forest_model"
            mock_config.mlflow_tracking_uri = "file:///app/mlruns"
            mock_config.environment = "production"

            result = get_latest_model_path()

            # Verify the complete path is constructed correctly
            assert result == "runs:/workflow_run_latest/random_forest_model"

            # Verify all MLflow interactions
            mock_mlflow.set_tracking_uri.assert_called_once()
            mock_mlflow.get_experiment_by_name.assert_called_once()
            mock_mlflow.search_runs.assert_called_once()
