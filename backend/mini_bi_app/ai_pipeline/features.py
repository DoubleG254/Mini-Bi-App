from http import server

import pandas as pd
import numpy as np
import re
import warnings

# Suppress the specific regex warning for cleaner output
warnings.filterwarnings("ignore", message=".*match groups.*")

def extract_features(df, col_name: str) -> dict:
    series = df[col_name]
    patterns = {
        'is_date': r'^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$',
        'is_timestamp': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
        'is_currency': r'^[\$€£]?\s*\d{1,3}(,\d{3})*(.\d{2})?$',
        'is_percentage': r'^-?\d+(\.\d+)?\s*%$',
        'is_uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        'is_time_period': r'^(Q[1-4]|H|FY\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$',
        'is_boolean': r'^(True|False|Yes|No|1|0|Y|N)$'
    }

    total_rows = len(series)
    null_count = series.isna().sum()
    non_null_series = series.dropna()
    
    # Initialize base dictionary
    col_features = {
        "null_ratio": float(null_count / total_rows) if total_rows > 0 else 0.0,
        "cardinality": int(non_null_series.nunique()),
        "cardinality_ratio": float(non_null_series.nunique() / total_rows) if total_rows > 0 else 0.0,
        "is_numeric": bool(pd.api.types.is_numeric_dtype(non_null_series)),
        "is_object": bool(pd.api.types.is_object_dtype(non_null_series)),
    }

    # --- 1. STATISTICAL FEATURES (Numeric Only) ---
    if pd.api.types.is_numeric_dtype(non_null_series) and not non_null_series.empty:
        col_features["min_val"] = float(non_null_series.min())
        col_features["max_val"] = float(non_null_series.max())
        col_features["mean_val"] = float(non_null_series.mean())
        col_features["std_val"] = float(non_null_series.std())
        col_features["neg_ratio"] = float((non_null_series < 0).sum() / len(non_null_series))
        col_features["is_integer"] = bool((non_null_series % 1 == 0).all())
        
              
                # --- ROBUST DECIMAL CALCULATION (FIXED) ---
        str_series = non_null_series.astype(str)
        
        # Split by '.' and extract the second part (index 1)
        # We use .apply to ensure we get a standard Series, not a StringMethods object
        def get_decimal_part(val):
            parts = str(val).split('.')
            return parts if len(parts) > 1 else None

        decimal_parts = str_series.apply(get_decimal_part)
        
        # Now decimal_parts is a standard Series, so fillna works perfectly
        decimal_lengths = decimal_parts.fillna('').str.len()
        col_features["decimal_places_mean"] = float(decimal_lengths.mean())
        # ------------------------------------------
        
        # For string-based pattern matching on numeric data, we still convert to string
        # But we only do this if the column is numeric to avoid double conversion later
        sample_vals = str_series.head(50)
    else:
        # If not numeric, initialize numeric stats as 0 or None
        col_features["min_val"] = 0.0
        col_features["max_val"] = 0.0
        col_features["mean_val"] = 0.0
        col_features["std_val"] = 0.0
        col_features["neg_ratio"] = 0.0
        col_features["is_integer"] = False
        col_features["decimal_places_mean"] = 0.0
        
        sample_vals = non_null_series.astype(str).head(50)

    # --- 2. PATTERN MATCHING & STRING STATS (Run for ALL columns) ---
    # This ensures these keys exist even if the column is numeric
    
    def calc_match_ratio(pattern):
        if sample_vals.empty: return 0.0
        return float(sample_vals.str.contains(pattern, regex=True).mean())

    col_features["match_date"] = calc_match_ratio(patterns['is_date'])
    col_features["match_timestamp"] = calc_match_ratio(patterns['is_timestamp'])
    col_features["match_currency"] = calc_match_ratio(patterns['is_currency'])
    col_features["match_percentage"] = calc_match_ratio(patterns['is_percentage'])
    col_features["match_uuid"] = calc_match_ratio(patterns['is_uuid'])
    col_features["match_time_period"] = calc_match_ratio(patterns['is_time_period'])
    col_features["match_boolean"] = calc_match_ratio(patterns['is_boolean'])
    
    # String length stats
    col_features["string_len_mean"] = float(sample_vals.str.len().mean()) if not sample_vals.empty else 0.0
    col_features["string_len_std"] = float(sample_vals.str.len().std()) if not sample_vals.empty else 0.0

    # --- 3. HEADER KEYWORD CHECKS (Run for ALL columns) ---
    col_lower = col_name.lower()
    col_features["has_id_keyword"] = any(k in col_lower for k in ['id', 'uuid', 'code', 'key'])
    col_features["has_date_keyword"] = any(k in col_lower for k in ['date', 'time', 'year', 'month'])
    col_features["has_money_keyword"] = any(k in col_lower for k in ['price', 'cost', 'revenue', 'total', 'amount'])
    col_features["has_change_keyword"] = any(k in col_lower for k in ['change', 'diff', 'delta', 'growth'])
    col_features["has_ratio_keyword"] = any(k in col_lower for k in ['ratio', 'margin', 'rate', 'percent'])
    col_features["has_geo_keyword"] = any(k in col_lower for k in ['country', 'region', 'city', 'state'])
    col_features["has_score_keyword"] = any(k in col_lower for k in ['score', 'rating', 'grade'])

    return col_features