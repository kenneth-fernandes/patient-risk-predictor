# Simple ML Training with MLflow - Patient Risk Prediction Model
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo

from src.config import config

from ..utils.logging_config import get_logger, setup_application_logging

# Setup logging for training module
setup_application_logging()
logger = get_logger(__name__)


def preprocess_features(features):
    """
    Preprocess features by converting integer columns to float64
    to handle potential missing values
    """
    logger.debug(
        "Starting feature preprocessing",
        extra={
            "event": "preprocessing_start",
            "original_shape": features.shape,
            "original_dtypes": dict(features.dtypes),
        },
    )

    # Convert all integer columns to float64
    int_columns = features.select_dtypes(include=["int64"]).columns.tolist()

    for column in int_columns:
        features[column] = features[column].astype("float64")

    logger.debug(
        "Feature preprocessing completed",
        extra={
            "event": "preprocessing_complete",
            "converted_columns": int_columns,
            "final_shape": features.shape,
            "final_dtypes": dict(features.dtypes),
        },
    )

    return features


def train_patient_risk_model(n_estimators=100, test_size=0.2, random_state=42):
    """
    Train a Random Forest model for patient risk prediction using MLflow tracking.

    Args:
        n_estimators (int): Number of trees in the random forest
        test_size (float): Proportion of dataset to include in the test split
        random_state (int): Random state for reproducibility

    Returns:
        tuple: (trained model, accuracy score)
    """
    logger.info(
        "Starting model training",
        extra={
            "event": "training_start",
            "n_estimators": n_estimators,
            "test_size": test_size,
            "random_state": random_state,
            "environment": config.environment,
        },
    )

    try:
        # Fetch UCI heart disease dataset (id=45)
        logger.info("Fetching UCI heart disease dataset", extra={"dataset_id": 45})
        dataset = fetch_ucirepo(id=45)

        logger.info(
            "Dataset loaded successfully",
            extra={
                "features_shape": dataset.data.features.shape,
                "targets_shape": dataset.data.targets.shape,
                "feature_names": list(dataset.data.features.columns),
            },
        )

        # Prepare and preprocess features
        x_features = preprocess_features(dataset.data.features)
        y = (
            dataset.data.targets.values.ravel()
        )  # Target: presence of medical condition (1) or not (0)

        # Create train/test splits for model evaluation
        logger.info("Creating train/test splits")
        x_train, x_test, y_train, y_test = train_test_split(
            x_features, y, test_size=test_size, random_state=random_state
        )

        logger.info(
            "Data split completed",
            extra={
                "train_shape": x_train.shape,
                "test_shape": x_test.shape,
                "train_positive_rate": float(y_train.mean()),
                "test_positive_rate": float(y_test.mean()),
            },
        )

        # Set MLflow tracking URI and experiment based on environment
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        mlflow.set_experiment(config.experiment_name)

        logger.info(
            "MLflow configuration set",
            extra={
                "mlflow_uri": config.mlflow_tracking_uri,
                "experiment_name": config.experiment_name,
                "model_name": config.model_name,
            },
        )

        # Start MLflow run to track parameters, metrics, and model
        with mlflow.start_run() as run:
            logger.info("Started MLflow run", extra={"run_id": run.info.run_id})

            # Initialize and train Random Forest model
            logger.info("Initializing Random Forest model")
            model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)

            logger.info("Training model...")
            model.fit(x_train, y_train)

            # Make predictions and calculate accuracy
            logger.info("Making predictions on test set")
            y_pred = model.predict(x_test)
            acc = accuracy_score(y_test, y_pred)

            logger.info(
                "Model evaluation completed",
                extra={
                    "accuracy": acc,
                    "test_samples": len(y_test),
                    "correct_predictions": int((y_pred == y_test).sum()),
                },
            )

            # Create model signature and example input for MLflow
            logger.debug("Creating MLflow model signature")
            signature = mlflow.models.infer_signature(x_train, y_train)
            input_example = x_train.iloc[:5]  # First 5 rows as example input

            # Log model parameters, metrics, and artifacts to MLflow
            logger.info("Logging model to MLflow")
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("test_size", test_size)
            mlflow.log_param("random_state", random_state)
            mlflow.log_metric("accuracy", acc)

            mlflow.sklearn.log_model(
                model, name=config.model_name, signature=signature, input_example=input_example
            )

            logger.info(
                "Model training completed successfully",
                extra={
                    "event": "training_success",
                    "final_accuracy": acc,
                    "run_id": run.info.run_id,
                    "model_name": config.model_name,
                    "n_estimators": n_estimators,
                },
            )

            return model, acc

    except Exception as e:
        logger.error(
            "Model training failed",
            extra={
                "event": "training_error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "n_estimators": n_estimators,
                "test_size": test_size,
                "random_state": random_state,
            },
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    # Execute training when script is run directly
    model, accuracy = train_patient_risk_model()
