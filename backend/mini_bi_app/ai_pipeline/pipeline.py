from classifier import classify_columns
from loader import load_dataset
from preprocess import preprocess
from features import extract_features
import os
# from .models import ColumnTrainingData
# import json

def run_pipeline(file_path):
    df= load_dataset(file_path)
    if df is None:
        print("Failed to load dataset. Exiting.")
        return
    df = preprocess(df)
    profiles = classify_columns(df)
    print(profiles)

# Construct the file path relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up 2 levels to reach the backend directory (ai_pipeline -> mini_bi_app -> backend)
backend_dir = os.path.dirname(os.path.dirname(script_dir))
file_path = os.path.join(backend_dir, "media", "datasets", "btb2024_commercial_dataset_4.csv")

run_pipeline(file_path)