from classifier import llm_classify
from loader import load_dataset
from preprocess import preprocess
from features import extract_features
# from .models import ColumnTrainingData
# import json

def run_pipeline(file_path):
    df= load_dataset(file_path)
    df = preprocess(df)
    for col in df.columns:
        feature=extract_features(df,col)
        print(f"Extracted features for column '{col}':\n {feature}")
        print("-------------------------------------------------------------")


        llm_result = llm_classify(col, feature)
        # print(f"LLM Classification for column '{col}': {llm_result}")
run_pipeline("Mini-Bi-App/backend/media/datasets/Lottery_Expenditures_-_Multi-Year_Report.csv")