import pandas as pd
from .context import DataFrameContext
from typing import Literal, Any


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
    """Provide the description of the dataset


    Returns:
        str: A string representation of the dataset
    """
    description = df_context.dataframe.describe().to_string()
    return description


def get_dataset_head(df_context: DataFrameContext, length: int | None = 5) -> str:
    """Get the dataset head. A sample of the data.

     Args:
        length (int): The number of samples to be fetched. Default is  5.

    Returns:
        str: A string respresentation head of the dataset
    """
    return df_context.dataframe.head(n=length).to_string()


def fetch_column(df_context: DataFrameContext, column_name: str) -> str:
    """Fetch a specific column

    Args:
        column_name (str): The name of the column to be fetched

    Returns:
        str: A string representation of the column
    """

    return df_context.dataframe[column_name].to_string()


def save_dataset(df_context: DataFrameContext, new_dataset_name: str):
    """Saves the dataset in the provided name

    Args:
        new_dataset_name (str): name to file to be saved to
    """
    df_context.dataframe.to_csv(new_dataset_name)


def get_all_columns(df_context: DataFrameContext) -> str:
    """Fetches all columns with their datatype

    Returns:
        str: A string representation of all columns with the dtype of each column
    """
    return df_context.dataframe.to_string()


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
        str: An error or a string representation of the column.
    """
    try:
        if value is None and method is None:
            return "ERROR: The value/ Method was not specified"
        # IF both are provided we prioritize the value
        elif value and method is None or (value and method):
            df_context.dataframe[column_name] = df_context.dataframe[
                column_name
            ].fillna(value)
            return str(df_context.dataframe[column_name])

        elif method and value is None:
            methods = {
                "mean": df_context.dataframe[column_name].mean(),
                "median": df_context.dataframe[column_name].median(),
                "mode": df_context.dataframe[column_name].mode()[0],
            }
            df_context.dataframe[column_name] = df_context.dataframe[
                column_name
            ].fillna(methods[method])
            return str(df_context.dataframe[column_name])
    except Exception as e:
        return f"Error: {e}"


# TODO: Value Counts, dtype change, Correlations
def replace_values(df_context: DataFrameContext, column_name: str, values: dict) -> str:
    """Replacing Existing values with new values . eg 'male' with 0 .

    Args:
        column_name (str): The name of the column where the replacement is supposed to be done
        values (dict): A key-value pair old: new of what is to be replaced with what.

    Returns:
        str: A value count to show the new values.
    """
    df_context.dataframe[column_name] = df_context.dataframe[column_name].replace(
        values
    )
    return df_context.dataframe[column_name].value_counts().to_string()


def value_count(df_context: DataFrameContext, column_name: str) -> str:
    """Perform a value count for a given column

    Args:
        column_name (str): The column to calculate  value count

    Returns:
        str: A string representation of the value count
    """
    return df_context.dataframe[column_name].value_counts().to_string()


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
