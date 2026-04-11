import numpy as np
import pandas as pd

def extract_features(df, col):
    series = df[col]

    is_numeric = pd.api.types.is_numeric_dtype(series)

    return {
        'mean': series.mean() if is_numeric else 0,
        'std': series.std() if is_numeric else 0,
        'min': series.min() if is_numeric else 0,
        'max': series.max() if is_numeric else 0,
        'unique_ratio': series.nunique() / len(series) if len(series) > 0 else 0,
        "is_numeric": int(is_numeric),
        "is_integer": int(np.all(series.dropna() % 1 == 0)) if is_numeric else 0,
        "name_length": len(col),
        "sample_values": series.dropna().unique()[:5].tolist()  
    }