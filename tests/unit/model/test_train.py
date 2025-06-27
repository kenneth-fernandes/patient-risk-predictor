"""Tests for model training module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from src.model.train import preprocess_features, train_patient_risk_model


class TestPreprocessFeatures:
    """Test feature preprocessing functionality."""

    def test_preprocess_features_converts_int_to_float(self):
        """Test that integer columns are converted to float64."""
        # Create DataFrame with mixed types
        data = pd.DataFrame(
            {
                "int_col": [1, 2, 3, 4, 5],
                "float_col": [1.1, 2.2, 3.3, 4.4, 5.5],
                "str_col": ["a", "b", "c", "d", "e"],
            }
        )

        # Ensure int_col is actually int64
        data["int_col"] = data["int_col"].astype("int64")

        result = preprocess_features(data)  # Function modifies in place

        # Check that int column was converted to float64
        assert result["int_col"].dtype == "float64"
        # Check that float column remains float
        assert result["float_col"].dtype == "float64"
        # Check that string column is unchanged
        assert result["str_col"].dtype == "object"

    def test_preprocess_features_preserves_data(self):
        """Test that data values are preserved during preprocessing."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        data = data.astype("int64")
        expected_values = data.values.astype("float64")

        result = preprocess_features(data)  # Function modifies in place

        # Check that values are preserved but types are converted
        assert result.dtypes["col1"] == "float64"
        assert result.dtypes["col2"] == "float64"
        # Check values are the same
        assert (result.values == expected_values).all()

    def test_preprocess_features_empty_dataframe(self):
        """Test preprocessing with empty DataFrame."""
        data = pd.DataFrame()
        result = preprocess_features(data)
        assert result.empty

    def test_preprocess_features_no_int_columns(self):
        """Test preprocessing when no integer columns exist."""
        data = pd.DataFrame({"float_col": [1.1, 2.2, 3.3], "str_col": ["a", "b", "c"]})

        result = preprocess_features(data)

        # Should return the same DataFrame
        pd.testing.assert_frame_equal(result, data)


