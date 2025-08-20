"""
Tukey HSD Update content for PipelineApp - embedded version for deployment
"""

TUKEY_HSD_UPDATE_CONTENT = '''# Statistical Analysis Updates

## Changes Made

### 1. Added Tukey HSD Post-hoc Test
- **Feature**: Automatic Tukey HSD test after significant ANOVA results
- **Location**: `StatisticalAnalysisWorker.run()` method
- **Trigger**: Runs automatically when:
  - One-way ANOVA is performed
  - ANOVA result is significant (p < 0.05)
  - More than 2 groups are compared
  - Statsmodels package is available

### 2. Enhanced Results Display
- **Tukey Results Section**: Added detailed display of pairwise comparisons
- **Format**: Shows group comparisons, mean differences, adjusted p-values, and confidence intervals
- **Significance Indicators**: Uses *** for significant and ns for non-significant comparisons

### 3. Fixed Export Functionality
- **Problem**: Export function failed with complex nested data structures
- **Solution**: 
  - Proper handling of different data types (int, float, bool, str)
  - Separate export for Tukey HSD results
  - UTF-8 encoding for text files
  - Better error handling with traceback information

### 4. Enhanced File Export
- **Multiple Files**: 
  - Main summary: `statistical_analysis_summary.txt`
  - Detailed results: `statistical_analysis_detailed.csv`
  - Tukey comparisons: `tukey_hsd_results.csv` (when available)
- **Error Handling**: Improved error messages and debugging information

### 5. Updated Dependencies
- **Added**: `statsmodels>=0.13.0` to requirements.txt
- **Purpose**: Required for Tukey HSD post-hoc tests

### 6. Improved User Interface
- **Help Text**: Updated to mention Tukey HSD availability
- **Welcome Message**: Enhanced to show available statistical packages
- **Test Info**: Clarified when Tukey HSD is performed

## Usage Instructions

### For One-way ANOVA with Tukey HSD:
1. Load your metrics data
2. Select a grouping factor with 3+ groups
3. Choose "One-way ANOVA" as test type
4. Select metrics to analyze
5. Run analysis

### Expected Output:
- Standard ANOVA results (F-statistic, p-value)
- If significant: Automatic Tukey HSD pairwise comparisons
- Export options for all results

## Example Tukey HSD Output:
```
🔍 Tukey HSD Post-hoc Test:
  • Group1 vs Group2: diff=4.811, p_adj=0.0000 ***
    95% CI: [3.412, 6.209]
  • Group1 vs Group3: diff=2.289, p_adj=0.0007 ***
    95% CI: [0.891, 3.688]
  • Group2 vs Group3: diff=-2.521, p_adj=0.0002 ***
    95% CI: [-3.920, -1.123]
```

## Files Modified:
- `source/gui/statistical_analysis_tab.py` - Main implementation
- `requirements.txt` - Added statsmodels dependency
- `test_tukey.py` - Test script for verification

## Notes:
- Tukey HSD requires statsmodels package
- Only runs after significant ANOVA results
- Results are included in both display and export
- Automatically handles multiple comparisons correction
'''
