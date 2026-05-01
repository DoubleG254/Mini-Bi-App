import pandas as pd
import numpy as np

def detect_relationships(df, profiles):
    relationships = []
    cols = list(df.columns)
    
    # Define semantic mappings based on your categorizations
    # Note: Ensure 'profiles' has 'semantic' keys matching your categories
    # e.g., profiles = {"revenue": {"semantic": "financial_total"}, ...}

    for col1 in cols:
        for col2 in cols:
            if col1 == col2:
                continue

            p1 = profiles.get(col1, {})
            p2 = profiles.get(col2, {})
            
            s1 = p1.get("semantic")
            s2 = p2.get("semantic")

            # 1. Time Series Trends (Date/Time + Financial/Performance)
            if s1 in ["date", "timestamp", "time_period"] and s2 in ["financial_total", "financial_change", "performance_score"]:
                relationships.append(("time_series", col1, col2))
            
            # 2. Category Comparisons (Category + Financial/Performance)
            elif s1 in ["category", "geographic", "ordinal"] and s2 in ["financial_total", "financial_change", "performance_score"]:
                relationships.append(("category_comparison", col1, col2))
            
            # 3. Correlations (Ratio/Measurement + Financial)
            elif s1 in ["ratio", "measurement", "countable"] and s2 in ["financial_total", "financial_change"]:
                relationships.append(("correlation", col1, col2))
            
            # 4. Geographic Analysis (Geographic + Financial)
            elif s1 == "geographic" and s2 in ["financial_total", "financial_change"]:
                relationships.append(("geographic_heatmap", col1, col2))

    return relationships

def analyze_relationships(df, relationships):
    results = []

    for rel_type, col1, col2 in relationships:
        # Handle Time Series
        if rel_type == "time_series":
            # Ensure col1 is datetime
            df_temp = df.copy()
            df_temp[col1] = pd.to_datetime(df_temp[col1], errors='coerce')
            # Sort by time and group (e.g., by month or day)
            if df_temp[col1].notna().all():
                # Resample logic could go here for better granularity
                grouped = df_temp.groupby(df_temp[col1].dt.to_period('M'))[col2].mean() 
                results.append({
                    "type": "time_series",
                    "x": col1,
                    "y": col2,
                    "data": grouped.to_dict()
                })

        # Handle Category Comparisons
        elif rel_type == "category_comparison":
            # Drop NaNs for grouping
            clean_df = df.dropna(subset=[col1, col2])
            grouped = clean_df.groupby(col1)[col2].mean().sort_values(ascending=False)
            results.append({
                "type": "category_comparison",
                "x": col1,
                "y": col2,
                "data": grouped.to_dict()
            })

        # Handle Correlations (Scatter/Heatmap)
        elif rel_type == "correlation":
            clean_df = df.dropna(subset=[col1, col2])
            if len(clean_df) > 1:
                corr = clean_df[col1].corr(clean_df[col2])
                results.append({
                    "type": "correlation",
                    "x": col1,
                    "y": col2,
                    "data": {"correlation": corr, "points": clean_df.to_dict()}
                })
        
        # Handle Geographic
        elif rel_type == "geographic_heatmap":
            clean_df = df.dropna(subset=[col1, col2])
            grouped = clean_df.groupby(col1)[col2].sum() # Sum for totals, mean for rates
            results.append({
                "type": "geographic_heatmap",
                "x": col1,
                "y": col2,
                "data": grouped.to_dict()
            })

    return results

def select_chart_type(result):
    t = result["type"]
    if t == "time_series":
        return "line" # Or "area" for financial totals
    elif t == "category_comparison":
        return "bar"
    elif t == "correlation":
        return "scatter"
    elif t == "geographic_heatmap":
        return "heatmap" # Requires a library like Plotly or Folium for maps
    return "bar"

def generate_charts_for_frontend(results):
    charts = {}
    for r in results:
        chart_type = select_chart_type(r)
        data_points = r["data"]
        
        # Normalize data based on chart type
        if chart_type == "line" or chart_type == "bar":
            # Convert dict to lists: {label: val} -> labels=[...], values=[...]
            labels = list(data_points.keys())
            values = list(data_points.values())
            
            # For time series, ensure labels are formatted strings if needed
            if chart_type == "line" and r["type"] == "time_series":
                # Optional: Format dates if they are datetime objects
                pass 

            chart_config = {
                "id": f"chart_{r['x']}_{r['y']}",
                "type": chart_type,
                "title": f"{r['y']} by {r['x']}",
                "labels": labels,
                "datasets": [{
                    "label": r['y'],
                    "data": values,
                    "borderColor": "#36a2eb", # Chart.js default blue
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "fill": chart_type == "line", # Fill area for line charts
                    "tension": 0.4 # Smooth curves for line charts
                }]
            }
            
            # Special handling for Correlation (Scatter)
            if r["type"] == "correlation":
                points_data = data_points.get("points", {})
                x_vals = points_data.get(r['x'], [])
                y_vals = points_data.get(r['y'], [])
                chart_config = {
                    "id": f"chart_{r['x']}_{r['y']}",
                    "type": "scatter",
                    "title": f"Correlation: {r['x']} vs {r['y']}",
                    "datasets": [{
                        "label": "Data Points",
                        "data": [{"x": x, "y": y} for x, y in zip(x_vals, y_vals)],
                        "backgroundColor": "rgba(255, 99, 132, 0.5)"
                    }],
                    "correlation_coefficient": data_points.get("correlation")
                }

            charts[f"chart_{r['x']}_{r['y']}"] = chart_config

    return charts