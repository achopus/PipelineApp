"""
Field Merging Guide content for PipelineApp - embedded version for deployment
"""

FIELD_MERGING_GUIDE_CONTENT = '''# Field Merging Feature - User Guide

## Overview

Field merging allows you to combine filename components into single grouping factors for statistical analysis. This is useful when you want to treat certain combinations of filename parts as one experimental factor.

## 🔧 How to Use Field Merging

### During Project Creation

1. **Set Up Filename Structure**: Configure your filename fields as usual
   - Example: "Subject", "Treatment", "Dosage", "Arena"

2. **Open Field Merging Dialog**: Click **"Configure Field Merging..."** button

3. **Create Merge Groups**: In the dialog:
   - View all available fields with their numbers
   - Click **"Add Merge Group"** to create a new group
   - Select fields to merge together (e.g., Subject + Treatment)
   - Create multiple groups for different combinations
   - Use **"Remove Selected"** and **"Clear All"** to manage groups

4. **Preview Results**: See how your merged fields will appear

### Example Usage

**Original Filename**: `Mouse1_Control_Low_Arena1.mp4`

**Field Setup**:
- Field 1: Subject
- Field 2: Treatment 
- Field 3: Dosage
- Field 4: Arena

**Merge Configuration**: Merge Subject + Treatment

**Result**: 
- `Subject_Treatment`: "Mouse1_Control"
- `Dosage`: "Low" 
- `Arena`: "Arena1"

## 🎯 Why Use Field Merging?

### **Simplified Statistical Analysis**
- **Cleaner Grouping**: Combine related factors for easier analysis
- **Fewer Variables**: Reduce the number of columns in your data
- **Custom Factors**: Create grouping factors specific to your research needs

### **Example Applications**

#### **Dose-Response Studies**
- Original: `Subject_Drug_Dose_Day.mp4`
- Merge: Subject + Day → `Subject_Day`
- Result: Analyze drug doses across subjects and days as one factor

#### **Multi-Site Studies**  
- Original: `Site_Subject_Treatment_Trial.mp4`
- Merge: Site + Subject → `Site_Subject`
- Result: Each subject uniquely identified across sites

#### **Complex Treatments**
- Original: `Mouse_Treatment_Route_Dose.mp4`
- Merge: Treatment + Route + Dose → `Full_Treatment`
- Result: Complete treatment description as single factor

## 📊 Benefits for Data Analysis

### **Statistical Clarity**
- **Reduced Complexity**: Fewer factors to manage in statistical tests
- **Meaningful Groups**: Create factors that match your experimental design
- **Flexible Analysis**: Adapt grouping to different research questions

### **Data Organization**
- **Clear Structure**: Maintain detailed filenames while simplifying analysis
- **Consistent Results**: Same merging applied across all files in project
- **Easy Documentation**: Merge settings saved in project configuration

## 💡 Best Practices

### **Planning Your Merge Strategy**

1. **Consider Your Analysis Goals**: 
   - What comparisons do you want to make?
   - Which factors should be analyzed together?

2. **Keep Related Fields Together**:
   - Merge fields representing the same experimental manipulation
   - Don't merge unrelated factors (e.g., Subject + Arena)

3. **Maintain Meaningful Separation**:
   - Don't over-merge - keep important distinctions
   - Consider downstream statistical needs

### **Example Strategies**

#### **For Drug Studies**
- Keep: Subject, Drug_Dose (merged), Time
- Rationale: Drug and dose form one treatment factor

#### **For Behavioral Phenotyping**
- Keep: Strain_Sex (merged), Age, Test_Day (merged)
- Rationale: Create unique subject identifiers and test sessions

#### **For Longitudinal Studies**
- Keep: Subject, Treatment, Session_Day (merged)
- Rationale: Combine session and day into temporal factor

## 🔍 Understanding the Results

### **In Your Metrics File**
After processing, your CSV will contain:
- **Original fields**: Unchanged individual components
- **Merged fields**: New columns with combined values
- **Statistical analysis**: Uses merged fields for grouping

### **Example Output**
```
Original fields:    Subject | Treatment | Dosage | Arena
Merged result:      Subject_Treatment  | Dosage | Arena
Values:            Mouse1_Control     | Low    | Arena1
```

### **Statistical Benefits**
- **Cleaner factor names** in statistical output
- **Fewer interaction terms** in complex analyses  
- **More intuitive results** interpretation

## ⚙️ Technical Notes

### **Merging Rules**
- Fields combined with underscore separator ("_")
- Merge groups saved in project configuration
- Applied consistently to all files in project
- Cannot merge the same field into multiple groups

### **Compatibility**
- Works with all statistical tests (t-test, ANOVA, two-way ANOVA)
- Compatible with existing projects (optional feature)
- No impact on trajectory visualization or other analyses

---

**Remember**: Field merging is designed to simplify your statistical analysis while maintaining the detailed information in your original filenames. Plan your merge strategy based on your specific research questions and analysis needs.'''
