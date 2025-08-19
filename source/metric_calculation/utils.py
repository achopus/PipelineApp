import pandas as pd
from typing import Dict
from pandas import DataFrame

def construct_metric_dataframe(metrics: Dict[str, Dict[str, float]]) -> DataFrame:
    filenames = list(metrics.keys())
    metrics_names = list(metrics[filenames[0]].keys())
    metrics_extracted = {m: [] for m in metrics_names}
    for metric in metrics_names:
        for filename in filenames:
            metrics_extracted[metric].append(metrics[filename].get(metric))
    data = {"Filename": filenames, **metrics_extracted}
    return pd.DataFrame(data)

"""
printable_metric_names = {
    "Filename": "Filename",
    "head_size": "Head Size",
    "body_size": "Body Size",
    "total_distance": "Total Distance",
    "thigmotaxis": "Thigmotaxis",
}
"""