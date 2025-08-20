"""
Logging configuration for the Video Tracking Application.
"""

import logging
import logging.handlers

from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, creates default log in app directory
        console_output: Whether to output logs to console
        max_file_size: Maximum size of log file before rotation (bytes)
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("PipelineApp")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        # Create default log file in application directory
        app_dir = Path(__file__).parent.parent
        logs_dir = app_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        log_file = str(logs_dir / "pipeline_app.log")
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "PipelineApp") -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the logger (typically module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize default logging configuration
_default_logger = None

def init_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> None:
    """
    Initialize the default logging configuration for the application.
    
    Args:
        log_level: Logging level
        log_file: Optional custom log file path
        console_output: Whether to output to console
    """
    global _default_logger
    _default_logger = setup_logging(log_level, log_file, console_output)


def get_default_logger() -> logging.Logger:
    """
    Get the default application logger.
    
    Returns:
        Default logger instance
    """
    global _default_logger
    if _default_logger is None:
        init_logging()
    assert _default_logger is not None  # Help type checker
    return _default_logger
