"""
README content for PipelineApp - embedded version for deployment
"""

README_CONTENT = '''# PipelineApp - Video Tracking Pipeline

A comprehensive GUI application for automated behavioral analysis of animal experiments, designed for Open Field Test (OFT) and Elevated Plus Maze (EPM) paradigms. This application provides an end-to-end pipeline from video annotation to comprehensive behavioral metrics analysis.

## 🎯 Key Features

### **Complete Analysis Pipeline**
- **Project Management**: Create and organize behavioral experiment projects
- **Video Annotation**: Mark arena corners and reference points with visual feedback
- **Automated Processing**: Submit videos for preprocessing and tracking analysis
- **Metrics Calculation**: Generate comprehensive behavioral measurements
- **Statistical Analysis**: Built-in statistical testing with publication-ready results

### **Advanced Analytics**
- **Movement Analysis**: Track distance traveled, velocity, and activity patterns
- **Spatial Behavior**: Measure center exploration, thigmotaxis, and wall proximity
- **Temporal Patterns**: Analyze behavior changes over configurable time windows
- **Statistical Testing**: t-tests, ANOVA, and two-way ANOVA with effect sizes
- **Visualization**: Publication-ready trajectory plots with customizable heatmaps

## 📖 How to Use the Application

### 1. Creating a New Project
**Navigate to Tab 1: Project Management**

1. Click **"Create New Project"**
2. Fill in your project details:
   - **Project Name**: Choose a descriptive name
   - **Author**: Your name or research group
   - **Experiment Type**: Select OFT (Open Field Test) or EPM (Elevated Plus Maze)
3. **Select Video Source**: Choose the folder containing your video files
4. **Configure Filename Structure**:
   - Set number of fields (parts separated by underscores)
   - Name each field (e.g., "Subject", "Treatment", "Dosage")
   - Example: `Mouse1_Control_Low_Arena1.mp4` → 4 fields
5. **Validation**: Ensure all video files match your filename structure
6. Click **"Create Project"** - videos will be copied to organized project folder

### 2. Video Annotation
**Navigate to Tab 2: Video Points Annotation**

1. Click **"Open video annotation tool"**
2. **Mark Arena Corners** for each video (4 points total):
   - **Top-left corner** (red point)
   - **Top-right corner** (green point)
   - **Bottom-right corner** (blue point)
   - **Bottom-left corner** (orange point)
3. **Navigation Controls**:
   - Use **arrow keys** to switch between videos
   - Press **R** to reset points for current video
   - Press **S** to save your progress
4. **Submit for Processing**: Once all videos are annotated, submit to cluster

### 3. Tracking and Results
**Navigate to Tab 3: Animal Tracking + Results**

1. **Run Tracking**: Process your annotated videos to extract animal positions
2. **Calculate Metrics**: Generate comprehensive behavioral measurements
3. **View Results**: 
   - Browse trajectory visualizations
   - Review calculated metrics in table format
   - Export results as CSV for further analysis

### 4. Statistical Analysis
**Navigate to Tab 4: Statistical Analysis**

1. **Load Data**: Import your CSV results file
2. **Configure Analysis**:
   - Select **grouping factors** based on your filename structure
   - Choose **behavioral metrics** to analyze
   - Select **statistical test type**:
     - **t-test**: Compare 2 groups
     - **One-way ANOVA**: Compare multiple groups
     - **Two-way ANOVA**: Analyze two factors and their interaction
3. **Run Analysis**: Click "Run Analysis" and wait for results
4. **Interpret Results**: View comprehensive statistical output
5. **Export**: Save results for publication

## 📊 Understanding Your Results

### **Behavioral Metrics Explained**

#### **Movement Metrics**
- **Total Distance**: How far the animal traveled during the entire session
- **Average Velocity**: Mean speed of movement (useful for activity levels)
- **Time Moving**: Percentage of time the animal was active vs. stationary
- **Peak Velocity**: Maximum speed reached (indicates burst activity)

#### **Spatial Behavior**
- **Time in Center**: How long the animal spent in the arena center
  - *Higher values* = More exploratory, less anxious behavior
  - *Lower values* = More anxious, wall-hugging behavior
- **Thigmotaxis Ratio**: Preference for arena edges vs. center
  - *Values close to 1* = Strong wall preference (higher anxiety)
  - *Values close to 0* = Center preference (lower anxiety)
- **Distance to Wall**: Average proximity to arena boundaries
  - *Lower values* = Stays close to walls
  - *Higher values* = Ventures toward center

#### **Temporal Patterns**
- **Time-binned Analysis**: Shows how behavior changes over time
  - Early bins: Initial response to novel environment
  - Later bins: Habituation and exploration patterns
- **Activity Over Time**: Movement patterns throughout the session

### **Statistical Results Interpretation**

#### **Understanding P-values**
- **p < 0.05**: Statistically significant difference between groups
- **p ≥ 0.05**: No statistically significant difference detected

#### **Effect Sizes (Two-way ANOVA)**
- **R² values** show how much of the behavior variation is explained:
  - **R² = 0.01-0.05**: Small effect
  - **R² = 0.06-0.13**: Medium effect  
  - **R² = 0.14+**: Large effect

#### **Interaction Effects**
- **Significant Interaction**: The effect of one factor depends on the other
  - Example: Drug effect varies by genotype
- **Non-significant Interaction**: Factors act independently
  - Example: Drug and genotype have separate, additive effects

## 🎯 Experimental Applications

### **Open Field Test (OFT)**
**Best for measuring:**
- General locomotor activity
- Anxiety-like behavior (center vs. edge preference)
- Exploratory behavior patterns
- Drug effects on movement and anxiety

### **Typical Research Questions**
- Does treatment reduce anxiety-like behavior?
- How does genotype affect locomotor activity?
- Are there sex differences in exploration patterns?
- Does the drug effect change over time?

## 📈 Tips for Best Results

### **Video Quality**
- Ensure good lighting and contrast
- Keep camera position consistent across sessions
- Minimize shadows and reflections in arena

### **Experimental Design**
- Balance group sizes when possible
- Randomize testing order
- Control for time of day effects
- Consider habituation periods

### **Data Interpretation**
- Always consider both statistical and biological significance
- Look for consistent patterns across multiple metrics
- Consider individual variation within groups
- Validate findings with additional experiments

## � Customizing Your Analysis

### **Filename Structure**
Design your filename structure to match your experimental factors:
- **Simple**: `Subject_Treatment.mp4`
- **Complex**: `Subject_Treatment_Dose_Day_Arena.mp4`
- Each field becomes a grouping factor for statistics

### **Time Binning**
- Default: 5-minute bins for temporal analysis
- Useful for tracking habituation and adaptation
- Shows early vs. late session differences

### **Arena Configuration**
- Standard: 80cm x 80cm open field
- Center defined as central 40% of arena
- Thigmotaxis zone: outer 20% of arena

## � Best Practices

### **Project Organization**
1. Use descriptive project names
2. Maintain consistent filename structures
3. Document experimental conditions
4. Keep backups of raw data

### **Statistical Analysis**
1. Plan your analysis before data collection
2. Consider multiple comparison corrections
3. Report effect sizes alongside p-values
4. Include descriptive statistics in results

### **Result Reporting**
1. Export statistical results for records
2. Save trajectory plots for presentations
3. Document analysis parameters used
4. Include sample sizes in reports

---

**Remember**: This application provides the tools for analysis, but proper experimental design and interpretation require understanding of your specific research context and behavioral paradigms.'''
