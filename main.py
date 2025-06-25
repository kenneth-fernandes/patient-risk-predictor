import sys
import uvicorn

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        # Import and run the training function
        from src.model.train import train_heart_disease_model

        train_heart_disease_model()
    else:
        # Parse host and port from command-line arguments, with defaults
        host = "0.0.0.0"
        port = 8000
        if len(sys.argv) > 1:
            host = sys.argv[1]
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print(f"Invalid port '{sys.argv[2]}', using default 8000.")
                port = 8000
        from src.api.app import app as fastapi_app

        uvicorn.run(fastapi_app, host=host, port=port, log_level="info")
else:
    # For ASGI servers
    from src.api.app import app as fastapi_app

    application = fastapi_app