class TestTrainPatientRiskModel:
    """Test model training functionality."""

    @patch("src.model.train.fetch_ucirepo")
    @patch("src.model.train.mlflow")
    def test_train_patient_risk_model_success(self, mock_mlflow, mock_fetch):
        """Test successful model training."""
        # Setup mock dataset
        mock_dataset = Mock()
        mock_features = pd.DataFrame(
            {
                "age": [63, 37, 41, 56, 57],
                "sex": [1, 1, 0, 1, 0],
                "cp": [3, 2, 1, 1, 0],
                "trestbps": [145, 130, 130, 120, 120],
                "chol": [233, 250, 204, 236, 354],
            }
        )
        mock_targets = pd.DataFrame({"target": [1, 1, 1, 1, 0]})

        mock_dataset.data.features = mock_features
        mock_dataset.data.targets = mock_targets
        mock_fetch.return_value = mock_dataset

        # Setup MLflow mocks
        mock_mlflow.start_run.return_value.__enter__ = Mock()
        mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=None)
        mock_mlflow.models.infer_signature.return_value = "mock_signature"

        # Run training
        model, accuracy = train_patient_risk_model(n_estimators=10, test_size=0.2)

        # Assertions
        assert isinstance(model, RandomForestClassifier)
        assert isinstance(accuracy, float)
        assert 0.0 <= accuracy <= 1.0

        # Check MLflow calls
        mock_mlflow.set_tracking_uri.assert_called_once()
        mock_mlflow.set_experiment.assert_called_once()
        mock_mlflow.start_run.assert_called_once()
        mock_mlflow.log_param.assert_called()
        mock_mlflow.log_metric.assert_called()
        mock_mlflow.sklearn.log_model.assert_called_once()

    @patch("src.model.train.fetch_ucirepo")
    @patch("src.model.train.mlflow")
    def test_train_with_custom_parameters(self, mock_mlflow, mock_fetch):
        """Test training with custom parameters."""
        # Setup mock dataset
        mock_dataset = Mock()
        mock_features = pd.DataFrame(
            {"age": [63, 37, 41, 56, 57, 44, 52, 34, 29, 67], "sex": [1, 1, 0, 1, 0, 1, 0, 1, 0, 1]}
        )
        mock_targets = pd.DataFrame({"target": [1, 1, 1, 1, 0, 0, 1, 0, 1, 0]})

        mock_dataset.data.features = mock_features
        mock_dataset.data.targets = mock_targets
        mock_fetch.return_value = mock_dataset

        # Setup MLflow mocks
        mock_mlflow.start_run.return_value.__enter__ = Mock()
        mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=None)
        mock_mlflow.models.infer_signature.return_value = "mock_signature"

        # Test with custom parameters
        model, accuracy = train_patient_risk_model(n_estimators=50, test_size=0.3, random_state=123)

        # Check that parameters were logged correctly
        mock_mlflow.log_param.assert_any_call("n_estimators", 50)

        # Check model parameters
        assert model.n_estimators == 50
        assert model.random_state == 123

    @patch("src.model.train.fetch_ucirepo")
    def test_train_dataset_fetch_failure(self, mock_fetch):
        """Test handling of dataset fetch failure."""
        mock_fetch.side_effect = Exception("Dataset fetch failed")

        with pytest.raises(Exception, match="Dataset fetch failed"):
            train_patient_risk_model()

    @patch("src.model.train.fetch_ucirepo")
    @patch("src.model.train.mlflow")
    def test_train_with_preprocessing(self, mock_mlflow, mock_fetch):
        """Test that preprocessing is applied to features."""
        # Setup mock dataset with integer types
        mock_dataset = Mock()
        mock_features = pd.DataFrame({"age": [63, 37, 41, 56, 57], "sex": [1, 1, 0, 1, 0]})
        # Ensure columns are int64
        mock_features = mock_features.astype("int64")
        mock_targets = pd.DataFrame({"target": [1, 1, 1, 1, 0]})

        mock_dataset.data.features = mock_features
        mock_dataset.data.targets = mock_targets
        mock_fetch.return_value = mock_dataset

        # Setup MLflow mocks
        mock_mlflow.start_run.return_value.__enter__ = Mock()
        mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=None)
        mock_mlflow.models.infer_signature.return_value = "mock_signature"

        # Mock preprocess_features to verify it's called
        with patch("src.model.train.preprocess_features") as mock_preprocess:
            mock_preprocess.return_value = mock_features.astype("float64")

            model, accuracy = train_patient_risk_model()

            # Verify preprocessing was called
            mock_preprocess.assert_called_once()

    @patch("src.model.train.fetch_ucirepo")
    @patch("src.model.train.mlflow")
    def test_train_mlflow_logging(self, mock_mlflow, mock_fetch):
        """Test that all MLflow logging calls are made correctly."""
        # Setup mock dataset
        mock_dataset = Mock()
        mock_features = pd.DataFrame(
            {"age": [63, 37, 41, 56, 57, 44, 52, 34], "sex": [1, 1, 0, 1, 0, 1, 0, 1]}
        )
        mock_targets = pd.DataFrame({"target": [1, 1, 1, 1, 0, 0, 1, 0]})

        mock_dataset.data.features = mock_features
        mock_dataset.data.targets = mock_targets
        mock_fetch.return_value = mock_dataset

        # Setup MLflow mocks
        mock_context = Mock()
        mock_mlflow.start_run.return_value = mock_context
        mock_context.__enter__ = Mock(return_value=mock_context)
        mock_context.__exit__ = Mock(return_value=None)
        mock_mlflow.models.infer_signature.return_value = "test_signature"

        # Run training
        model, accuracy = train_patient_risk_model(n_estimators=25)

        # Verify MLflow setup calls
        mock_mlflow.set_tracking_uri.assert_called_once()
        mock_mlflow.set_experiment.assert_called_once_with("patient_risk_prediction")

        # Verify logging calls within the run context
        mock_mlflow.log_param.assert_any_call("n_estimators", 25)
        mock_mlflow.log_param.assert_any_call("test_size", 0.2)  # Default value
        mock_mlflow.log_param.assert_any_call("random_state", 42)  # Default value
        mock_mlflow.log_metric.assert_called_once()
        mock_mlflow.sklearn.log_model.assert_called_once()

        # Check log_model parameters
        log_model_call = mock_mlflow.sklearn.log_model.call_args
        assert log_model_call[0][0] == model  # First positional arg is the model
        assert log_model_call[1]["name"] == "random_forest_model"
        assert log_model_call[1]["signature"] == "test_signature"
        # The new implementation also includes input_example parameter
        assert "input_example" in log_model_call[1]

    @patch("src.model.train.fetch_ucirepo")
    @patch("src.model.train.mlflow")
    def test_train_accuracy_calculation(self, mock_mlflow, mock_fetch):
        """Test accuracy calculation and bounds."""
        # Create a dataset where we can predict the accuracy
        mock_dataset = Mock()
        # Use a simple dataset where all samples are the same class
        mock_features = pd.DataFrame(
            {"feature1": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "feature2": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}
        )
        mock_targets = pd.DataFrame({"target": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]})

        mock_dataset.data.features = mock_features
        mock_dataset.data.targets = mock_targets
        mock_fetch.return_value = mock_dataset

        # Setup MLflow mocks
        mock_mlflow.start_run.return_value.__enter__ = Mock()
        mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=None)
        mock_mlflow.models.infer_signature.return_value = "mock_signature"

        # Run training with a fixed random state for reproducibility
        model, accuracy = train_patient_risk_model(random_state=42)

        # Check that accuracy is within valid bounds
        assert 0.0 <= accuracy <= 1.0

        # Check that accuracy was logged to MLflow
        logged_accuracy = None
        for call in mock_mlflow.log_metric.call_args_list:
            if call[0][0] == "accuracy":
                logged_accuracy = call[0][1]
                break

        assert logged_accuracy == accuracy

    def test_train_patient_risk_model_parameters(self):
        """Test that function accepts all expected parameters."""
        # This test just checks that the function signature is correct
        # We're not actually running it to avoid external dependencies
        import inspect

        sig = inspect.signature(train_patient_risk_model)
        params = list(sig.parameters.keys())

        expected_params = ["n_estimators", "test_size", "random_state"]
        for param in expected_params:
            assert param in params

        # Check default values
        assert sig.parameters["n_estimators"].default == 100
        assert sig.parameters["test_size"].default == 0.2
        assert sig.parameters["random_state"].default == 42


