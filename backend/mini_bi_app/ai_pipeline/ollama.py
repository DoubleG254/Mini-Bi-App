import ollama
import json
import time
import re

class OllamaLabeler:
    
    def __init__(self, model="deepseek-r1:7b"):
        self.model = model
        self.semantic_types = [
            "identifier", "date", "timestamp", "time_period",
             "category", "ordinal", "geographic", "measurement",
            "countable", "ratio", "financial_total", "financial_change",
            "performance_score","boolean", "other"
        ]
    
    def build_prompt(self, col_name: str, features: dict) -> str:
        return f"""
You are a data classification expert. Classify the column based on 
its name, statistical features, and sample values.

Column Name: {col_name}
Sample Values: {features['sample_values']}
Features:{features}
  

Valid semantic types: {', '.join(self.semantic_types)}

Valid aggregation methods: sum, mean, count, none

Respond ONLY in this exact JSON format:
{{
  "semantic": "<type>",
  "aggregation": "<method>"
}}
"""
    
    def label_column(self, col_name: str, features: dict, 
                      retries=3) -> dict | None:
        prompt = self.build_prompt(col_name, features)
        
        for attempt in range(retries):
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.1}  # Low temp for consistency
                )
                
                content = response["message"] ["content"].strip()
                
                # Extract JSON from response
                json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    
                    # Validate response
                    if result.get("semantic") in self.semantic_types:
                        return result
            
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        return None
    
   