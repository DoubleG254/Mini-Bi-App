from operator import ge
# from mini_bi_app.models import Report
from .classifier import classify_columns
from .loader import load_dataset
from .preprocess import preprocess
from .relationship import detect_relationships, analyze_relationships,generate_charts_for_frontend
import os

# import json

def run_pipeline(file_path,dataset_instance=None):
    df= load_dataset(file_path)
    if df is None:
        print("Failed to load dataset. Exiting.")
        return
    df = preprocess(df)
    profiles = classify_columns(df,dataset_instance)
    print(profiles)
    # relationships = detect_relationships(df, profiles)
    # analysis_results = analyze_relationships(df, relationships)
    # charts = generate_charts_for_frontend(analysis_results)
    # report = Report.objects.create(
    #     dataset=dataset_instance,
    #     summary=profiles,
    #     charts=charts
    # )
    
    # return report


# Construct the file path relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up 2 levels to reach the backend directory (ai_pipeline -> mini_bi_app -> backend)
backend_dir = os.path.dirname(os.path.dirname(script_dir))
file_path = os.path.join(backend_dir, "media", "datasets", "Data.Gov-FY25Q4.csv")

if __name__ == "__main__":
    run_pipeline(file_path)