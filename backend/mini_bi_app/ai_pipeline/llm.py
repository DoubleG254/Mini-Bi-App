import subprocess
import json
import re

def query_llm(prompt):
    
    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1:1.5b","--think=false"],
            input=prompt,
            text=True,
            encoding='utf-8',
            capture_output=True,
            timeout=1000
        )
        
        print(f"[DEBUG] Ollama return code: {result.returncode}")
        print(f"[DEBUG] Ollama stdout length: {len(result.stdout) if result.stdout else 0}")
        
        if result.returncode != 0:
            print(f"[DEBUG] Ollama stderr: {result.stderr}")
            return '{"semantic": "general", "aggregation": "mean"}'
        
        if result.stdout and result.stdout.strip():
            return result.stdout
        else:
            print("[DEBUG] Ollama returned empty output. Using default classification.")
            return '{"semantic": "general", "aggregation": "mean"}'
            
    except subprocess.TimeoutExpired:
        print("[DEBUG] Ollama timed out (30s). Using default classification.")
        return '{"semantic": "general", "aggregation": "mean"}'
    except Exception as e:
        print(f"[DEBUG] Ollama error: {type(e).__name__}: {e}")
        return None


def llm_classify(col_name, features,sample_values):
    SYSTEM_PROMPT = """
    You are an expert data analyst specializing in column classification.
    Your task is to classify dataset columns into semantic types based on
    their name, statistics, and sample values.

    SEMANTIC TYPES AND THEIR RULES:
    ================================

    - "identifier": Unique row IDs (user_id, order_id, patient_id)
    → High unique ratio (>0.9), sequential integers
    - "code": Standardized codes (GL accounts, SKU, SWIFT, postal codes)
    → Numeric or alphanumeric but NOT measurable, represents a label

    :
    - "date": Calendar dates (2023-01-15, 01/15/2023)
    → String date patterns, not numeric values
    - "timestamp": Date + time (2023-01-15 14:30
    - "time_period": Years, quarters, semesters, fiscal periods
    → Small range integers like 2019-2025, or strings like "Q1 2023"
    → CRITICAL: Years (2019, 2020...) are time_period NOT financial data
    - "duration": Time intervals (5 days, 2 hours)

   
    - "category": Discrete labels with low cardinality
    → Department names, account types, payment methods, status
    → CRITICAL: aggregation is always "none" NOT "count"
    - "ordinal": Ordered categories (low/medium/high, A/B/C grades)
    - "geographic": Locations, countries, cities, states, regions
    → State abbreviations (OR, CA, NY), country codes (USA, GBR)
    → CRITICAL: State/country codes are "geographic" NOT "other"

    - "measurement": Physical quantities (height, weight, temperature, age)
    → Continuous values with meaningful units
    - "count": Integer counts of occurrences
    → num_transactions, num_employees, quantity ordered
    → aggregation = "sum"
    - "ratio": Percentages, rates, proportions (0-1 or 0-100 range)
    → aggregation = "mean"

   
    - "financial_total": Absolute monetary amounts
    → price, revenue, salary, cost, balance, invoice amount
    → Can be large values, may include negatives (refunds)
    → aggregation = "sum"
    → CRITICAL: "amount", "price", "cost", "revenue" = financial_total
    - "financial_change": Monetary deltas, differences, adjustments
    → profit, loss, discount, variance, growth_amount
    → aggregation = "sum"
    → CRITICAL: Only use when column represents a CHANGE not a total

   
    - "performance_score": Ratings, scores, GPA, credit scores
    → aggregation = "mean"
    - "index": Indexed reference values (stock index, price index)
    - "quality_metric": Accuracy, precision, F1 scores

    
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
    Features: {features}
    Sample_values: {sample_values}

   

    Respond ONLY in this exact JSON format with no extra text or thinking:
    {{
    "semantic": "<type>",
    "aggregation": "<method>"
    }}
    """

    response = query_llm(SYSTEM_PROMPT + USER_PROMPT_TEMPLATE.format(
        col_name=col_name,
        features = features,
        sample_values = sample_values
                ))
    print(f"LLM raw response for column '{col_name}': {response}")

    try:
        # Extract JSON from response (handles cases where LLM adds explanation before/after)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            print(f"[ERROR] Could not find JSON in response")
            return {"semantic": "general", "aggregation": "mean"}
    except Exception as e:
        print(f"[ERROR] Failed to parse LLM response: {e}")
        return {"semantic": "general", "aggregation": "mean"}





