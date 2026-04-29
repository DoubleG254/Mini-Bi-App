import json
import random
import math
import numpy as np
from datetime import datetime, timedelta, date

# --- Configuration ---
NUM_SAMPLES = 5000  # Number of rows per column simulation
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# --- Semantic Definitions & Rules ---
SEMANTIC_RULES = {
    'identifier': {'agg': 'none', 'is_numeric': True, 'is_int': True, 'unique_ratio': 1.0},
    'code': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.3},
    'date': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.8},
    'timestamp': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.95},
    'time_period': {'agg': 'none', 'is_numeric': True, 'is_int': True, 'unique_ratio': 0.05},
    'duration': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.2},
    'category': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.1},
    'ordinal': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.15},
    'geographic': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.15},
    'measurement': {'agg': 'mean', 'is_numeric': True, 'is_int': False, 'unique_ratio': 0.6},
    'count': {'agg': 'sum', 'is_numeric': True, 'is_int': True, 'unique_ratio': 0.4},
    'ratio': {'agg': 'mean', 'is_numeric': True, 'is_int': False, 'unique_ratio': 0.7},
    'financial_total': {'agg': 'sum', 'is_numeric': True, 'is_int': False, 'unique_ratio': 0.9},
    'financial_change': {'agg': 'sum', 'is_numeric': True, 'is_int': False, 'unique_ratio': 0.85},
    'performance_score': {'agg': 'mean', 'is_numeric': True, 'is_int': False, 'unique_ratio': 0.5},
    'index': {'agg': 'mean', 'is_numeric': True, 'is_int': False, 'unique_ratio': 0.9},
    'quality_metric': {'agg': 'mean', 'is_numeric': True, 'is_int': False, 'unique_ratio': 0.8},
    'text': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.95},
    'email': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 1.0},
    'url': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 1.0},
    'phone': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.9},
    'boolean': {'agg': 'sum', 'is_numeric': True, 'is_int': True, 'unique_ratio': 0.1},
    'other': {'agg': 'none', 'is_numeric': False, 'is_int': False, 'unique_ratio': 0.05}
}

COLUMN_NAMES = {
    'identifier': ['user_id', 'order_id', 'transaction_id', 'customer_id', 'invoice_id', 'uuid', 'row_id', 'account_id'],
    'code': ['gl_account', 'sku_code', 'swift_code', 'postal_code', 'product_code', 'vendor_code', 'region_code', 'status_code', 'tax_id'],
    'date': ['transaction_date', 'order_date', 'payment_date', 'ship_date', 'expiry_date', 'birth_date', 'created_at', 'updated_at'],
    'timestamp': ['payment_ts', 'login_time', 'event_time', 'created_ts', 'last_seen', 'checkout_time'],
    'time_period': ['fiscal_year', 'quarter', 'fiscal_quarter', 'year', 'month', 'week_number', 'period_id', 'reporting_period'],
    'duration': ['payment_days', 'lease_term', 'warranty_period', 'delivery_time', 'tenure_days', 'grace_period'],
    'category': ['department', 'account_type', 'payment_method', 'transaction_status', 'product_category', 'business_unit', 'cost_center', 'vendor_type'],
    'ordinal': ['risk_rating', 'priority_level', 'credit_grade', 'satisfaction_score', 'urgency_level', 'quality_grade', 'approval_status', 'compliance_level'],
    'geographic': ['state_code', 'country_code', 'region_name', 'city_name', 'zip_code', 'province', 'district', 'sales_region', 'country'],
    'measurement': ['customer_age', 'weight_kg', 'height_cm', 'temperature_c', 'distance_km', 'volume_liters', 'area_sqft', 'speed_kmh'],
    'count': ['num_transactions', 'employee_count', 'order_qty', 'item_count', 'ticket_count', 'user_count', 'page_views', 'click_count', 'refund_count'],
    'ratio': ['interest_rate', 'default_rate', 'conversion_rate', 'margin_pct', 'tax_rate', 'discount_rate', 'utilization_rate', 'churn_rate', 'yield_rate'],
    'financial_total': ['invoice_amount', 'total_revenue', 'cost_of_goods', 'salary_amount', 'account_balance', 'payment_due', 'refund_amount', 'tax_liability', 'loan_principal', 'gross_profit', 'net_income', 'operating_expense', 'marketing_spend', 'rent_cost', 'price', 'amount', 'cost', 'revenue'],
    'financial_change': ['profit_loss', 'price_variance', 'budget_variance', 'discount_amount', 'growth_amount', 'yoy_change', 'margin_delta', 'expense_variance', 'revenue_growth', 'loss_amount', 'adjustment'],
    'performance_score': ['credit_score', 'customer_rating', 'employee_score', 'vendor_rating', 'quality_score', 'satisfaction_index', 'performance_index', 'reliability_score', 'efficiency_score', 'health_score'],
    'index': ['stock_index', 'price_index', 'consumer_index', 'market_index', 'inflation_index', 'hpi_index', 'ppi_index', 'gdp_index', 'sentiment_index'],
    'quality_metric': ['accuracy_score', 'f1_score', 'precision_rate', 'recall_rate', 'specificity_score', 'coverage_rate', 'compliance_rate', 'defect_rate', 'error_rate', 'success_rate'],
    'text': ['vendor_name', 'transaction_notes', 'customer_comments', 'product_description', 'memo', 'internal_notes', 'remarks', 'feedback_text', 'description', 'comment_field', 'company_name'],
    'email': ['customer_email', 'vendor_email', 'contact_email', 'billing_email', 'support_email', 'admin_email', 'sales_email'],
    'url': ['website_url', 'landing_page', 'checkout_url', 'redirect_url', 'affiliate_link', 'tracking_url', 'profile_url', 'api_endpoint'],
    'phone': ['contact_phone', 'billing_phone', 'support_phone', 'mobile_number', 'office_phone', 'fax_number', 'emergency_contact'],
    'boolean': ['is_verified', 'is_high_risk', 'is_active', 'is_approved', 'is_subscribed', 'is_premium', 'is_flagged', 'is_deleted', 'is_archived', 'is_completed', 'flag'],
    'other': ['legacy_flag', 'system_code', 'internal_ref', 'misc_data', 'temp_value', 'unnamed: 57', 'unnamed: 58']
}

