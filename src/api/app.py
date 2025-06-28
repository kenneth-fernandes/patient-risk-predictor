import os

import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException

from ..config.config import config
from ..utils.logging_config import get_logger, setup_application_logging
from ..utils.middleware import HealthCheckLoggingMiddleware, LoggingMiddleware
from .ml_utils import get_latest_model_path  # Use relative import
from .schemas import PatientData  # Use relative import

# Setup logging
setup_application_logging()
logger = get_logger(__name__)

# FastAPI app
app = FastAPI(
    title="Patient Risk Predictor",
    description="ML-powered heart disease risk prediction API",
    version="1.0.0",
)

# Add middleware for logging and request tracking
app.add_middleware(LoggingMiddleware)
app.add_middleware(HealthCheckLoggingMiddleware)

# Global model variable
model = None


def load_model():
    """Load model from MLflow."""
    global model
    try:
        logger.info("Starting model loading process")
        model_path = get_latest_model_path()

        if model_path is None:
            logger.info(
                "No trained model found - API will start without model",
                extra={"event": "no_model_available"},
            )
            model = None
            setattr(app, "model", None)
            return model

        logger.info("Loading model from MLflow", extra={"model_path": model_path})
        model = mlflow.sklearn.load_model(model_path)
        setattr(app, "model", model)  # Attach model to app for testing

        logger.info(
            "Model loaded successfully",
            extra={
                "model_path": model_path,
                "model_type": type(model).__name__,
                "event": "model_load_success",
            },
        )
    except Exception as e:
        model = None
        setattr(app, "model", None)  # Attach None to app for testing

        logger.error(
            "Model loading failed",
            extra={
                "event": "model_load_failure",
                "error_type": type(e).__name__,
                "error_message": str(e),
            },
            exc_info=True,
        )
    return model


def get_model():
    """Get the current model instance."""
    return model


# Load model at startup (only if not in test environment)
if os.getenv("ENVIRONMENT") != "test":
    load_model()
else:
    # In test environment, start with no model
    setattr(app, "model", None)


@app.get("/")
def health_check():
    """Health check endpoint to verify API and model status."""
    current_model = get_model()
    is_healthy = current_model is not None

    if is_healthy:
        message = "Model is up and running"
        logger.debug("Health check passed", extra={"event": "health_check_success"})
    else:
        message = "Model not loaded"
        logger.warning(
            "Health check failed - model not loaded", extra={"event": "health_check_failure"}
        )

    return {
        "message": message,
        "status": "healthy" if is_healthy else "unhealthy",
        "model_loaded": is_healthy,
    }


@app.post("/reload-model")
def reload_model():
    """Reload the model from MLflow (useful after training)."""
    logger.info("Model reload requested", extra={"event": "model_reload_request"})
    
    previous_model_status = get_model() is not None
    load_model()
    new_model_status = get_model() is not None
    
    if new_model_status:
        message = "Model reloaded successfully"
        status = "success"
        logger.info("Model reload successful", extra={"event": "model_reload_success"})
    else:
        message = "No trained model found to load"
        status = "no_model_available"
        logger.info("Model reload failed - no model available", extra={"event": "model_reload_no_model"})
    
    return {
        "message": message,
        "status": status,
        "previous_model_loaded": previous_model_status,
        "current_model_loaded": new_model_status,
    }


@app.post("/predict")
def predict(data: PatientData):
    """Predict heart disease risk based on patient data."""
    logger.info(
        "Prediction request received",
        extra={"event": "prediction_request", "input_data": data.model_dump()},
    )

    current_model = get_model()
    
    # Auto-reload behavior only in development/testing environments
    if current_model is None and config.environment in ["development", "test", "local"]:
        logger.info(
            "Development mode: attempting auto-reload", 
            extra={"event": "auto_reload_attempt", "environment": config.environment}
        )
        load_model()
        current_model = get_model()
    
    if current_model is None:
        # Environment-specific error messages
        if config.environment in ["development", "test", "local"]:
            detail = "No model available. Train a model first or call /reload-model to retry."
            log_level = "warning"
        else:
            detail = "Model not loaded. Call /reload-model after training."
            log_level = "error"
        
        if log_level == "warning":
            logger.warning(
                "Prediction failed - no model available",
                extra={
                    "event": "prediction_model_unavailable",
                    "environment": config.environment,
                    "auto_reload_attempted": True
                },
            )
        else:
            logger.error(
                "Prediction failed - no model available",
                extra={
                    "event": "prediction_model_unavailable",
                    "environment": config.environment,
                    "auto_reload_attempted": False
                },
            )
        raise HTTPException(status_code=503, detail=detail)

    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([data.model_dump()])

        logger.debug(
            "Making prediction",
            extra={
                "event": "prediction_processing",
                "input_shape": input_df.shape,
                "model_type": type(current_model).__name__,
            },
        )

        prediction = current_model.predict(input_df)[0]
        risk_score = int(prediction)

        logger.info(
            "Prediction completed successfully",
            extra={
                "event": "prediction_success",
                "risk_score": risk_score,
                "input_features": list(input_df.columns),
            },
        )

        return {"risk": risk_score, "risk_level": "high" if risk_score == 1 else "low"}

    except Exception as e:
        logger.error(
            "Prediction processing failed",
            extra={
                "event": "prediction_error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "input_data": data.model_dump(),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