class TestModelTrainingIntegration:
    """Integration tests for model training."""

    @patch("src.model.train.fetch_ucirepo")
    @patch("src.model.train.config")
    def test_config_integration(self, mock_config, mock_fetch):
        """Test that config values are used correctly."""
        # Setup config mock
        mock_config.mlflow_tracking_uri = "file:///test/mlruns"
        mock_config.experiment_name = "test_experiment"
        mock_config.model_name = "test_model"
        mock_config.environment = "test"

        # Setup dataset mock
        mock_dataset = Mock()
        mock_features = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
        mock_targets = pd.DataFrame({"target": [1, 0, 1, 0, 1]})
        mock_dataset.data.features = mock_features
        mock_dataset.data.targets = mock_targets
        mock_fetch.return_value = mock_dataset

        with patch("src.model.train.mlflow") as mock_mlflow:
            mock_mlflow.start_run.return_value.__enter__ = Mock()
            mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=None)
            mock_mlflow.models.infer_signature.return_value = "signature"

            train_patient_risk_model()

            # Verify config values were used
            mock_mlflow.set_tracking_uri.assert_called_with("file:///test/mlruns")
            mock_mlflow.set_experiment.assert_called_with("test_experiment")

            # Check model logging used config
            log_model_call = mock_mlflow.sklearn.log_model.call_args
            assert log_model_call[1]["name"] == "test_model"
