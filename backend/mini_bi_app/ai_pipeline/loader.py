import pandas as pd
import os

def load_dataset(file_path):
    """
    Load a file and return its content as a DataFrame.
    
    Parameters:
    file_path (str): The path to the file to be loaded.
    
    Returns:
    pd.DataFrame: The content of the file as a DataFrame.
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path, low_memory=False, dtype=str)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only .csv, .xlsx, and .xls are supported.")
    except Exception as e:
        print(f"Error loading file: {e}")
        print(f"Attempted path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        return None