# PipelineApp - Video Tracking Pipeline

A comprehensive PyQt5-based GUI application for automated behavioral analysis of animal experiments, specifically designed for Open Field Test (OFT) and Elevated Plus Maze (EPM) paradigms. The application provides an end-to-end pipeline from video annotation to metrics calculation with cluster computing support.

## 🎯 Features

### **Project Management**
- Create and manage behavioral experiment projects
- Configurable filename structure validation for organized data
- Project configuration stored in YAML format
- Support for multiple experiment types (OFT, EPM)

### **Video Processing Pipeline**
1. **Video Points Annotation** - Mark arena corners and reference points
2. **Cluster Preprocessing** - Submit video preprocessing jobs to SLURM cluster
3. **Animal Tracking** - Deep learning-based pose estimation and tracking
4. **Metrics Calculation** - Comprehensive behavioral metrics analysis

### **Advanced Analytics**
- **Trajectory Analysis**: Position tracking and movement patterns
- **Behavioral Metrics**: Distance traveled, velocity, thigmotaxis, center exploration
- **Time-binned Analysis**: Configurable time windows for temporal analysis
- **Visualization**: Publication-ready trajectory plots with heatmaps

### **Cluster Integration**
- SSH-based communication with SLURM clusters
- Automated job submission and monitoring
- Robust error handling and retry mechanisms
- Environment variable configuration for different clusters

## 🚀 Installation

