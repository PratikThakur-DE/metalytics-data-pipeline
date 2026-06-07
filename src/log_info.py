import os
import logging
import sys
from datetime import datetime

def setup_logging() -> None:
    """Sets up the logging configuration for the application.
    
    The log messages include timestamps, log levels, and the actual log message.
    """
    log_dir = "logs"
    current_datetime = datetime.now()
    log_file_name = f"app_log_{current_datetime.strftime('%Y-%m-%d_%H')}.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    # Create the log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    stdout_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(stdout_handler)
