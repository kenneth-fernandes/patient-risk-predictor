import os
import sys
import uvicorn
from src.config import config
from src.utils.logging_config import get_logger, setup_application_logging

def parse_arguments():
    """Parse command line arguments for log level and other options."""
    args = {
        'command': None,
        'host': None,
        'port': None,
        'log_level': None
    }
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "train":
            args['command'] = 'train'
        elif arg in ["--log-level", "-l"]:
            if i + 1 < len(sys.argv):
                args['log_level'] = sys.argv[i + 1].upper()
                i += 1
            else:
                print("Error: --log-level requires a value (DEBUG, INFO, WARNING, ERROR)")
                sys.exit(1)
        elif arg in ["--help", "-h"]:
            print_usage()
            sys.exit(0)
        elif not args['host'] and not arg.startswith('-'):
            args['host'] = arg
        elif not args['port'] and not arg.startswith('-'):
            try:
                args['port'] = int(arg)
            except ValueError:
                print(f"Error: Invalid port '{arg}', must be a number")
                sys.exit(1)
        i += 1
    
    return args

def print_usage():
    """Print usage information."""
    print("Usage: python main.py [COMMAND] [OPTIONS] [HOST] [PORT]")
    print("")
    print("Commands:")
    print("  train                Train the ML model")
    print("  (no command)         Start the API server")
    print("")
    print("Options:")
    print("  -l, --log-level LEVEL    Set log level (DEBUG, INFO, WARNING, ERROR)")
    print("  -h, --help              Show this help message")
    print("")
    print("Examples:")
    print("  python main.py                           # Start API with default settings")
    print("  python main.py --log-level DEBUG         # Start API with DEBUG logging")
    print("  python main.py train --log-level INFO    # Train model with INFO logging")
    print("  python main.py 0.0.0.0 8080             # Start API on specific host:port")
    print("  python main.py --log-level ERROR 127.0.0.1 8000  # Custom host, port, and log level")

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Set log level from command line if provided
    if args['log_level']:
        os.environ['LOG_LEVEL'] = args['log_level']
        print(f"Log level set to: {args['log_level']}")
    
    # Setup logging after setting environment variables
    setup_application_logging()
    logger = get_logger(__name__)
    
    if args['command'] == 'train':
        # Import and run the training function
        from src.model.train import train_patient_risk_model
        
        logger.info(
            "Starting model training",
            extra={
                "event": "main_training_start",
                "environment": config.environment,
                "command": "train"
            }
        )
        
        try:
            model, accuracy = train_patient_risk_model()
            logger.info(
                "Model training completed from main",
                extra={
                    "event": "main_training_success",
                    "accuracy": accuracy,
                    "model_type": type(model).__name__
                }
            )
        except Exception as e:
            logger.error(
                "Model training failed from main",
                extra={
                    "event": "main_training_error",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                exc_info=True
            )
            sys.exit(1)
    else:
        # Use config defaults, allow command-line overrides
        host = args['host'] if args['host'] else config.api_host
        port = args['port'] if args['port'] else config.api_port
        
        logger.info(
            "Starting API server",
            extra={
                "event": "api_server_start",
                "environment": config.environment,
                "host": host,
                "port": port,
                "log_level": config.log_level
            }
        )
        
        from src.api.app import app as fastapi_app
        uvicorn.run(
            fastapi_app, 
            host=host, 
            port=port, 
            log_level=config.log_level.lower(),
            access_log=True
        )
else:
    # For ASGI servers
    from src.api.app import app as fastapi_app

    application = fastapi_app