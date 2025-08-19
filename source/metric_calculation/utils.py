"""
Utility functions for metric calculations.
"""

import pandas as pd
from typing import Dict
from pandas import DataFrame


def construct_metric_dataframe(metrics: Dict[str, Dict[str, float]]) -> DataFrame:
    """
    Construct a pandas DataFrame from metrics dictionary.
    
    Args:
        metrics: Dictionary mapping filenames to their metrics
        
    Returns:
        DataFrame: Formatted metrics data
    """
    filenames = list(metrics.keys())
    if not filenames:
        return pd.DataFrame()
        
    metrics_names = list(metrics[filenames[0]].keys())
    metrics_extracted = {m: [] for m in metrics_names}
    
    for metric in metrics_names:
        for filename in filenames:
            metrics_extracted[metric].append(metrics[filename].get(metric))
            
    data = {"Filename": filenames, **metrics_extracted}
    return pd.DataFrame(data)
