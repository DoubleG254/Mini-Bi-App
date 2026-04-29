import subprocess
import json

def query_llm(prompt):
    result = subprocess.run(
        ["ollama", "run", "gemma3:1b"],
        input=prompt,
        text=True,
        capture_output=True
    )
    return result.stdout


def llm_classify(col_name, features):
    SYSTEM_PROMPT = """
    You are an expert data analyst specializing in column classification.
    Your task is to classify dataset columns into semantic types based on
    their name, statistics, and sample values.

    SEMANTIC TYPES AND THEIR RULES:
    ================================

    IDENTIFIERS (never aggregate):
    - "identifier": Unique row IDs (user_id, order_id, patient_id)
    → High unique ratio (>0.9), sequential integers
    - "code": Standardized codes (GL accounts, SKU, SWIFT, postal codes)
    → Numeric or alphanumeric but NOT measurable, represents a label

    TEMPORAL (never aggregate):
    - "date": Calendar dates (2023-01-15, 01/15/2023)
    → String date patterns, not numeric values
    - "timestamp": Date + time (2023-01-15 14:30
    - "time_period": Years, quarters, semesters, fiscal periods
    → Small range integers like 2019-2025, or strings like "Q1 2023"
    → CRITICAL: Years (2019, 2020...) are time_period NOT financial data
    - "duration": Time intervals (5 days, 2 hours)

    CATEGORICAL (aggregation = none):
    - "category": Discrete labels with low cardinality
    → Department names, account types, payment methods, status
    → CRITICAL: aggregation is always "none" NOT "count"
    - "ordinal": Ordered categories (low/medium/high, A/B/C grades)
    - "geographic": Locations, countries, cities, states, regions
    → State abbreviations (OR, CA, NY), country codes (USA, GBR)
    → CRITICAL: State/country codes are "geographic" NOT "other"

    NUMERIC MEASUREMENTS:
    - "measurement": Physical quantities (height, weight, temperature, age)
    → Continuous values with meaningful units
    - "count": Integer counts of occurrences
    → num_transactions, num_employees, quantity ordered
    → aggregation = "sum"
    - "ratio": Percentages, rates, proportions (0-1 or 0-100 range)
    → aggregation = "mean"

    FINANCIAL:
    - "financial_total": Absolute monetary amounts
    → price, revenue, salary, cost, balance, invoice amount
    → Can be large values, may include negatives (refunds)
    → aggregation = "sum"
    → CRITICAL: "amount", "price", "cost", "revenue" = financial_total
    - "financial_change": Monetary deltas, differences, adjustments
    → profit, loss, discount, variance, growth_amount
    → aggregation = "sum"
    → CRITICAL: Only use when column represents a CHANGE not a total

    PERFORMANCE:
    - "performance_score": Ratings, scores, GPA, credit scores
    → aggregation = "mean"
    - "index": Indexed reference values (stock index, price index)
    - "quality_metric": Accuracy, precision, F1 scores

    TEXT (aggregation = none):
    - "text": Free-form text, descriptions, comments, notes
    - "email": Email addresses
    - "url": Web addresses  
    - "phone": Phone numbers
    → CRITICAL: Vendor names, company names = "text" NOT "other"

    BOOLEAN (aggregation = "sum"):
    - "boolean": True/False, Yes/No, 1/0 flags

    FALLBACK:
    - "other": Only use when NO other type fits

    AGGREGATION RULES:
    ==================
    - "none"  → identifier, code, date, timestamp, time_period, duration,
                category, ordinal, geographic, text, email, url, phone
    - "sum"   → count, financial_total, financial_change, boolean
    - "mean"  → measurement, ratio, performance_score, quality_metric, index
    - "count" → NEVER use this as aggregation (use "none" for categories)

    DECISION EXAMPLES:
    ==================
    fiscal_year with values [2019, 2020, 2021] → time_period, none
    department with values ['HR', 'Finance']   → category, none
    amount with values [1500.00, 2300.50]      → financial_total, sum
    vendor_name with values ['ACME Inc']       → text, none
    state with values ['OR', 'CA', 'NY']       → geographic, none
    gl_acct with values [79020, 85010]         → code, none
    profit with values [500, -200, 300]        → financial_change, sum
    """
    USER_PROMPT_TEMPLATE = """
    Classify this dataset column:

    Column Name: "{col_name}"
    Sample Values: {sample_values}
    Is Numeric: {is_numeric}
    Is Integer: {is_integer}
    Unique Ratio: {unique_ratio}
    Mean: {mean}
    Std: {std}
    Min: {min}
    Max: {max}

    Think step by step:
    1. What do the sample values look like?
    2. What does the column name suggest?
    3. Apply the classification rules above

    Respond ONLY in this exact JSON format with no extra text:
    {{
    "semantic": "<type>",
    "aggregation": "<method>"
    }}
    """

    response = query_llm(SYSTEM_PROMPT + USER_PROMPT_TEMPLATE.format(
        col_name=col_name,
        sample_values=features['sample_values'],
        is_numeric=features['is_numeric'],
        is_integer=features['is_integer'],
        unique_ratio=features['unique_ratio'],
        mean=features['mean'],
        std=features['std'],
        min=features['min'],
        max=features['max']
    ))
    print(f"LLM raw response for column '{col_name}': {response}")

    try:
        # return json.loads(response)
        return response.strip()
    except:
        return {"semantic": "general", "aggregation": "mean"}




USER_PROMPT_TEMPLATE = """
Classify this dataset column:

Column Name: "{col_name}"
Sample Values: {sample_values}
Is Numeric: {is_numeric}
Is Integer: {is_integer}
Unique Ratio: {unique_ratio}
Mean: {mean}
Std: {std}
Min: {min}
Max: {max}

Think step by step:
1. What do the sample values look like?
2. What does the column name suggest?
3. Apply the classification rules above

Respond ONLY in this exact JSON format with no extra text:
{{
  "semantic": "<type>",
  "aggregation": "<method>"
}}
"""

