import numpy as np
import pandas as pd

import pandas as pd
import numpy as np
import re

def extract_features(df, col):
    series = df[col]
    is_numeric = pd.api.types.is_numeric_dtype(series)
    non_null_series = series.dropna()
    
    # 1. Basic Numeric Stats
    mean_val = series.mean() if is_numeric else 0
    std_val = series.std() if is_numeric else 0
    min_val = series.min() if is_numeric else 0
    max_val = series.max() if is_numeric else 0
    
    # 2. Advanced Stats (only if numeric and enough data)
    skewness = 0
    kurtosis = 0
    zero_ratio = 0
    
    if is_numeric and len(non_null_series) > 1:
        skewness = non_null_series.skew()
        kurtosis = non_null_series.kurtosis()
        zero_count = (non_null_series == 0).sum()
        zero_ratio = zero_count / len(non_null_series)
    
    # Calculate unique ratio (number of unique values / total non-null values)
    unique_count = non_null_series.nunique()
    total_count = len(non_null_series)
    unique_ratio = unique_count / total_count if total_count > 0 else 0
    
    # 3. Semantic Type Detection (Heuristics based on column name and content)
    col_lower = col.lower()
    
    # Check for specific keywords in column name
    has_cost = 1 if 'cost' in col_lower or 'price' in col_lower else 0
    has_revenue = 1 if 'revenue' in col_lower or 'income' in col_lower else 0
    has_id = 1 if 'id' in col_lower or 'uuid' in col_lower else 0
    has_date = 1 if any(x in col_lower for x in ['date', 'time', 'timestamp', 'created', 'updated']) else 0
    # Keywords
    geo_keywords = ['region', 'country', 'city', 'state', 'location']
    has_geo_keywords = 1 if any(kw in col_lower for kw in geo_keywords) else 0
    
    cat_keywords = ['category', 'type', 'status', 'group', 'class']
    has_cat_keywords = 1 if any(kw in col_lower for kw in cat_keywords) else 0
    
    # Check for ratio-like names
    has_ratio = 1 if 'ratio' in col_lower or 'rate' in col_lower or '%' in col_lower else 0
    
    # Check for score-like names
    has_score = 1 if 'score' in col_lower or 'rating' in col_lower else 0
    
    # Check for bounds (e.g., min/max columns)
    has_bound = 1 if 'bound' in col_lower or 'limit' in col_lower else 0
    
    # Check for registration or region codes
    has_reg = 1 if 'reg' in col_lower or 'region' in col_lower else 0
    
    # Check if column name is generic (e.g., "unnamed", "col1", "field")
    is_unnamed = 1 if re.match(r'^(unnamed|col\d+|field\d+)$', col_lower) else 0
    
    # Initialize pattern features with defaults for non-string types
    has_url_pattern = 0
    has_email_pattern = 0
    has_phone_pattern = 0
    has_at_symbol = 0
    has_http = 0
    has_dots = 0
    phone_ratio = 0
    
    # Only apply string pattern detection if series is string type
    if pd.api.types.is_string_dtype(non_null_series) or non_null_series.dtype == 'object':
        # Convert to string for pattern matching
        str_series = non_null_series.astype(str)
        
        # 1. URL Detection
        url_pattern = r'http[s]?://|www\.'
        url_count = str_series.str.contains(url_pattern, regex=True, na=False).sum()
        has_url_pattern = 1 if url_count > 0 else 0
        
        # 2. Email Detection
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_count = str_series.str.contains(email_pattern, regex=True, na=False).sum()
        has_email_pattern = 1 if email_count > 0 else 0
        
        # 3. Phone Detection (Flexible: handles spaces, dashes, parentheses)
        # Matches strings that look like phone numbers (e.g., 123-456-7890, (123) 456-7890)
        phone_pattern = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
        # Check if a significant portion of non-null values match the pattern
        phone_matches = str_series.str.match(phone_pattern, na=False)
        phone_ratio = phone_matches.sum() / len(str_series) if len(str_series) > 0 else 0
        has_phone_pattern = 1 if phone_ratio > 0.5 else 0 # If >50% look like phones
        
        # 4. Check for specific characters often found in these types
        all_str = str_series.str.cat(sep=' ')
        has_at_symbol = 1 if '@' in all_str else 0
        has_http = 1 if 'http' in all_str else 0
        has_dots = 1 if str_series.str.contains(r'\.', regex=True, na=False).sum() > 0 else 0

    
    return {
        'mean': mean_val,
        'std': std_val,
        'min': min_val,
        'max': max_val,
        'skewness': skewness,
        'kurtosis': kurtosis,
        'zero_ratio': zero_ratio,
        'unique_ratio': unique_ratio,
        'has_cost': has_cost,
        'has_revenue': has_revenue,
        'has_id': has_id,
        'has_date': has_date,
        'has_ratio': has_ratio,
        'has_score': has_score,
        'has_bound': has_bound,
        'has_reg': has_reg,
        'is_unnamed': is_unnamed,
        'has_url_pattern': has_url_pattern,
        'has_email_pattern': has_email_pattern,
        'has_phone_pattern': has_phone_pattern,
        'has_at_symbol': has_at_symbol,
        'has_http': has_http,
        'has_dots': has_dots,
        'has_geo_keywords': has_geo_keywords,
        'has_cat_keywords': has_cat_keywords,
        'phone_ratio': phone_ratio,
        'name_length': len(col)
    }