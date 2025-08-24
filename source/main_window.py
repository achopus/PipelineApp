"""
Main Window for the Video Tracking Pipeline Application.
"""

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
from pandas import DataFrame
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget
)

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Local application imports
from file_management.status import Status
from file_management.folders import Folder, PROJECT_FOLDER
from gui.project_management_tab import ProjectManagementTab
from gui.scaling import get_scaling_manager
from gui.settings_dialog import SettingsDialog
from gui.manual_dialog import show_manual_dialog
from gui.statistical_analysis_tab import StatisticalAnalysisTab
from gui.style import get_scaled_dark_style
from gui.tracking_results_tab import TrackingResultsTab
from gui.video_points_annotation_tab import VideoPointsAnnotationTab
from metric_calculation.metrics_pipeline import run_metrics_pipeline
from metric_calculation.utils import construct_metric_dataframe
from utils.logging_config import init_logging, get_logger
from utils.settings_manager import reload_settings, set_project_path


class MetricCalculationWorker(QThread):
    """Worker thread for running metric calculations."""
    
    progress_update = pyqtSignal(int, int, str)  # current, total, video_name
    calculation_complete = pyqtSignal(dict, dict)  # metrics, status
    error_occurred = pyqtSignal(str)
    
    def __init__(self, folder_path: str, pairs: list, metrics: dict, status: Optional[Dict[str, Status]]):
        super().__init__()
        self.folder_path = folder_path
        self.pairs = pairs
        self.metrics = metrics
        self.status = status or {}
    
    def run(self):
        """Run the metric calculations."""
        try:
            for i, (video_path, frame_path) in enumerate(self.pairs):
                # Emit progress update
                self.progress_update.emit(i, len(self.pairs), video_path)
                
                # Run metrics pipeline for this video
                metrics = run_metrics_pipeline(
                    frame_path=os.path.join(self.folder_path, Folder.TRACKING.value, frame_path),
                    source_video_path=os.path.join(self.folder_path, Folder.VIDEOS.value, video_path),
                    save_path=os.path.join(self.folder_path, Folder.IMAGES.value, f"{Path(video_path).stem}.png")
                )
                
                # Store results
                self.metrics[Path(video_path).name] = metrics
                if self.status is not None:
                    self.status[Path(video_path).name] = Status.RESULTS_DONE
            
            # Emit completion signal with updated metrics and status
            self.calculation_complete.emit(self.metrics, self.status)
            
        except Exception as e:
            self.error_occurred.emit(f"Error during metric calculation: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window containing all tabs."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize logging
        init_logging(log_level="INFO", console_output=True)
        self.logger = get_logger(__name__)
        self.logger.info("Initializing PipelineApp main window")
        
        # Initialize scaling manager first
        self.scaling_manager = get_scaling_manager()
        self.setWindowTitle("Video tracking")
        
        # Set window icon with proper path resolution
        self._set_window_icon()

        # Initialize data attributes
        self.folder_path: Optional[str] = None
        self._yaml_path: Optional[str] = None
        self.status: Optional[Dict[str, Status]] = None
        self.metrics: Dict[str, Dict[str, float]] = {}
        self.metrics_dataframe: Optional[DataFrame] = None
        self.video_widget = None
        self.metric_worker: Optional[MetricCalculationWorker] = None

        # Set up the tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Create tab instances
        self.project_management_tab = ProjectManagementTab(self)
        self.video_points_tab = VideoPointsAnnotationTab(self)
        self.tracking_results_tab = TrackingResultsTab(self)
        self.statistical_analysis_tab = StatisticalAnalysisTab(self)

        # Add tabs to the tab widget
        self.tabs.addTab(self.project_management_tab, "1. Project Management")
        self.tabs.addTab(self.video_points_tab, "2. Video Points Annotation")
        self.tabs.addTab(self.tracking_results_tab, "3. Animal tracking + Results")
        self.tabs.addTab(self.statistical_analysis_tab, "4. Statistical Analysis")
        # Set tab bar style for wider tabs
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 400px;
                padding: 10px;
                font-size: 12pt;
            }
        """)

        # Create menu bar with settings and exit buttons
        self.create_menu_bar()

        # Initially disable tabs 2, 3, and 4
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)

        self.setCentralWidget(self.tabs)
        
        # Start maximized
        self.showFullScreen()
    
    @property
    def yaml_path(self) -> Optional[str]:
        """Get the current project YAML path."""
        return self._yaml_path
    
    @yaml_path.setter
    def yaml_path(self, value: Optional[str]) -> None:
        """Set the current project YAML path and update settings manager."""
        self._yaml_path = value
        # Update the settings manager with the new project path
        set_project_path(value)

    def _set_window_icon(self):
        """Set the window icon with proper error handling."""
        try:
            # Try multiple possible icon locations
            possible_paths = [
                # Resources folder next to main_window.py
                os.path.join(os.path.dirname(__file__), "resources", "rat_icon.ico"),
                # Resources folder at project root
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "rat_icon.ico"),
                # Assets folder at project root
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "rat_icon.ico"),
                # Direct in source folder
                os.path.join(os.path.dirname(__file__), "rat_icon.ico")
            ]
            
            icon_set = False
            for icon_path in possible_paths:
                self.logger.info(f"Trying icon path: {icon_path}")
                if os.path.exists(icon_path):
                    self.setWindowIcon(QIcon(icon_path))
                    self.logger.info(f"Successfully set window icon from: {icon_path}")
                    icon_set = True
                    break
            
            if not icon_set:
                self.logger.warning("Could not find rat_icon.ico in any expected location")
                
        except Exception as e:
            self.logger.error(f"Error setting window icon: {e}")

    def create_menu_bar(self) -> None:
        """Create a menu bar with manual, settings and exit buttons."""
        # Create menu bar
        self.menubar = self.menuBar()
        if self.menubar is None:
            return
        
        # Add items in reverse order due to right-to-left layout
        # This will show as: Manual | Settings | Exit (left to right)
        
        # Create exit action (added first, appears rightmost)
        exit_action = QAction("❌ Exit", self)
        exit_action.setFont(QFont("Segoe UI", 12, QFont.Bold))
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close_application)
        self.menubar.addAction(exit_action)
        
        # Create settings action (added second, appears in middle)
        settings_action = QAction("⚙️ Settings", self)
        settings_action.setFont(QFont("Segoe UI", 12, QFont.Bold))
        settings_action.setStatusTip('Configure pipeline settings')
        settings_action.triggered.connect(self.open_settings)
        self.menubar.addAction(settings_action)
        
        # Create manual/help menu (added last, appears leftmost)
        manual_menu = QAction("📖 Manual", self)
        manual_menu.setFont(QFont("Segoe UI", 12, QFont.Bold))
        manual_menu.setStatusTip('Access documentation and guides')
        manual_menu.triggered.connect(lambda: show_manual_dialog(self))

        self.menubar.addAction(manual_menu)
        
        # Style the menu bar with right alignment for the buttons
        self.menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border-bottom: 2px solid #4dd0e1;
                padding: 5px;
                font-size: 12pt;
                text-align: right;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                float: right;
            }
            QMenuBar::item:selected {
                background-color: #4dd0e1;
                color: white;
            }
            QMenuBar::item:pressed {
                background-color: #26a69a;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #4dd0e1;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                margin: 1px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #4dd0e1;
                color: white;
            }
            QMenu::item:pressed {
                background-color: #26a69a;
            }
        """)
        # Set menu bar to layout right-to-left
        self.menubar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def open_settings(self) -> None:
        """Open the settings dialog."""
        dialog = SettingsDialog(self.yaml_path, self)
        if dialog.exec_() == QDialog.Accepted:
            # Settings were saved, reload them in the settings manager
            reload_settings(self.yaml_path)
            self.logger.info("Pipeline settings updated")
    
    def create_exit_button(self) -> None:
        """Create an exit button in the top right corner."""
        # Create menu bar
        self.menubar = self.menuBar()
        if self.menubar is None:
            return
        
        # Create exit action
        exit_action = QAction("❌ Exit", self)
        exit_action.setFont(QFont("Segoe UI", 12, QFont.Bold))
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close_application)
        self.menubar.addAction(exit_action)
        
        # Style the menu bar with right alignment for the exit button
        self.menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border-bottom: 2px solid #4dd0e1;
                padding: 5px;
                font-size: 12pt;
                text-align: right;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                float: right;
            }
            QMenuBar::item:selected {
                background-color: #ff4444;
                color: white;
            }
            QMenuBar::item:pressed {
                background-color: #cc3333;
            }
        """)

    def close_application(self) -> None:
        """Close the application with confirmation."""
        reply = QMessageBox.question(
            self, 
            'Exit Application', 
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()

    def on_tab_changed(self) -> None:
        """Handle tab change events."""
        try:
            if hasattr(self.project_management_tab, 'update_progress_table'):
                self.project_management_tab.update_progress_table()
        except Exception:
            pass

    def enable_video_points_tab(self) -> None:
        """Enable and set up the video points annotation tab."""
        self.video_points_tab.setup_ui()
        self.tabs.setTabEnabled(1, True)

    def enable_tracking_tab(self) -> None:
        """Enable and set up the tracking and results tab."""
        self.tracking_results_tab.setup_ui()
        self.tabs.setTabEnabled(2, True)

    def enable_statistical_analysis_tab(self) -> None:
        """Enable and set up the statistical analysis tab."""
        self.tabs.setTabEnabled(3, True)
        # Defer the data refresh to prevent window flashes during YAML loading
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self._delayed_refresh_statistical_tab)
    
    def _delayed_refresh_statistical_tab(self) -> None:
        """Delayed refresh of statistical analysis tab data."""
        if hasattr(self.statistical_analysis_tab, 'refresh_data'):
            self.statistical_analysis_tab.refresh_data()

    def update_metrics_progress(self, i: int, n: int, video_name: str) -> None:
        """Update the metrics progress display."""
        self.tracking_results_tab.update_metrics_progress(i, n, video_name)

    def metrics_pipeline_wrapper(self) -> None:
        """Wrapper for the metrics pipeline processing using threading."""
        if self.folder_path is None:
            return
            
        source_videos = os.listdir(os.path.join(self.folder_path, Folder.VIDEOS.value))
        trackings = [
            tr for tr in os.listdir(os.path.join(self.folder_path, Folder.TRACKING.value))
            if tr.endswith(".csv")
        ]
        
        pairs = []
        for video_file in source_videos:
            video_name = Path(video_file).stem
            for tracking_file in trackings:
                tracking_name = Path(tracking_file).stem
                if video_name in tracking_name:
                    pairs.append((video_file, tracking_file))
                    break
        
        n_pairs = len(pairs)
        if n_pairs == 0:
            no_data_dialog = QDialog(self)
            no_data_dialog.setWindowTitle("No tracking data to process.")
            no_data_dialog.resize(600, 200)
            from PyQt5.QtWidgets import QVBoxLayout, QLabel
            from PyQt5.QtGui import QFont
            no_data_layout = QVBoxLayout()
            progress_label = QLabel("No tracking data found for videos")
            progress_label.setFont(QFont("", 14))
            no_data_layout.addWidget(progress_label)
            no_data_dialog.setLayout(no_data_layout)
            no_data_dialog.setModal(True)
            no_data_dialog.exec_()
            return

        # Start the threaded metric calculation
        self.metric_worker = MetricCalculationWorker(
            self.folder_path, pairs, self.metrics, self.status
        )
        
        # Connect signals
        self.metric_worker.progress_update.connect(self.update_metrics_progress)
        self.metric_worker.calculation_complete.connect(self.on_metrics_calculation_complete)
        self.metric_worker.error_occurred.connect(self.on_metrics_calculation_error)
        
        # Start the worker thread
        self.metric_worker.start()

    def on_metrics_calculation_complete(self, metrics: dict, status: dict) -> None:
        """Handle completion of metric calculations."""
        # Update instance variables
        self.metrics = metrics
        self.status = status
        
        # Update UI
        if self.tracking_results_tab.metrics_progress_text:
            self.tracking_results_tab.metrics_progress_text.setText("Metrics calculation completed.")
        QApplication.processEvents()
        
        if hasattr(self.project_management_tab, 'update_progress_table'):
            self.project_management_tab.update_progress_table()
        
        # Generate dataframes and save results only if folder_path is valid
        if self.folder_path is not None:
            self.metrics_dataframe = construct_metric_dataframe(self.metrics, self.yaml_path)
            self.metrics_dataframe.to_csv(
                os.path.join(self.folder_path, Folder.RESULTS.value, "metrics_dataframe.csv"), 
                index=False
            )
            self.metrics_dataframe.to_excel(
                os.path.join(self.folder_path, Folder.RESULTS.value, "metrics_dataframe.xlsx"), 
                index=False
            )
            self.update_metrics_table()
            
            # Enable statistical analysis tab now that we have metrics data
            self.enable_statistical_analysis_tab()
        
        # Clean up the worker
        self.metric_worker = None

    def on_metrics_calculation_error(self, error_message: str) -> None:
        """Handle errors during metric calculations."""
        QMessageBox.critical(self, "Metric Calculation Error", 
                           f"An error occurred during metric calculation:\n\n{error_message}")
        
        # Reset progress display
        if self.tracking_results_tab.metrics_progress_text:
            self.tracking_results_tab.metrics_progress_text.setText("Metric calculation failed.")
        
        # Clean up the worker
        self.metric_worker = None

    def update_metrics_table(self) -> None:
        """Update the metrics table with current data."""
        self.tracking_results_tab.update_metrics_table(self.metrics_dataframe)

    def check_preprocessing_status(self) -> None:
        """Check and display the preprocessing status of files."""
        if self.yaml_path:
            self.tracking_results_tab.check_preprocessing_status(self.yaml_path)


def main():
    """Main entry point for the application."""
    # Initialize logging before creating QApplication
    init_logging(log_level="INFO", console_output=True)
    logger = get_logger(__name__)
    logger.info("Starting PipelineApp")
    
    app = QApplication(sys.argv)
    
    # Set application properties for better rendering
    app.setApplicationName("Video Tracking Pipeline")
    app.setApplicationDisplayName("PipelineApp")
    app.setApplicationVersion("0.1.0")
    
    logger.info("Created QApplication, initializing main window")
    
    # Create and show the main window
    window = MainWindow()
    
    # Apply the enhanced dark style to the main window instead of the entire app
    window.setStyleSheet(get_scaled_dark_style())
    
    window.show()
    logger.info("Main window displayed, entering event loop")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
