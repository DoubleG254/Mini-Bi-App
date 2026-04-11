from classifier import llm_classify
from loader import load_dataset
from preprocess import preprocess
from features import extract_features

def run_pipeline(file_path):
    df= load_dataset(file_path)
    df = preprocess(df)
    for col in df.columns:
        feature=extract_features(df,col)
        print(f"Extracted features for column '{col}': {feature}")
        # llm_result = llm_classify(col, feature)
        # print(f"LLM Classification for column '{col}': {llm_result}")
run_pipeline("backend/media/datasets/bios.csv")