"""
Utility functions for cluster networking operations.
"""

import os
from dotenv import load_dotenv


def convert_to_linux_path(windows_path: str) -> str:
    """
    Convert a Windows path to a Linux path for cluster operations.
    
    Args:
        windows_path: The Windows file path
        
    Returns:
        str: Converted Linux path for cluster use
        
    Raises:
        ValueError: If the path conversion fails
    """
    if not windows_path:
        raise ValueError("Path cannot be empty")
        
    load_dotenv()
    cluster_base = os.getenv("CLUSTER_BASE_PATH", "/proj/BV_data/")
    
    # Normalize and convert backslashes to forward slashes
    linux_path = os.path.normpath(windows_path).replace("\\", "/")
    
    # Find TrackingPRC in the path and replace with cluster base
    tracking_index = linux_path.find("TrackingPRC")
    if tracking_index != -1:
        linux_path = cluster_base + linux_path[tracking_index:]
    else:
        # If TrackingPRC not found, try to construct a reasonable path
        # Extract the last meaningful part of the path
        path_parts = linux_path.split("/")
        # Look for common project folder patterns
        for i, part in enumerate(path_parts):
            if part in ["Projects", "projects", "data", "Data"]:
                linux_path = cluster_base + "/".join(path_parts[i+1:])
                break
        else:
            # If no known pattern, use the basename
            linux_path = cluster_base + os.path.basename(linux_path)
    
    return linux_path


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists and is accessible.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        bool: True if file exists and is accessible
    """
    try:
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
    except (OSError, TypeError):
        return False


def validate_directory_exists(dir_path: str) -> bool:
    """
    Validate that a directory exists and is accessible.
    
    Args:
        dir_path: Path to the directory to check
        
    Returns:
        bool: True if directory exists and is accessible
    """
    try:
        return os.path.isdir(dir_path) and os.access(dir_path, os.R_OK)
    except (OSError, TypeError):
        return False
