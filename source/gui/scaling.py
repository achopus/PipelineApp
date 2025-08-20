"""
Automatic scaling utilities for different screen resolutions.
"""

import sys
from typing import Tuple, Union, Optional
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QRect
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ScalingManager:
    """Manages automatic scaling for different screen resolutions."""
    
    def __init__(self):
        self._base_width = 1920  # Base design width
        self._base_height = 1080  # Base design height
        self._scale_factor = 1.0
        self._font_scale_factor = 1.0
        self._screen_rect: Optional[QRect] = None
        self._calculate_scaling()
    
    def _calculate_scaling(self) -> None:
        """Calculate scaling factors based on current screen resolution."""
        app = QApplication.instance()
        if app is None:
            return
            
        # Get screen geometry using QDesktopWidget (PyQt5 compatible)
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        self._screen_rect = screen_rect
        
        # Calculate scale factors
        width_scale = screen_rect.width() / self._base_width
        height_scale = screen_rect.height() / self._base_height
        
        # Use the smaller scale factor to maintain aspect ratio
        self._scale_factor = min(width_scale, height_scale)
        
        # For very small screens, don't scale down too much
        self._scale_factor = max(self._scale_factor, 0.6)
        
        # For very large screens, don't scale up too much
        self._scale_factor = min(self._scale_factor, 1.5)
        
        # Font scaling should be slightly different to maintain readability
        self._font_scale_factor = max(0.8, min(1.3, self._scale_factor))
        
        if self._screen_rect is not None:
            logger.debug(f"Screen resolution: {self._screen_rect.width()}x{self._screen_rect.height()}")
            logger.debug(f"Scale factor: {self._scale_factor:.2f}")
            logger.debug(f"Font scale factor: {self._font_scale_factor:.2f}")
    
    @property
    def scale_factor(self) -> float:
        """Get the current scale factor."""
        return self._scale_factor
    
    @property
    def font_scale_factor(self) -> float:
        """Get the current font scale factor."""
        return self._font_scale_factor
    
    @property
    def screen_rect(self) -> Optional[QRect]:
        """Get the screen rectangle."""
        return self._screen_rect
    
    def scale_size(self, size: Union[int, Tuple[int, int]]) -> Union[int, Tuple[int, int]]:
        """Scale a size value or tuple."""
        if isinstance(size, tuple):
            return (int(size[0] * self._scale_factor), int(size[1] * self._scale_factor))
        return int(size * self._scale_factor)
    
    def scale_font_size(self, font_size: int) -> int:
        """Scale a font size."""
        return max(8, int(font_size * self._font_scale_factor))
    
    def scale_position(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Scale a position tuple."""
        return (int(pos[0] * self._scale_factor), int(pos[1] * self._scale_factor))
    
    def get_scaled_button_size(self, base_width: int, base_height: int) -> Tuple[int, int]:
        """Get scaled button size."""
        scaled = self.scale_size((base_width, base_height))
        if isinstance(scaled, tuple):
            return scaled
        return (scaled, scaled)  # Fallback, shouldn't happen
    
    def get_optimal_window_size(self) -> Tuple[int, int]:
        """Get optimal window size for current screen."""
        if self._screen_rect is None:
            return (1200, 800)
        
        # Use 90% of screen size for windowed mode
        width = int(self._screen_rect.width() * 0.9)
        height = int(self._screen_rect.height() * 0.9)
        return (width, height)
    
    def should_use_fullscreen(self) -> bool:
        """Determine if fullscreen mode should be used."""
        if self._screen_rect is None:
            return False
        
        # Use fullscreen for smaller screens
        return self._screen_rect.width() < 1600 or self._screen_rect.height() < 900
    
    def get_scaled_stylesheet(self, base_stylesheet: str) -> str:
        """Scale font sizes in a stylesheet."""
        lines = base_stylesheet.split('\n')
        scaled_lines = []
        
        for line in lines:
            if 'font-size:' in line:
                # Extract font size and scale it
                parts = line.split('font-size:')
                if len(parts) == 2:
                    size_part = parts[1].strip()
                    if size_part.endswith('pt;'):
                        try:
                            size = int(size_part[:-3])
                            scaled_size = self.scale_font_size(size)
                            line = parts[0] + f'font-size: {scaled_size}pt;'
                        except ValueError:
                            pass
                    elif size_part.endswith('px;'):
                        try:
                            size = int(size_part[:-3])
                            scaled_size = self.scale_font_size(size)
                            line = parts[0] + f'font-size: {scaled_size}px;'
                        except ValueError:
                            pass
            elif 'padding:' in line and 'px' in line:
                # Scale padding values
                parts = line.split('padding:')
                if len(parts) == 2:
                    padding_part = parts[1].strip()
                    if padding_part.endswith('px;'):
                        try:
                            padding = int(padding_part[:-3])
                            scaled_padding = int(padding * self._scale_factor)
                            line = parts[0] + f'padding: {scaled_padding}px;'
                        except ValueError:
                            pass
            
            scaled_lines.append(line)
        
        return '\n'.join(scaled_lines)


# Global scaling manager instance
_scaling_manager = None


def get_scaling_manager() -> ScalingManager:
    """Get the global scaling manager instance."""
    global _scaling_manager
    if _scaling_manager is None:
        _scaling_manager = ScalingManager()
    return _scaling_manager


def scale_size(size: Union[int, Tuple[int, int]]) -> Union[int, Tuple[int, int]]:
    """Convenience function to scale a size."""
    return get_scaling_manager().scale_size(size)


def scale_font_size(font_size: int) -> int:
    """Convenience function to scale a font size."""
    return get_scaling_manager().scale_font_size(font_size)


def scale_position(pos: Tuple[int, int]) -> Tuple[int, int]:
    """Convenience function to scale a position."""
    return get_scaling_manager().scale_position(pos)
