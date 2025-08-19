"""
Statistical Analysis Tab for the Video Tracking Application.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import pandas as pd
import numpy as np
from pandas import DataFrame
try:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
    from statsmodels.stats.anova import anova_lm
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QListWidget, QListWidgetItem, QTextEdit,
    QGroupBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QCheckBox, QSplitter, QProgressBar, QApplication, QScrollArea
)

# Statistical test imports
try:
    from scipy import stats
    from scipy.stats import ttest_ind, f_oneway, levene, shapiro
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from gui.scaling import get_scaling_manager


class StatisticalAnalysisWorker(QThread):
    """Worker thread for running statistical analyses."""
    
    results_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data: DataFrame, grouping_factor: str, selected_metrics: List[str], test_type: str, grouping_factor2: str | None = None):
        super().__init__()
        self.data = data
        self.grouping_factor = grouping_factor
        self.grouping_factor2 = grouping_factor2
        self.selected_metrics = selected_metrics
        self.test_type = test_type
    
    def run(self):
        """Run the statistical analysis."""
        try:
            self.progress_update.emit("Starting statistical analysis...")
            
            results = {}
            
            for i, metric in enumerate(self.selected_metrics):
                self.progress_update.emit(f"Analyzing {metric} ({i+1}/{len(self.selected_metrics)})...")
                
                # Group data by the grouping factor
                groups = self.data.groupby(self.grouping_factor)[metric].apply(list).to_dict()
                group_names = list(groups.keys())
                group_values = [groups[name] for name in group_names]
                
                # Remove NaN values
                group_values = [[x for x in group if not pd.isna(x)] for group in group_values]
                
                if len(group_values) < 2:
                    results[metric] = {
                        'error': 'Need at least 2 groups for comparison',
                        'groups': group_names,
                        'n_per_group': [len(group) for group in group_values]
                    }
                    continue
                
                # Basic descriptive statistics
                descriptive = {}
                for name, values in zip(group_names, group_values):
                    if len(values) > 0:
                        descriptive[f'{name}_mean'] = np.mean(values)
                        descriptive[f'{name}_std'] = np.std(values, ddof=1)
                        descriptive[f'{name}_n'] = len(values)
                    else:
                        descriptive[f'{name}_mean'] = np.nan
                        descriptive[f'{name}_std'] = np.nan
                        descriptive[f'{name}_n'] = 0
                
                # Statistical tests
                test_results = {}
                
                if self.test_type == "t-test" and len(group_values) == 2:
                    # Two-sample t-test
                    if len(group_values[0]) > 0 and len(group_values[1]) > 0:
                        # Test for equal variances (Levene's test)
                        try:
                            levene_stat, levene_p = levene(group_values[0], group_values[1])
                            equal_var = levene_p > 0.05
                            
                            # Perform t-test
                            t_stat, p_value = ttest_ind(group_values[0], group_values[1], equal_var=equal_var)
                            
                            test_results = {
                                'test_type': f't-test ({"equal" if equal_var else "unequal"} variances)',
                                'statistic': float(t_stat), # type: ignore
                                'p_value': float(p_value), # type: ignore
                                'significant': float(p_value) < 0.05, # type: ignore
                                'levene_statistic': levene_stat,
                                'levene_p': levene_p,
                                'equal_variances': equal_var
                            }
                        except Exception as e:
                            test_results = {'error': f'T-test failed: {str(e)}'}
                
                elif self.test_type == "One-way ANOVA" and len(group_values) >= 2:
                    # One-way ANOVA
                    valid_groups = [group for group in group_values if len(group) > 0]
                    if len(valid_groups) >= 2:
                        try:
                            f_stat, p_value = f_oneway(*valid_groups)
                            
                            test_results = {
                                'test_type': 'One-way ANOVA',
                                'statistic': f_stat,
                                'p_value': p_value,
                                'significant': p_value < 0.05,
                                'df_between': len(valid_groups) - 1,
                                'df_within': sum(len(group) for group in valid_groups) - len(valid_groups)
                            }
                        except Exception as e:
                            test_results = {'error': f'ANOVA failed: {str(e)}'}
                
                elif self.test_type == "Two-way ANOVA" and self.grouping_factor2:
                    # Two-way ANOVA with interaction
                    if not STATSMODELS_AVAILABLE:
                        test_results = {'error': 'Two-way ANOVA requires statsmodels package. Please install: pip install statsmodels'}
                    else:
                        try:
                            # Prepare data for two-way ANOVA
                            anova_data = self.data[[self.grouping_factor, self.grouping_factor2, metric]].dropna()
                            
                            if len(anova_data) < 4:  # Need at least 4 observations for two-way ANOVA
                                test_results = {'error': 'Two-way ANOVA requires at least 4 observations'}
                            else:
                                # Create the formula for two-way ANOVA with interaction
                                formula = f"{metric} ~ C({self.grouping_factor}) + C({self.grouping_factor2}) + C({self.grouping_factor}):C({self.grouping_factor2})"
                                
                                # Fit the model
                                model = ols(formula, data=anova_data).fit()
                                anova_table = anova_lm(model, typ=2)
                                
                                # Extract results with proper type handling
                                f1_f = anova_table.loc[f'C({self.grouping_factor})', 'F']
                                f1_p = anova_table.loc[f'C({self.grouping_factor})', 'PR(>F)']
                                f2_f = anova_table.loc[f'C({self.grouping_factor2})', 'F']
                                f2_p = anova_table.loc[f'C({self.grouping_factor2})', 'PR(>F)']
                                int_f = anova_table.loc[f'C({self.grouping_factor}):C({self.grouping_factor2})', 'F']
                                int_p = anova_table.loc[f'C({self.grouping_factor}):C({self.grouping_factor2})', 'PR(>F)']
                                
                                test_results = {
                                    'test_type': 'Two-way ANOVA',
                                    'factor1': self.grouping_factor,
                                    'factor2': self.grouping_factor2,
                                    'factor1_f': float(f1_f) if pd.notna(f1_f) else 0.0, # type: ignore
                                    'factor1_p': float(f1_p) if pd.notna(f1_p) else 1.0, # type: ignore
                                    'factor1_significant': (float(f1_p) < 0.05) if pd.notna(f1_p) else False, # type: ignore
                                    'factor2_f': float(f2_f) if pd.notna(f2_f) else 0.0, # type: ignore
                                    'factor2_p': float(f2_p) if pd.notna(f2_p) else 1.0, # type: ignore
                                    'factor2_significant': (float(f2_p) < 0.05) if pd.notna(f2_p) else False, # type: ignore
                                    'interaction_f': float(int_f) if pd.notna(int_f) else 0.0, # type: ignore
                                    'interaction_p': float(int_p) if pd.notna(int_p) else 1.0, # type: ignore
                                    'interaction_significant': (float(int_p) < 0.05) if pd.notna(int_p) else False, # type: ignore
                                    'r_squared': float(model.rsquared),
                                    'adj_r_squared': float(model.rsquared_adj),
                                    'n_observations': len(anova_data)
                                }
                                
                                # Add descriptive statistics by combination of factors
                                descriptive_2way = {}
                                grouped = anova_data.groupby([self.grouping_factor, self.grouping_factor2])[metric]
                                for (f1_val, f2_val), group_data in grouped:
                                    key = f"{f1_val}_{f2_val}"
                                    descriptive_2way[f'{key}_mean'] = float(group_data.mean())
                                    descriptive_2way[f'{key}_std'] = float(group_data.std())
                                    descriptive_2way[f'{key}_n'] = len(group_data)
                                
                                test_results['descriptive_2way'] = descriptive_2way
                                
                        except Exception as e:
                            test_results = {'error': f'Two-way ANOVA failed: {str(e)}'}
                
                else:
                    test_results = {'error': f'Invalid test configuration: {self.test_type} with {len(group_values)} groups'}
                
                results[metric] = {
                    'descriptive': descriptive,
                    'test_results': test_results,
                    'groups': group_names,
                    'n_per_group': [len(group) for group in group_values]
                }
            
            self.progress_update.emit("Analysis complete!")
            self.results_ready.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(f"Analysis failed: {str(e)}")


class StatisticalAnalysisTab(QWidget):
    """Widget containing the statistical analysis functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.scaling_manager = get_scaling_manager()
        
        # Data attributes
        self.metrics_dataframe: Optional[DataFrame] = None
        self.yaml_config: Optional[Dict] = None
        self.grouping_factors: List[str] = []
        
        # UI components
        self.factor_combo: Optional[QComboBox] = None
        self.metrics_list: Optional[QListWidget] = None
        self.test_type_combo: Optional[QComboBox] = None
        self.results_text: Optional[QTextEdit] = None
        self.results_table: Optional[QTableWidget] = None
        self.progress_bar: Optional[QProgressBar] = None
        
        # Worker thread
        self.analysis_worker: Optional[StatisticalAnalysisWorker] = None
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the user interface for the statistical analysis tab."""
        main_layout = QHBoxLayout(self)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([350, 650])
        
        main_layout.addWidget(splitter)
    
    def create_control_panel(self) -> QWidget:
        """Create the left control panel."""
        # Create scroll area for the control panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(300)  # Ensure minimum width for visibility
        
        panel = QWidget()
        panel.setMinimumHeight(800)  # Ensure content height for scrolling
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("📊 Statistical Analysis")
        title.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(16), QFont.Bold))
        title.setStyleSheet("color: #4dd0e1; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Data loading section
        data_group = QGroupBox("Data Loading")
        data_layout = QVBoxLayout(data_group)
        
        self.load_data_btn = QPushButton("Load Metrics Data")
        self.load_data_btn.clicked.connect(self.load_metrics_data)
        self.load_data_btn.setMinimumHeight(self.scaling_manager.scale_size(40)) # type: ignore
        data_layout.addWidget(self.load_data_btn)
        
        self.data_status_label = QLabel("No data loaded")
        self.data_status_label.setStyleSheet("color: #888; font-style: italic;")
        data_layout.addWidget(self.data_status_label)
        
        layout.addWidget(data_group)
        
        # Grouping factor selection
        factor_group = QGroupBox("Grouping Factor")
        factor_layout = QVBoxLayout(factor_group)
        
        factor_layout.addWidget(QLabel("Select factor for grouping:"))
        self.factor_combo = QComboBox()
        self.factor_combo.currentTextChanged.connect(self.on_factor_changed)
        factor_layout.addWidget(self.factor_combo)
        
        self.factor_info_label = QLabel("")
        self.factor_info_label.setStyleSheet("color: #888; font-size: 10pt;")
        self.factor_info_label.setWordWrap(True)
        factor_layout.addWidget(self.factor_info_label)
        
        layout.addWidget(factor_group)
        
        # Second factor selection (for two-way ANOVA)
        factor2_group = QGroupBox("Second Grouping Factor (Two-way ANOVA only)")
        factor2_layout = QVBoxLayout(factor2_group)
        
        factor2_layout.addWidget(QLabel("Select second factor:"))
        self.factor2_combo = QComboBox()
        self.factor2_combo.currentTextChanged.connect(self.on_factor2_changed)
        factor2_layout.addWidget(self.factor2_combo)
        
        self.factor2_info_label = QLabel("")
        self.factor2_info_label.setStyleSheet("color: #888; font-size: 10pt;")
        self.factor2_info_label.setWordWrap(True)
        factor2_layout.addWidget(self.factor2_info_label)
        
        # Initially hide the second factor group
        factor2_group.setVisible(False)
        self.factor2_group = factor2_group
        
        layout.addWidget(factor2_group)
        
        # Metrics selection
        metrics_group = QGroupBox("Metrics Selection")
        metrics_layout = QVBoxLayout(metrics_group)
        
        metrics_layout.addWidget(QLabel("Select metrics to analyze:"))
        
        # Buttons for select all/none
        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_none_btn = QPushButton("Select None")
        self.select_all_btn.clicked.connect(self.select_all_metrics)
        self.select_none_btn.clicked.connect(self.select_no_metrics)
        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.select_none_btn)
        metrics_layout.addLayout(btn_layout)
        
        self.metrics_list = QListWidget()
        # Use checkbox-based selection instead of multi-selection
        metrics_layout.addWidget(self.metrics_list)
        
        layout.addWidget(metrics_group)
        
        # Test type selection
        test_group = QGroupBox("Statistical Test")
        test_layout = QVBoxLayout(test_group)
        
        test_layout.addWidget(QLabel("Select test type:"))
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(["t-test", "One-way ANOVA", "Two-way ANOVA"])
        self.test_type_combo.currentTextChanged.connect(self.on_test_type_changed)
        test_layout.addWidget(self.test_type_combo)

        self.test_info_label = QLabel("t-test: Compare 2 groups\nOne-way ANOVA: Compare 2+ groups\nTwo-way ANOVA: Analyze interaction between 2 factors")
        self.test_info_label.setStyleSheet("color: #888; font-size: 9pt;")
        test_layout.addWidget(self.test_info_label)
        
        layout.addWidget(test_group)
        
        # Analysis button
        self.analyze_btn = QPushButton("🔬 Run Analysis")
        self.analyze_btn.clicked.connect(self.run_analysis)
        self.analyze_btn.setMinimumHeight(self.scaling_manager.scale_size(50)) # pyright: ignore[reportArgumentType]
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #4CAF50, stop:1 #45a049);
                border: 2px solid #4CAF50;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #45a049, stop:1 #4CAF50);
            }
            QPushButton:disabled {
                background: #666;
                border: 2px solid #666;
                color: #999;
            }
        """)
        layout.addWidget(self.analyze_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        if self.progress_bar:
            self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        # Set the panel as the widget for the scroll area
        scroll_area.setWidget(panel)
        
        return scroll_area
    
    def create_results_panel(self) -> QWidget:
        """Create the right results panel."""
        # Create scroll area for the results panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(400)  # Ensure minimum width for visibility
        
        panel = QWidget()
        panel.setMinimumHeight(600)  # Ensure content height for scrolling
        layout = QVBoxLayout(panel)
        
        # Results title
        title = QLabel("Analysis Results")
        title.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(14), QFont.Bold))
        title.setStyleSheet("color: #4dd0e1; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Results display (tabbed or splitter)
        results_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Text results
        text_group = QGroupBox("Summary")
        text_layout = QVBoxLayout(text_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", self.scaling_manager.scale_font_size(10)))
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 5px;
                color: #f0f0f0;
                padding: 10px;
            }
        """)
        text_layout.addWidget(self.results_text)
        results_splitter.addWidget(text_group)
        
        # Table results
        table_group = QGroupBox("Detailed Results")
        table_layout = QVBoxLayout(table_group)
        
        self.results_table = QTableWidget()
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 5px;
                gridline-color: #555;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QHeaderView::section {
                background-color: #555;
                color: #f0f0f0;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
        """)
        table_layout.addWidget(self.results_table)
        results_splitter.addWidget(table_group)
        
        # Export button
        self.export_btn = QPushButton("💾 Export Results")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        table_layout.addWidget(self.export_btn)
        
        results_splitter.setSizes([200, 300])
        layout.addWidget(results_splitter)
        
        # Initial message
        self.results_text.setText(
            "📋 Welcome to Statistical Analysis!\n\n"
            "Steps to get started:\n"
            "1. Load metrics data from your project\n"
            "2. Select a grouping factor (based on filename structure)\n"
            "3. Choose metrics to analyze\n"
            "4. Select appropriate statistical test\n"
            "5. Run analysis\n\n"
            f"📊 Statistical tests available:\n"
            f"• t-test: Compare means between 2 groups\n"
            f"• ANOVA: Compare means between 2+ groups\n\n"
            f"⚠️ Note: SciPy is {'available' if SCIPY_AVAILABLE else 'NOT available'} for statistical tests."
        )
        
        # Set the panel as the widget for the scroll area
        scroll_area.setWidget(panel)
        
        return scroll_area
    
    def load_metrics_data(self) -> None:
        """Load metrics data from the current project."""
        try:
            if not self.parent_window or not hasattr(self.parent_window, 'folder_path'):
                QMessageBox.warning(self, "Warning", "No project loaded. Please load a project first.")
                return
            
            folder_path = self.parent_window.folder_path
            yaml_path = self.parent_window.yaml_path
            
            # Load CSV data
            csv_path = os.path.join(folder_path, "results", "metrics_dataframe.csv")
            if not os.path.exists(csv_path):
                QMessageBox.warning(self, "Warning", 
                    "No metrics data found. Please run tracking and calculate metrics first.")
                return
            
            self.metrics_dataframe = pd.read_csv(csv_path)
            
            # Load YAML configuration
            if yaml_path and os.path.exists(yaml_path):
                with open(yaml_path, 'r') as f:
                    self.yaml_config = yaml.safe_load(f)
            
            # Extract grouping factors from filename structure
            self.extract_grouping_factors()
            
            # Update UI
            self.update_data_status()
            self.populate_metrics_list()
            self.populate_factor_combo()

            self.analyze_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
    
    def extract_grouping_factors(self) -> None:
        """Extract grouping factors from the dataframe columns."""
        self.grouping_factors = []
        
        if not self.yaml_config or self.metrics_dataframe is None:
            return
        
        filename_structure = self.yaml_config.get('filename_structure', {})
        field_names = filename_structure.get('field_names', [])
        
        if not field_names:
            return
        
        # Check if the field columns exist in the dataframe (they should if construct_metric_dataframe worked)
        existing_fields = [field for field in field_names if field in self.metrics_dataframe.columns]
        
        if existing_fields:
            self.grouping_factors = existing_fields
        else:
            # Fallback: if for some reason the columns don't exist, try to extract from filename column
            if 'Filename' in self.metrics_dataframe.columns:
                sample_filename = self.metrics_dataframe['Filename'].iloc[0] if len(self.metrics_dataframe) > 0 else ""
                base_name = os.path.splitext(sample_filename)[0]
                parts = base_name.split('_')
                
                if len(parts) == len(field_names):
                    self.grouping_factors = field_names
                    # Add extracted factors as columns to dataframe
                    for i, factor_name in enumerate(field_names):
                        self.metrics_dataframe[factor_name] = self.metrics_dataframe['Filename'].apply(
                            lambda x: os.path.splitext(x)[0].split('_')[i] if len(os.path.splitext(x)[0].split('_')) > i else ''
                        )
    
    def update_data_status(self) -> None:
        """Update the data status label."""
        if self.metrics_dataframe is not None:
            n_rows, n_cols = self.metrics_dataframe.shape
            self.data_status_label.setText(f"✅ Loaded: {n_rows} files, {n_cols-1} metrics")
            self.data_status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.data_status_label.setText("❌ No data loaded")
            self.data_status_label.setStyleSheet("color: #f44336;")
    
    def populate_metrics_list(self) -> None:
        """Populate the metrics selection list."""
        if self.metrics_list is None or self.metrics_dataframe is None:
            return
        
        self.metrics_list.clear()
        
        # Get numeric columns (exclude any filename column and grouping factors)
        exclude_cols = self.grouping_factors.copy()
        if 'Filename' in self.metrics_dataframe.columns:
            exclude_cols.append('Filename')
        
        numeric_cols = [col for col in self.metrics_dataframe.columns 
                       if col not in exclude_cols and 
                       pd.api.types.is_numeric_dtype(self.metrics_dataframe[col])]
        
        for col in numeric_cols:
            item = QListWidgetItem(col)
            item.setCheckState(Qt.CheckState(0))  # Qt.Unchecked
            self.metrics_list.addItem(item)
    
    def populate_factor_combo(self) -> None:
        """Populate the grouping factor combo box."""
        if self.factor_combo is None:
            return
        
        self.factor_combo.clear()
        self.factor_combo.addItems(self.grouping_factors)
        
        # Also populate the second factor combo if it exists
        if hasattr(self, 'factor2_combo') and self.factor2_combo is not None:
            self.factor2_combo.clear()
            self.factor2_combo.addItems(self.grouping_factors)
    
    def on_factor_changed(self) -> None:
        """Handle grouping factor selection change."""
        if not self.factor_combo or self.metrics_dataframe is None:
            return
        
        factor = self.factor_combo.currentText()
        if factor in self.metrics_dataframe.columns:
            unique_values = self.metrics_dataframe[factor].unique()
            n_groups = len(unique_values)
            
            info_text = f"Groups found: {', '.join(map(str, unique_values))}\n"
            info_text += f"Number of groups: {n_groups}"
            
            self.factor_info_label.setText(info_text)
    
    def on_test_type_changed(self) -> None:
        """Handle test type selection change."""
        if not self.test_type_combo:
            return
            
        test_type = self.test_type_combo.currentText()
        
        # Show/hide second factor group based on test type
        if hasattr(self, 'factor2_group'):
            self.factor2_group.setVisible(test_type == "Two-way ANOVA")
    
    def on_factor2_changed(self) -> None:
        """Handle second grouping factor selection change."""
        if not self.factor2_combo or self.metrics_dataframe is None:
            return
        
        factor = self.factor2_combo.currentText()
        if factor in self.metrics_dataframe.columns:
            unique_values = self.metrics_dataframe[factor].unique()
            n_groups = len(unique_values)
            
            info_text = f"Groups found: {', '.join(map(str, unique_values))}\n"
            info_text += f"Number of groups: {n_groups}"
            
            self.factor2_info_label.setText(info_text)
    
    def select_all_metrics(self) -> None:
        """Select all metrics in the list."""
        if not self.metrics_list:
            return
        
        for i in range(self.metrics_list.count()):
            item = self.metrics_list.item(i)
            if item:
                item.setCheckState(Qt.CheckState(2))  # Qt.Checked

    def select_no_metrics(self) -> None:
        """Deselect all metrics in the list."""
        if not self.metrics_list:
            return
        
        for i in range(self.metrics_list.count()):
            item = self.metrics_list.item(i)
            if item:
                item.setCheckState(Qt.CheckState(0))  # Qt.Unchecked

    def get_selected_metrics(self) -> List[str]:
        """Get the list of selected metrics."""
        if not self.metrics_list:
            return []
        
        selected = []
        for i in range(self.metrics_list.count()):
            item = self.metrics_list.item(i)
            if item and item.checkState() == Qt.CheckState(2):  # Qt.Checked
                selected.append(item.text())
        
        return selected
    
    def run_analysis(self) -> None:
        """Run the statistical analysis."""
        if not SCIPY_AVAILABLE:
            QMessageBox.warning(self, "Warning", 
                "SciPy is not available. Please install SciPy to run statistical tests.")
            return

        if self.progress_bar is None:
            QMessageBox.critical(self, "Error", "UI components not properly initialized.")
            return
        
        # Validate inputs
        if self.metrics_dataframe is None:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return
        
        selected_metrics = self.get_selected_metrics()
        if not selected_metrics:
            QMessageBox.warning(self, "Warning", "Please select at least one metric.")
            return
        
        grouping_factor = self.factor_combo.currentText() if self.factor_combo else ""
        if not grouping_factor:
            QMessageBox.warning(self, "Warning", "Please select a grouping factor.")
            return
        
        test_type = self.test_type_combo.currentText() if self.test_type_combo else ""
        
        # Get second factor for two-way ANOVA
        grouping_factor2 = None
        if test_type == "Two-way ANOVA":
            if hasattr(self, 'factor2_combo') and self.factor2_combo:
                grouping_factor2 = self.factor2_combo.currentText()
                if not grouping_factor2:
                    QMessageBox.warning(self, "Warning", "Please select a second grouping factor for two-way ANOVA.")
                    return
                if grouping_factor2 == grouping_factor:
                    QMessageBox.warning(self, "Warning", "Please select different factors for two-way ANOVA.")
                    return
                if grouping_factor2 not in self.metrics_dataframe.columns:
                    QMessageBox.warning(self, "Warning", f"Second grouping factor '{grouping_factor2}' not found in data.")
                    return
        
        # Validate grouping factor
        if grouping_factor not in self.metrics_dataframe.columns:
            QMessageBox.warning(self, "Warning", f"Grouping factor '{grouping_factor}' not found in data.")
            return
        
        unique_groups = self.metrics_dataframe[grouping_factor].nunique()
        if test_type == "t-test" and unique_groups != 2:
            QMessageBox.warning(self, "Warning", 
                f"t-test requires exactly 2 groups, but {unique_groups} groups found. Use ANOVA instead.")
            return
        
        if unique_groups < 2:
            QMessageBox.warning(self, "Warning", 
                "Need at least 2 groups for statistical comparison.")
            return
        
        # Start analysis in worker thread
        self.analysis_worker = StatisticalAnalysisWorker(
            self.metrics_dataframe, grouping_factor, selected_metrics, test_type, grouping_factor2
        )
        
        self.analysis_worker.results_ready.connect(self.display_results)
        self.analysis_worker.progress_update.connect(self.update_progress)
        self.analysis_worker.error_occurred.connect(self.handle_error)
        
        # Update UI for analysis
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.analysis_worker.start()
    
    def update_progress(self, message: str) -> None:
        """Update progress display."""
        if self.results_text is not None:
            self.results_text.append(f"⏳ {message}")
            QApplication.processEvents()
    
    def handle_error(self, error_message: str) -> None:
        """Handle analysis errors."""
        self.analyze_btn.setEnabled(True)
        if self.progress_bar:
            self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Analysis Error", error_message)
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """Display the analysis results."""
        self.analyze_btn.setEnabled(True)
        if self.progress_bar:
            self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)
        
        # Clear previous results
        if self.results_text:
            self.results_text.clear()
        if self.results_table:
            self.results_table.clear()
        
        # Display summary
        summary_text = "📊 STATISTICAL ANALYSIS RESULTS\n"
        summary_text += "=" * 50 + "\n\n"
        
        grouping_factor = self.factor_combo.currentText() if self.factor_combo else ""
        test_type = self.test_type_combo.currentText() if self.test_type_combo else ""
        
        summary_text += f"🏷️  Grouping Factor: {grouping_factor}\n"
        summary_text += f"🧪 Test Type: {test_type}\n"
        summary_text += f"📈 Metrics Analyzed: {len(results)}\n\n"
        
        # Prepare table data
        table_data = []
        
        significant_count = 0
        
        for metric, result in results.items():
            summary_text += f"\n📊 METRIC: {metric}\n"
            summary_text += "-" * 30 + "\n"
            
            if 'error' in result:
                summary_text += f"❌ Error: {result['error']}\n"
                continue
            
            # Descriptive statistics
            descriptive = result.get('descriptive', {})
            test_results = result.get('test_results', {})
            
            summary_text += "📈 Descriptive Statistics:\n"
            
            # Group by group analysis
            groups = result.get('groups', [])
            for group in groups:
                mean_key = f'{group}_mean'
                std_key = f'{group}_std'
                n_key = f'{group}_n'
                
                if mean_key in descriptive:
                    mean_val = descriptive[mean_key]
                    std_val = descriptive[std_key]
                    n_val = descriptive[n_key]
                    
                    summary_text += f"  • {group}: M={mean_val:.3f}, SD={std_val:.3f}, n={n_val}\n"
            
            # Test results
            if test_results and 'error' not in test_results:
                summary_text += f"\n🧪 {test_results.get('test_type', 'Statistical Test')}:\n"
                statistic = test_results.get('statistic', 0)
                p_value = test_results.get('p_value', 1)
                significant = test_results.get('significant', False)
                
                summary_text += f"  • Statistic: {statistic:.4f}\n"
                summary_text += f"  • p-value: {p_value:.6f}\n"
                summary_text += f"  • Significant: {'YES' if significant else 'NO'} (α = 0.05)\n"
                
                if significant:
                    significant_count += 1
                
                # Additional info for t-test
                if 'levene_p' in test_results:
                    levene_p = test_results['levene_p']
                    equal_var = test_results.get('equal_variances', True)
                    summary_text += f"  • Equal variances: {'YES' if equal_var else 'NO'} (Levene p={levene_p:.4f})\n"
                
                # Additional info for ANOVA
                if 'df_between' in test_results:
                    df_between = test_results['df_between']
                    df_within = test_results['df_within']
                    summary_text += f"  • df: {df_between}, {df_within}\n"
                
                # Additional info for Two-way ANOVA
                if test_results.get('test_type') == 'Two-way ANOVA':
                    factor1 = test_results.get('factor1', '')
                    factor2 = test_results.get('factor2', '')
                    
                    summary_text += f"\n  📈 Factor 1 ({factor1}):\n"
                    summary_text += f"    • F = {test_results.get('factor1_f', 0):.4f}\n"
                    summary_text += f"    • p = {test_results.get('factor1_p', 1):.6f}\n"
                    summary_text += f"    • Significant: {'YES' if test_results.get('factor1_significant', False) else 'NO'}\n"
                    
                    summary_text += f"\n  📈 Factor 2 ({factor2}):\n"
                    summary_text += f"    • F = {test_results.get('factor2_f', 0):.4f}\n"
                    summary_text += f"    • p = {test_results.get('factor2_p', 1):.6f}\n"
                    summary_text += f"    • Significant: {'YES' if test_results.get('factor2_significant', False) else 'NO'}\n"
                    
                    summary_text += f"\n  🔄 Interaction ({factor1} × {factor2}):\n"
                    summary_text += f"    • F = {test_results.get('interaction_f', 0):.4f}\n"
                    summary_text += f"    • p = {test_results.get('interaction_p', 1):.6f}\n"
                    summary_text += f"    • Significant: {'YES' if test_results.get('interaction_significant', False) else 'NO'}\n"
                    
                    r_squared = test_results.get('r_squared', 0)
                    adj_r_squared = test_results.get('adj_r_squared', 0)
                    summary_text += f"\n  📊 Model Fit:\n"
                    summary_text += f"    • R² = {r_squared:.4f}\n"
                    summary_text += f"    • Adjusted R² = {adj_r_squared:.4f}\n"
                    
                    # Display descriptive statistics by factor combinations
                    if 'descriptive_2way' in test_results:
                        summary_text += f"\n  📈 Group Means by Factor Combination:\n"
                        desc_2way = test_results['descriptive_2way']
                        for key, value in desc_2way.items():
                            if key.endswith('_mean'):
                                group_name = key.replace('_mean', '').replace('_', ' × ')
                                std_key = key.replace('_mean', '_std')
                                n_key = key.replace('_mean', '_n')
                                std_val = desc_2way.get(std_key, 0)
                                n_val = desc_2way.get(n_key, 0)
                                summary_text += f"    • {group_name}: M={value:.3f}, SD={std_val:.3f}, n={n_val}\n"
                
                # Prepare table row
                if test_results.get('test_type') == 'Two-way ANOVA':
                    # For two-way ANOVA, create multiple rows (one for each effect)
                    factor1 = test_results.get('factor1', '')
                    factor2 = test_results.get('factor2', '')
                    
                    # Factor 1 row
                    table_row1 = {
                        'Metric': metric,
                        'Test': f'Two-way ANOVA: {factor1}',
                        'Statistic': f"{test_results.get('factor1_f', 0):.4f}",
                        'p-value': f"{test_results.get('factor1_p', 1):.6f}",
                        'Significant': 'Yes' if test_results.get('factor1_significant', False) else 'No'
                    }
                    table_data.append(table_row1)
                    
                    # Factor 2 row
                    table_row2 = {
                        'Metric': metric,
                        'Test': f'Two-way ANOVA: {factor2}',
                        'Statistic': f"{test_results.get('factor2_f', 0):.4f}",
                        'p-value': f"{test_results.get('factor2_p', 1):.6f}",
                        'Significant': 'Yes' if test_results.get('factor2_significant', False) else 'No'
                    }
                    table_data.append(table_row2)
                    
                    # Interaction row
                    table_row3 = {
                        'Metric': metric,
                        'Test': f'Two-way ANOVA: {factor1} × {factor2}',
                        'Statistic': f"{test_results.get('interaction_f', 0):.4f}",
                        'p-value': f"{test_results.get('interaction_p', 1):.6f}",
                        'Significant': 'Yes' if test_results.get('interaction_significant', False) else 'No'
                    }
                    table_data.append(table_row3)
                    
                    # Update significant count for two-way ANOVA
                    if test_results.get('factor1_significant', False):
                        significant_count += 1
                    if test_results.get('factor2_significant', False):
                        significant_count += 1
                    if test_results.get('interaction_significant', False):
                        significant_count += 1
                else:
                    # Standard table row for t-test and one-way ANOVA
                    table_row = {
                        'Metric': metric,
                        'Test': test_results.get('test_type', ''),
                        'Statistic': f"{statistic:.4f}",
                        'p-value': f"{p_value:.6f}",
                        'Significant': 'Yes' if significant else 'No'
                    }
                    
                    # Add group means
                    for group in groups:
                        mean_key = f'{group}_mean'
                        if mean_key in descriptive:
                            table_row[f'{group}_Mean'] = f"{descriptive[mean_key]:.3f}"
                    
                    table_data.append(table_row)
                    
                    if significant:
                        significant_count += 1
            
            elif 'error' in test_results:
                summary_text += f"❌ Test Error: {test_results['error']}\n"
        
        # Summary statistics
        summary_text += f"\n📋 SUMMARY\n"
        summary_text += "=" * 20 + "\n"
        summary_text += f"Total metrics tested: {len(results)}\n"
        summary_text += f"Significant results: {significant_count}\n"
        summary_text += f"Non-significant: {len(results) - significant_count}\n"
        
        if significant_count > 0:
            summary_text += f"\n🎯 {significant_count} metric(s) showed significant differences!\n"
        else:
            summary_text += f"\n📊 No significant differences found.\n"

        if self.results_text:
            self.results_text.setText(summary_text)

        # Populate table
        if table_data:
            self.populate_results_table(table_data)
        
        # Store results for export
        self.current_results = results
    
    def populate_results_table(self, table_data: List[Dict[str, str]]) -> None:
        """Populate the results table."""
        if not table_data or not self.results_table:
            return
        
        # Get all possible columns
        all_columns = set()
        for row in table_data:
            all_columns.update(row.keys())
        
        columns = list(all_columns)
        
        # Set up table
        self.results_table.setRowCount(len(table_data))
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Populate data
        for row_idx, row_data in enumerate(table_data):
            for col_idx, column in enumerate(columns):
                value = row_data.get(column, "")
                item = QTableWidgetItem(str(value))
                
                # Color significant results
                if column == 'Significant' and value == 'Yes':
                    item.setBackground(QColor(0, 255, 0))  # green
                    item.setForeground(QColor(255, 255, 255))  # white
                elif column == 'Significant' and value == 'No':
                    item.setBackground(QColor(139, 0, 0))  # dark red
                    item.setForeground(QColor(255, 255, 255))  # white
                
                # Note: Item will be editable by default, but functionality should work
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.results_table.resizeColumnsToContents()
    
    def export_results(self) -> None:
        """Export analysis results to file."""
        if not hasattr(self, 'current_results'):
            QMessageBox.warning(self, "Warning", "No results to export.")
            return
        
        try:
            if not self.parent_window or not hasattr(self.parent_window, 'folder_path'):
                QMessageBox.warning(self, "Warning", "No project folder available.")
                return
            
            results_folder = os.path.join(self.parent_window.folder_path, "results")
            os.makedirs(results_folder, exist_ok=True)
            
            # Export text summary
            text_path = os.path.join(results_folder, "statistical_analysis_summary.txt")
            if self.results_text:
                with open(text_path, 'w') as f:
                    f.write(self.results_text.toPlainText())
            
            # Export detailed results as CSV
            csv_path = os.path.join(results_folder, "statistical_analysis_detailed.csv")
            
            detailed_data = []
            for metric, result in self.current_results.items():
                if 'error' in result:
                    continue
                
                descriptive = result.get('descriptive', {})
                test_results = result.get('test_results', {})
                
                if 'error' in test_results:
                    continue
                
                row = {'Metric': metric}
                row.update(descriptive)
                row.update(test_results)
                detailed_data.append(row)
            
            if detailed_data:
                df_export = pd.DataFrame(detailed_data)
                df_export.to_csv(csv_path, index=False)
            
            QMessageBox.information(self, "Export Complete", 
                f"Results exported to:\n• {text_path}\n• {csv_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")
    
    def refresh_data(self) -> None:
        """Refresh data from the parent window if available."""
        if self.parent_window and hasattr(self.parent_window, 'metrics_dataframe'):
            if self.parent_window.metrics_dataframe is not None:
                self.metrics_dataframe = self.parent_window.metrics_dataframe
                
                # Also get the YAML config
                if hasattr(self.parent_window, 'yaml_path') and self.parent_window.yaml_path:
                    try:
                        with open(self.parent_window.yaml_path, 'r') as f:
                            self.yaml_config = yaml.safe_load(f)
                    except Exception:
                        # Silently handle YAML loading errors to prevent dialog flashes
                        pass
                
                # Extract grouping factors
                self.extract_grouping_factors()
                
                # Update UI
                self.update_data_status()
                self.populate_metrics_list()
                self.populate_factor_combo()
