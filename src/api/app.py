from fastapi import FastAPI, HTTPException
from .schemas import PatientData  # Use relative import
import pandas as pd
import mlflow.sklearn
import os
from .ml_utils import get_latest_model_path  # Use relative import

# FastAPI app
app = FastAPI(title="Heart Disease Risk Predictor")


# Load model from MLflow
try:
    model_path = get_latest_model_path()
    model = mlflow.sklearn.load_model(model_path)
except Exception as e:
    model = None
    print(f"Model loading failed: {e}")


@app.get("/")
def health_check():
    # Return status based on model loading
    return {"message": "Model is up and running" if model else "Model not loaded"}


@app.post("/predict")
def predict(data: PatientData):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please check server logs.")
    
    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([data.model_dump()])
        prediction = model.predict(input_df)[0]
        return {"risk": int(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
