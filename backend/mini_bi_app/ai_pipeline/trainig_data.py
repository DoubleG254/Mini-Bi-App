import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import json
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_bi.settings')
django.setup()

from mini_bi_app.models import ColumnTrainingData

ColumnTrainingData.objects.all().delete()  # Clear existing data to avoid duplicates

def get_training_data():
    training_data = ColumnTrainingData.objects.all()
    return training_data
def add_training_data(column_name, features, semantic_label, aggregation=None): 
    training_entry = ColumnTrainingData(
        column_name=column_name,
        features=features,
        semantic_label=semantic_label,
        aggregation=aggregation
    )
    training_entry.save()

# Get the directory of this script and construct the path to the JSON file
script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, 'financial_training_data_complete.json')

with open(json_file_path, 'r') as f:  
    Training_data = json.load(f)
for entry in Training_data:
    add_training_data(
        column_name=entry['column_name'],
        features=entry['features'],
        semantic_label=entry['semantic_label'],
        aggregation=entry['aggregation']
    )

print("Training data added successfully!")
print(f"Total training entries: {len(Training_data)}")