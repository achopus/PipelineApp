"""
GUI styling and constants for the Pipeline Application.
"""

import os
from PyQt5.QtGui import QColor
from dotenv import load_dotenv

load_dotenv()
PROJECT_FOLDER = os.getenv("PROJECT_FOLDER", "//srv-fs.ad.nudz.cz/BV_data/TrackingPRC")

DARK_STYLE = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-size: 18px;
}
QLineEdit, QTextEdit, QTableWidget, QTabWidget::pane {
    background-color: #3c3f41;
    border: 1px solid #555;
    color: #f0f0f0;
}
QPushButton {
    background-color: #555;
    border: 1px solid #888;
    padding: 4px 8px;
}
QPushButton:hover {
    background-color: #666;
}
QHeaderView::section {
    background-color: #3c3f41;
    color: #f0f0f0;
    border: 1px solid #555;
}
QTabBar::tab {
    background-color: #21657E;
    padding: 6px;
    font-size: 25px;
    height: 40px;
    width: 400px;
    border: 0.5px solid #BFFDFF;
}
QTabBar::tab:selected {
    background-color: #00868B;
    font-size: 30px;
}
"""

STATUS_COLORS = {
    "LOADED": QColor("#2B0066"),           # Deep purple
    "READY_PREPROCESS": QColor("#004D99"), # Deep blue
    "READY_TRACKING": QColor("#006680"),   # Blue-teal
    "TRACKED": QColor("#008066"),          # Teal
    "RESULTS_DONE": QColor("#006633"),     # Deep green
    "ERROR": QColor("#7D0000")             # Red
}
