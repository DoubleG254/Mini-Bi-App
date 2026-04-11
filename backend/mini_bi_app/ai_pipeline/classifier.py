import subprocess
import json

def query_llm(prompt):
    result = subprocess.run(
        ["ollama", "run", "deepseek-r1:1.5b"],
        input=prompt,
        text=True,
        capture_output=True
    )
    return result.stdout


def llm_classify(col_name, features):
    prompt = f"""
    Classify the semantic type and recommend an aggregation method for the dataset column based on its name and features.
    1. Semantic type (choose one from the list or create a new one reasonably):
    - financial_total
    - performance_score
    - countable
    - ratio
    - category
    - identifier
    - other
 
 2. Recommended aggregation:
    - sum
    - mean
   - count
   - none


    Column: {col_name}
    Features: {features}

    only respond in the following JSON format
    {{
      "semantic": "...",
      "aggregation": "..."
    }}
    """

    response = query_llm(prompt)

    try:
        # return json.loads(response)
        return response.strip()
    except:
        return {"semantic": "general", "aggregation": "mean"}