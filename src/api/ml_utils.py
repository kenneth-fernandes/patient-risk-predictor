from pathlib import Path


def get_latest_model_path(
    experiment_id="295239570571117835", model_name="random_forest_model"
):
    """
    Find the latest model path in the MLflow experiment directory.
    """
    mlruns_dir = Path("mlruns") / experiment_id
    if not mlruns_dir.exists():
        raise FileNotFoundError("MLflow runs directory not found.")

    # Check models directory first (preferred MLflow structure)
    models_dir = mlruns_dir / "models"
    if models_dir.exists():
        model_dirs = sorted(
            [d for d in models_dir.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
        if model_dirs:
            return str(model_dirs[0] / "artifacts")
    
    # Fallback: check run directories for artifacts
    runs = sorted(
        [d for d in mlruns_dir.iterdir() if d.is_dir() and d.name != "models"],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    for run in runs:
        model_dir = run / "artifacts" / model_name
        if model_dir.exists():
            return str(model_dir)
    raise FileNotFoundError("No trained model found in mlruns.")
