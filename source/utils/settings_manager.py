"""
Settings manager for pipeline configuration.
"""

import json
import os
from typing import Dict, Any, Optional

from gui.style import PROJECT_FOLDER


class SettingsManager:
    """Singleton class to manage pipeline settings."""
    
    _instance: Optional['SettingsManager'] = None
    _settings: Dict[str, Any] = {}
    _current_project_path: Optional[str] = None
    
    def __new__(cls) -> 'SettingsManager':
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings for all parameters."""
        return {
            # Arena and general parameters
            "arena_side_cm": 80.0,
            "arena_size_px": 1000,
            "corner_px": 100,
            
            # Body size calculation
            "body_size_mode": "auto",  # "auto" or "manual"
            "manual_body_size": 1.0,
            "body_size_detection_threshold": 0.9,
            "body_size_on_line_threshold": 0.25,
            
            # Head size calculation
            "head_size_mode": "auto",  # "auto" or "manual"
            "manual_head_size": 1.0,
            
            # Trajectory processing
            "trajectory_detection_threshold": 0.6,
            "motion_blur_sigma": 2.0,
            "velocity_threshold": 1.0,
            
            # Thigmotaxis calculation
            "thigmotaxis_bin_count": 25,
            
            # Time-based metrics
            "timebin_minutes": 5.0,
            "max_time_minutes": float('inf'),
            
            # Visualization
            "viz_border_size": 8,
            "viz_start_time": 0.0,
            "viz_end_time": float('inf'),
            
            # Cluster removal
            "cluster_removal_enabled": True,
            "min_cluster_size_seconds": 1.0,
            "cluster_padding_factor": 0.2  # Was cluster_size // 5, now 20% of cluster size
        }
    
    def _load_settings(self, project_path: Optional[str] = None) -> None:
        """Load settings from file."""
        if project_path:
            self._current_project_path = project_path
        
        settings_path = self._get_settings_path()
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                self._settings = self.get_default_settings()
                self._settings.update(loaded_settings)
            except Exception:
                self._settings = self.get_default_settings()
        else:
            self._settings = self.get_default_settings()
    
    def _get_settings_path(self) -> str:
        """Get the path to the settings file."""
        if self._current_project_path and os.path.exists(self._current_project_path):
            # Use project-specific settings
            project_folder = os.path.dirname(self._current_project_path)
            return os.path.join(project_folder, "pipeline_settings.json")
        else:
            # Fall back to global settings in PROJECT_FOLDER
            if not os.path.exists(PROJECT_FOLDER):
                os.makedirs(PROJECT_FOLDER)
            return os.path.join(PROJECT_FOLDER, "pipeline_settings.json")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        return self._settings.get(key, default)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()
    
    def reload_settings(self, project_path: Optional[str] = None) -> None:
        """Reload settings from file."""
        self._load_settings(project_path)
    
    def set_project_path(self, project_path: Optional[str]) -> None:
        """Set the current project path and reload settings."""
        self._current_project_path = project_path
        self._load_settings()
    
    def save_settings(self, settings: Dict[str, Any]) -> None:
        """Save settings to file."""
        self._settings = settings
        settings_path = self._get_settings_path()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        
        with open(settings_path, 'w') as f:
            json.dump(self._settings, f, indent=2)


# Global instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get the global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value."""
    return get_settings_manager().get_setting(key, default)


def reload_settings(project_path: Optional[str] = None) -> None:
    """Reload settings from file."""
    get_settings_manager().reload_settings(project_path)


def set_project_path(project_path: Optional[str]) -> None:
    """Set the current project path for settings."""
    get_settings_manager().set_project_path(project_path)
