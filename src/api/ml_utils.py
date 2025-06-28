import mlflow

from src.config import config

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


def get_latest_model_path(experiment_name=None, model_name=None):
    """
    Find the latest model from the MLflow tracking server.

    Args:
        experiment_name: Name of the MLflow experiment
        model_name: Name of the model artifact

    Returns:
        str: MLflow model URI, or None if no model exists yet

    Raises:
        FileNotFoundError: If MLflow access fails for technical reasons
    """
    # Use config defaults if not provided
    experiment_name = experiment_name or config.experiment_name
    model_name = model_name or config.model_name

    logger.info(
        "Starting model path retrieval",
        extra={
            "event": "model_path_retrieval_start",
            "experiment_name": experiment_name,
            "model_name": model_name,
            "mlflow_uri": config.mlflow_tracking_uri,
            "environment": config.environment,
        },
    )

    # Set MLflow tracking URI based on environment
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)

    try:
        # Get experiment by name
        logger.debug("Searching for MLflow experiment", extra={"experiment_name": experiment_name})
        experiment = mlflow.get_experiment_by_name(experiment_name)

        if experiment is None:
            logger.info(
                "MLflow experiment not found - no models trained yet",
                extra={"event": "experiment_not_found", "experiment_name": experiment_name},
            )
            return None

        logger.debug(
            "Found MLflow experiment",
            extra={"experiment_id": experiment.experiment_id, "experiment_name": experiment_name},
        )

        # Search for runs in the experiment, ordered by start_time descending
        logger.debug("Searching for latest model run")
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=1
        )

        if runs.empty:
            logger.info(
                "No model runs found in experiment - no models trained yet",
                extra={
                    "event": "no_runs_found",
                    "experiment_name": experiment_name,
                    "experiment_id": experiment.experiment_id,
                },
            )
            return None

        latest_run_id = runs.iloc[0]["run_id"]
        run_start_time = runs.iloc[0]["start_time"]
        model_uri = f"runs:/{latest_run_id}/{model_name}"

        logger.info(
            "Successfully found latest model",
            extra={
                "event": "model_path_found",
                "model_uri": model_uri,
                "run_id": latest_run_id,
                "run_start_time": str(run_start_time),
                "experiment_name": experiment_name,
                "model_name": model_name,
            },
        )

        return model_uri

    except Exception as e:
        # Check if this is a connectivity issue vs. missing data
        if "connection" in str(e).lower() or "network" in str(e).lower():
            logger.error(
                "MLflow connectivity error",
                extra={
                    "event": "mlflow_connection_error",
                    "experiment_name": experiment_name,
                    "model_name": model_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )
            raise FileNotFoundError(f"Failed to connect to MLflow: {str(e)}")
        else:
            logger.info(
                "No models available yet - training required",
                extra={
                    "event": "no_models_available",
                    "experiment_name": experiment_name,
                    "model_name": model_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
            return None