### Prerequisites
- Python 3.11+
- PyQt5
- OpenCV
- NumPy, Pandas, SciPy
- Matplotlib
- SSH access to a SLURM cluster (for processing)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/achopus/PipelineApp.git
   cd PipelineApp
   ```

2. **Install dependencies**
   ```bash
   pip install PyQt5 opencv-python numpy pandas scipy matplotlib paramiko python-dotenv pyyaml tqdm
   ```

3. **Configure environment variables**
   Create a `.env` file in `source/cluster_networking/`:
   ```env
   SSH_HOST=your-cluster-host.com
   SSH_PORT=22
   SSH_USER=your-username
   SSH_PASS=your-password
   CLUSTER_BASE_PATH=/path/to/cluster/data
   CLUSTER_HOME_PATH=/home/your-username
   CLUSTER_CONDA_ENV=your-conda-environment
   PROJECT_FOLDER=//path/to/your/projects
   ```

4. **Run the application**
   ```bash
   python source/main_window.py
   ```

## 📖 Usage Guide

### 1. Project Creation
- **Tab 1: Project Management**
  - Click "Create New Project"
  - Fill in project details (name, author, experiment type)
  - Select source folder containing video files
  - Configure filename structure (number of fields and field names)
  - Validate that all video filenames match the expected structure
  - Videos are copied to the project folder with organized structure

### 2. Video Annotation
- **Tab 2: Video Points Annotation**
  - Click "Open video annotation tool"
  - For each video, mark 4 corner points of the arena:
    - Top-left (red)
    - Top-right (green) 
    - Bottom-right (blue)
    - Bottom-left (orange)
  - Use keyboard shortcuts:
    - Arrow keys: Navigate between videos
    - `R`: Reset current video points
    - `S`: Save progress
  - Submit annotated videos to cluster for preprocessing

### 3. Tracking and Analysis
- **Tab 3: Animal Tracking + Results**
  - Run tracking on preprocessed videos
  - Calculate behavioral metrics
  - View trajectory visualizations
  - Export results as CSV

## 📊 Metrics Calculated

### **Movement Metrics**
- **Total Distance**: Cumulative distance traveled
- **Velocity**: Instantaneous and average movement speed
- **Time Moving**: Percentage of time the animal is active

### **Spatial Metrics**
- **Thigmotaxis**: Preference for arena periphery vs center
- **Center Time**: Time spent in arena center
- **Distance to Wall**: Spatial distribution analysis

### **Temporal Analysis**
- **Time-binned Metrics**: Analysis in configurable time windows (default: 5 minutes)
- **Activity Patterns**: Movement patterns over time

### **Behavioral Indicators**
- **Exploration**: Center exploration vs wall-following behavior
- **Anxiety-like Behavior**: Thigmotaxis and center avoidance measures

## 🏗️ Project Structure

```
PipelineApp/
├── source/
│   ├── main_window.py              # Main application entry point
│   ├── cluster_networking/         # Cluster communication modules
│   │   ├── ssh_handling.py         # SSH and SLURM job management
│   │   ├── preprocessing.py        # Video preprocessing pipeline
│   │   ├── tracking.py             # Animal tracking pipeline
│   │   └── utils.py                # Utility functions
│   ├── file_management/            # File status and management
│   │   ├── active_file_check.py    # File processing status tracking
│   │   └── status.py               # Status enumeration
│   ├── gui/                        # User interface components
│   │   ├── create_project.py       # Project creation dialog
│   │   ├── project_management_tab.py # Project management interface
│   │   ├── video_points_annotation_tab.py # Video annotation interface
│   │   ├── video_points_widget.py  # Video annotation widget
│   │   ├── tracking_results_tab.py # Results and metrics interface
│   │   └── style.py                # GUI styling and constants
│   └── metric_calculation/         # Behavioral analysis modules
│       ├── metrics_pipeline.py     # Main metrics calculation pipeline
│       ├── trajectory.py           # Trajectory processing and analysis
│       ├── metrics.py              # Behavioral metrics calculations
│       ├── visualization.py        # Trajectory plotting and visualization
│       └── utils.py                # Metrics utility functions
└── README.md
```

## 🔧 Configuration

### **Filename Structure Configuration**
Projects support configurable filename structures to organize experimental data:
- Define number of fields (separated by underscores)
- Name each field (e.g., "subject", "condition", "trial")
- Automatic validation ensures all files follow the same structure
- Example: `mouse1_control_trial1.mp4` → subject: "mouse1", condition: "control", trial: "trial1"

### **Cluster Configuration**
The application supports various cluster configurations through environment variables:
- Custom SLURM partition and resource requirements
- Configurable conda environments
- Flexible path mapping between local and cluster filesystems

### **Processing Parameters**
Key processing parameters can be adjusted in the code:
- **Arena size**: Default 80cm x 80cm
- **Detection threshold**: Minimum confidence for pose detection
- **Motion blur sigma**: Gaussian smoothing for trajectory
- **Time bin size**: Temporal analysis window (default: 5 minutes)

## 🎨 User Interface

### **Dark Theme**
- Modern dark theme optimized for extended use
- Color-coded status indicators
- Intuitive tab-based workflow

### **Progress Tracking**
- Real-time progress bars for file operations
- Status visualization for pipeline stages
- Detailed logging and error reporting

### **Interactive Video Annotation**
- Frame-by-frame video navigation
- Visual feedback for annotation points
- Batch processing support

## 🔬 Scientific Applications

This pipeline is designed for:
- **Behavioral Neuroscience**: Anxiety, depression, locomotor activity studies
- **Pharmacology**: Drug effects on behavior and movement
- **Genetic Studies**: Behavioral phenotyping of transgenic animals
- **Environmental Studies**: Effects of environmental factors on behavior

### **Supported Paradigms**
- **Open Field Test (OFT)**: General locomotor activity and anxiety-like behavior
- **Elevated Plus Maze (EPM)**: Anxiety-related behavior (planned implementation)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for behavioral neuroscience research
- Designed for high-throughput experimental workflows
- Optimized for cluster computing environments

## 📞 Support

For questions or issues:
1. Check the project status indicators in Tab 1
2. Review the processing logs for error messages
3. Ensure cluster connectivity and credentials are correct
4. Verify video file formats and filename structure

---

**Note**: This application requires access to a SLURM cluster for video preprocessing and tracking. Local processing capabilities may be added in future versions.