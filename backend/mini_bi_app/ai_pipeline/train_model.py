import os
import django
import numpy as np
import joblib

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

    for row in data:
        features = row.features
        label = row.semantic_label

        X.append([
            features.get("mean", 0),
            features.get("max", 0),
            features.get("min", 0),
            features.get("unique_ratio", 0),
            features.get("is_numeric", 0),
            features.get("is_integer", 0),
            features.get("name_length", 0),
        ])

        y.append({
            "label": label,
            "aggregation": row.aggregation
        })

    return np.array(X), np.array(y)


# -------------------------------
# 2. Train Model
# -------------------------------
def train_model(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
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

    X, y = load_training_data()

    if len(X) == 0:
        print("No training data found.")
        exit()

    model = train_model(X, y)

    save_model(model)

    print("Training complete!")