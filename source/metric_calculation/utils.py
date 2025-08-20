"""
Utility functions for metric calculations.
"""

import os
import yaml
import pandas as pd
from typing import Dict, Optional
from pandas import DataFrame
from utils.logging_config import get_logger

logger = get_logger(__name__)


def apply_merge_groups_to_columns(filename_columns: Dict[str, list], field_names: list[str], merge_groups: list[list[int]]) -> Dict[str, list]:
    """
    Apply merge groups to filename columns by combining specified fields.
    
    Args:
        filename_columns: Dictionary mapping field names to their values
        field_names: List of original field names
        merge_groups: List of lists, each containing field indices to merge
        
    Returns:
        Dict[str, list]: New filename columns with merged fields
    """
    if not merge_groups:
        return filename_columns
    
    # Create sets to track which indices are merged
    merged_indices = set()
    for group in merge_groups:
        merged_indices.update(group)
    
    new_columns = {}
    num_rows = len(next(iter(filename_columns.values()))) if filename_columns else 0
    
    # Add merged groups first
    for group in merge_groups:
        # Get field names for this group
        group_names = [field_names[i] for i in group if i < len(field_names)]
        merged_name = "_".join(group_names)
        
        # Combine values from all fields in the group
        merged_values = []
        for row_idx in range(num_rows):
            group_values = []
            for field_idx in group:
                if field_idx < len(field_names):
                    field_name = field_names[field_idx]
                    if field_name in filename_columns and row_idx < len(filename_columns[field_name]):
                        group_values.append(filename_columns[field_name][row_idx])
                    else:
                        group_values.append('')
            merged_values.append("_".join(group_values))
        
        new_columns[merged_name] = merged_values
    
    # Add non-merged fields
    for i, field_name in enumerate(field_names):
        if i not in merged_indices and field_name in filename_columns:
            new_columns[field_name] = filename_columns[field_name]
    
    return new_columns


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
            merge_groups = filename_structure.get('merge_groups', [])
            
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
                
                # Apply merge groups if they exist
                if merge_groups:
                    filename_columns = apply_merge_groups_to_columns(filename_columns, field_names, merge_groups)
        except Exception as e:
            # If parsing fails, fall back to just using the filename
            logger.warning(f"Could not parse YAML filename structure: {e}")
            filename_columns = {}
    
    # Create the final data dictionary
    if filename_columns:
        # Include parsed filename columns + metrics
        data = {**filename_columns, **metrics_extracted}
    else:
        # Fall back to original behavior with full filename
        data = {"Filename": filenames, **metrics_extracted}
    
    return pd.DataFrame(data)
