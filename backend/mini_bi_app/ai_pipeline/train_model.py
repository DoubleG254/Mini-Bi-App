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
# 1. Define Feature Keys
# -------------------------------
# These must match the keys generated in extract_single_column_features
FEATURE_KEYS = [
    # Statistical
    "null_ratio",
    "cardinality",
    "cardinality_ratio",
    "min_val",
    "max_val",
    "mean_val",
    "std_val",
    "neg_ratio",
    "is_integer",
    "decimal_places_mean",
    
    # Type Indicators
    "is_numeric",
    "is_object",
    
    # Pattern Matches (Regex)
    "match_date",
    "match_timestamp",
    "match_currency",
    "match_percentage",
    "match_uuid",
    "match_time_period",
    "match_boolean",
    
    # String Stats
    "string_len_mean",
    "string_len_std",
    
    # Header Keywords
    "has_id_keyword",
    "has_date_keyword",
    "has_money_keyword",
    "has_change_keyword",
    "has_ratio_keyword",
    "has_geo_keyword",
    "has_score_keyword"
]

# -------------------------------
# 2. Load Data from Database
# -------------------------------
def load_training_data():
    data = ColumnTrainingData.objects.all()

    X = []
    y = []
    metadata = []

    if not data.exists():
        print("No training data found in the database.")
        return np.array([]), np.array([]), []

    for row in data:
        features = row.features  # This is the dict from generate_data.py
        label = row.semantic_label

        # Extract values for the defined feature keys, defaulting to 0 if missing
        row_features = []
        for key in FEATURE_KEYS:
            val = features.get(key)
            if val is None:
                row_features.append(0.0)
            else:
                # Ensure numeric types (cast bools to 0/1 if necessary, though sklearn handles bools)
                try:
                    row_features.append(float(val))
                except (ValueError, TypeError):
                    row_features.append(0.0)

        X.append(row_features)
        y.append(label)
        
        # Optional: Store metadata if needed for debugging
        metadata.append({
            "label": label,
            "column_name": features.get("column_name", "unknown")
        })

    return np.array(X), np.array(y), metadata


# -------------------------------
# 3. Train Model
# -------------------------------
def train_model(X, y):
    if len(X) == 0:
        print("No data to train on.")
        return None

    # Stratify only if we have enough samples per class
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        # Fallback if some classes have fewer than 2 samples
        print("Warning: Not enough samples per class for stratification. Using random split.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    model = RandomForestClassifier(
        class_weight='balanced',
        n_estimators=200,  # Increased estimators for better performance
        max_depth=15,      # Increased depth to capture complex patterns
        min_samples_split=5,
        random_state=42,
        n_jobs=-1          # Use all CPU cores
    )

    print("Training Random Forest with {} features...".format(len(FEATURE_KEYS)))
    model.fit(X_train, y_train)

    # -------------------------------
    # 4. Evaluate Model
    # -------------------------------
    y_pred = model.predict(X_test)

    print("\n--- Model Evaluation ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature Importance (Optional: Print top 5 features)
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    print("\nTop 5 Most Important Features:")
    for i in range(5):
        print(f"{i+1}. {FEATURE_KEYS[indices[i]]}: {importances[indices[i]]:.4f}")

    return model


# -------------------------------
# 5. Save Model
# -------------------------------
def save_model(model):
    if model is None:
        return

    model_path = os.path.join(
        os.path.dirname(__file__),
        "semantic_classifier.pkl"
    )

    joblib.dump(model, model_path)
    print(f"\nModel saved at: {model_path}")


# -------------------------------
# 6. Main Execution
# -------------------------------
if __name__ == "__main__":
    print("Starting Semantic Column Classification Training...")
    print(f"Database: {ColumnTrainingData.objects.count()} records found.")

    X, y, metadata = load_training_data()

    if len(X) == 0:
        print("No training data found. Please run generate_data.py first.")
        exit()

    model = train_model(X, y)

    if model:
        save_model(model)
        print("Training complete!")
    else:
        print("Training failed.")