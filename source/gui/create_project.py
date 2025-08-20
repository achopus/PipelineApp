import os
from datetime import datetime
from typing import Optional

import yaml
from shutil import copy as shutil_copy

from PyQt5.QtWidgets import (
    QHBoxLayout, 
    QComboBox, 
    QLineEdit, 
    QDialog, 
    QVBoxLayout, 
    QLabel, 
    QPushButton, 
    QFileDialog,
    QWidget,
    QProgressDialog,
    QApplication,
    QSpinBox,
    QListWidget,
    QMessageBox,
    QGroupBox,
    QTextEdit,
    QCheckBox,
    QListWidgetItem
)
from PyQt5.QtCore import Qt, Qt as QtCore, QThread, pyqtSignal

from gui.style import PROJECT_FOLDER


class FileCopyWorker(QThread):
    """Worker thread for copying files during project creation."""
    
    progress_update = pyqtSignal(int, int, str)  # current, total, filename
    copy_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, source_folder: str, dest_folder: str, files_to_copy: list[str]):
        super().__init__()
        self.source_folder = source_folder
        self.dest_folder = dest_folder
        self.files_to_copy = files_to_copy
        self.should_cancel = False
    
    def cancel(self):
        """Cancel the file copying operation."""
        self.should_cancel = True
    
    def run(self):
        """Run the file copying process."""
        try:
            for i, video_file in enumerate(self.files_to_copy):
                if self.should_cancel:
                    return
                
                # Emit progress update
                self.progress_update.emit(i, len(self.files_to_copy), video_file)
                
                # Copy the file
                source_path = os.path.join(self.source_folder, video_file)
                dest_path = os.path.join(self.dest_folder, video_file)
                shutil_copy(source_path, dest_path)
            
            # Emit completion signal
            self.copy_complete.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Error copying files: {str(e)}")


