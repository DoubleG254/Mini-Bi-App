import os
import sys
import django
import numpy as np
import joblib

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mini_bi.settings")
django.setup()

from mini_bi_app.models import ColumnTrainingData
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


# -------------------------------
# 1. Load Data from Database
# -------------------------------
def load_training_data():
    data = ColumnTrainingData.objects.all()

    X = []
    y = []
    metadata = []  # Store aggregation separately

    for row in data:
        features = row.features
        label = row.semantic_label

        X.append([
            features.get("mean", 0),
            features.get("std", 0),
            features.get("max", 0),
            features.get("min", 0),
            features.get("skewness", 0),
            features.get("kurtosis", 0),
            features.get("zero_ratio", 0),
            features.get("unique_ratio", 0),
            features.get("has_cost", 0),
            features.get("has_revenue", 0),
            features.get("has_id", 0),
            features.get("has_date", 0),
            features.get("has_ratio", 0),
            features.get("has_score", 0),
            features.get("has_bound", 0),
            features.get("has_reg", 0),
            features.get("has_url_pattern", 0),
            features.get("has_email_pattern", 0),
            features.get("has_phone_pattern", 0),
            features.get("has_at_symbol", 0),
            features.get("has_http", 0),
            features.get("has_dots", 0),
            features.get("phone_ratio", 0),
            features.get("has_geo_keywords", 0),
            features.get("has_cat_keywords", 0),
            features.get("is_unnamed", 0),
            features.get("name_length", 0),
        ])

        y.append(label)
        metadata.append({
            "label": label,
            "aggregation": row.aggregation
        })

    return np.array(X), np.array(y), metadata


# -------------------------------
# 2. Train Model
# -------------------------------
def train_model(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        class_weight='balanced',
        n_estimators=100,
        max_depth=10,
        random_state=42
    )

    model.fit(X_train, y_train)

    # -------------------------------
    # 3. Evaluate Model
    # -------------------------------
    y_pred = model.predict(X_test)

    print("\nModel Evaluation:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    return model


# -------------------------------
# 4. Save Model
# -------------------------------
def save_model(model):
    model_path = os.path.join(
        os.path.dirname(__file__),
        "model.pkl"
    )

    joblib.dump(model, model_path)
    print(f"\nModel saved at: {model_path}")


# -------------------------------
# 5. Main Execution
# -------------------------------
if __name__ == "__main__":
    print("Training Semantic Classification Model...")

    X, y, metadata = load_training_data()

    if len(X) == 0:
        print("No training data found.")
        exit()

    model = train_model(X, y)

    save_model(model)

    print("Training complete!")