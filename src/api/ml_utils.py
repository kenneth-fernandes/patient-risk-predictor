import mlflow
from src.config import config


def get_latest_model_path(
    experiment_name=None, model_name=None
):
    """
    Find the latest model from the MLflow tracking server.
    """
    # Use config defaults if not provided
    experiment_name = experiment_name or config.experiment_name
    model_name = model_name or config.model_name
    
    # Set MLflow tracking URI based on environment
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    print(f"Using MLflow URI: {config.mlflow_tracking_uri} (environment: {config.environment})")
    
    try:
        # Get experiment by name
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            raise ValueError(f"Experiment '{experiment_name}' not found")
        
        # Search for runs in the experiment, ordered by start_time descending
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=1
        )
        
        if runs.empty:
            raise FileNotFoundError("No runs found in experiment")
        
        latest_run_id = runs.iloc[0]['run_id']
        model_uri = f"runs:/{latest_run_id}/{model_name}"
        
        return model_uri
        
    except Exception as e:
        raise FileNotFoundError(f"Failed to get latest model: {str(e)}")
