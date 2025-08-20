"""
Utility modules for PipelineApp.

This package provides common utility functions for logging, configuration,
and other shared functionality across the application.

Modules:
    logging_config: Logging configuration and setup utilities
    settings_manager: Application settings management
"""

__version__ = "1.0.0"
__author__ = "Vojtech Brejtr"

from .logging_config import setup_logging, get_logger, init_logging, get_default_logger

__all__ = [
    "setup_logging",
    "get_logger", 
    "init_logging",
    "get_default_logger",
]
