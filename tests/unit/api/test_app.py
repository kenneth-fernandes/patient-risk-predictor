"""Tests for FastAPI application module."""

from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api.app import app, health_check, predict


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_model_loaded():
    """Mock a successfully loaded model."""
    mock_model = Mock()
    mock_model.predict.return_value = np.array([1])
    return mock_model


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check_with_model(self, client):
        """Test health check when model is loaded."""
        with patch("src.api.app.model") as mock_model:
            with patch("src.api.app.get_model", return_value=mock_model):
                response = client.get("/")

                assert response.status_code == 200
                assert response.json() == {
                    "message": "Model is up and running",
                    "status": "healthy",
                    "model_loaded": True,
                }

    def test_health_check_without_model(self, client):
        """Test health check when model is not loaded."""
        with patch("src.api.app.model", None):
            with patch("src.api.app.get_model", return_value=None):
                response = client.get("/")

                assert response.status_code == 200
                assert response.json() == {
                    "message": "Model not loaded",
                    "status": "unhealthy",
                    "model_loaded": False,
                }

    def test_health_check_function_directly(self):
        """Test health_check function directly."""
        with patch("src.api.app.model") as mock_model:
            with patch("src.api.app.get_model", return_value=mock_model):
                result = health_check()
                assert result == {
                    "message": "Model is up and running",
                    "status": "healthy",
                    "model_loaded": True,
                }

        with patch("src.api.app.model", None):
            with patch("src.api.app.get_model", return_value=None):
                result = health_check()
                assert result == {
                    "message": "Model not loaded",
                    "status": "unhealthy",
                    "model_loaded": False,
                }


