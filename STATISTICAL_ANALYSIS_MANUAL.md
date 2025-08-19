# Statistical Analysis Manual - PipelineApp

## 📊 Overview

The Statistical Analysis tab provides comprehensive statistical testing capabilities for behavioral analysis data. It automatically parses filename structures to create grouping factors and supports t-tests, one-way ANOVA, and two-way ANOVA with interaction effects.

## 🚀 Getting Started

### Prerequisites
- **Data Format**: CSV files with behavioral metrics
- **Filename Structure**: YAML configuration with `field_names` defining experimental factors
- **Required Package**: `statsmodels` for two-way ANOVA functionality

### Installation
```bash
pip install statsmodels
```

## 📋 Tab Overview

The Statistical Analysis tab (Tab 4) contains several sections:

1. **Data Loading** - Load and validate CSV results
2. **Grouping Factor Selection** - Choose primary factor for analysis
3. **Second Grouping Factor** - Choose secondary factor (two-way ANOVA only)
4. **Metrics Selection** - Select behavioral metrics to analyze
5. **Statistical Test Configuration** - Choose test type
6. **Results Display** - View comprehensive statistical results

## 🔧 Step-by-Step Usage

### Step 1: Load Data
1. Click **"Load CSV Data"** button
2. Select your behavioral metrics CSV file
3. The system automatically:
   - Parses filenames based on your YAML `field_names` configuration
   - Creates separate columns for each filename component
   - Identifies numeric metrics suitable for analysis

**Example Filename Parsing:**
```
Filename: "Mouse1_Treatment_High_Exp1_Arena1.mp4"
YAML field_names: ["Subject", "Treatment", "Dosage", "Experiment", "Arena"]
Result: 5 separate columns created for grouping
```

### Step 2: Select Test Type
Choose from three statistical test options:

#### **t-test (Independent Samples)**
- **Purpose**: Compare behavioral metrics between exactly 2 groups
- **Requirements**: One grouping factor with exactly 2 levels
- **Output**: 
  - t-statistic and p-value
  - Levene's test for equal variances
  - Welch's correction for unequal variances

#### **One-way ANOVA**
- **Purpose**: Compare behavioral metrics across 2+ groups
- **Requirements**: One grouping factor with 2 or more levels
- **Output**:
  - F-statistic and p-value
  - Degrees of freedom
  - Descriptive statistics for each group

#### **Two-way ANOVA**
- **Purpose**: Analyze main effects and interactions between two factors
- **Requirements**: Two different grouping factors
- **Output**:
  - Main effect for Factor 1
  - Main effect for Factor 2
  - Interaction effect (Factor 1 × Factor 2)
  - R² and adjusted R² for model fit
  - Descriptive statistics for each factor combination

### Step 3: Select Grouping Factors

#### **Primary Factor Selection**
1. Use the **"Grouping Factor"** dropdown
2. Choose from available factors (based on your filename structure)
3. View group information: unique values and group counts

#### **Secondary Factor Selection** (Two-way ANOVA only)
1. Select **"Two-way ANOVA"** from test type dropdown
2. The **"Second Grouping Factor"** section appears
3. Choose a different factor from the second dropdown
4. System validates that factors are different

### Step 4: Select Metrics
1. **Metrics Selection** list shows all numeric behavioral metrics
2. **Select metrics** using checkboxes (multiple selection supported)
3. Use **"Select All"** or **"Select None"** buttons for quick selection
4. Common metrics include:
   - `total_distance`
   - `time_moving`
   - `time_in_center`
   - `thigmotaxis_ratio`
   - `avg_velocity`

### Step 5: Run Analysis
1. Click **"🔬 Run Analysis"** button
2. Analysis runs in background thread (UI remains responsive)
3. Progress updates appear in results area
4. Results display automatically when complete

## 📈 Understanding Results

### Summary Text Results

#### **t-test Results**
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

#### **One-way ANOVA Results**
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

#### **Two-way ANOVA Results**
```
📊 METRIC: avg_velocity
------------------------------
📈 Descriptive Statistics:
(Standard group means as above)

🧪 Two-way ANOVA:

  📈 Factor 1 (Treatment):
    • F = 5.6789
    • p = 0.023456
    • Significant: YES

  📈 Factor 2 (Subject):
    • F = 2.3456
    • p = 0.134567
    • Significant: NO

  🔄 Interaction (Treatment × Subject):
    • F = 3.4567
    • p = 0.045678
    • Significant: YES

  📊 Model Fit:
    • R² = 0.6234
    • Adjusted R² = 0.5678

  📈 Group Means by Factor Combination:
    • Control × Subject1: M=123.45, SD=12.34, n=3
    • Control × Subject2: M=145.67, SD=15.67, n=3
    • Treatment × Subject1: M=167.89, SD=18.90, n=3
    • Treatment × Subject2: M=189.01, SD=21.23, n=3
```

### Detailed Table Results

The results table provides organized data with separate rows for each effect:

