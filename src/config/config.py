import os
import socket
from pathlib import Path


def load_env_file(env_file_path):
    """Load environment variables from .env file."""
    if not os.path.exists(env_file_path):
        return
    
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Set environment variable (allows override if already set)
                if not os.getenv(key.strip()):
                    os.environ[key.strip()] = value.strip()


def is_running_in_docker():
    """Detect if code is running inside a Docker container."""
    try:
        # Check for Docker-specific files/env vars
        if os.path.exists('/.dockerenv'):
            return True
        if os.getenv('DOCKER_CONTAINER') == 'true':
            return True
        
        # Check if current working directory suggests Docker environment
        cwd = os.getcwd()
        if cwd == '/app':
            return True
            
        # Check if we can resolve Docker service names (only test if other indicators suggest Docker)
        if os.getenv('MLFLOW_TRACKING_URI', '').startswith('http://mlflow:'):
            try:
                socket.gethostbyname('mlflow')
                return True
            except socket.gaierror:
                pass
        return False
    except:
        return False


class Config:
    """Configuration class that auto-detects environment."""
    
    def __init__(self):
        # Load appropriate .env file based on environment detection
        self.is_docker = is_running_in_docker()
        self.is_running_in_docker = self.is_docker  # Alias for test compatibility
        self._load_env_files()
        self._mlflow_uri = None
        
        # Debug info
        print(f"Environment detection: {'docker' if self.is_docker else 'local'}")
        print(f"Current working directory: {os.getcwd()}")
    
    def _load_env_files(self):
        """Load environment variables from appropriate .env files."""
        project_root = Path(__file__).parent.parent.parent
        
        if self.is_docker:
            # Load Docker environment file
            docker_env = project_root / "config" / "docker.env"
            load_env_file(docker_env)
            print(f"Loaded Docker environment from: {docker_env}")
        else:
            # Load local environment file
            local_env = project_root / "config" / "local.env"
            load_env_file(local_env)
            print(f"Loaded local environment from: {local_env}")
        
    @property
    def mlflow_tracking_uri(self):
        """MLflow tracking server URI."""
        if self._mlflow_uri is None:
            # First priority: environment variable from .env file or manual override
            env_uri = os.getenv("MLFLOW_TRACKING_URI")
            if env_uri:
                self._mlflow_uri = env_uri
            elif self.is_docker:
                self._mlflow_uri = "http://mlflow:5000"
            else:
                # Fallback for local execution without .env file
                current_dir = os.getcwd()
                self._mlflow_uri = f"file://{current_dir}/mlruns"
            
            print(f"MLflow URI resolved to: {self._mlflow_uri}")
            
        return self._mlflow_uri
    
    @property
    def api_host(self):
        """API server host."""
        return os.getenv("HOST", "0.0.0.0" if self.is_docker else "127.0.0.1")
    
    @property
    def api_port(self):
        """API server port."""
        return int(os.getenv("PORT", 8000))
    
    @property
    def environment(self):
        """Current environment string."""
        return os.getenv("ENVIRONMENT", "docker" if self.is_docker else "local")
    
    @property
    def log_level(self):
        """Log level for the application."""
        return os.getenv("LOG_LEVEL", "info")
    
    @property
    def workers(self):
        """Number of workers for the application."""
        return int(os.getenv("WORKERS", 2 if self.is_docker else 1))
    
    @property
    def experiment_name(self):
        """MLflow experiment name."""
        return "patient_risk_prediction"
    
    @property
    def model_name(self):
        """Model artifact name."""
        return "random_forest_model"
    


# Global config instance
config = Config()