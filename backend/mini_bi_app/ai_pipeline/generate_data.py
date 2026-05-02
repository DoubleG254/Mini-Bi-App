import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta

# --- 1. Define the Feature Extraction Function (from previous step) ---
import pandas as pd
import numpy as np
import re
import warnings

# Suppress the specific regex warning for cleaner output
warnings.filterwarnings("ignore", message=".*match groups.*")

def extract_single_column_features(series: pd.Series, col_name: str) -> dict:
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
# --- 2. Synthetic Data Generators ---
def generate_uuid():
    return f"{random.randint(10000000,99999999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(100000000000,999999999999)}"

def generate_date():
    start = datetime(2020, 1, 1)
    end = datetime(2026, 1, 1)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

def generate_timestamp():
    start = datetime(2020, 1, 1)
    end = datetime(2026, 1, 1)
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_secs = random.randint(0, 86400)
    return (start + timedelta(days=random_days, seconds=random_secs)).strftime('%Y-%m-%d %H:%M:%S')

def generate_financial_total():
    return round(random.uniform(1000, 5000000), 2)

def generate_financial_change():
    return round(random.uniform(-500000, 500000), 2)

def generate_ratio():
    return round(random.uniform(0.01, 1.5), 4)

def generate_percentage():
    return f"{round(random.uniform(0, 100), 2)}%"

def generate_geo():
    return random.choice(['USA', 'UK', 'Germany', 'France', 'Japan', 'Canada', 'Brazil', 'India'])

def generate_time_period():
    return random.choice(['Q1', 'Q2', 'Q3', 'Q4', 'H1', 'H2', 'FY2023', 'FY2024', 'Jan', 'Feb', 'Mar'])

def generate_boolean():
    return random.choice(['True', 'False', 'Yes', 'No', '1', '0'])

def generate_score():
    return random.randint(1, 100)

def generate_countable():
    return random.randint(1, 10000)

def generate_category():
    return random.choice(['Electronics', 'Clothing', 'Food', 'Services', 'Utilities'])

# --- 3. Training Data Generator ---
def generate_training_dataset(num_samples=1000):
    """
    Generates a list of dictionaries containing:
    - column_name
    - features (dict)
    - semantic_label (string)
    - sample_data (list of 5 values)
    """
    semantic_types = [
        "identifier", "date", "timestamp", "time_period", "category", 
        "ordinal", "geographic", "measurement", "countable", "ratio", 
        "financial_total", "financial_change", "performance_score", "boolean", "other"
    ]
    
    # Mapping of semantic type to generator function and column name pattern
    type_map = {
        "identifier": (generate_uuid, "user_id"),
        "date": (generate_date, "transaction_date"),
        "timestamp": (generate_timestamp, "created_at"),
        "time_period": (generate_time_period, "fiscal_quarter"),
        "category": (generate_category, "product_category"),
        "ordinal": (generate_countable, "rank"), # Using countable as ordinal proxy
        "geographic": (generate_geo, "country"),
        "measurement": (lambda: round(random.uniform(0.5, 100.5), 2), "weight_kg"),
        "countable": (generate_countable, "quantity_sold"),
        "ratio": (generate_ratio, "profit_margin"),
        "financial_total": (generate_financial_total, "revenue"),
        "financial_change": (generate_financial_change, "yoy_growth"),
        "performance_score": (generate_score, "customer_score"),
        "boolean": (generate_boolean, "is_active"),
        "other": (lambda: f"random_text_{random.randint(1,100)}", "notes")
    }

    training_data = []

    for _ in range(num_samples):
        # Randomly select a semantic type
        label = random.choice(semantic_types)
        gen_func, base_name = type_map[label]
        
        # Generate column name (add some noise/variation)
        suffixes = ["", "_id", "_val", "_2024", "_final"]
        col_name = f"{base_name}{random.choice(suffixes)}"
        
        # Generate data (100 rows per column for feature extraction)
        data = [gen_func() for _ in range(100)]
        series = pd.Series(data)
        
        # Extract features
        features = extract_single_column_features(series, col_name)
        
        # Prepare sample data (first 5 values)
        sample_data = data[:5]
        
        # Construct the record
        record = {
            "column_name": col_name,
            "features": features,
            "semantic_label": label,
            "sample_data": sample_data
        }
        
        training_data.append(record)
    
    return training_data

# --- 4. Execution & Export ---
if __name__ == "__main__":
    print("Generating synthetic training data...")
    dataset = generate_training_dataset(num_samples=2000) # Generate 500 samples
    
    # Convert to JSON string
    json_output = json.dumps(dataset, indent=2)
    
    # Save to file
    with open("financial_column_training_data.json", "w") as f:
        f.write(json_output)
    
    print(f"Successfully generated {len(dataset)} training records.")
    print("Saved to 'financial_column_training_data.json'")
    
    # Print a sample record for verification
    print("\n--- Sample Record ---")
    print(json.dumps(dataset, indent=2))