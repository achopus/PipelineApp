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
    QTextEdit
)
from PyQt5.QtCore import Qt

from gui.style import PROJECT_FOLDER


class CreateProjectDialog(QDialog):
    """Dialog to create a new project."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setModal(True)
        self.resize(800, 1000)

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
        folder_layout.addWidget(self.folder_field)
        btn_select_folder = QPushButton("Select Folder")
        btn_select_folder.setFixedSize(120, 30)
        btn_select_folder.clicked.connect(self.select_folder)
        folder_layout.addWidget(btn_select_folder)
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
        filename_layout.addWidget(self.field_names_list)
        
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

        # Initialize field names
        self.update_field_names()
        
        # Initial validation (in case fields have default text)
        self.validate()

    def update_field_names(self) -> None:
        """Update the field names list based on the number of fields."""
        self.field_names_list.clear()
        num_fields = self.num_fields_spin.value()

        default_names = ["Subject", "Treatment", "Dosage", "Experiment Type", "Arena", "Empty 1", "Empty 2", "Empty 3", "Empty 4", "Empty 5"]

        for i in range(num_fields):
            default_name = default_names[i] if i < len(default_names) else f"field_{i+1}"
            item = QLineEdit(default_name)
            item.textChanged.connect(self.validate)
            self.field_names_list.addItem("")
            self.field_names_list.setItemWidget(self.field_names_list.item(i), item)
        
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
                    for field_name, value in zip(field_names, parts):
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
        # Create progress dialog
        progress_dialog = QProgressDialog(
            "Copying video files to project folder...", 
            "Cancel", 
            0, 
            len(valid_files),
            dialog
        )
        progress_dialog.setWindowTitle("Creating Project")
        progress_dialog.setMinimumDuration(0)  # Show immediately
        progress_dialog.show()
        
        for i, video in enumerate(valid_files):
            if progress_dialog.wasCanceled():
                # Clean up partially created project if cancelled
                import shutil
                shutil.rmtree(project_path)
                raise RuntimeError("Project creation was cancelled by user")
                
            progress_dialog.setLabelText(f"Copying: {video}")
            progress_dialog.setValue(i)
            QApplication.processEvents()  # Keep UI responsive
            
            source_path = os.path.join(dialog.folder_field.text(), video)
            dest_path = os.path.join(project_path, 'videos', video)
            shutil_copy(source_path, dest_path)
        
        progress_dialog.setValue(len(valid_files))  # Complete
        progress_dialog.close()
    
    # Create YAML configuration with filename structure info
    yaml_dict = {
        "project_name": project_name,
        "creation_time": creation_time,
        "author": dialog.author_name.text(),
        "experiment_type": dialog.dropdown.currentText(),
        "filename_structure": {
            "num_fields": expected_fields,
            "field_names": field_names,
            "description": f"Filenames should have {expected_fields} fields separated by '_': " + 
                          " _ ".join(field_names)
        }
    }
    
    yaml_path = os.path.join(project_path, "config.yaml")
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_dict, f, default_flow_style=False, allow_unicode=True)
    
    return yaml_path