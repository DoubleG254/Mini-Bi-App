import pandas as pd

def load_dataset(file_path):
    """
    Load a file and return its content as a DataFrame.
    
    Parameters:
    file_path (str): The path to the file to be loaded.
    
    Returns:
    pd.DataFrame: The content of the file as a DataFrame.
    """
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only .csv, .xlsx, and .xls are supported.")
    except Exception as e:
        print(f"Error loading file: {e}")
        return None