def generate_value(sem_type, config):
    """Generates a single realistic value based on semantic type."""
    if sem_type == 'identifier':
        return f"ID_{random.randint(10000, 999999)}" if random.random() > 0.2 else random.randint(10000, 999999)
    if sem_type == 'code':
        prefixes = ['GL', 'SKU', 'SWIFT', 'POST', 'PROD', 'VEND', 'REG', 'TAX']
        return f"{random.choice(prefixes)}-{random.randint(100, 9999)}"
    if sem_type == 'date':
        d = date(2020, 1, 1) + timedelta(days=random.randint(0, 1500))
        formats = [d.isoformat(), d.strftime("%m/%d/%Y"), d.strftime("%d-%b-%Y")]
        return random.choice(formats)
    if sem_type == 'timestamp':
        dt = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1500), hours=random.randint(0,23), minutes=random.randint(0,59))
        return dt.isoformat()
    if sem_type == 'time_period':
        if random.random() > 0.5:
            return random.randint(2019, 2025)
        else:
            return f"Q{random.randint(1,4)} {random.randint(2020, 2025)}"
    if sem_type == 'duration':
        units = ['days', 'hours', 'months', 'years']
        return f"{random.randint(1, 365)} {random.choice(units)}"
    if sem_type == 'category':
        return random.choice(['Sales', 'Marketing', 'HR', 'Finance', 'Ops', 'IT', 'Logistics', 'Support'])
    if sem_type == 'ordinal':
        return random.choice(['Low', 'Medium', 'High', 'Critical', 'None'])
    if sem_type == 'geographic':
        if random.random() > 0.5:
            return random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'OH', 'WA', 'PA'])
        else:
            return random.choice(['USA', 'GBR', 'CAN', 'DEU', 'FRA', 'JPN'])
    if sem_type == 'text':
        return random.choice(['Pending Review', 'Approved', 'Closed', 'Open', 'In Progress', 'Vendor A', 'Company X'])
    if sem_type == 'measurement':
        return round(random.uniform(10, 1000), 2)
    if sem_type == 'count':
        return random.randint(0, 500)
    if sem_type == 'ratio':
        return round(random.uniform(0, 1), 4)
    if sem_type == 'financial_total':
        base = random.uniform(100, 50000)
        if random.random() > 0.9: base = -base
        return round(base, 2)
    if sem_type == 'financial_change':
        return round(random.uniform(-5000, 5000), 2)
    if sem_type == 'performance_score':
        return round(random.uniform(1.0, 100.0), 2)
    if sem_type == 'index':
        return round(random.uniform(1000, 50000), 2)
    if sem_type == 'quality_metric':
        return round(random.uniform(0.0, 1.0), 4)
    if sem_type == 'boolean':
        return 1 if random.random() > 0.5 else 0
    if sem_type == 'email':
        domains = ['example.com', 'corp.com', 'mail.com']
        return f"user{random.randint(1,999)}@{random.choice(domains)}"
    if sem_type == 'url':
        return f"https://www.{random.choice(['site', 'shop', 'app'])}.com/{random.randint(1,999)}"
    if sem_type == 'phone':
        return f"+1-555-{random.randint(1000, 9999)}"
    if sem_type == 'other':
        return f"Unknown_{random.randint(1, 100)}"
    return "N/A"