#### **Two-way ANOVA Table Structure**
| Metric | Test | Statistic | p-value | Significant |
|--------|------|-----------|---------|-------------|
| avg_velocity | Two-way ANOVA: Treatment | 5.6789 | 0.023456 | Yes |
| avg_velocity | Two-way ANOVA: Subject | 2.3456 | 0.134567 | No |
| avg_velocity | Two-way ANOVA: Treatment × Subject | 3.4567 | 0.045678 | Yes |

## 🔍 Interpretation Guide

### Statistical Significance
- **p < 0.05**: Statistically significant difference
- **p ≥ 0.05**: No statistically significant difference

### Effect Sizes (Two-way ANOVA)
- **R² = 0.01**: Small effect (1% of variance explained)
- **R² = 0.06**: Medium effect (6% of variance explained)
- **R² = 0.14**: Large effect (14% of variance explained)

### Two-way ANOVA Interpretation

#### **Main Effects**
- **Significant Factor 1**: Factor 1 independently affects the behavioral metric
- **Significant Factor 2**: Factor 2 independently affects the behavioral metric

#### **Interaction Effects**
- **Significant Interaction**: The effect of Factor 1 depends on the level of Factor 2
- **Non-significant Interaction**: Factors act independently (additive effects)

#### **Practical Examples**

**Example 1: Drug Treatment × Time**
```
Factor 1 (Drug): Significant (p = 0.02)
Factor 2 (Time): Significant (p = 0.01)
Interaction: Non-significant (p = 0.45)
```
**Interpretation**: Both drug treatment and time affect behavior independently. The drug effect is consistent across all time points.

**Example 2: Genotype × Environment**
```
Factor 1 (Genotype): Non-significant (p = 0.12)
Factor 2 (Environment): Significant (p = 0.03)
Interaction: Significant (p = 0.01)
```
**Interpretation**: Environment affects behavior, but the effect depends on genotype. Different genotypes respond differently to environmental changes.

## 🚨 Troubleshooting

### Common Issues

#### **"No grouping factors found"**
- **Cause**: YAML file missing `field_names` or filename parsing failed
- **Solution**: Check YAML configuration and ensure filenames match expected structure

#### **"Need at least 2 groups for comparison"**
- **Cause**: Selected factor has only 1 unique value
- **Solution**: Choose a factor with multiple levels or check data integrity

#### **"Two-way ANOVA requires statsmodels package"**
- **Cause**: Statsmodels not installed
- **Solution**: `pip install statsmodels`

#### **"t-test requires exactly 2 groups"**
- **Cause**: Selected factor has more than 2 levels
- **Solution**: Use One-way ANOVA instead or create a binary grouping factor

### Data Quality Checks

#### **Before Analysis**
1. **Check sample sizes**: Ensure adequate sample sizes per group (n ≥ 3 recommended)
2. **Verify factor levels**: Confirm grouping factors have expected unique values
3. **Data completeness**: Remove or handle missing values appropriately

#### **After Analysis**
1. **Check assumptions**: 
   - Normal distribution (especially for small samples)
   - Equal variances (Levene's test provided for t-tests)
   - Independence of observations
2. **Effect size interpretation**: Consider practical significance alongside statistical significance
3. **Multiple comparisons**: Consider correction for multiple testing if analyzing many metrics

## 📊 Export and Reporting

### Export Functionality
1. Click **"📋 Export Results"** after running analysis
2. Choose export location and filename
3. Results saved in structured format for publication

### Reporting Best Practices

#### **For Publications**
1. **Report effect sizes** alongside p-values
2. **Include descriptive statistics** (means, standard deviations, sample sizes)
3. **Describe statistical methods** used
4. **Report interaction interpretations** for two-way ANOVA

#### **Example Methods Section**
```
"Statistical analyses were performed using independent t-tests for two-group 
comparisons and two-way ANOVA for factorial designs. Levene's test was used 
to assess equality of variances. For two-way ANOVA, main effects and 
interaction effects were examined, with R² reported as a measure of effect 
size. Statistical significance was set at α = 0.05."
```

## 🎯 Advanced Tips

### Experimental Design Considerations

#### **Power Analysis**
- Consider sample size requirements before data collection
- Unequal group sizes can reduce statistical power
- Balance groups when possible

#### **Factor Selection**
- Choose meaningful grouping factors based on experimental design
- Consider biological/experimental relevance of interactions
- Avoid factors with highly unbalanced groups

#### **Metric Selection**
- Focus on primary outcome measures
- Consider multiple comparison corrections for exploratory analyses
- Validate metrics align with research hypotheses

### Statistical Best Practices

#### **Two-way ANOVA**
- **Significant interaction**: Focus on simple effects rather than main effects
- **Non-significant interaction**: Main effects can be interpreted directly
- **Model fit**: Higher R² indicates better model explanation of variance

#### **Multiple Metrics**
- Consider family-wise error rate when testing multiple metrics
- Bonferroni correction: α_corrected = 0.05 / number_of_tests
- Focus on biologically meaningful effects

---

## 📞 Support

For questions about statistical analysis:
1. Check this manual for common issues
2. Verify data format and YAML configuration
3. Ensure all required packages are installed
4. Review statistical assumptions for your chosen test

**Remember**: Statistical significance should be interpreted alongside biological significance and effect sizes for meaningful scientific conclusions.
