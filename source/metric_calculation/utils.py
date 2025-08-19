"""
Utility functions for metric calculations.
"""

import os
import yaml
import pandas as pd
from typing import Dict, Optional
from pandas import DataFrame


def construct_metric_dataframe(metrics: Dict[str, Dict[str, float]], yaml_path: Optional[str] = None) -> DataFrame:
    """
    Construct a pandas DataFrame from metrics dictionary.
    
    Args:
        metrics: Dictionary mapping filenames to their metrics
        yaml_path: Optional path to YAML configuration file for filename parsing
        
    Returns:
        DataFrame: Formatted metrics data with parsed filename columns if YAML available
    """
    filenames = list(metrics.keys())
    if not filenames:
        return pd.DataFrame()
        
    metrics_names = list(metrics[filenames[0]].keys())
    metrics_extracted = {m: [] for m in metrics_names}
    
    for metric in metrics_names:
        for filename in filenames:
            metrics_extracted[metric].append(metrics[filename].get(metric))
    
    # Parse filename structure if YAML configuration is available
    filename_columns = {}
    if yaml_path and os.path.exists(yaml_path):
        try:
            with open(yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            filename_structure = yaml_config.get('filename_structure', {})
            field_names = filename_structure.get('field_names', [])
            
            if field_names:
                # Initialize columns for each field
                for field_name in field_names:
                    filename_columns[field_name] = []
                
                # Parse each filename
                for filename in filenames:
                    # Remove file extension and split by underscore
                    base_name = os.path.splitext(filename)[0]
                    parts = base_name.split('_')
                    
                    # Extract each field, use empty string if not enough parts
                    for i, field_name in enumerate(field_names):
                        if i < len(parts):
                            filename_columns[field_name].append(parts[i])
                        else:
                            filename_columns[field_name].append('')
        except Exception as e:
            # If parsing fails, fall back to just using the filename
            print(f"Warning: Could not parse YAML filename structure: {e}")
            filename_columns = {}
    
    # Create the final data dictionary
    if filename_columns:
        # Include parsed filename columns + metrics
        data = {**filename_columns, **metrics_extracted}
    else:
        # Fall back to original behavior with full filename
        data = {"Filename": filenames, **metrics_extracted}
    
    return pd.DataFrame(data)
