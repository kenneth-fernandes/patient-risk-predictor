"""
API Module - FastAPI Patient Risk Prediction Server

This module provides the FastAPI application for patient risk prediction,
including data schemas, model utilities, and prediction endpoints.
"""

from .app import app, health_check, model, predict
from .ml_utils import get_latest_model_path
from .schemas import PatientData

__all__ = [
    "app",
    "health_check",
    "predict",
    "model",
    "PatientData",
    "get_latest_model_path",
]
