import os

import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException

from .ml_utils import get_latest_model_path  # Use relative import
from .schemas import PatientData  # Use relative import

# FastAPI app
app = FastAPI(title="Patient Risk Predictor")

# Global model variable
model = None


def load_model():
    """Load model from MLflow."""
    global model
    try:
        model_path = get_latest_model_path()
        model = mlflow.sklearn.load_model(model_path)
        setattr(app, "model", model)  # Attach model to app for testing
        print(f"Model loaded successfully from: {model_path}")
    except Exception as e:
        model = None
        setattr(app, "model", None)  # Attach None to app for testing
        print(f"Model loading failed: {e}")
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
    # Return status based on model loading
    current_model = get_model()
    return {"message": "Model is up and running" if current_model else "Model not loaded"}


@app.post("/predict")
def predict(data: PatientData):
    current_model = get_model()
    if current_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please check server logs.")

    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([data.model_dump()])
        prediction = current_model.predict(input_df)[0]
        return {"risk": int(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
