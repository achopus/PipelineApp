"""
Backend processing modules for PipelineApp cluster operations.

This package provides video processing and pose estimation functionality
designed to run on cluster environments.

Modules:
    extract_pose: DeepLabCut-based pose extraction from videos
    preprocessing: Video perspective transformation and format conversion
"""

__version__ = "1.0.0"
__author__ = "Vojtech Brejtr"

from .extract_pose import extract_pose
from .preprocessing import VideoPreprocessor

__all__ = [
    "extract_pose",
    "VideoPreprocessor",
]
