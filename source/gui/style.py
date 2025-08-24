"""
GUI styling and constants for the Pipeline Application.
"""
from PyQt5.QtGui import QColor


def get_scaled_dark_style() -> str:
    """Get the dark style with scaled font sizes based on screen resolution."""
    # Import here to avoid circular imports
    from gui.scaling import get_scaling_manager
    
    scaling_manager = get_scaling_manager()
    
    base_font_size = scaling_manager.scale_font_size(12)
    small_font_size = scaling_manager.scale_font_size(10)
    medium_font_size = scaling_manager.scale_font_size(11)
    large_font_size = scaling_manager.scale_font_size(14)
    xlarge_font_size = scaling_manager.scale_font_size(15)
    
    base_padding = max(4, int(8 * scaling_manager.scale_factor))
    large_padding = max(6, int(12 * scaling_manager.scale_factor))
    
    return f"""
QApplication {{
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QWidget {{
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-size: {base_font_size}pt;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-weight: 400;
}}

QMainWindow {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #2b2b2b, stop:1 #323232);
}}

QLineEdit, QTextEdit {{
    background-color: #3c3f41;
    border: 2px solid #555;
    border-radius: 6px;
    color: #f0f0f0;
    padding: {base_padding}px {large_padding}px;
    font-size: {medium_font_size}pt;
    selection-background-color: #4a90e2;
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 2px solid #4a90e2;
    background-color: #404244;
}}

QLineEdit:read-only {{
    background-color: #353535;
    color: #d0d0d0;
}}


QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6a6a6a, stop:1 #555);
    border: 2px solid #888;
    border-radius: 8px;
    color: #f0f0f0;
    padding: {base_padding}px {large_padding * 2}px;
    font-size: {medium_font_size}pt;
    font-weight: 500;
    min-height: {int(40 * scaling_manager.scale_factor)}px;
    min-width: {int(120 * scaling_manager.scale_factor)}px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #7a7a7a, stop:1 #666);
    border: 2px solid #999;
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #555, stop:1 #6a6a6a);
    border: 2px solid #777;
}}

QPushButton:disabled {{
    background-color: #404040;
    border: 2px solid #606060;
    color: #808080;
}}

QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4a4a4a, stop:1 #3c3f41);
    color: #f0f0f0;
    border: 1px solid #666;
    padding: {base_padding}px;
    font-weight: bold;
    font-size: {small_font_size}pt;
}}

QTabWidget::pane {{
    background-color: #2b2b2b;
    border: 2px solid #555;
    border-radius: 8px;
    margin-top: 2px;
}}

QTabBar::tab {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #21657E, stop:1 #1a5066);
    padding: {large_padding}px {large_padding * 2}px;
    font-size: {large_font_size}pt;
    font-weight: 600;
    height: {int(25 * scaling_manager.scale_factor)}px;
    min-width: {int(300 * scaling_manager.scale_factor)}px;
    min-height: {int(50 * scaling_manager.scale_factor)}px;
    border: 2px solid #BFFDFF;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 2px;
    color: #f0f0f0;
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #00a8b8, stop:1 #00868B);
    font-size: {xlarge_font_size}pt;
    border: 2px solid #4dd0e1;
    margin-bottom: -2px;
}}

QTabBar::tab:hover:!selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a7a8e, stop:1 #21657E);
}}

QLabel {{
    color: #f0f0f0;
    font-size: {medium_font_size}pt;
    font-weight: 500;
}}

QComboBox {{
    background-color: #3c3f41;
    border: 2px solid #555;
    border-radius: 6px;
    color: #f0f0f0;
    padding: {base_padding}px {large_padding}px;
    font-size: {medium_font_size}pt;
    min-width: {int(100 * scaling_manager.scale_factor)}px;
}}

QComboBox:hover {{
    border: 2px solid #4a90e2;
}}

QComboBox::drop-down {{
    border: none;
    width: {int(20 * scaling_manager.scale_factor)}px;
}}

QComboBox::down-arrow {{
    border: none;
    background: transparent;
}}

QSpinBox {{
    background-color: #3c3f41;
    border: 2px solid #555;
    border-radius: 6px;
    color: #f0f0f0;
    padding: {base_padding}px;
    font-size: {medium_font_size}pt;
}}

QSpinBox:focus {{
    border: 2px solid #4a90e2;
}}

QGroupBox {{
    font-size: {base_font_size}pt;
    font-weight: bold;
    color: #f0f0f0;
    border: 2px solid #555;
    border-radius: 8px;
    margin-top: {int(10 * scaling_manager.scale_factor)}px;
    padding-top: {int(10 * scaling_manager.scale_factor)}px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: {int(10 * scaling_manager.scale_factor)}px;
    padding: 0 {base_padding}px 0 {base_padding}px;
    background-color: #2b2b2b;
}}

QProgressDialog {{
    background-color: #2b2b2b;
    color: #f0f0f0;
}}

QProgressBar {{
    background-color: #3c3f41;
    border: 2px solid #555;
    border-radius: 6px;
    text-align: center;
    font-size: {small_font_size}pt;
    font-weight: bold;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4a90e2, stop:1 #357abd);
    border-radius: 4px;
}}

QMessageBox {{
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-size: {medium_font_size}pt;
}}

QScrollBar:vertical {{
    background-color: #3c3f41;
    width: {int(16 * scaling_manager.scale_factor)}px;
    border-radius: 8px;
    border: 1px solid #555;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6a6a6a, stop:0.5 #777, stop:1 #666);
    border: 1px solid #888;
    border-radius: 6px;
    min-height: {int(20 * scaling_manager.scale_factor)}px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #7a7a7a, stop:0.5 #888, stop:1 #777);
    border: 1px solid #999;
}}

QScrollBar::handle:vertical:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4a90e2, stop:0.5 #357abd, stop:1 #4a90e2);
    border: 1px solid #4a90e2;
}}

QScrollBar::add-line:vertical {{
    background-color: #3c3f41;
    height: {int(16 * scaling_manager.scale_factor)}px;
    border: 1px solid #555;
    border-radius: 8px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}}

QScrollBar::add-line:vertical:hover {{
    background-color: #4a4a4a;
}}

QScrollBar::add-line:vertical:pressed {{
    background-color: #4a90e2;
}}

QScrollBar::sub-line:vertical {{
    background-color: #3c3f41;
    height: {int(16 * scaling_manager.scale_factor)}px;
    border: 1px solid #555;
    border-radius: 8px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}}

QScrollBar::sub-line:vertical:hover {{
    background-color: #4a4a4a;
}}

QScrollBar::sub-line:vertical:pressed {{
    background-color: #4a90e2;
}}

QScrollBar::up-arrow:vertical {{
    border: none;
    width: {int(8 * scaling_manager.scale_factor)}px;
    height: {int(8 * scaling_manager.scale_factor)}px;
    background: transparent;
    image: none;
}}

QScrollBar::down-arrow:vertical {{
    border: none;
    width: {int(8 * scaling_manager.scale_factor)}px;
    height: {int(8 * scaling_manager.scale_factor)}px;
    background: transparent;
    image: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background-color: #3c3f41;
    height: {int(16 * scaling_manager.scale_factor)}px;
    border-radius: 8px;
    border: 1px solid #555;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6a6a6a, stop:0.5 #777, stop:1 #666);
    border: 1px solid #888;
    border-radius: 6px;
    min-width: {int(20 * scaling_manager.scale_factor)}px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #7a7a7a, stop:0.5 #888, stop:1 #777);
    border: 1px solid #999;
}}

QScrollBar::handle:horizontal:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4a90e2, stop:0.5 #357abd, stop:1 #4a90e2);
    border: 1px solid #4a90e2;
}}

QScrollBar::add-line:horizontal {{
    background-color: #3c3f41;
    width: {int(16 * scaling_manager.scale_factor)}px;
    border: 1px solid #555;
    border-radius: 8px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}}

QScrollBar::add-line:horizontal:hover {{
    background-color: #4a4a4a;
}}

QScrollBar::add-line:horizontal:pressed {{
    background-color: #4a90e2;
}}

QScrollBar::sub-line:horizontal {{
    background-color: #3c3f41;
    width: {int(16 * scaling_manager.scale_factor)}px;
    border: 1px solid #555;
    border-radius: 8px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}}

QScrollBar::sub-line:horizontal:hover {{
    background-color: #4a4a4a;
}}

QScrollBar::sub-line:horizontal:pressed {{
    background-color: #4a90e2;
}}

QScrollBar::left-arrow:horizontal {{
    border: none;
    width: {int(8 * scaling_manager.scale_factor)}px;
    height: {int(8 * scaling_manager.scale_factor)}px;
    background: transparent;
    image: none;
}}

QScrollBar::right-arrow:horizontal {{
    border: none;
    width: {int(8 * scaling_manager.scale_factor)}px;
    height: {int(8 * scaling_manager.scale_factor)}px;
    background: transparent;
    image: none;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
}}
"""


# Keep the old DARK_STYLE for backward compatibility
DARK_STYLE = get_scaled_dark_style()

STATUS_COLORS = {
    "LOADED": QColor("#2B0066"),           # Deep purple
    "READY_PREPROCESS": QColor("#004D99"), # Deep blue
    "READY_TRACKING": QColor("#006680"),   # Blue-teal
    "TRACKED": QColor("#008066"),          # Teal
    "RESULTS_DONE": QColor("#006633"),     # Deep green
    "ERROR": QColor("#7D0000")             # Red
}
