"""
Cluster networking modules for PipelineApp.

This package provides functionality for remote cluster operations,
SSH handling, and distributed processing tasks.

Modules:
    expected_runtime: Runtime estimation for cluster tasks
    preprocessing: Remote preprocessing operations
    ssh_handling: SSH connection and command execution
    tracking: Remote tracking task management
    utils: Utility functions for cluster operations
"""

__version__ = "1.0.0"
__author__ = "Vojtech Brejtr"

# Import cluster networking components - avoiding circular imports
# Users should import specific modules as needed