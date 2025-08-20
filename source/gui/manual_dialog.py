"""
Manual dialog for displaying README and documentation content within the application.
"""

import re
from typing import Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QScrollArea, QWidget, QLabel, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QTextDocument

# Import embedded documentation content
from documentation.readme_content import README_CONTENT
from documentation.statistical_analysis_manual import STATISTICAL_ANALYSIS_MANUAL_CONTENT
from documentation.field_merging_guide import FIELD_MERGING_GUIDE_CONTENT
from documentation.tukey_hsd_update import TUKEY_HSD_UPDATE_CONTENT


class ManualDialog(QDialog):
    """Dialog for displaying formatted documentation content."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Pipeline Documentation")
        self.setModal(True)
        self.resize(1800, 1000)
        
        self.setup_ui()
        self.load_all_documentation()
    
    def setup_ui(self) -> None:
        """Setup the user interface with tabs for different documents."""
        layout = QVBoxLayout()
        
        # Create tab widget for different documentation
        self.tab_widget = QTabWidget()
        
        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("QPushButton { padding: 8px 16px; border-radius: 4px; }")
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addWidget(self.tab_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_all_documentation(self) -> None:
        """Load all documentation content from embedded Python modules."""
        # Documentation content from embedded modules
        docs = [
            ("📋 README", README_CONTENT),
            ("📊 Statistical Analysis", STATISTICAL_ANALYSIS_MANUAL_CONTENT),
            ("🔗 Field Merging Guide", FIELD_MERGING_GUIDE_CONTENT),
            ("📈 Tukey HSD Update", TUKEY_HSD_UPDATE_CONTENT)
        ]
        
        for tab_name, content in docs:
            try:
                # Create tab with formatted content
                tab_widget = self.create_documentation_tab(content, tab_name)
                self.tab_widget.addTab(tab_widget, tab_name)
                
            except Exception as e:
                error_widget = self.create_error_tab(f"Error loading {tab_name}: {str(e)}")
                self.tab_widget.addTab(error_widget, tab_name)
    
    def create_documentation_tab(self, markdown_content: str, title: str) -> QWidget:
        """Create a tab widget with formatted documentation content."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Create text display
        text_display = QTextEdit()
        text_display.setReadOnly(True)
        
        # Convert markdown to HTML for better formatting
        html_content = self.markdown_to_html(markdown_content)
        text_display.setHtml(html_content)
        
        # Set styling for dark theme
        text_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 6px;
                padding: 16px;
                font-family: 'Segoe UI', 'Consolas', sans-serif;
                font-size: 13px;
                line-height: 1.6;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6d6d6d;
            }
        """)
        
        layout.addWidget(text_display)
        tab.setLayout(layout)
        return tab
    
    def create_error_tab(self, error_message: str) -> QWidget:
        """Create a tab showing an error message."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        error_label = QLabel(error_message)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #dc3545; font-size: 14px; padding: 20px;")
        
        layout.addWidget(error_label)
        tab.setLayout(layout)
        return tab
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """Convert basic markdown to HTML for display."""
        html = markdown_text
        
        # Headers with dark theme colors
        html = re.sub(r'^### (.*$)', r'<h3 style="color: #4fc3f7; margin-top: 24px; margin-bottom: 12px; font-weight: 600;">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2 style="color: #81c784; margin-top: 28px; margin-bottom: 16px; border-bottom: 2px solid #81c784; padding-bottom: 6px; font-weight: 600;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*$)', r'<h1 style="color: #ffb74d; margin-top: 32px; margin-bottom: 20px; text-align: center; border-bottom: 3px solid #ffb74d; padding-bottom: 12px; font-weight: 700;">\1</h1>', html, flags=re.MULTILINE)
        
        # Bold text with accent color
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #ffcc02; font-weight: 600;">\1</strong>', html)
        
        # Italic text
        html = re.sub(r'\*(.*?)\*', r'<em style="color: #e1bee7;">\1</em>', html)
        
        # Inline code with dark theme
        html = re.sub(r'`([^`]+)`', r'<code style="background-color: #2d2d2d; color: #f8bbd9; padding: 3px 6px; border-radius: 4px; font-family: Consolas, monospace; border: 1px solid #3e3e3e;">\1</code>', html)
        
        # Code blocks with dark theme
        html = re.sub(r'```([\s\S]*?)```', r'<pre style="background-color: #0d1117; color: #c9d1d9; padding: 16px; border-radius: 6px; overflow-x: auto; font-family: Consolas, monospace; margin: 12px 0; border: 1px solid #30363d;"><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # Lists (unordered) with dark theme
        html = re.sub(r'^- (.*$)', r'<li style="margin: 4px 0; color: #d4d4d4;">\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li.*?</li>)', r'<ul style="margin: 12px 0; padding-left: 24px; color: #d4d4d4;">\1</ul>', html, flags=re.DOTALL)
        
        # Lists (ordered)
        html = re.sub(r'^\d+\. (.*$)', r'<li style="margin: 4px 0; color: #d4d4d4;">\1</li>', html, flags=re.MULTILINE)
        
        # Links with accent color
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color: #58a6ff; text-decoration: none; border-bottom: 1px solid #58a6ff;">\1</a>', html)
        
        # Line breaks
        html = html.replace('\n\n', '<br><br>')
        html = html.replace('\n', '<br>')
        
        # Wrap in div with dark theme styling
        styled_html = f'''
        <div style="
            font-family: 'Segoe UI', 'Consolas', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1;
            color: #d4d4d4;
            background-color: #1e1e1e;
            max-width: 100%;
            margin: 0 auto;
            padding: 5x;
        ">
            {html}
        </div>
        '''
        
        return styled_html


def show_manual_dialog(parent: Optional[QWidget] = None) -> None:
    """Show the manual dialog."""
    dialog = ManualDialog(parent)
    dialog.exec_()
