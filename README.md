# PipelineApp - Video Tracking Pipeline

A comprehensive PyQt5-based GUI application for automated behavioral analysis of animal experiments, designed for Open Field Test (OFT) and Elevated Plus Maze (EPM) paradigms. This application provides an end-to-end pipeline from video annotation to comprehensive behavioral metrics analysis with integrated statistical testing capabilities.

## 🎯 Key Features

### **Complete Analysis Pipeline**
- **Project Management**: Create and organize behavioral experiment projects with configurable filename structures
- **Video Points Annotation**: Mark arena corners with visual feedback for spatial calibration
- **Cluster Processing**: Submit videos for preprocessing and tracking analysis via SLURM cluster
- **Metrics Calculation**: Generate comprehensive behavioral measurements with temporal binning
- **Statistical Analysis**: Built-in statistical testing with t-tests, one-way ANOVA, and two-way ANOVA

### **Advanced Analytics**
- **Movement Analysis**: Velocity calculation, distance tracking, and activity patterns
- **Spatial Behavior**: Thigmotaxis, center exploration, and wall proximity analysis
- **Temporal Patterns**: Configurable time-binned analysis (default: 5-minute windows)
- **Statistical Testing**: Comprehensive statistical analysis with effect sizes and post-hoc tests
- **Visualization**: Trajectory plots with publication-ready image exports

## 🚀 Installation

### Prerequisites
- Python 3.11+
- SSH access to a SLURM cluster (for video processing)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/achopus/PipelineApp.git
   cd PipelineApp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
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

## 📖 How to Use the Application

### 1. Project Management (Tab 1)
**Navigate to Tab 1: Project Management**

1. **Create New Project**:
   - Click **"🖊️ Create New Project"**
   - Fill in project details (name, author, experiment type)
   - Select folder containing your video files
   - Configure filename structure:
     - Set number of fields (separated by underscores)
     - Name each field (e.g., "Subject", "Treatment", "Day")
     - Optional: Set up field merging for statistical grouping
   - Example: `Mouse1_Control_Low_Day1.mp4` → 4 fields

2. **Load Existing Project**:
   - Click **"📂 Load Existing Project"**
   - Select project YAML file
   - Project details and progress status will be displayed

### 2. Video Points Annotation (Tab 2)
**Navigate to Tab 2: Video Points Annotation**

1. **Mark Arena Corners** for each video (4 points required):
   - **Top-left corner** (red point)
   - **Top-right corner** (green point) 
   - **Bottom-right corner** (blue point)
   - **Bottom-left corner** (orange point)

2. **Navigation and Controls**:
   - **Arrow keys**: Navigate between videos
   - **R key**: Reset points for current video
   - **S key**: Save progress
   - **Mouse clicks**: Place corner points

3. **Submit for Processing**: Click "Process data on computational cluster" when all videos are annotated

### 3. Animal Tracking + Results (Tab 3)
**Navigate to Tab 3: Animal Tracking + Results**

1. **Run Tracking**: 
   - Click **"🚀 Run Tracking"** to submit videos to cluster
   - Expected runtime notification will be displayed
   - Track progress via status updates

2. **Calculate Results**:
   - Click **"📊 Get Results"** after tracking is complete
   - Metrics will be calculated for all tracked videos
   - Progress updates shown during calculation

3. **View Results**:
   - **Trajectory Preview**: Browse generated trajectory images
   - **Metrics Table**: View calculated behavioral metrics
   - **Folder Access**: Quick access to images and results folders

### 4. Statistical Analysis (Tab 4)
**Navigate to Tab 4: Statistical Analysis**

1. **Load Data**: Import CSV results file with automatic filename parsing
2. **Configure Analysis**:
   - Select **grouping factors** from your filename structure
   - Choose **behavioral metrics** to analyze
   - Select **statistical test**:
     - **t-test**: Compare exactly 2 groups
     - **One-way ANOVA**: Compare multiple groups with one factor
     - **Two-way ANOVA**: Analyze two factors and their interaction
