"""
API Module - FastAPI Heart Disease Risk Prediction Server

This module provides the FastAPI application for heart disease risk prediction,
including data schemas, model utilities, and prediction endpoints.
"""

from .app import app, health_check, predict, model
from .schemas import PatientData
from .ml_utils import get_latest_model_path

__all__ = [
    "app",
    "health_check", 
    "predict",
    "model",
    "PatientData",
    "get_latest_model_path",
]