class TestPredictEndpoint:
    """Test prediction endpoint."""

    def test_predict_success(self, client, sample_patient_data):
        """Test successful prediction."""
        with patch("src.api.app.model") as mock_model:
            mock_model.predict.return_value = np.array([1])
            with patch("src.api.app.get_model", return_value=mock_model):
                response = client.post("/predict", json=sample_patient_data)

                assert response.status_code == 200
                assert response.json() == {"risk": 1, "risk_level": "high"}

                # Verify model was called with correct data
                mock_model.predict.assert_called_once()
                call_args = mock_model.predict.call_args[0][0]
                assert isinstance(call_args, pd.DataFrame)
                assert len(call_args) == 1  # Single prediction

    def test_predict_model_not_loaded(self, client, sample_patient_data):
        """Test prediction when model is not loaded."""
        with patch("src.api.app.model", None):
            with patch("src.api.app.get_model", return_value=None):
                response = client.post("/predict", json=sample_patient_data)

                assert response.status_code == 503
                assert "Model not loaded" in response.json()["detail"]

    def test_predict_invalid_input_missing_fields(self, client):
        """Test prediction with missing required fields."""
        incomplete_data = {
            "age": 63.0,
            "sex": 1.0
            # Missing other required fields
        }

        response = client.post("/predict", json=incomplete_data)

        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()

    def test_predict_invalid_input_wrong_types(self, client):
        """Test prediction with wrong data types."""
        invalid_data = {
            "age": "not_a_number",
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

        response = client.post("/predict", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_predict_model_prediction_error(self, client, sample_patient_data):
        """Test handling of model prediction errors."""
        with patch("src.api.app.model") as mock_model:
            mock_model.predict.side_effect = Exception("Model prediction failed")
            with patch("src.api.app.get_model", return_value=mock_model):
                response = client.post("/predict", json=sample_patient_data)

                assert response.status_code == 500
                assert "Prediction failed" in response.json()["detail"]
                assert "Model prediction failed" in response.json()["detail"]

    def test_predict_dataframe_conversion(self, client, sample_patient_data):
        """Test that input data is correctly converted to DataFrame."""
        with patch("src.api.app.model") as mock_model:
            mock_model.predict.return_value = np.array([0])
            with patch("src.api.app.get_model", return_value=mock_model):
                with patch("src.api.app.pd.DataFrame") as mock_dataframe:
                    mock_df_instance = Mock()
                    mock_dataframe.return_value = mock_df_instance
                    mock_model.predict.return_value = np.array([0])

                    client.post("/predict", json=sample_patient_data)

                    # Verify DataFrame was created with correct data
                    mock_dataframe.assert_called_once_with([sample_patient_data])
                    mock_model.predict.assert_called_once_with(mock_df_instance)

    def test_predict_different_risk_values(self, client, sample_patient_data):
        """Test prediction with different risk values."""
        test_cases = [
            (np.array([0]), 0, "low"),
            (np.array([1]), 1, "high"),
            (np.array([0.0]), 0, "low"),
            (np.array([1.0]), 1, "high"),
        ]

        for model_output, expected_risk, expected_level in test_cases:
            with patch("src.api.app.model") as mock_model:
                mock_model.predict.return_value = model_output
                with patch("src.api.app.get_model", return_value=mock_model):
                    response = client.post("/predict", json=sample_patient_data)

                    assert response.status_code == 200
                    assert response.json() == {"risk": expected_risk, "risk_level": expected_level}

    def test_predict_function_directly(self, sample_patient_data):
        """Test predict function directly."""
        from src.api.schemas import PatientData

        patient_data = PatientData(**sample_patient_data)

        with patch("src.api.app.model") as mock_model:
            mock_model.predict.return_value = np.array([1])
            with patch("src.api.app.get_model", return_value=mock_model):
                result = predict(patient_data)

                assert result == {"risk": 1, "risk_level": "high"}
                mock_model.predict.assert_called_once()

    def test_predict_function_no_model(self, sample_patient_data):
        """Test predict function when model is None."""
        from src.api.schemas import PatientData

        patient_data = PatientData(**sample_patient_data)

        with patch("src.api.app.model", None):
            with patch("src.api.app.get_model", return_value=None):
                with pytest.raises(HTTPException) as exc_info:
                    predict(patient_data)

                assert exc_info.value.status_code == 503
                assert "Model not loaded" in str(exc_info.value.detail)


class TestAppConfiguration:
    """Test FastAPI app configuration."""

    def test_app_title(self):
        """Test that app has correct title."""
        assert app.title == "Patient Risk Predictor"

    def test_app_endpoints_exist(self, client):
        """Test that required endpoints exist."""
        # Check health endpoint
        response = client.get("/")
        assert response.status_code == 200

        # Check predict endpoint (even if it fails due to validation)
        response = client.post("/predict", json={})
        assert response.status_code in [422, 503]  # Validation error or service unavailable

    def test_app_openapi_docs(self, client):
        """Test that OpenAPI documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/openapi.json")
        assert response.status_code == 200


class TestModelLoading:
    """Test model loading behavior."""

    def test_model_loading_success_simulation(self):
        """Test successful model loading simulation."""
        with patch("src.api.ml_utils.get_latest_model_path") as mock_get_path:
            with patch("src.api.ml_utils.mlflow.sklearn.load_model") as mock_load_model:
                mock_get_path.return_value = "runs:/test_run/test_model"
                mock_model = Mock()
                mock_load_model.return_value = mock_model

                # Test the model loading logic directly
                import mlflow.sklearn

                from src.api.ml_utils import get_latest_model_path

                model_path = get_latest_model_path()
                model = mlflow.sklearn.load_model(model_path)

                assert model is not None
                mock_get_path.assert_called_once()
                mock_load_model.assert_called_once_with("runs:/test_run/test_model")

    def test_model_loading_failure_simulation(self):
        """Test model loading failure simulation."""
        with patch("src.api.ml_utils.get_latest_model_path") as mock_get_path:
            mock_get_path.side_effect = Exception("Model path not found")

            # Test that error handling works
            try:
                from src.api.ml_utils import get_latest_model_path

                get_latest_model_path()
                assert False, "Should have raised exception"
            except Exception as e:
                assert "Model path not found" in str(e)
                mock_get_path.assert_called_once()


class TestEndToEndWorkflow:
    """End-to-end tests for API workflow."""

    def test_complete_prediction_workflow(self, client):
        """Test complete workflow from request to response."""
        # Realistic patient data
        patient_data = {
            "age": 54.0,
            "sex": 1.0,
            "cp": 0.0,
            "trestbps": 124.0,
            "chol": 266.0,
            "fbs": 0.0,
            "restecg": 0.0,
            "thalach": 109.0,
            "exang": 1.0,
            "oldpeak": 2.2,
            "slope": 1.0,
            "ca": 1.0,
            "thal": 3.0,
        }

        with patch("src.api.app.model") as mock_model:
            mock_model.predict.return_value = np.array([1])
            with patch("src.api.app.get_model", return_value=mock_model):
                # Make prediction request
                response = client.post("/predict", json=patient_data)

                # Verify response
                assert response.status_code == 200
                result = response.json()
                assert "risk" in result
                assert "risk_level" in result
                assert result["risk"] in [0, 1]
                assert result["risk_level"] in ["low", "high"]

                # Verify model was called correctly
                mock_model.predict.assert_called_once()

                # Verify input was processed correctly
                call_args = mock_model.predict.call_args[0][0]
                assert isinstance(call_args, pd.DataFrame)
                assert len(call_args) == 1
                assert call_args.iloc[0]["age"] == 54.0