3. **Run Analysis**: Click "🔬 Run Analysis" for comprehensive statistical output
4. **Export Results**: Save statistical summaries and detailed results

## 📊 Behavioral Metrics Calculated

### **Core Movement Metrics**
- **`total_distance`**: Total distance traveled throughout session
- **`is_moving`**: Proportion of time animal is actively moving
- **Velocity calculations**: Speed analysis with configurable thresholds

### **Spatial Behavior Metrics**
- **`thigmotaxis`**: Wall-hugging behavior (0 = center preference, 1 = wall preference)
- **`is_center`**: Proportion of time spent in arena center
- **`is_moving_in_center`**: Active exploration of center region
- **Distance to wall**: Proximity analysis to arena boundaries

### **Temporal Analysis**
- **Time-binned distances**: Distance traveled in configurable time windows
- **Format**: `D_0_to_5`, `D_5_to_10`, etc. (default 5-minute bins)
- **Adaptive binning**: Automatically handles sessions of different lengths

### **Advanced Metrics**
- **Velocity thresholding**: Configurable minimum velocity for movement detection
- **Motion smoothing**: Gaussian filtering for trajectory noise reduction
- **Arena size normalization**: Automatic scaling based on arena dimensions

## 📈 Statistical Analysis Features

### **Automatic Data Processing**
- **Filename Parsing**: Extracts experimental factors from video filenames
- **Data Validation**: Ensures consistent grouping and data quality
- **Missing Data Handling**: Robust processing of incomplete datasets

### **Statistical Tests Available**

#### **Independent t-test**
- Compare behavioral metrics between exactly 2 groups
- Levene's test for variance equality assessment
- Welch's t-test for unequal variances when needed
- Comprehensive descriptive statistics

#### **One-way ANOVA**
- Compare multiple groups on behavioral measures
- F-statistics with degrees of freedom
- Significance testing with p-values
- Automatic Tukey HSD post-hoc testing (when statsmodels available)

#### **Two-way ANOVA**
- Analyze main effects and interactions between two factors
- Factor A and Factor B main effects
- A × B interaction effects
- R² and adjusted R² for effect size quantification
- Model fit assessment

### **Results Presentation**
- **Comprehensive Output**: Descriptive statistics, test results, and effect sizes
- **Significance Indicators**: Clear marking of significant results
- **Export Options**: Multiple file formats for publication and archiving
- **Real-time Processing**: Threaded analysis prevents interface freezing

## 🏗️ Project Structure

