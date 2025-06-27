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
        str: MLflow model URI

    Raises:
        FileNotFoundError: If no model is found or MLflow access fails
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
            logger.error(
                "MLflow experiment not found",
                extra={"event": "experiment_not_found", "experiment_name": experiment_name},
            )
            raise ValueError(f"Experiment '{experiment_name}' not found")

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
            logger.error(
                "No model runs found in experiment",
                extra={
                    "event": "no_runs_found",
                    "experiment_name": experiment_name,
                    "experiment_id": experiment.experiment_id,
                },
            )
            raise FileNotFoundError("No runs found in experiment")

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
        logger.error(
            "Failed to retrieve model path",
            extra={
                "event": "model_path_error",
                "experiment_name": experiment_name,
                "model_name": model_name,
                "error_type": type(e).__name__,
                "error_message": str(e),
            },
            exc_info=True,
        )
        raise FileNotFoundError(f"Failed to get latest model: {str(e)}")
