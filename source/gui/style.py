from PyQt5.QtGui import QColor

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
    background-color:#21657E;
    padding: 6px;
    font-size: 25px;
    height: 40px;
    width: 300px;
    border: 0.5px solid #BFFDFF;
}
QTabBar::tab:selected {
    background-color: #00868B;
    font-size: 30 px
}
"""

"#BFFDFF"


STATUS_COLORS = {
    "Loaded": QColor("#3A004B"),               # neutral gray
    "Preprocessing ready": QColor("#2C3C00"),  # light green
    "Error": QColor("#7D0000"),                # light red/pink
    "Tracking ready": QColor("#826300"),
    "Finished": QColor("#005213"),
    "Results available": QColor("#000456")
    # add more exact matches here
}
