# Field Merging Feature - User Guide

## Overview

The PipelineApp now supports field merging functionality, allowing users to combine predefined filename fields during project creation. This feature is particularly useful when you want to treat certain combinations of filename components as a single grouping factor for statistical analysis.

## How It Works

### During Project Creation

1. **Configure Filename Structure**: Set up your filename fields as usual (e.g., "Subject", "Treatment", "Dosage", "Arena")

2. **Open Field Merging Dialog**: Click the "Configure Field Merging..." button to open the dedicated field merging configuration dialog

3. **Define Merge Groups**: In the Field Merging Dialog:
   - View all available fields with their numbers
   - Click "Add Merge Group" to create a new merge group
   - Select the fields you want to merge together (e.g., Subject + Treatment)
   - Each field can only be in one merge group
   - You can create multiple merge groups for different combinations
   - Use "Remove Selected" to delete merge groups
   - Use "Clear All" to remove all merge groups

4. **Preview Results**: The main dialog shows a status summary of configured merge groups

5. **Validate Filenames**: The filename validation preview will show both original fields and merged fields

### Example

**Original Filename**: `Mouse1_Control_Low_Arena1.mp4`

**Field Configuration**:
- Field 1: Subject
- Field 2: Treatment 
- Field 3: Dosage
- Field 4: Arena

**Merge Configuration**:
- Group 1: Merge Subject + Treatment

**Result in Metrics Table**:
- `Subject_Treatment`: "Mouse1_Control"
- `Dosage`: "Low"
- `Arena`: "Arena1"

## Benefits

### Statistical Analysis
- **Simplified Grouping**: Combine related factors for cleaner statistical analysis
- **Reduced Complexity**: Fewer columns in your metrics dataframe
- **Custom Combinations**: Create meaningful grouping factors specific to your experiment

### Data Organization
- **Flexible Structure**: Maintain detailed filename structure while creating consolidated views
- **Backward Compatibility**: Projects without merge groups continue to work as before
- **Clear Documentation**: Merge configurations are saved in the project YAML file
- **Clean Interface**: Field merging configuration moved to separate dialog to keep main project creation dialog uncluttered

## Configuration Storage

Merge group configurations are stored in the project's `config.yaml` file:

```yaml
filename_structure:
  num_fields: 4
  field_names: ["Subject", "Treatment", "Dosage", "Arena"]
  merge_groups: [[0, 1]]  # Merge indices 0 and 1 (Subject + Treatment)
  description: "Filenames should have 4 fields separated by '_': Subject _ Treatment _ Dosage _ Arena"
```

## Usage Tips

1. **Plan Ahead**: Consider your statistical analysis needs when designing merge groups
2. **Group Related Factors**: Merge fields that represent different aspects of the same experimental factor
3. **Keep It Simple**: Don't over-merge - maintain meaningful separation where needed
4. **Test First**: Use the validation preview to ensure your merge configuration works as expected
5. **Easy Access**: The "Configure Field Merging..." button provides quick access to merge settings without cluttering the main dialog

## Technical Implementation

The field merging happens during metrics dataframe construction:

1. **Parsing**: Filenames are split into individual fields as usual
2. **Merging**: Specified fields are combined with "_" separator
3. **Column Creation**: New merged columns replace original constituent columns
4. **Statistical Analysis**: Merged fields appear as single grouping factors

This ensures that downstream statistical analysis tools work seamlessly with merged fields without requiring additional configuration.