class MergeGroupDialog(QDialog):
    """Dialog to configure a merge group for filename fields."""
    
    def __init__(self, field_names: list[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Configure Merge Group")
        self.setModal(True)
        self.resize(400, 300)
        
        self.field_names = field_names
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Select fields to merge together:"))
        layout.addWidget(QLabel("(Fields will be combined with '_' separator)"))
        
        # Create checkboxes for each field
        self.field_checkboxes = []
        for i, field_name in enumerate(field_names):
            checkbox = QCheckBox(f"{i+1}. {field_name}")
            self.field_checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_selected_indices(self) -> list[int]:
        """Get the indices of selected fields."""
        return [i for i, checkbox in enumerate(self.field_checkboxes) if checkbox.isChecked()]


class FieldMergingDialog(QDialog):
    """Dialog to configure field merging for filename fields."""
    
    def __init__(self, field_names: list[str], existing_merge_groups: list[list[int]], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Configure Field Merging")
        self.setModal(True)
        self.resize(600, 500)
        
        self.field_names = field_names
        self.merge_groups = [group.copy() for group in existing_merge_groups]  # Deep copy
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Field Merging Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        info_label = QLabel("Define which fields should be merged together in the metrics table.\n"
                           "Example: Merge 'Subject' + 'Treatment' to create 'Subject_Treatment' column.")
        info_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(info_label)
        
        # Merge groups configuration
        merge_group = QGroupBox("Merge Groups")
        merge_layout = QVBoxLayout()
        
        self.merge_list = QListWidget()
        self.merge_list.setMaximumHeight(200)
        self.merge_list.setStyleSheet("QListWidget::item { height: 40px; padding: 5px; }")
        merge_layout.addWidget(self.merge_list)
        
        # Buttons for managing merge groups
        buttons_layout = QHBoxLayout()
        self.add_merge_btn = QPushButton("Add Merge Group")
        self.add_merge_btn.clicked.connect(self.add_merge_group)
        self.remove_merge_btn = QPushButton("Remove Selected")
        self.remove_merge_btn.clicked.connect(self.remove_merge_group)
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all_groups)
        
        buttons_layout.addWidget(self.add_merge_btn)
        buttons_layout.addWidget(self.remove_merge_btn)
        buttons_layout.addWidget(self.clear_all_btn)
        buttons_layout.addStretch()
        merge_layout.addLayout(buttons_layout)
        
        merge_group.setLayout(merge_layout)
        layout.addWidget(merge_group)
        
        # Dialog buttons
        dialog_buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; }")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("QPushButton { padding: 8px 16px; border-radius: 4px; }")
        
        dialog_buttons_layout.addStretch()
        dialog_buttons_layout.addWidget(ok_btn)
        dialog_buttons_layout.addWidget(cancel_btn)
        layout.addLayout(dialog_buttons_layout)
        
        self.setLayout(layout)
        
        # Initialize display
        self.update_merge_display()
    
    def add_merge_group(self) -> None:
        """Add a new merge group."""
        if len(self.field_names) < 2:
            QMessageBox.warning(self, "Warning", "Need at least 2 fields to create a merge group.")
            return
        
        dialog = MergeGroupDialog(self.field_names, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_indices = dialog.get_selected_indices()
            if len(selected_indices) < 2:
                QMessageBox.warning(self, "Warning", "Please select at least 2 fields to merge.")
                return
            
            # Check for overlapping merge groups
            for existing_group in self.merge_groups:
                if any(idx in existing_group for idx in selected_indices):
                    QMessageBox.warning(self, "Warning", 
                        "One or more selected fields are already in another merge group. "
                        "Each field can only be in one merge group.")
                    return
            
            self.merge_groups.append(selected_indices)
            self.update_merge_display()
    
    def remove_merge_group(self) -> None:
        """Remove the selected merge group."""
        current_row = self.merge_list.currentRow()
        if current_row >= 0 and current_row < len(self.merge_groups):
            self.merge_groups.pop(current_row)
            self.update_merge_display()
    
    def clear_all_groups(self) -> None:
        """Clear all merge groups."""
        if self.merge_groups:
            reply = QMessageBox.question(self, "Confirm Clear", 
                "Are you sure you want to remove all merge groups?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.merge_groups = []
                self.update_merge_display()
    
    def update_merge_display(self) -> None:
        """Update the merge groups display."""
        self.merge_list.clear()
        
        for i, group in enumerate(self.merge_groups):
            group_names = [self.field_names[idx] for idx in group if idx < len(self.field_names)]
            merge_name = " + ".join(group_names)
            result_name = "_".join(group_names)
            display_text = f"Group {i+1}: {merge_name} → {result_name}"
            self.merge_list.addItem(display_text)
    
    def get_merge_groups(self) -> list[list[int]]:
        """Get the configured merge groups."""
        return [group.copy() for group in self.merge_groups]


class CreateProjectDialog(QDialog):
    """Dialog to create a new project."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setModal(True)
        self.resize(1200, 1000)

        layout = QVBoxLayout()

        # Project name
        layout.addWidget(QLabel("Project Name:"))
        self.project_name = QLineEdit()
        layout.addWidget(self.project_name)
        self.project_name.textChanged.connect(self.validate)

        # Author
        layout.addWidget(QLabel("Author:"))
        self.author_name = QLineEdit()
        layout.addWidget(self.author_name)
        self.author_name.textChanged.connect(self.validate)

        # Project type
        layout.addWidget(QLabel("Experiment type:"))
        self.dropdown = QComboBox()
        self.dropdown.addItems(["OFT", "EPM (Not implemented)", "[PLACEHOLDER]"])
        layout.addWidget(self.dropdown)

        # Source folder selection
        folder_layout = QHBoxLayout()
        self.folder_field = QLineEdit()
        self.folder_field.setReadOnly(True)
        self.folder_field.setFixedHeight(40)  # Match button height
        folder_layout.addWidget(self.folder_field)
        btn_select_folder = QPushButton("Select Folder")
        btn_select_folder.setFixedSize(120, 40)  # Match field height
        btn_select_folder.clicked.connect(self.select_folder)
        folder_layout.addWidget(btn_select_folder)
        folder_layout.setAlignment(QtCore.AlignmentFlag.AlignCenter)  # Center both horizontally and vertically
        layout.addWidget(QLabel("Source Folder:"))
        layout.addLayout(folder_layout)

        # Filename structure configuration
        self.filename_group = QGroupBox("Filename Structure Configuration")
        filename_layout = QVBoxLayout()
        
        # Number of fields
        fields_layout = QHBoxLayout()
        fields_layout.addWidget(QLabel("Number of filename fields (separated by '_'):"))
        self.num_fields_spin = QSpinBox()
        self.num_fields_spin.setMinimum(1)
        self.num_fields_spin.setMaximum(10)
        self.num_fields_spin.setValue(3)
        self.num_fields_spin.valueChanged.connect(self.update_field_names)
        fields_layout.addWidget(self.num_fields_spin)
        fields_layout.addStretch()
        filename_layout.addLayout(fields_layout)
        
        # Field names
        filename_layout.addWidget(QLabel("Field Names:"))
        self.field_names_list = QListWidget()
        self.field_names_list.setMaximumHeight(200)
        # Set list item height for better visibility
        self.field_names_list.setStyleSheet("QListWidget::item { height: 50px; }")
        filename_layout.addWidget(self.field_names_list)
        
        # Field merging configuration button
        merge_button_layout = QHBoxLayout()
        self.configure_merging_btn = QPushButton("Configure Field Merging...")
        self.configure_merging_btn.clicked.connect(self.open_field_merging_dialog)
        self.configure_merging_btn.setFixedHeight(40)
        self.configure_merging_btn.setStyleSheet("QPushButton { padding: 10px; }")
        merge_button_layout.addWidget(self.configure_merging_btn)
        #merge_button_layout.addStretch()
        filename_layout.addLayout(merge_button_layout)
        filename_layout.addSpacing(10)
        
        # Merge status display
        self.merge_status_label = QLabel("No field merging configured")
        self.merge_status_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        filename_layout.addWidget(self.merge_status_label)
        
        # Preview area
        filename_layout.addWidget(QLabel("Filename Validation Preview:"))
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(250)
        self.preview_text.setReadOnly(True)
        filename_layout.addWidget(self.preview_text)
        
        # Validate button
        self.validate_btn = QPushButton("Validate Filenames")
        self.validate_btn.clicked.connect(self.validate_filenames)
        self.validate_btn.setEnabled(False)
        filename_layout.addWidget(self.validate_btn)
        
        self.filename_group.setLayout(filename_layout)
        layout.addWidget(self.filename_group)

        # OK and Cancel buttons
        buttons_layout = QHBoxLayout()
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setEnabled(False)  # disabled initially
        self.btn_ok.setStyleSheet("border: 1px solid red;")
        self.btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Initialize merge groups first
        self.merge_groups = []  # List of lists, each containing field indices that should be merged

        # Initialize field names
        self.update_field_names()
        
        # Initial validation (in case fields have default text)
        self.validate()

    def open_field_merging_dialog(self) -> None:
        """Open the field merging configuration dialog."""
        field_names = self.get_field_names()
        if len(field_names) < 2:
            QMessageBox.warning(self, "Warning", "Need at least 2 fields to configure field merging.")
            return
        
        dialog = FieldMergingDialog(field_names, self.merge_groups, self)
        if dialog.exec_() == QDialog.Accepted:
            self.merge_groups = dialog.get_merge_groups()
            self.update_merge_status_display()

    def update_merge_status_display(self) -> None:
        """Update the merge status display."""
        if not self.merge_groups:
            self.merge_status_label.setText("No field merging configured")
            self.merge_status_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        else:
            field_names = self.get_field_names()
            status_text = f"Field merging configured ({len(self.merge_groups)} group{'s' if len(self.merge_groups) > 1 else ''}):\n"
            
            for i, group in enumerate(self.merge_groups):
                group_names = [field_names[idx] for idx in group if idx < len(field_names)]
                merge_name = " + ".join(group_names)
                status_text += f"  Group {i+1}: {merge_name}\n"
            
            self.merge_status_label.setText(status_text.strip())
            self.merge_status_label.setStyleSheet("color: #4CAF50; padding: 5px; font-weight: bold;")

    def get_merge_groups(self) -> list:
        """Get the current merge groups configuration."""
        return self.merge_groups.copy()

    def apply_merge_groups(self, field_names: list[str], field_values: list[str]) -> tuple[list[str], list[str]]:
        """Apply merge groups to field names and values."""
        if not self.merge_groups:
            return field_names, field_values
        
        # Create sets to track which indices are merged
        merged_indices = set()
        for group in self.merge_groups:
            merged_indices.update(group)
        
        merged_field_names = []
        merged_values = []
        
        # Add merged groups first
        for group in self.merge_groups:
            group_names = [field_names[i] for i in group if i < len(field_names)]
            group_values = [field_values[i] for i in group if i < len(field_values)]
            
            merged_name = "_".join(group_names)
            merged_value = "_".join(group_values)
            
            merged_field_names.append(merged_name)
            merged_values.append(merged_value)
        
        # Add non-merged fields
        for i, (name, value) in enumerate(zip(field_names, field_values)):
            if i not in merged_indices:
                merged_field_names.append(name)
                merged_values.append(value)
        
        return merged_field_names, merged_values

    def update_field_names(self) -> None:
        """Update the field names list based on the number of fields."""
        self.field_names_list.clear()
        num_fields = self.num_fields_spin.value()

        default_names = ["Subject", "Treatment", "Dosage", "Experiment Type", "Arena", "Empty 1", "Empty 2", "Empty 3", "Empty 4", "Empty 5"]

        for i in range(num_fields):
            default_name = default_names[i] if i < len(default_names) else f"field_{i+1}"
            item = QLineEdit(default_name)
            item.textChanged.connect(self.validate)
            item.textChanged.connect(self.update_merge_status_display)
            self.field_names_list.addItem("")
            self.field_names_list.setItemWidget(self.field_names_list.item(i), item)
        
        # Clear merge groups if field count changed significantly
        max_field_idx = max([max(group) for group in self.merge_groups] + [-1])
        if max_field_idx >= num_fields:
            self.merge_groups = []
        
        self.update_merge_status_display()
        self.validate()

    def get_field_names(self) -> list[str]:
        """Get the current field names from the list."""
        field_names = []
        for i in range(self.field_names_list.count()):
            widget = self.field_names_list.itemWidget(self.field_names_list.item(i))
            if isinstance(widget, QLineEdit):
                field_names.append(widget.text().strip())
        return field_names

    def validate_filenames(self) -> None:
        """Validate that all video filenames can be split correctly."""
        if not self.folder_field.text():
            QMessageBox.warning(self, "Warning", "Please select a source folder first.")
            return
        
        try:
            source_video_files = [
                vid for vid in os.listdir(self.folder_field.text()) 
                if vid.endswith(('.mp4', '.avi'))
            ]
            
            if not source_video_files:
                self.preview_text.setText("No video files (.mp4, .avi) found in the selected folder.")
                return
            
            expected_fields = self.num_fields_spin.value()
            field_names = self.get_field_names()
            
            valid_files = []
            invalid_files = []
            
            for video_file in source_video_files:
                # Remove extension and split by underscore
                name_without_ext = os.path.splitext(video_file)[0]
                parts = name_without_ext.split('_')
                
                if len(parts) == expected_fields:
                    valid_files.append(video_file)
                else:
                    invalid_files.append(f"{video_file} (has {len(parts)} fields, expected {expected_fields})")
            
            # Display results
            result_text = f"Found {len(source_video_files)} video files:\n"
            result_text += f"✓ Valid: {len(valid_files)} files\n"
            
            if invalid_files:
                result_text += f"✗ Invalid: {len(invalid_files)} files\n"
                result_text += "\nInvalid files:\n" + "\n".join(invalid_files[:5])
                if len(invalid_files) > 5:
                    result_text += f"\n... and {len(invalid_files) - 5} more"
            else:
                result_text += "\nAll files have the correct structure!"
                if valid_files:
                    # Show example parsing
                    example_file = valid_files[0]
                    name_without_ext = os.path.splitext(example_file)[0]
                    parts = name_without_ext.split('_')
                    result_text += f"\n\nExample parsing ({example_file}):\n"
                    
                    # Show both original fields and merged fields
                    result_text += "Original fields:\n"
                    for field_name, value in zip(field_names, parts):
                        result_text += f"  {field_name}: {value}\n"
                    
                    # Show merged fields if any
                    if self.merge_groups:
                        result_text += "\nAfter merging:\n"
                        merged_field_names, merged_values = self.apply_merge_groups(field_names, parts)
                        for field_name, value in zip(merged_field_names, merged_values):
                            result_text += f"  {field_name}: {value}\n"
            
            self.preview_text.setText(result_text)
            
            # Enable/disable OK button based on validation
            if invalid_files:
                QMessageBox.warning(self, "Validation Failed", 
                    f"Found {len(invalid_files)} files that don't match the expected filename structure. "
                    "Please check the filename format or adjust the number of fields.")
            
        except Exception as e:
            self.preview_text.setText(f"Error validating files: {str(e)}")

    def set_enabled(self, text_name: str, text_author: str, text_folder: str) -> None:
        """Enable or disable the OK button based on field validity."""
        field_names = self.get_field_names()
        valid_field_names = all(name.strip() for name in field_names)
        
        enabled = (bool(text_name.strip()) and 
                  bool(text_author.strip()) and 
                  bool(text_folder.strip()) and 
                  valid_field_names)
        
        self.btn_ok.setEnabled(enabled)
        self.validate_btn.setEnabled(bool(text_folder.strip()))
        
        if enabled:
            self.btn_ok.setStyleSheet("border: 1px solid green;")
        else:
            self.btn_ok.setStyleSheet("border: 1px solid red;")

    def select_folder(self) -> None:
        """Open a dialog to select the source folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.folder_field.setText(folder)
            self.preview_text.clear()  # Clear previous validation results
            self.validate()  # validate after setting folder

    def validate(self) -> None:
        """Validate all input fields and update UI accordingly."""
        # Read current texts
        name = self.project_name.text()
        author = self.author_name.text()
        folder = self.folder_field.text()

        # Enable/disable OK button
        self.set_enabled(name, author, folder)

        # Border colors: red if empty, green if filled
        self.set_field_color(self.project_name, name)
        self.set_field_color(self.author_name, author)
        self.set_field_color(self.folder_field, folder)

    def set_field_color(self, field: QLineEdit, text: str) -> None:
        """Set the border color of a field based on whether it has text."""
        if text.strip():
            field.setStyleSheet("border: 1px solid green;")
        else:
            field.setStyleSheet("border: 1px solid red;")


def create_project_folder(dialog: CreateProjectDialog) -> str:
    """
    Create a new project folder structure and configuration file.
    
    Args:
        dialog: The dialog containing project information
        
    Returns:
        str: Path to the created YAML configuration file
    """
    if not os.path.exists(PROJECT_FOLDER):
        os.mkdir(PROJECT_FOLDER)
    
    # Main folder creation
    project_name = dialog.project_name.text()
    creation_time = datetime.now()
    folder_name = f"{project_name}_{creation_time.strftime('%d_%m_%Y__%H_%M')}"
    
    project_path = os.path.join(PROJECT_FOLDER, folder_name)
    if os.path.exists(project_path):
        raise ValueError(f"This project already exists. Choose a different name.")
    os.mkdir(project_path)
    
    # Subfolder creation
    subfolders = ['videos', 'points', 'videos_preprocessed', 'tracking', 'results', 'images']
    for subfolder in subfolders:
        os.mkdir(os.path.join(project_path, subfolder))
        
    # Get filename structure info
    expected_fields = dialog.num_fields_spin.value()
    field_names = dialog.get_field_names()
    merge_groups = dialog.get_merge_groups()
    
    # Video copy to project folder with validation
    source_video_files = [
        vid for vid in os.listdir(dialog.folder_field.text()) 
        if vid.endswith(('.mp4', '.avi'))
    ]
    
    # Validate all filenames before copying
    invalid_files = []
    valid_files = []
    
    for video_file in source_video_files:
        name_without_ext = os.path.splitext(video_file)[0]
        parts = name_without_ext.split('_')
        
        if len(parts) == expected_fields:
            valid_files.append(video_file)
        else:
            invalid_files.append(video_file)
    
    if invalid_files:
        # Clean up the created project folder
        import shutil
        shutil.rmtree(project_path)
        raise ValueError(f"Found {len(invalid_files)} files with incorrect filename structure. "
                        f"Expected {expected_fields} fields separated by '_'. "
                        f"Invalid files: {', '.join(invalid_files[:3])}"
                        f"{'...' if len(invalid_files) > 3 else ''}")
    
    if valid_files:
        # Use threaded file copying
        success = _copy_files_threaded(
            dialog.folder_field.text(),
            os.path.join(project_path, 'videos'),
            valid_files,
            dialog
        )
        
        if not success:
            # Clean up partially created project if cancelled or failed
            import shutil
            shutil.rmtree(project_path)
            raise RuntimeError("Project creation was cancelled or failed")
    
    # Create YAML configuration with filename structure info
    yaml_dict = {
        "project_name": project_name,
        "creation_time": creation_time,
        "author": dialog.author_name.text(),
        "experiment_type": dialog.dropdown.currentText(),
        "filename_structure": {
            "num_fields": expected_fields,
            "field_names": field_names,
            "merge_groups": merge_groups,
            "description": f"Filenames should have {expected_fields} fields separated by '_': " + 
                          " _ ".join(field_names)
        }
    }
    
    yaml_path = os.path.join(project_path, "config.yaml")
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_dict, f, default_flow_style=False, allow_unicode=True)
    
    return yaml_path


def _copy_files_threaded(source_folder: str, dest_folder: str, files_to_copy: list[str], parent_dialog) -> bool:
    """
    Copy files using a background thread with progress dialog.
    
    Args:
        source_folder: Source directory path
        dest_folder: Destination directory path  
        files_to_copy: List of filenames to copy
        parent_dialog: Parent dialog for progress display
        
    Returns:
        bool: True if successful, False if cancelled or failed
    """
    # Create progress dialog
    progress_dialog = QProgressDialog(
        "Copying video files to project folder...", 
        "Cancel", 
        0, 
        len(files_to_copy),
        parent_dialog
    )
    progress_dialog.setWindowTitle("Creating Project")
    progress_dialog.setMinimumDuration(0)  # Show immediately
    progress_dialog.setModal(True)
    
    # Create and configure the worker thread
    copy_worker = FileCopyWorker(source_folder, dest_folder, files_to_copy)
    
    # Track completion status
    copy_success = [False]  # Use list to allow modification in nested functions
    copy_error = [None]  # type: list[Optional[str]]
    
    def on_progress_update(current: int, total: int, filename: str):
        """Handle progress updates from the worker thread."""
        progress_dialog.setLabelText(f"Copying: {filename}")
        progress_dialog.setValue(current)
        
        # Check if user cancelled
        if progress_dialog.wasCanceled():
            copy_worker.cancel()
    
    def on_copy_complete():
        """Handle successful completion of file copying."""
        copy_success[0] = True
        progress_dialog.setValue(len(files_to_copy))  # Complete
        progress_dialog.accept()  # Close dialog
    
    def on_copy_error(error_message: str):
        """Handle errors during file copying."""
        copy_error[0] = error_message
        progress_dialog.reject()  # Close dialog
    
    # Connect worker signals
    copy_worker.progress_update.connect(on_progress_update)
    copy_worker.copy_complete.connect(on_copy_complete)
    copy_worker.error_occurred.connect(on_copy_error)
    
    # Start the worker and show progress dialog
    copy_worker.start()
    result = progress_dialog.exec_()  # This blocks until dialog is closed
    
    # Wait for worker to finish
    copy_worker.wait()
    
    # Handle results
    if copy_error[0]:
        QMessageBox.critical(parent_dialog, "Copy Error", 
                           f"An error occurred while copying files:\n\n{copy_error[0]}")
        return False
    elif result == QDialog.Rejected and not copy_success[0]:
        # User cancelled
        return False
    else:
        return copy_success[0]