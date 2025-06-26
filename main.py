import sys
import uvicorn
from src.config import config

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        # Import and run the training function
        from src.model.train import train_patient_risk_model
        print(f"Training in {config.environment} environment")
        train_patient_risk_model()
    else:
        # Use config defaults, allow command-line overrides
        host = config.api_host
        port = config.api_port
        
        if len(sys.argv) > 1:
            host = sys.argv[1]
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print(f"Invalid port '{sys.argv[2]}', using default {config.api_port}.")
        
        print(f"Starting API in {config.environment} environment on {host}:{port}")
        
        from src.api.app import app as fastapi_app
        uvicorn.run(fastapi_app, host=host, port=port, log_level="info")
else:
    # For ASGI servers
    from src.api.app import app as fastapi_app

    application = fastapi_app