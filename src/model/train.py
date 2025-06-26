# Simple ML Training with MLflow - Patient Risk Prediction Model
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from ucimlrepo import fetch_ucirepo
from src.config import config

def preprocess_features(features):
    """
    Preprocess features by converting integer columns to float64
    to handle potential missing values
    """
    # Convert all integer columns to float64
    for column in features.select_dtypes(include=["int64"]).columns:
        features[column] = features[column].astype("float64")
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
    # Fetch UCI heart disease dataset (id=45)
    dataset = fetch_ucirepo(id=45)

    # Prepare and preprocess features
    x_features = preprocess_features(dataset.data.features)
    y = dataset.data.targets.values.ravel()  # Target: presence of medical condition (1) or not (0)

    # Create train/test splits for model evaluation
    x_train, x_test, y_train, y_test = train_test_split(
        x_features, y, test_size=test_size, random_state=random_state
    )

    # Set MLflow tracking URI and experiment based on environment
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment(config.experiment_name)
    print(f"Using MLflow URI: {config.mlflow_tracking_uri} (environment: {config.environment})")

    # Start MLflow run to track parameters, metrics, and model
    with mlflow.start_run():
        # Initialize and train Random Forest model
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        model.fit(x_train, y_train)

        # Make predictions and calculate accuracy
        y_pred = model.predict(x_test)
        acc = accuracy_score(y_test, y_pred)

        # Create model signature and example input for MLflow
        signature = mlflow.models.infer_signature(x_train, y_train)
        input_example = x_train.iloc[:5]  # First 5 rows as example input

        # Log model parameters, metrics, and artifacts to MLflow
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(
            model, 
            name=config.model_name,
            signature=signature,
            input_example=input_example
        )

        print(f"Model trained. Accuracy: {acc:.4f}")
        return model, acc

if __name__ == "__main__":
    # Execute training when script is run directly
    model, accuracy = train_patient_risk_model()
