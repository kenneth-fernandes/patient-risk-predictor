"""
Patient Risk Predictor - Medical Risk Assessment System

A machine learning application for predicting patient medical risk using
Random Forest classification with MLflow tracking and FastAPI server.
"""

__version__ = "1.0.0"
__author__ = "Kenneth Fernandes"

from . import api, model

__all__ = [
    "api",
    "model",
    "__version__",
    "__author__",
]
