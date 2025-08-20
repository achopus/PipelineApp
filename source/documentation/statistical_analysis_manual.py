"""
Statistical Analysis Manual content for PipelineApp - embedded version for deployment
"""

STATISTICAL_ANALYSIS_MANUAL_CONTENT = '''# Statistical Analysis Manual - PipelineApp

## 📊 Overview

The Statistical Analysis tab provides comprehensive statistical testing capabilities for your behavioral analysis data. This guide will help you understand how to use the statistical features and interpret your results effectively.

## 🚀 Getting Started

### What You Need
- **CSV file** with your behavioral metrics (generated from Tab 3)
- **Project configuration** with properly named filename fields
- **Understanding** of your experimental design and grouping factors

### Supported Statistical Tests
- **t-test**: Compare behavioral metrics between exactly 2 groups
- **One-way ANOVA**: Compare behavioral metrics across multiple groups (2+)
- **Two-way ANOVA**: Analyze two factors and their interaction effects

## � How to Use the Statistical Analysis Tab

### Step 1: Load Your Data
1. Click **"Load CSV Data"** button
2. Select your behavioral metrics CSV file (from Tab 3 results)
3. The system will automatically:
   - Parse your filenames based on your project configuration
   - Create grouping columns (Subject, Treatment, etc.)
   - Identify numeric metrics suitable for analysis
   - Display a preview of your data

### Step 2: Choose Your Statistical Test

#### **When to Use t-test**
- **Purpose**: Compare two groups on behavioral metrics
- **Example**: Control vs. Treatment group
- **Requirements**: Exactly 2 groups in your selected factor
- **Best for**: Simple comparisons, pilot studies

#### **When to Use One-way ANOVA**
- **Purpose**: Compare multiple groups on behavioral metrics  
- **Example**: Control vs. Low Dose vs. High Dose
- **Requirements**: 2 or more groups in your selected factor
- **Best for**: Dose-response studies, multiple conditions

#### **When to Use Two-way ANOVA**
- **Purpose**: Analyze two factors and their interaction
- **Example**: Treatment (Control/Drug) × Sex (Male/Female)
- **Requirements**: Two different grouping factors
- **Best for**: Complex experimental designs, interaction studies

### Step 3: Select Your Grouping Factors

#### **Primary Factor**
1. Use the **"Grouping Factor"** dropdown
2. Choose from factors based on your filename structure
3. View the **group summary** to confirm your selection
   - See unique values (e.g., "Control", "Treatment")  
   - Check group sizes (n=10 per group)

#### **Secondary Factor** (Two-way ANOVA only)
1. The second dropdown appears when you select "Two-way ANOVA"
2. Choose a **different factor** from your filename structure
3. System prevents selecting the same factor twice

### Step 4: Choose Behavioral Metrics
1. **Select metrics** from the checkbox list
2. **Multiple selection** supported - analyze several metrics at once
3. **Quick buttons**:
   - "Select All" - choose all available metrics
   - "Select None" - clear all selections
4. **Common metrics** include:
   - `total_distance` - how far the animal traveled
   - `time_in_center` - anxiety-related measure
   - `avg_velocity` - general activity level
   - `thigmotaxis_ratio` - wall-hugging behavior

### Step 5: Run Your Analysis
1. Click **"🔬 Run Analysis"** button
2. **Progress updates** appear in the results area
3. **Analysis runs in background** - interface stays responsive
4. **Results appear automatically** when complete

## 📈 Understanding Your Statistical Results

### t-test Results Interpretation

```
📊 METRIC: total_distance
------------------------------
📈 Descriptive Statistics:
  • Control: M=1245.678, SD=156.234, n=12
  • Treatment: M=1456.789, SD=189.567, n=11

🧪 t-test (equal variances):
  • Statistic: -2.4567
  • p-value: 0.023456
  • Significant: YES (α = 0.05)
  • Equal variances: YES (Levene p=0.3456)
```

**What this means:**
- **Means (M)**: Average values for each group
- **Standard Deviations (SD)**: Variability within each group
- **Sample sizes (n)**: Number of subjects per group
- **p-value < 0.05**: Statistically significant difference
- **Equal variances**: Groups have similar variability (good for t-test)

### One-way ANOVA Results Interpretation

```
📊 METRIC: time_in_center
------------------------------
📈 Descriptive Statistics:
  • Low: M=123.45, SD=23.45, n=8
  • Medium: M=145.67, SD=28.90, n=8  
  • High: M=167.89, SD=31.23, n=7

🧪 One-way ANOVA:
  • Statistic: 4.5678
  • p-value: 0.012345
  • Significant: YES (α = 0.05)
  • df: 2, 20
```

**What this means:**
- **F-statistic**: Overall test of group differences
- **p-value < 0.05**: At least one group differs significantly
- **Degrees of freedom (df)**: Related to group and sample sizes
- **Descriptive stats**: Show the pattern of differences between groups

### Two-way ANOVA Results Interpretation

```
📊 METRIC: avg_velocity
------------------------------
🧪 Two-way ANOVA:

  📈 Factor 1 (Treatment):
    • F = 5.6789
    • p = 0.023456
    • Significant: YES

  📈 Factor 2 (Sex):
    • F = 2.3456
    • p = 0.134567
    • Significant: NO

  🔄 Interaction (Treatment × Sex):
    • F = 3.4567
    • p = 0.045678
    • Significant: YES

  📊 Model Fit:
    • R² = 0.6234
    • Adjusted R² = 0.5678
```

**What this means:**

#### **Main Effects**
- **Treatment significant**: Treatment affects velocity regardless of sex
- **Sex not significant**: Males and females don't differ overall in velocity

#### **Interaction Effect** 
- **Significant interaction**: Treatment effect depends on sex
- **Example interpretation**: Drug increases velocity in males but decreases it in females

#### **Effect Size (R²)**
- **R² = 0.62**: Model explains 62% of the velocity variation
- **Large effect**: Substantial practical significance

## 🔍 Practical Interpretation Guidelines

### Statistical Significance vs. Biological Significance
- **p < 0.05**: Statistically significant (unlikely due to chance)
- **Effect size**: How big is the difference? (R² for ANOVA)
- **Biological relevance**: Does the difference matter for your research question?

### Effect Size Interpretation (R²)
- **R² = 0.01-0.05**: Small effect (1-5% variance explained)
- **R² = 0.06-0.13**: Medium effect (6-13% variance explained)  
- **R² = 0.14+**: Large effect (14%+ variance explained)

### Understanding Interactions

#### **Significant Interaction Example**
**Drug × Genotype interaction on anxiety behavior:**
- Wild-type mice: Drug reduces anxiety
- Knockout mice: Drug increases anxiety
- **Conclusion**: Drug effect depends on genotype

#### **Non-significant Interaction Example**  
**Drug × Time interaction on locomotion:**
- Both genotypes show increased locomotion with drug
- Effect size similar at all time points
- **Conclusion**: Drug and time have independent effects

## 🎯 Common Research Scenarios

### **Dose-Response Study**
- **Design**: Control, Low Dose, High Dose
- **Analysis**: One-way ANOVA  
- **Look for**: Progressive changes across doses
- **Follow-up**: Post-hoc tests if significant

### **Treatment × Sex Interaction**
- **Design**: 2 treatments × 2 sexes (4 groups total)
- **Analysis**: Two-way ANOVA
- **Look for**: Different treatment effects in males vs. females
- **Interpretation**: Consider separate analyses by sex if interaction significant

### **Longitudinal Design** 
- **Design**: Same animals tested at multiple time points
- **Analysis**: Two-way ANOVA (Treatment × Time)
- **Look for**: Changes over time, treatment differences at specific times
- **Note**: Consider repeated measures if using same animals

## 🚨 Troubleshooting Common Issues

### **"No grouping factors found"**
- **Problem**: Filename structure not recognized
- **Solution**: Check your project configuration and filename format
- **Example**: Files should follow pattern like `Subject_Treatment_Day.mp4`

### **"Need at least 2 groups for comparison"**
- **Problem**: Selected factor has only 1 unique value
- **Solution**: Choose a different grouping factor or check your data

### **"t-test requires exactly 2 groups"**
- **Problem**: Selected factor has more than 2 levels
- **Solution**: Use One-way ANOVA instead, or create binary grouping

### **Very small p-values (p < 0.001)**
- **Result**: Usually displayed as p < 0.001 or ***
- **Interpretation**: Very strong evidence against null hypothesis
- **Caution**: Still consider biological significance and effect size

## 📊 Best Practices for Analysis

### **Before Analysis**
1. **Check your data**: Ensure reasonable sample sizes (n ≥ 3 per group)
2. **Verify factors**: Confirm grouping factors have expected values
3. **Plan analysis**: Decide on statistical tests before looking at data
4. **Consider power**: Larger samples detect smaller effects

### **During Analysis**
1. **Start simple**: Use t-tests or one-way ANOVA before complex designs
2. **Check assumptions**: Look for equal group sizes and reasonable variability
3. **Multiple metrics**: Analyze related metrics together for consistency
4. **Document methods**: Note which tests and factors you used

### **After Analysis**
1. **Export results**: Save statistical output for your records
2. **Consider corrections**: Account for multiple comparisons if testing many metrics
3. **Report effect sizes**: Include R² or other effect size measures
4. **Interpret practically**: Consider what differences mean for your research

## 📋 Reporting Your Results

### **For Publications**
1. **Describe methods**: "Statistical analyses used independent t-tests..."
2. **Report sample sizes**: Include n for each group
3. **Include effect sizes**: R² for ANOVA, Cohen's d for t-tests
4. **Show descriptive stats**: Means, SDs, and group sizes

### **Example Results Section**
*"Two-way ANOVA revealed a significant main effect of treatment (F(1,20) = 5.68, p = 0.023, R² = 0.22) and a significant treatment × sex interaction (F(1,20) = 3.45, p = 0.046, R² = 0.15). Post-hoc analyses showed that drug treatment increased locomotion in males (M = 145.6 ± 23.4) compared to controls (M = 123.4 ± 18.9), but had no effect in females."*

---

**Remember**: Statistical significance tells you about the likelihood of your results occurring by chance. Biological significance depends on the size of effects and their relevance to your research questions. Always consider both when interpreting your results.'''
