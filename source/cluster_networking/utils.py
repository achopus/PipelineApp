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
    """
    load_dotenv()
    cluster_base = os.getenv("CLUSTER_BASE_PATH", "/proj/BV_data/")
    
    linux_path = os.path.normpath(windows_path).replace("\\", "/")
    
    # Find TrackingPRC in the path and replace with cluster base
    tracking_index = linux_path.find("TrackingPRC")
    if tracking_index != -1:
        linux_path = cluster_base + linux_path[tracking_index:]
    
    return linux_path
