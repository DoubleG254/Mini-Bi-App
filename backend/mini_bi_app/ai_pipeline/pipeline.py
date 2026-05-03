from operator import ge
# from mini_bi_app.models import Report
from .classifier import classify_columns
from .loader import load_dataset
from .preprocess import preprocess
from .relationship import detect_relationships, analyze_relationships,generate_charts_for_frontend
import os
import warnings

# Suppress scikit-learn parallel warnings
warnings.filterwarnings("ignore", message=".*sklearn.utils.parallel.delayed.*")
warnings.filterwarnings("ignore", message=".*sklearn.utils.parallel.Parallel.*")

# import json

def run_pipeline(file_path,dataset_instance=None):
    df= load_dataset(file_path)
    if df is None:
        print("Failed to load dataset. Exiting.")
        return
    df = preprocess(df)
    profiles = classify_columns(df,dataset_instance)
    print(profiles)
    relationships = detect_relationships(df, profiles)
    analysis_results = analyze_relationships(df, relationships)
    charts = generate_charts_for_frontend(analysis_results)
    report = Report.objects.create(
        dataset=dataset_instance,
        summary=profiles,
        charts=charts
    )
    
    return report


# # Construct the file path relative to this script's location
# script_dir = os.path.dirname(os.path.abspath(__file__))
# # Navigate up 2 levels to reach the backend directory (ai_pipeline -> mini_bi_app -> backend)
# backend_dir = os.path.dirname(os.path.dirname(script_dir))
# test_data_dir = os.path.join(backend_dir, "test_data")

# if __name__ == "__main__":
#     # Check if test_data directory exists
#     if not os.path.exists(test_data_dir):
#         print(f"Error: test_data directory not found at {test_data_dir}")
#         exit(1)
    
#     # Get all CSV and Excel files from test_data directory
#     supported_extensions = ('.csv', '.xlsx', '.xls')
#     files = [f for f in os.listdir(test_data_dir) if f.lower().endswith(supported_extensions)]
    
#     if not files:
#         print(f"No CSV or Excel files found in {test_data_dir}")
#         exit(1)
    
#     print(f"Found {len(files)} file(s) to process:\n")
    
#     # Process each file
#     for idx, filename in enumerate(files, 1):
#         file_path = os.path.join(test_data_dir, filename)
#         print(f"\n{'='*80}")
#         print(f"[{idx}/{len(files)}] Processing: {filename}")
#         print(f"{'='*80}")
        
#         try:
#             run_pipeline(file_path)
#         except Exception as e:
#             print(f"ERROR processing {filename}: {e}")
#             continue
    
#     print(f"\n{'='*80}")
#     print(f"Pipeline completed. Processed {len(files)} file(s).")
#     print(f"{'='*80}")