def calculate_stats(values, is_numeric):
    """Calculates statistical features for the model."""
    if not is_numeric:
        return {
            'mean': 0, 'std': 0, 'min': 0, 'max': 0,
            'skewness': 0.0, 'kurtosis': 0.0, 'zero_ratio': 0.0
        }
    
    clean_vals = [v for v in values if isinstance(v, (int, float))]
    if not clean_vals:
        return {
            'mean': 0, 'std': 0, 'min': 0, 'max': 0,
            'skewness': 0.0, 'kurtosis': 0.0, 'zero_ratio': 0.0
        }

    arr = np.array(clean_vals)
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    
    skew = float(np.mean(((arr - mean_val) / std_val) ** 3)) if std_val > 0 else 0.0
    kurt = float(np.mean(((arr - mean_val) / std_val) ** 4) - 3) if std_val > 0 else 0.0
    
    zero_count = np.sum(arr == 0)
    zero_ratio = float(zero_count / len(arr))
    
    return {
        'mean': round(mean_val, 2),
        'std': round(std_val, 2),
        'min': round(min_val, 2),
        'max': round(max_val, 2),
        'skewness': round(skew, 3),
        'kurtosis': round(kurt, 3),
        'zero_ratio': round(zero_ratio, 3)
    }

def extract_name_features(col_name):
    """Extracts binary features from column name."""
    name_lower = col_name.lower()
    
    # Geographic keywords
    geo_keywords = ['region', 'country', 'city', 'state', 'location']
    has_geo_keywords = 1 if any(kw in name_lower for kw in geo_keywords) else 0
    
    # Category keywords
    cat_keywords = ['category', 'type', 'status', 'group', 'class']
    has_cat_keywords = 1 if any(kw in name_lower for kw in cat_keywords) else 0
    
    return {
        'has_cost': 1 if 'cost' in name_lower or 'price' in name_lower or 'expense' in name_lower else 0,
        'has_revenue': 1 if 'revenue' in name_lower or 'income' in name_lower or 'profit' in name_lower else 0,
        'has_id': 1 if 'id' in name_lower or 'code' in name_lower or 'uuid' in name_lower else 0,
        'has_date': 1 if 'date' in name_lower or 'time' in name_lower or 'year' in name_lower or 'month' in name_lower else 0,
        'has_ratio': 1 if 'rate' in name_lower or 'ratio' in name_lower or 'percent' in name_lower else 0,
        'has_score': 1 if 'score' in name_lower or 'rating' in name_lower or 'index' in name_lower else 0,
        'has_bound': 1 if 'low' in name_lower or 'high' in name_lower or 'mid' in name_lower or 'bound' in name_lower else 0,
        'has_reg': 1 if 'regression' in name_lower or 'coef' in name_lower or 'beta' in name_lower else 0,
        'is_unnamed': 1 if 'unnamed' in name_lower or 'col_' in name_lower else 0,
        'has_geo_keywords': has_geo_keywords,
        'has_cat_keywords': has_cat_keywords,
        'name_length': len(col_name)
    }

