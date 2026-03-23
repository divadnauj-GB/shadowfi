import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = None, level: str = "INFO", name: str = "qtorchlab"):
    """
    Sets up a global logger for the project.

    Args:
        log_file (str, optional): Path to the log file. If None, no file logging.
        level (str, optional): Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Defaults to 'INFO'.
        name (str, optional): The name of the logger instance. Defaults to 'qtorchlab'.
                              Using a specific name avoids interfering with other libraries' loggers.

    Returns:
        logging.Logger: The configured logger instance.
    """
    # Get the root logger for the specified name
    logger = logging.getLogger(name)

    # Prevent adding handlers multiple times if setup_logging is called more than once
    if logger.handlers:
        for handler in list(logger.handlers):  # Iterate over a copy of the list
            logger.removeHandler(handler)

    logger.setLevel(level.upper())  # Set the overall logging level

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler (always add for visibility)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (optional)
    if log_file:
        log_file_path = Path(log_file)
        log_file_path.parent.mkdir(
            parents=True, exist_ok=True
        )  # Ensure log directory exists
        file_handler = logging.FileHandler(log_file_path, mode="a")  # Append mode
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # This prevents propagation to the root logger, which might have its own handlers
    # and could lead to duplicate messages if basicConfig was used elsewhere.
    logger.propagate = False

    return logger