```
PipelineApp/
├── source/
│   ├── main_window.py                    # Application entry point
│   ├── cluster_networking/               # Cluster communication
│   │   ├── ssh_handling.py               # SSH and SLURM management
│   │   ├── preprocessing.py              # Video preprocessing pipeline
│   │   ├── tracking.py                   # Animal tracking pipeline
│   │   └── expected_runtime.py           # Runtime estimation
│   ├── file_management/                  # File operations
│   │   ├── active_file_check.py          # Processing status tracking
│   │   └── status.py                     # Status enumeration
│   ├── gui/                              # User interface
│   │   ├── project_management_tab.py     # Tab 1: Project management
│   │   ├── video_points_annotation_tab.py # Tab 2: Video annotation
│   │   ├── tracking_results_tab.py       # Tab 3: Results and metrics
│   │   ├── statistical_analysis_tab.py   # Tab 4: Statistical analysis
│   │   ├── create_project.py             # Project creation dialog
│   │   ├── manual_dialog.py              # Documentation viewer
│   │   └── scaling.py                    # DPI scaling management
│   ├── metric_calculation/               # Behavioral analysis
│   │   ├── metrics_pipeline.py           # Main metrics pipeline
│   │   ├── metrics.py                    # Core metrics calculations
│   │   ├── trajectory.py                 # Trajectory processing
│   │   └── visualization.py              # Plot generation
│   ├── documentation/                    # Embedded documentation
│   │   ├── readme_content.py             # README content
│   │   ├── statistical_analysis_manual.py # Statistics guide
│   │   ├── field_merging_guide.py        # Field merging tutorial
│   │   └── tukey_hsd_update.py           # Recent updates info
│   └── utils/                            # Utilities
│       └── settings_manager.py           # Configuration management
├── installer/                            # Windows installer
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## 🔧 Configuration

### **Settings Management**
Key parameters can be configured via `utils/settings_manager.py`:
- **Arena dimensions**: Default 80cm × 80cm
- **Velocity threshold**: Minimum speed for movement detection (default: 1.0)
- **Time binning**: Analysis window size (default: 5 minutes)
- **Thigmotaxis bins**: Spatial resolution for wall preference (default: 25 bins)

### **Filename Structure**
Projects support flexible filename structures:
- **Field Definition**: Number and names of filename components
- **Field Merging**: Combine fields for statistical grouping
- **Validation**: Automatic checking of filename consistency
- **Example**: `Subject_Treatment_Dose_Day.mp4` creates 4 grouping factors

### **Cluster Configuration**
Environment variables control cluster interaction:
- **Connection**: SSH credentials and host information
- **Paths**: Local and remote file system mapping
- **Environment**: Conda environment for processing jobs
- **Resources**: SLURM partition and resource allocation

## 🎨 User Interface Features

### **Modern Design**
- **Dark Theme**: Optimized for extended use with reduced eye strain
- **Responsive Layout**: Automatic scaling for different screen sizes
- **Color-coded Status**: Visual indicators for processing pipeline stages
- **Tab-based Workflow**: Logical progression through analysis steps

### **Real-time Feedback**
- **Progress Tracking**: Live updates during long-running operations
- **Status Visualization**: Color-coded file processing status
- **Error Handling**: Comprehensive error reporting and recovery
- **Documentation**: Built-in manual and help system

### **Data Visualization**
- **Trajectory Plots**: High-quality trajectory visualizations
- **Navigation Tools**: Browse through result images
- **Export Options**: Publication-ready image and data export
- **Interactive Tables**: Sortable and searchable results display

## 🔬 Scientific Applications

### **Supported Paradigms**
- **Open Field Test (OFT)**: Locomotor activity and anxiety-like behavior assessment
- **Elevated Plus Maze (EPM)**: Anxiety-related behavior analysis (framework ready)

### **Research Applications**
- **Behavioral Neuroscience**: Anxiety, depression, and locomotor studies
- **Pharmacology**: Drug effects on behavior and movement patterns
- **Genetics**: Behavioral phenotyping of transgenic animals
- **Environmental Studies**: Effects of environmental manipulations

### **Experimental Design Support**
- **Multi-factor Designs**: Complex experimental designs with multiple variables
- **Temporal Analysis**: Track behavioral changes over time
- **Dose-Response Studies**: Analyze graded treatment effects
- **Interaction Studies**: Understand how factors combine to affect behavior

## 📞 Support and Documentation

### **Built-in Help System**
- **📋 User Manual**: Comprehensive usage guide accessible via GUI
- **📊 Statistical Analysis Manual**: Detailed statistics tutorial
- **🔗 Field Merging Guide**: Tutorial for complex filename structures
- **📈 Update Information**: Recent feature additions and changes

### **Troubleshooting**
- **Status Indicators**: Check processing pipeline status in Tab 1
- **Log Files**: Detailed error logging for debugging
- **Cluster Connectivity**: Verify SSH credentials and network access
- **File Validation**: Ensure video formats and filename structures are correct

## 🤝 Contributing

Contributions welcome! Key areas for development:
- Additional behavioral metrics
- New statistical tests
- Enhanced visualization options
- Local processing capabilities
- Additional experimental paradigms

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Designed for high-throughput behavioral neuroscience research
- Optimized for cluster computing environments
- Built with modern PyQt5 interface design principles

---

**Note**: This application requires SSH access to a SLURM cluster for video preprocessing and animal tracking. Ensure proper cluster configuration before beginning analysis.