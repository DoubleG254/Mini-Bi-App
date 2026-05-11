import pandas as pd
from .context import DataFrameContext
from typing import Literal, Any
import os
from pathlib import Path
from django.conf import settings

if not settings.configured:
    import sys
    # Add the Django project root to the path
    django_project_root = Path(__file__).parent.parent.parent.parent  # Goes up to Mini-Bi-App/backend/
    sys.path.insert(0, str(django_project_root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_bi.settings')
    import django
    django.setup()
def drop_row(context: DataFrameContext, index: int):
    """Dropping rows from the dataset

    Args:
        index (int): The index of the row to be dropped
    """
    context.dataframe.drop(index, inplace=True)


def drop_column(context: DataFrameContext, column_name: str | list[str]):
    """Dropping columns from a dataset.
        Confirm That the column exists before using this tool.

    Args:
        column_name (str | list[str]): Either name of column to be dropped or list of columns to be dropped

    Returns:
        str: A string representation of the columns after the column/columns have been dropped
    """
    context.dataframe.drop(column_name, axis=1, inplace=True)
    return str(context.dataframe.columns)


def get_dataset_description(df_context: DataFrameContext):
    """Provide a concise description of the dataset (basic statistics only)

    Returns:
        str: A string representation of basic dataset statistics
    """
    description = df_context.dataframe.describe().head(10).to_string()
    return description


def get_dataset_head(df_context: DataFrameContext, length: int | None = 5) -> str:
    """Get the dataset head. A sample of the data.

     Args:
        length (int): The number of samples to be fetched. Default is  5.

    Returns:
        str: A string respresentation head of the dataset
    """
    if df_context.dataframe is None:
        return "Error: DataFrame is None"
    return df_context.dataframe.head(n=length).to_string()


def fetch_column(df_context: DataFrameContext, column_name: str) -> str:
    """Fetch a specific column (first 20 rows)

    Args:
        column_name (str): The name of the column to be fetched

    Returns:
        str: A string representation of the first 20 rows of the column
    """

    return df_context.dataframe[column_name].head(20).to_string()



def save_dataset(df_context: DataFrameContext, new_dataset_name: str):
    """Saves the dataset to backend/media/cleaned_datasets."""
    
    # 1. Ensure .csv extension
    if not new_dataset_name.lower().endswith('.csv'):
        new_dataset_name += '.csv'
    
    # 2. Calculate Path
    current_file_path = Path(__file__).resolve()
    
    # DEBUG: Print current location to verify
    print(f"[DEBUG] Current File Path: {current_file_path}")
    
    # Go up 3 levels to reach 'backend'
    # Level 1: agent/
    # Level 2: mini_bi_app/
    # Level 3: backend/
    base_dir = current_file_path.parent.parent.parent
    
    target_dir = base_dir / "media" / "cleaned_datasets"
    
    print(f"[DEBUG] Calculated Base Dir: {base_dir}")
    print(f"[DEBUG] Target Dir: {target_dir}")
    
    # 3. Ensure directory exists
    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"[DEBUG] Directory verified: {target_dir}")
    except Exception as e:
        print(f"[ERROR] Failed to create directory: {e}")
        raise e

    # 4. Construct full path
    file_path = target_dir / new_dataset_name
    print(f"[DEBUG] Saving to: {file_path}")
    
    # 5. Save
    try:
        if df_context is None or not hasattr(df_context, 'dataframe'):
            raise ValueError("df_context is missing or invalid.")
            
        df_context.dataframe.to_csv(file_path, index=False)
        print(f"[SUCCESS] File saved to: {file_path}")
        return str(file_path)
    except Exception as e:
        print(f"[ERROR] Failed to save file: {e}")
        raise e
    


def get_all_columns(df_context: DataFrameContext) -> str:
    """Fetches all columns with their datatype

    Returns:
        str: A string representation of all columns with the dtype of each column
    """
    columns_info = df_context.dataframe.dtypes.to_string()
    return f"Columns and Data Types:\n{columns_info}"


def get_null_values(df_context: DataFrameContext) -> str:
    """Fetches the number of null values on the dataset

    Returns:
        str: A string representation of the sum of null values on each column
    """
    return df_context.dataframe.isna().sum().to_string()


def fill_null_values(
    df_context: DataFrameContext,
    column_name: str,
    value: Any | None = None,
    method: Literal["mean", "mode", "median"] = None,
) -> str:
    """Fills null values in columns depending on the value or method provided to it.
        Either a value or a fill in method is provided and used to fill in NaN.

    Args:
        column_name (str): The name of the column whose null Values are to be filled
        value (Any | None, optional): The value to be filled if method not provided. Defaults to None.
        method (Literal[&quot;mean&quot;, &quot;mode&quot;, &quot;median&quot;], optional):The method to be used to fill null values. Defaults to None.

    Returns:
        str: A summary of the operation.
    """
    try:
        if value is None and method is None:
            return "ERROR: The value/ Method was not specified"
        # IF both are provided we prioritize the value
        elif value and method is None or (value and method):
            null_count_before = df_context.dataframe[column_name].isna().sum()
            df_context.dataframe[column_name] = df_context.dataframe[
                column_name
            ].fillna(value)
            null_count_after = df_context.dataframe[column_name].isna().sum()
            return f"Filled {null_count_before} null values with '{value}'. Remaining nulls: {null_count_after}"

        elif method and value is None:
            null_count_before = df_context.dataframe[column_name].isna().sum()
            methods = {
                "mean": df_context.dataframe[column_name].mean(),
                "median": df_context.dataframe[column_name].median(),
                "mode": df_context.dataframe[column_name].mode()[0],
            }
            df_context.dataframe[column_name] = df_context.dataframe[
                column_name
            ].fillna(methods[method])
            null_count_after = df_context.dataframe[column_name].isna().sum()
            return f"Filled {null_count_before} null values using {method}. Remaining nulls: {null_count_after}"
    except Exception as e:
        return f"Error: {e}"


# TODO: Value Counts, dtype change, Correlations
def replace_values(df_context: DataFrameContext, column_name: str, values: dict) -> str:
    """Replacing Existing values with new values . eg 'male' with 0 .

    Args:
        column_name (str): The name of the column where the replacement is supposed to be done
        values (dict): A key-value pair old: new of what is to be replaced with what.

    Returns:
        str: A summary of the replacement operation.
    """
    df_context.dataframe[column_name] = df_context.dataframe[column_name].replace(
        values
    )
    return f"Replaced values in '{column_name}'. Top 5 new values:\n" + df_context.dataframe[column_name].value_counts().head(5).to_string()


def value_count(df_context: DataFrameContext, column_name: str) -> str:
    """Perform a value count for a given column (top 10 values)

    Args:
        column_name (str): The column to calculate value count

    Returns:
        str: A string representation of the top 10 value counts
    """
    return df_context.dataframe[column_name].value_counts().head(10).to_string()


def change_column_dtype(
    df_context: DataFrameContext,
    column_name: str,
    new_datatype: Literal["int", "float", "str"],
) -> str:
    """Change the column data type

    Args:
        column_name (str): The name of the column
        new_datatype (Literal[&quot;int&quot;, &quot;float&quot;, &quot;str&quot;]): The datatype it is being changed to.

    Returns:
        str: The dtype of the column after change
    """
    df_context.dataframe[column_name] = df_context.dataframe[column_name].astype(new_datatype)
    return str(df_context.dataframe[column_name].dtype)