def extract_pattern_features(values):
    """Extracts pattern detection features from data values."""
    import re
    
    # Convert values to strings for pattern matching
    str_values = [str(v) for v in values if v is not None]
    all_str = ' '.join(str_values)
    
    # Calculate unique ratio (number of unique values / total values)
    unique_count = len(set(str_values))
    total_count = len(str_values)
    unique_ratio = unique_count / total_count if total_count > 0 else 0
    
    # 1. URL Detection
    url_pattern = r'http[s]?://|www\.'
    url_count = sum(1 for v in str_values if re.search(url_pattern, v))
    has_url_pattern = 1 if url_count > 0 else 0
    
    # 2. Email Detection
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_count = sum(1 for v in str_values if re.search(email_pattern, v))
    has_email_pattern = 1 if email_count > 0 else 0
    
    # 3. Phone Detection
    phone_pattern = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
    phone_matches = sum(1 for v in str_values if re.match(phone_pattern, v))
    phone_ratio = phone_matches / len(str_values) if len(str_values) > 0 else 0
    has_phone_pattern = 1 if phone_ratio > 0.5 else 0
    
    # 4. Check for specific characters
    has_at_symbol = 1 if '@' in all_str else 0
    has_http = 1 if 'http' in all_str else 0
    has_dots = 1 if '.' in all_str else 0
    
    return {
        'unique_ratio': round(unique_ratio, 3),
        'has_url_pattern': has_url_pattern,
        'has_email_pattern': has_email_pattern,
        'has_phone_pattern': has_phone_pattern,
        'has_at_symbol': has_at_symbol,
        'has_http': has_http,
        'has_dots': has_dots,
        'phone_ratio': round(phone_ratio, 3)
    }

def generate_training_dataset():
    dataset = []
    
    # Define distribution to ensure balanced training
    # Weighting towards financial and numeric types to match real-world needs
    type_weights = {
        'financial_total': 20, 'financial_change': 10, 'count': 10, 'ratio': 8,
        'identifier': 8, 'code': 5, 'date': 5, 'timestamp': 4, 'time_period': 4,
        'category': 6, 'ordinal': 3, 'geographic': 3, 'measurement': 4,
        'performance_score': 4, 'index': 2, 'quality_metric': 2,
        'text': 5, 'email': 2, 'url': 1, 'phone': 1, 'boolean': 3, 'other': 2
    }
    
       # Create a list of types based on weights to ensure balanced sampling
    type_list = []
    for t, w in type_weights.items():
        type_list.extend([t] * w)
    
    # Shuffle to randomize order
    random.shuffle(type_list)
    
    # Generate multiple examples by repeating the type list
    # This ensures balanced distribution while reaching 5000 samples
    target_samples = 5000
    num_repeats = (target_samples + len(type_list) - 1) // len(type_list)  # Ceiling division
    extended_type_list = type_list * num_repeats
    
    # Generate examples until we reach target samples
    for sem_type in extended_type_list[:target_samples]:
        config = SEMANTIC_RULES[sem_type]
        
        # Select a random column name for this type
        name_pool = COLUMN_NAMES.get(sem_type, [f"{sem_type}_col"])
        col_name = random.choice(name_pool)
        
        # Generate synthetic data values (NUM_SAMPLES rows)
        raw_values = [generate_value(sem_type, config) for _ in range(NUM_SAMPLES)]
        
        # Calculate statistical features
        stats = calculate_stats(raw_values, config['is_numeric'])
        
        # Extract name-based features
        name_features = extract_name_features(col_name)
        
        # Extract pattern-based features
        pattern_features = extract_pattern_features(raw_values)
        
        # Merge stats, name features, and pattern features
        features = {**stats, **name_features, **pattern_features}
        
        # Add metadata
        record = {
            'column_name': col_name,
            'semantic_label': sem_type,
            'aggregation': config['agg'],
            'features': features,
            'sample_data': raw_values[:10] # Store first 10 values for inspection
        }
        dataset.append(record)

    return dataset

if __name__ == "__main__":
    print("Generating comprehensive financial training dataset...")
    training_data = generate_training_dataset()
    
    # Save to JSON
    output_file = 'financial_training_data_complete.json'
    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2, default=str)
    
    print(f" Successfully generated {len(training_data)} column examples.")
    print(f" Saved to: {output_file}")
    
    # Optional: Print a summary of generated types
    type_counts = {}
    for item in training_data:
        t = item['semantic_label']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print("\n Distribution of Semantic Types:")
    for t, count in sorted(type_counts.items()):
        print(f"  - {t}: {count}")