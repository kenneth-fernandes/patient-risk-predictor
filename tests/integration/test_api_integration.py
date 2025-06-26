"""Integration tests for the complete API workflow."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from src.api.app import app


@pytest.fixture
def integration_client():
    """Test client for integration tests."""
    return TestClient(app)


@pytest.fixture
def mock_trained_model():
    """Mock a trained model for integration testing."""
    model = Mock()
    model.predict.return_value = np.array([1])
    model.predict_proba.return_value = np.array([[0.3, 0.7]])
    return model


class TestAPIIntegration:
    """Integration tests for API functionality."""
    
    def test_health_check_integration(self, integration_client):
        """Test health check endpoint integration."""
        response = integration_client.get("/")
        
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Should return either model loaded or not loaded message
        message = response.json()["message"]
        assert message in ["Model is up and running", "Model not loaded"]
    
    def test_predict_endpoint_integration_with_mock_model(self, integration_client, sample_patient_data):
        """Test prediction endpoint with mocked model."""
        with patch('src.api.app.model') as mock_model:
            mock_model.__bool__ = Mock(return_value=True)
            mock_model.predict.return_value = np.array([1])
            
            response = integration_client.post("/predict", json=sample_patient_data)
            
            assert response.status_code == 200
            result = response.json()
            assert "risk" in result
            assert result["risk"] in [0, 1]
    
    def test_openapi_schema_integration(self, integration_client):
        """Test that OpenAPI schema is properly generated."""
        response = integration_client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Check basic OpenAPI structure
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Check our endpoints are documented
        assert "/" in schema["paths"]
        assert "/predict" in schema["paths"]
        
        # Check predict endpoint has proper schema
        predict_schema = schema["paths"]["/predict"]["post"]
        assert "requestBody" in predict_schema
        assert "responses" in predict_schema
    
    def test_docs_endpoint_integration(self, integration_client):
        """Test that documentation endpoint works."""
        response = integration_client.get("/docs")
        assert response.status_code == 200
    
    def test_multiple_predictions_integration(self, integration_client, sample_patient_data):
        """Test multiple consecutive predictions."""
        with patch('src.api.app.model') as mock_model:
            mock_model.__bool__ = Mock(return_value=True)
            
            # Test multiple predictions with different outcomes
            test_cases = [
                (np.array([0]), 0),
                (np.array([1]), 1),
                (np.array([0]), 0),
                (np.array([1]), 1),
            ]
            
            for model_output, expected_risk in test_cases:
                mock_model.predict.return_value = model_output
                
                response = integration_client.post("/predict", json=sample_patient_data)
                
                assert response.status_code == 200
                assert response.json()["risk"] == expected_risk
    
    def test_error_handling_integration(self, integration_client):
        """Test error handling across the API."""
        # Test with completely invalid JSON
        response = integration_client.post("/predict", json="invalid")
        assert response.status_code == 422
        
        # Test with missing fields
        response = integration_client.post("/predict", json={"age": 50})
        assert response.status_code == 422
        
        # Test with invalid field types
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
            "thal": 1.0
        }
        response = integration_client.post("/predict", json=invalid_data)
        assert response.status_code == 422


class TestConfigIntegration:
    """Integration tests for configuration loading."""
    
    def test_config_loading_integration(self):
        """Test that config loads without errors."""
        from src.config import config
        
        # Config should be accessible
        assert hasattr(config, 'api_host')
        assert hasattr(config, 'api_port')
        assert hasattr(config, 'mlflow_tracking_uri')
        assert hasattr(config, 'environment')
        
        # Values should be reasonable
        assert isinstance(config.api_port, int)
        assert config.api_port > 0
        assert isinstance(config.api_host, str)
        assert len(config.api_host) > 0


class TestMLUtilsIntegration:
    """Integration tests for ML utilities."""
    
    @patch('src.api.ml_utils.mlflow')
    def test_get_latest_model_path_integration(self, mock_mlflow):
        """Test model path retrieval integration."""
        from src.api.ml_utils import get_latest_model_path
        
        # Setup mock MLflow
        mock_experiment = Mock()
        mock_experiment.experiment_id = "test_123"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment
        
        mock_runs = pd.DataFrame({
            'run_id': ['latest_run'],
            'start_time': ['2024-01-01']
        })
        mock_mlflow.search_runs.return_value = mock_runs
        
        result = get_latest_model_path()
        
        # Should return a valid model URI format
        assert result.startswith("runs:/")
        assert "/" in result
        
        # Should have called MLflow methods
        mock_mlflow.set_tracking_uri.assert_called_once()
        mock_mlflow.get_experiment_by_name.assert_called_once()
        mock_mlflow.search_runs.assert_called_once()


class TestDataFlowIntegration:
    """Test data flow through the entire application."""
    
    def test_patient_data_transformation_flow(self, integration_client):
        """Test data transformation from request to model input."""
        patient_input = {
            "age": 63,  # Will be converted to float
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
        }
        
        with patch('src.api.app.model') as mock_model:
            mock_model.__bool__ = Mock(return_value=True)
            mock_model.predict.return_value = np.array([1])
            
            response = integration_client.post("/predict", json=patient_input)
            
            assert response.status_code == 200
            
            # Verify model was called with DataFrame
            mock_model.predict.assert_called_once()
            call_args = mock_model.predict.call_args[0][0]
            assert isinstance(call_args, pd.DataFrame)
            
            # Verify data types are correct (should be float)
            for column in call_args.columns:
                assert call_args[column].dtype in ['float64', 'int64']
    
    def test_end_to_end_realistic_scenario(self, integration_client):
        """Test end-to-end scenario with realistic data."""
        # Simulate a realistic patient case
        high_risk_patient = {
            "age": 67.0,
            "sex": 1.0,     # Male
            "cp": 3.0,      # Asymptomatic chest pain
            "trestbps": 160.0,  # High blood pressure
            "chol": 286.0,  # High cholesterol
            "fbs": 0.0,
            "restecg": 0.0,
            "thalach": 108.0,   # Low max heart rate
            "exang": 1.0,   # Exercise induced angina
            "oldpeak": 1.5,
            "slope": 1.0,
            "ca": 3.0,      # Multiple vessels
            "thal": 2.0
        }
        
        low_risk_patient = {
            "age": 29.0,
            "sex": 0.0,     # Female
            "cp": 0.0,      # Typical angina
            "trestbps": 110.0,  # Normal blood pressure
            "chol": 180.0,  # Normal cholesterol
            "fbs": 0.0,
            "restecg": 0.0,
            "thalach": 180.0,   # High max heart rate
            "exang": 0.0,   # No exercise induced angina
            "oldpeak": 0.0,
            "slope": 2.0,
            "ca": 0.0,      # No vessels
            "thal": 2.0
        }
        
        with patch('src.api.app.model') as mock_model:
            mock_model.__bool__ = Mock(return_value=True)
            
            # Test high risk patient
            mock_model.predict.return_value = np.array([1])
            response = integration_client.post("/predict", json=high_risk_patient)
            assert response.status_code == 200
            assert response.json()["risk"] == 1
            
            # Test low risk patient
            mock_model.predict.return_value = np.array([0])
            response = integration_client.post("/predict", json=low_risk_patient)
            assert response.status_code == 200
            assert response.json()["risk"] == 0


class TestErrorRecoveryIntegration:
    """Test error recovery and resilience."""
    
    def test_model_failure_recovery(self, integration_client, sample_patient_data):
        """Test that API handles model failures gracefully."""
        with patch('src.api.app.model') as mock_model:
            mock_model.__bool__ = Mock(return_value=True)
            
            # Simulate different types of model failures
            failure_scenarios = [
                ValueError("Invalid input shape"),
                RuntimeError("Model prediction failed"),
                Exception("Unexpected error")
            ]
            
            for error in failure_scenarios:
                mock_model.predict.side_effect = error
                
                response = integration_client.post("/predict", json=sample_patient_data)
                
                # Should return 500 with error details
                assert response.status_code == 500
                assert "Prediction failed" in response.json()["detail"]
    
    def test_concurrent_requests_integration(self, integration_client, sample_patient_data):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        with patch('src.api.app.model') as mock_model:
            mock_model.__bool__ = Mock(return_value=True)
            mock_model.predict.return_value = np.array([1])
            
            # Use a lock to ensure model is called for each request
            call_count = 0
            lock = threading.Lock()
            
            def mock_predict(*args, **kwargs):
                nonlocal call_count
                with lock:
                    call_count += 1
                return np.array([1])
            
            mock_model.predict.side_effect = mock_predict
            
            # Make multiple concurrent requests
            def make_request():
                return integration_client.post("/predict", json=sample_patient_data)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in futures]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                assert response.json()["risk"] == 1
            
            # Model should have been called for each request
            assert call_count == 10