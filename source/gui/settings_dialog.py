"""
Settings dialog for configuring metric calculation parameters.
"""

import json
import os
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QDoubleSpinBox, QSpinBox, QGroupBox, QGridLayout,
    QPushButton, QMessageBox, QCheckBox, QComboBox, QTextEdit,
    QScrollArea, QFormLayout, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from utils.settings_manager import get_settings_manager


class SettingsDialog(QDialog):
    """Dialog for configuring metric calculation settings."""
    
    def __init__(self, project_path: Optional[str] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Pipeline Settings")
        self.setModal(True)
        self.resize(1900, 800)
        
        self.project_path = project_path
        
        # Set the project path in settings manager if provided
        if self.project_path:
            get_settings_manager().set_project_path(self.project_path)
        
        # Default settings
        self.default_settings = self.get_default_settings()
        self.current_settings = self.load_settings()
        
        self.setup_ui()
        self.load_current_values()
    
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
            "cluster_padding_factor": 0.2,  # Was cluster_size // 5, now 20% of cluster size
            
            # Cluster/SSH Settings
            "ssh_host": "sup200.ad.nudz.cz",
            "ssh_port": 22,
            "ssh_user": "pcp\\vojtech.brejtr",
            "ssh_password": "",  # Will be loaded from .env
            "ssh_max_retries": 3,
            "ssh_retry_delay": 5.0,
            
            # Cluster Paths
            "cluster_base_path": "/proj/BV_data/",
            "cluster_home_path": "/home/vojtech.brejtr",
            "cluster_conda_env": "DLC",
            
            # SLURM Preprocessing Settings
            "slurm_preprocessing_cpus": 1,
            "slurm_preprocessing_memory": "8gb",
            "slurm_preprocessing_time": "1-00:00:00",
            "slurm_preprocessing_partition": "",  # Default partition
            
            # SLURM Tracking Settings
            "slurm_tracking_cpus": 4,
            "slurm_tracking_memory": "16gb",
            "slurm_tracking_time": "1-00:00:00",
            "slurm_tracking_partition": "PipelineProdGPU",
            
            # Backend Processing Settings
            "dlc_config_path": "/home/vojtech.brejtr/projects/DLC_Basler/NPS-Basler-2025-02-19/config.yaml",
            "dlc_video_type": ".mp4",
            "dlc_shuffle": 1,
            "dlc_batch_size": 16,
            "dlc_save_as_csv": True,
            
            # Video Preprocessing Settings
            "preprocessing_boundary": 100,
            "preprocessing_output_width": 1000,
            "preprocessing_output_height": 1000
        }
    
    def setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Set tab bar style to match main window
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                min-width: 250px;
                padding: 10px;
                font-size: 12pt;
            }
        """)
        
        # Arena and General tab
        self.create_arena_tab()
        
        # Body and Head Size tab
        self.create_body_head_tab()
        
        # Processing tab
        self.create_processing_tab()
        
        # Visualization tab
        self.create_visualization_tab()
        
        # Advanced tab
        self.create_advanced_tab()
        
        # Cluster Settings tab
        self.create_cluster_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; }")
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("QPushButton { padding: 8px 16px; border-radius: 4px; }")
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_arena_tab(self) -> None:
        """Create the arena and general parameters tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Arena parameters group
        arena_group = QGroupBox("Arena Parameters")
        arena_layout = QFormLayout()
        
        self.arena_side_cm = QDoubleSpinBox()
        self.arena_side_cm.setRange(1.0, 1000.0)
        self.arena_side_cm.setSuffix(" cm")
        self.arena_side_cm.setDecimals(1)
        arena_layout.addRow("Arena Side Length:", self.arena_side_cm)
        
        self.arena_size_px = QSpinBox()
        self.arena_size_px.setRange(100, 10000)
        self.arena_size_px.setSuffix(" pixels")
        arena_layout.addRow("Arena Size (pixels):", self.arena_size_px)
        
        self.corner_px = QSpinBox()
        self.corner_px.setRange(0, 1000)
        self.corner_px.setSuffix(" pixels")
        arena_layout.addRow("Corner Offset:", self.corner_px)
        
        arena_group.setLayout(arena_layout)
        layout.addWidget(arena_group)
        
        # Time parameters group
        time_group = QGroupBox("Time Parameters")
        time_layout = QFormLayout()
        
        self.timebin_minutes = QDoubleSpinBox()
        self.timebin_minutes.setRange(0.1, 60.0)
        self.timebin_minutes.setSuffix(" minutes")
        self.timebin_minutes.setDecimals(1)
        time_layout.addRow("Time Bin Size:", self.timebin_minutes)
        
        self.max_time_minutes = QDoubleSpinBox()
        self.max_time_minutes.setRange(1.0, 10000.0)
        self.max_time_minutes.setSuffix(" minutes")
        self.max_time_minutes.setDecimals(1)
        self.max_time_minutes.setSpecialValueText("No limit")
        time_layout.addRow("Maximum Analysis Time:", self.max_time_minutes)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Arena & Time")
    
    def create_body_head_tab(self) -> None:
        """Create the body and head size configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Body size group
        body_group = QGroupBox("Body Size Configuration")
        body_layout = QVBoxLayout()
        
        info_label = QLabel("Body size controls the distance-to-wall threshold for center detection.")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        body_layout.addWidget(info_label)
        
        self.body_size_mode = QComboBox()
        self.body_size_mode.addItems(["Auto-calculate from video", "Use manual value"])
        self.body_size_mode.currentTextChanged.connect(self.on_body_size_mode_changed)
        body_layout.addWidget(QLabel("Body Size Mode:"))
        body_layout.addWidget(self.body_size_mode)
        
        self.manual_body_size = QDoubleSpinBox()
        self.manual_body_size.setRange(0.1, 100.0)
        self.manual_body_size.setSuffix(" cm")
        self.manual_body_size.setDecimals(2)
        body_layout.addWidget(QLabel("Manual Body Size:"))
        body_layout.addWidget(self.manual_body_size)
        
        # Body size calculation parameters
        body_calc_layout = QFormLayout()
        
        self.body_size_detection_threshold = QDoubleSpinBox()
        self.body_size_detection_threshold.setRange(0.1, 1.0)
        self.body_size_detection_threshold.setDecimals(2)
        self.body_size_detection_threshold.setSingleStep(0.05)
        body_calc_layout.addRow("Detection Threshold:", self.body_size_detection_threshold)
        
        self.body_size_on_line_threshold = QDoubleSpinBox()
        self.body_size_on_line_threshold.setRange(0.01, 5.0)
        self.body_size_on_line_threshold.setDecimals(2)
        self.body_size_on_line_threshold.setSuffix(" cm")
        body_calc_layout.addRow("On-Line Threshold:", self.body_size_on_line_threshold)
        
        body_layout.addLayout(body_calc_layout)
        body_group.setLayout(body_layout)
        layout.addWidget(body_group)
        
        # Head size group
        head_group = QGroupBox("Head Size Configuration")
        head_layout = QVBoxLayout()
        
        info_label2 = QLabel("Head size is used for calculating velocity thresholds for movement detection.")
        info_label2.setStyleSheet("color: #666; font-style: italic;")
        head_layout.addWidget(info_label2)
        
        self.head_size_mode = QComboBox()
        self.head_size_mode.addItems(["Auto-calculate from video", "Use manual value"])
        self.head_size_mode.currentTextChanged.connect(self.on_head_size_mode_changed)
        head_layout.addWidget(QLabel("Head Size Mode:"))
        head_layout.addWidget(self.head_size_mode)
        
        self.manual_head_size = QDoubleSpinBox()
        self.manual_head_size.setRange(0.1, 100.0)
        self.manual_head_size.setSuffix(" cm")
        self.manual_head_size.setDecimals(2)
        head_layout.addWidget(QLabel("Manual Head Size:"))
        head_layout.addWidget(self.manual_head_size)
        
        head_group.setLayout(head_layout)
        layout.addWidget(head_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Body & Head Size")
    
    def create_processing_tab(self) -> None:
        """Create the processing parameters tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Trajectory processing group
        trajectory_group = QGroupBox("Trajectory Processing")
        trajectory_layout = QFormLayout()
        
        self.trajectory_detection_threshold = QDoubleSpinBox()
        self.trajectory_detection_threshold.setRange(0.1, 1.0)
        self.trajectory_detection_threshold.setDecimals(2)
        self.trajectory_detection_threshold.setSingleStep(0.05)
        trajectory_layout.addRow("Detection Threshold:", self.trajectory_detection_threshold)
        
        self.motion_blur_sigma = QDoubleSpinBox()
        self.motion_blur_sigma.setRange(0.1, 10.0)
        self.motion_blur_sigma.setDecimals(1)
        trajectory_layout.addRow("Motion Blur Sigma:", self.motion_blur_sigma)
        
        self.velocity_threshold = QDoubleSpinBox()
        self.velocity_threshold.setRange(0.1, 50.0)
        self.velocity_threshold.setSuffix(" cm/s")
        self.velocity_threshold.setDecimals(1)
        trajectory_layout.addRow("Velocity Threshold:", self.velocity_threshold)
        
        trajectory_group.setLayout(trajectory_layout)
        layout.addWidget(trajectory_group)
        
        # Thigmotaxis group
        thigmo_group = QGroupBox("Thigmotaxis Analysis")
        thigmo_layout = QFormLayout()
        
        self.thigmotaxis_bin_count = QSpinBox()
        self.thigmotaxis_bin_count.setRange(4, 100)
        thigmo_layout.addRow("Grid Bin Count:", self.thigmotaxis_bin_count)
        
        thigmo_group.setLayout(thigmo_layout)
        layout.addWidget(thigmo_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Processing")
    
    def create_visualization_tab(self) -> None:
        """Create the visualization parameters tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        viz_group = QGroupBox("Visualization Parameters")
        viz_layout = QFormLayout()
        
        self.viz_border_size = QSpinBox()
        self.viz_border_size.setRange(0, 50)
        self.viz_border_size.setSuffix(" cm")
        viz_layout.addRow("Border Size:", self.viz_border_size)
        
        self.viz_start_time = QDoubleSpinBox()
        self.viz_start_time.setRange(0.0, 10000.0)
        self.viz_start_time.setSuffix(" minutes")
        self.viz_start_time.setDecimals(1)
        viz_layout.addRow("Visualization Start Time:", self.viz_start_time)
        
        self.viz_end_time = QDoubleSpinBox()
        self.viz_end_time.setRange(1.0, 10000.0)
        self.viz_end_time.setSuffix(" minutes")
        self.viz_end_time.setDecimals(1)
        self.viz_end_time.setSpecialValueText("End of video")
        viz_layout.addRow("Visualization End Time:", self.viz_end_time)
        
        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Visualization")
    
    def create_advanced_tab(self) -> None:
        """Create the advanced parameters tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Cluster removal group
        cluster_group = QGroupBox("Cluster Removal")
        cluster_layout = QVBoxLayout()
        
        info_label = QLabel("Remove small isolated detection clusters to reduce noise.")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        cluster_layout.addWidget(info_label)
        
        self.cluster_removal_enabled = QCheckBox("Enable cluster removal")
        cluster_layout.addWidget(self.cluster_removal_enabled)
        
        cluster_params_layout = QFormLayout()
        
        self.min_cluster_size_seconds = QDoubleSpinBox()
        self.min_cluster_size_seconds.setRange(0.1, 60.0)
        self.min_cluster_size_seconds.setSuffix(" seconds")
        self.min_cluster_size_seconds.setDecimals(1)
        cluster_params_layout.addRow("Minimum Cluster Size:", self.min_cluster_size_seconds)
        
        self.cluster_padding_factor = QDoubleSpinBox()
        self.cluster_padding_factor.setRange(0.0, 1.0)
        self.cluster_padding_factor.setDecimals(2)
        self.cluster_padding_factor.setSingleStep(0.05)
        cluster_params_layout.addRow("Padding Factor:", self.cluster_padding_factor)
        
        cluster_layout.addLayout(cluster_params_layout)
        cluster_group.setLayout(cluster_layout)
        layout.addWidget(cluster_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Advanced")
    
    def create_cluster_tab(self) -> None:
        """Create the cluster settings tab."""
        tab = QWidget()
        main_layout = QVBoxLayout()
        
        # Warning message at the top
        warning_label = QLabel("⚠️ WARNING: Changing these settings may result in errors or failed cluster operations.\n"
                              "Only modify these settings if you understand their impact on cluster processing.")
        warning_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        warning_label.setWordWrap(True)
        main_layout.addWidget(warning_label)
        
        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # SSH Connection Settings and Cluster Paths in a horizontal layout
        connection_layout = QHBoxLayout()
        
        # SSH Connection Settings
        ssh_group = QGroupBox("SSH Connection Settings")
        ssh_layout = QFormLayout()
        
        self.ssh_host = QLineEdit()
        ssh_layout.addRow("SSH Host:", self.ssh_host)
        
        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        ssh_layout.addRow("SSH Port:", self.ssh_port)
        
        self.ssh_user = QLineEdit()
        ssh_layout.addRow("SSH User:", self.ssh_user)
        
        self.ssh_max_retries = QSpinBox()
        self.ssh_max_retries.setRange(1, 10)
        self.ssh_max_retries.setMaximumWidth(100)
        ssh_layout.addRow("Max Retries:", self.ssh_max_retries)
        
        self.ssh_retry_delay = QDoubleSpinBox()
        self.ssh_retry_delay.setRange(1.0, 60.0)
        self.ssh_retry_delay.setSuffix(" seconds")
        ssh_layout.addRow("Retry Delay:", self.ssh_retry_delay)
        
        ssh_group.setLayout(ssh_layout)
        connection_layout.addWidget(ssh_group)
        
        # Cluster Paths Settings
        paths_group = QGroupBox("Cluster Paths")
        paths_layout = QFormLayout()
        
        self.cluster_base_path = QLineEdit()
        paths_layout.addRow("Base Path:", self.cluster_base_path)
        
        self.cluster_home_path = QLineEdit()
        paths_layout.addRow("Home Path:", self.cluster_home_path)
        
        self.cluster_conda_env = QLineEdit()
        paths_layout.addRow("Conda Environment:", self.cluster_conda_env)
        
        paths_group.setLayout(paths_layout)
        connection_layout.addWidget(paths_group)
        
        layout.addLayout(connection_layout)
        
        # SLURM Settings in a horizontal layout
        slurm_layout = QHBoxLayout()
        
        # SLURM Preprocessing Settings
        slurm_prep_group = QGroupBox("SLURM Preprocessing Settings")
        slurm_prep_layout = QFormLayout()
        
        self.slurm_preprocessing_cpus = QSpinBox()
        self.slurm_preprocessing_cpus.setRange(1, 32)
        slurm_prep_layout.addRow("CPUs per Task:", self.slurm_preprocessing_cpus)
        
        self.slurm_preprocessing_memory = QLineEdit()
        slurm_prep_layout.addRow("Memory (e.g., 8gb):", self.slurm_preprocessing_memory)
        
        self.slurm_preprocessing_time = QLineEdit()
        slurm_prep_layout.addRow("Time Limit:", self.slurm_preprocessing_time)
        
        self.slurm_preprocessing_partition = QLineEdit()
        slurm_prep_layout.addRow("Partition (optional):", self.slurm_preprocessing_partition)
        
        slurm_prep_group.setLayout(slurm_prep_layout)
        slurm_layout.addWidget(slurm_prep_group)
        
        # SLURM Tracking Settings
        slurm_track_group = QGroupBox("SLURM Tracking Settings")
        slurm_track_layout = QFormLayout()
        
        self.slurm_tracking_cpus = QSpinBox()
        self.slurm_tracking_cpus.setRange(1, 32)
        slurm_track_layout.addRow("CPUs per Task:", self.slurm_tracking_cpus)
        
        self.slurm_tracking_memory = QLineEdit()
        slurm_track_layout.addRow("Memory (e.g., 16gb):", self.slurm_tracking_memory)
        
        self.slurm_tracking_time = QLineEdit()
        slurm_track_layout.addRow("Time Limit:", self.slurm_tracking_time)
        
        self.slurm_tracking_partition = QLineEdit()
        slurm_track_layout.addRow("Partition:", self.slurm_tracking_partition)
        
        slurm_track_group.setLayout(slurm_track_layout)
        slurm_layout.addWidget(slurm_track_group)
        
        layout.addLayout(slurm_layout)
        
        # Backend Settings in a horizontal layout
        backend_layout = QHBoxLayout()
        
        # DeepLabCut Settings
        dlc_group = QGroupBox("DeepLabCut Backend Settings")
        dlc_layout = QFormLayout()
        
        self.dlc_config_path = QLineEdit()
        dlc_layout.addRow("Config Path:", self.dlc_config_path)
        
        self.dlc_video_type = QComboBox()
        self.dlc_video_type.addItems([".mp4", ".avi", ".mov", ".mkv"])
        dlc_layout.addRow("Video Type:", self.dlc_video_type)
        
        self.dlc_shuffle = QSpinBox()
        self.dlc_shuffle.setRange(1, 10)
        dlc_layout.addRow("Shuffle:", self.dlc_shuffle)
        
        self.dlc_batch_size = QSpinBox()
        self.dlc_batch_size.setRange(1, 128)
        dlc_layout.addRow("Batch Size:", self.dlc_batch_size)
        
        self.dlc_save_as_csv = QCheckBox("Save as CSV")
        dlc_layout.addRow("Output Format:", self.dlc_save_as_csv)
        
        dlc_group.setLayout(dlc_layout)
        backend_layout.addWidget(dlc_group)
        
        # Video Preprocessing Settings
        preproc_group = QGroupBox("Video Preprocessing Settings")
        preproc_layout = QFormLayout()
        
        self.preprocessing_boundary = QSpinBox()
        self.preprocessing_boundary.setRange(0, 500)
        self.preprocessing_boundary.setSuffix(" pixels")
        preproc_layout.addRow("Boundary Padding:", self.preprocessing_boundary)
        
        self.preprocessing_output_width = QSpinBox()
        self.preprocessing_output_width.setRange(100, 5000)
        self.preprocessing_output_width.setSuffix(" pixels")
        preproc_layout.addRow("Output Width:", self.preprocessing_output_width)
        
        self.preprocessing_output_height = QSpinBox()
        self.preprocessing_output_height.setRange(100, 5000)
        self.preprocessing_output_height.setSuffix(" pixels")
        preproc_layout.addRow("Output Height:", self.preprocessing_output_height)
        
        preproc_group.setLayout(preproc_layout)
        backend_layout.addWidget(preproc_group)
        
        layout.addLayout(backend_layout)
        
        # Set up scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        tab.setLayout(main_layout)
        self.tab_widget.addTab(tab, "Cluster Settings")
    
    def on_body_size_mode_changed(self) -> None:
        """Handle body size mode change."""
        is_manual = self.body_size_mode.currentIndex() == 1
        self.manual_body_size.setEnabled(is_manual)
    
    def on_head_size_mode_changed(self) -> None:
        """Handle head size mode change."""
        is_manual = self.head_size_mode.currentIndex() == 1
        self.manual_head_size.setEnabled(is_manual)
    
    def load_current_values(self) -> None:
        """Load current settings into the UI."""
        # Arena and time
        self.arena_side_cm.setValue(self.current_settings["arena_side_cm"])
        self.arena_size_px.setValue(self.current_settings["arena_size_px"])
        self.corner_px.setValue(self.current_settings["corner_px"])
        self.timebin_minutes.setValue(self.current_settings["timebin_minutes"])
        
        max_time = self.current_settings["max_time_minutes"]
        if max_time == float('inf'):
            self.max_time_minutes.setValue(self.max_time_minutes.minimum())
        else:
            self.max_time_minutes.setValue(max_time)
        
        # Body and head size
        self.body_size_mode.setCurrentIndex(0 if self.current_settings["body_size_mode"] == "auto" else 1)
        self.manual_body_size.setValue(self.current_settings["manual_body_size"])
        self.body_size_detection_threshold.setValue(self.current_settings["body_size_detection_threshold"])
        self.body_size_on_line_threshold.setValue(self.current_settings["body_size_on_line_threshold"])
        
        self.head_size_mode.setCurrentIndex(0 if self.current_settings["head_size_mode"] == "auto" else 1)
        self.manual_head_size.setValue(self.current_settings["manual_head_size"])
        
        # Processing
        self.trajectory_detection_threshold.setValue(self.current_settings["trajectory_detection_threshold"])
        self.motion_blur_sigma.setValue(self.current_settings["motion_blur_sigma"])
        self.velocity_threshold.setValue(self.current_settings["velocity_threshold"])
        self.thigmotaxis_bin_count.setValue(self.current_settings["thigmotaxis_bin_count"])
        
        # Visualization
        self.viz_border_size.setValue(self.current_settings["viz_border_size"])
        self.viz_start_time.setValue(self.current_settings["viz_start_time"])
        
        viz_end_time = self.current_settings["viz_end_time"]
        if viz_end_time == float('inf'):
            self.viz_end_time.setValue(self.viz_end_time.minimum())
        else:
            self.viz_end_time.setValue(viz_end_time)
        
        # Advanced
        self.cluster_removal_enabled.setChecked(self.current_settings["cluster_removal_enabled"])
        self.min_cluster_size_seconds.setValue(self.current_settings["min_cluster_size_seconds"])
        self.cluster_padding_factor.setValue(self.current_settings["cluster_padding_factor"])
        
        # Cluster settings - use .get() with defaults to handle missing keys
        self.ssh_host.setText(self.current_settings.get("ssh_host", self.default_settings["ssh_host"]))
        self.ssh_port.setValue(self.current_settings.get("ssh_port", self.default_settings["ssh_port"]))
        self.ssh_user.setText(self.current_settings.get("ssh_user", self.default_settings["ssh_user"]))
        self.ssh_max_retries.setValue(self.current_settings.get("ssh_max_retries", self.default_settings["ssh_max_retries"]))
        self.ssh_retry_delay.setValue(self.current_settings.get("ssh_retry_delay", self.default_settings["ssh_retry_delay"]))
        
        self.cluster_base_path.setText(self.current_settings.get("cluster_base_path", self.default_settings["cluster_base_path"]))
        self.cluster_home_path.setText(self.current_settings.get("cluster_home_path", self.default_settings["cluster_home_path"]))
        self.cluster_conda_env.setText(self.current_settings.get("cluster_conda_env", self.default_settings["cluster_conda_env"]))
        
        self.slurm_preprocessing_cpus.setValue(self.current_settings.get("slurm_preprocessing_cpus", self.default_settings["slurm_preprocessing_cpus"]))
        self.slurm_preprocessing_memory.setText(self.current_settings.get("slurm_preprocessing_memory", self.default_settings["slurm_preprocessing_memory"]))
        self.slurm_preprocessing_time.setText(self.current_settings.get("slurm_preprocessing_time", self.default_settings["slurm_preprocessing_time"]))
        self.slurm_preprocessing_partition.setText(self.current_settings.get("slurm_preprocessing_partition", self.default_settings["slurm_preprocessing_partition"]))
        
        self.slurm_tracking_cpus.setValue(self.current_settings.get("slurm_tracking_cpus", self.default_settings["slurm_tracking_cpus"]))
        self.slurm_tracking_memory.setText(self.current_settings.get("slurm_tracking_memory", self.default_settings["slurm_tracking_memory"]))
        self.slurm_tracking_time.setText(self.current_settings.get("slurm_tracking_time", self.default_settings["slurm_tracking_time"]))
        self.slurm_tracking_partition.setText(self.current_settings.get("slurm_tracking_partition", self.default_settings["slurm_tracking_partition"]))
        
        self.dlc_config_path.setText(self.current_settings.get("dlc_config_path", self.default_settings["dlc_config_path"]))
        self.dlc_video_type.setCurrentText(self.current_settings.get("dlc_video_type", self.default_settings["dlc_video_type"]))
        self.dlc_shuffle.setValue(self.current_settings.get("dlc_shuffle", self.default_settings["dlc_shuffle"]))
        self.dlc_batch_size.setValue(self.current_settings.get("dlc_batch_size", self.default_settings["dlc_batch_size"]))
        self.dlc_save_as_csv.setChecked(self.current_settings.get("dlc_save_as_csv", self.default_settings["dlc_save_as_csv"]))
        
        self.preprocessing_boundary.setValue(self.current_settings.get("preprocessing_boundary", self.default_settings["preprocessing_boundary"]))
        self.preprocessing_output_width.setValue(self.current_settings.get("preprocessing_output_width", self.default_settings["preprocessing_output_width"]))
        self.preprocessing_output_height.setValue(self.current_settings.get("preprocessing_output_height", self.default_settings["preprocessing_output_height"]))
        
        # Update enabled states
        self.on_body_size_mode_changed()
        self.on_head_size_mode_changed()
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings from the UI."""
        return {
            # Arena and time
            "arena_side_cm": self.arena_side_cm.value(),
            "arena_size_px": self.arena_size_px.value(),
            "corner_px": self.corner_px.value(),
            "timebin_minutes": self.timebin_minutes.value(),
            "max_time_minutes": float('inf') if self.max_time_minutes.value() == self.max_time_minutes.minimum() else self.max_time_minutes.value(),
            
            # Body and head size
            "body_size_mode": "auto" if self.body_size_mode.currentIndex() == 0 else "manual",
            "manual_body_size": self.manual_body_size.value(),
            "body_size_detection_threshold": self.body_size_detection_threshold.value(),
            "body_size_on_line_threshold": self.body_size_on_line_threshold.value(),
            "head_size_mode": "auto" if self.head_size_mode.currentIndex() == 0 else "manual",
            "manual_head_size": self.manual_head_size.value(),
            
            # Processing
            "trajectory_detection_threshold": self.trajectory_detection_threshold.value(),
            "motion_blur_sigma": self.motion_blur_sigma.value(),
            "velocity_threshold": self.velocity_threshold.value(),
            "thigmotaxis_bin_count": self.thigmotaxis_bin_count.value(),
            
            # Visualization
            "viz_border_size": self.viz_border_size.value(),
            "viz_start_time": self.viz_start_time.value(),
            "viz_end_time": float('inf') if self.viz_end_time.value() == self.viz_end_time.minimum() else self.viz_end_time.value(),
            
            # Advanced
            "cluster_removal_enabled": self.cluster_removal_enabled.isChecked(),
            "min_cluster_size_seconds": self.min_cluster_size_seconds.value(),
            "cluster_padding_factor": self.cluster_padding_factor.value(),
            
            # Cluster/SSH Settings
            "ssh_host": self.ssh_host.text(),
            "ssh_port": self.ssh_port.value(),
            "ssh_user": self.ssh_user.text(),
            "ssh_max_retries": self.ssh_max_retries.value(),
            "ssh_retry_delay": self.ssh_retry_delay.value(),
            
            # Cluster Paths
            "cluster_base_path": self.cluster_base_path.text(),
            "cluster_home_path": self.cluster_home_path.text(),
            "cluster_conda_env": self.cluster_conda_env.text(),
            
            # SLURM Preprocessing Settings
            "slurm_preprocessing_cpus": self.slurm_preprocessing_cpus.value(),
            "slurm_preprocessing_memory": self.slurm_preprocessing_memory.text(),
            "slurm_preprocessing_time": self.slurm_preprocessing_time.text(),
            "slurm_preprocessing_partition": self.slurm_preprocessing_partition.text(),
            
            # SLURM Tracking Settings
            "slurm_tracking_cpus": self.slurm_tracking_cpus.value(),
            "slurm_tracking_memory": self.slurm_tracking_memory.text(),
            "slurm_tracking_time": self.slurm_tracking_time.text(),
            "slurm_tracking_partition": self.slurm_tracking_partition.text(),
            
            # Backend Processing Settings
            "dlc_config_path": self.dlc_config_path.text(),
            "dlc_video_type": self.dlc_video_type.currentText(),
            "dlc_shuffle": self.dlc_shuffle.value(),
            "dlc_batch_size": self.dlc_batch_size.value(),
            "dlc_save_as_csv": self.dlc_save_as_csv.isChecked(),
            
            # Video Preprocessing Settings
            "preprocessing_boundary": self.preprocessing_boundary.value(),
            "preprocessing_output_width": self.preprocessing_output_width.value(),
            "preprocessing_output_height": self.preprocessing_output_height.value()
        }
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_settings = self.default_settings.copy()
            self.load_current_values()
    
    def save_settings(self) -> None:
        """Save the current settings."""
        self.current_settings = self.get_current_settings()
        
        try:
            # Use settings manager to save
            get_settings_manager().save_settings(self.current_settings)
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from the settings manager."""
        return get_settings_manager().get_all_settings()


def get_pipeline_settings(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Get the current pipeline settings."""
    settings_manager = get_settings_manager()
    if project_path:
        settings_manager.set_project_path(project_path)
    return settings_manager.get_all_settings()
