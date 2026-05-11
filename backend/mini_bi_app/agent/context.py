"""
So context, -> The agent should have a context ie the dataset it is handling in order to inject
it to the available tools when needed.
Hizi zote ni speculation, Sijui vile naplan kuimplement hii shit
"""

from pandas import DataFrame
import pandas as pd



# class RunContext:
#     def __init__(self):
#         pass


# class FileContext(RunContext):
#     def __init__(self, path):
#         super().__init__()

# Sijui nafaa kutengeneza nini

class DataFrameContext:
    def __init__(self, dataset: str | DataFrame):
        """Creates a Dataframe Context for the model

        Args:
            dataset (str | DataFrame): Either path to the dataset or a pandas DataFrame
        """
        self.dataframe = dataset if isinstance(dataset, DataFrame) else self._load_dataset(dataset)


    def _load_dataset(self, dataset: str) -> DataFrame:
        if dataset.endswith(".xlsx"):
            return pd.read_excel(dataset)
        elif dataset.endswith(".csv"):
            return pd.read_csv(dataset)