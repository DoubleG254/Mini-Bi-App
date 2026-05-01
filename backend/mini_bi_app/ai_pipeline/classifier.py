import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import django
from django.conf import settings
# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_bi.settings')
django.setup()
import joblib
from .features import extract_features
from .llm import llm_classify
# from mini_bi_app.models import ColumnTrainingData
from mini_bi_app.models import ColumnPrediction

# Construct the model path relative to this script's location
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
model = joblib.load(MODEL_PATH)

def classify_column(df, col, dataset_instance=None):
    features = extract_features(df, col)
    # print(f"Classifying column: {col} with features: {features}")

    prediction = model.predict([list(features.values())])[0]
    confidence = max(model.predict_proba([list(features.values())])[0])

    def get_aggregation_from_label(semantic_label):
   
        if semantic_label in ['count', 'financial_total', 'financial_change', 'boolean']:
            return 'sum'
        elif semantic_label in ['measurement', 'ratio', 'performance_score', 'quality_metric', 'index']:
            return 'mean'
        else:
            return 'none'

    # if confidence < 0.7:
    #     llm_result = llm_classify(col, features)

    #     # store for learning
    #     ColumnTrainingData.objects.create(
    #         column_name=col,
    #         features=features,
    #         semantic_label=llm_result["semantic"],
    #         aggregation=llm_result["aggregation"]
    #     )


    #     return llm_result

    if dataset_instance:
        ColumnPrediction.objects.create(
            dataset=dataset_instance,
            column_name=col,
            semantic_label=prediction,
            confidence_score=confidence,
            aggregation=get_aggregation_from_label(prediction)
        )

    return {
        "semantic": prediction,
        "confidence": confidence,
        "aggregation": get_aggregation_from_label(prediction)
    }


def classify_columns(df,dataset_instance=None):
    profiles = {}

    for col in df.columns:
        profiles[col] = classify_column(df, col,dataset_instance)

    return profiles