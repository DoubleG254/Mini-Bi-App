"""
So context, -> The agent should have a context ie the dataset it is handling in order to inject
it to the available tools when needed.
Hizi zote ni speculation, Sijui vile naplan kuimplement hii shit
"""

from pandas import DataFrame
import pandas as pd
from django.conf import settings

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
        self.dataframe = (
            dataset if isinstance(dataset, DataFrame) else self._load_dataset(dataset)
        )

    def _load_dataset(self, dataset: str) -> DataFrame:
        self.dataset_name = dataset.split("/")[-1].split(".")[0]
        if dataset.endswith(".xlsx"):
            return pd.read_excel(dataset)
        elif dataset.endswith(".csv"):
            return pd.read_csv(dataset)

    def update_to_clean_dataset(self):
        clean_path = (
            f"{settings.BASE_DIR}/media/cleaned_datasets/{self.dataset_name}.csv"
        )
        self.dataframe.to_csv(
            clean_path,
            index=False,
        )
        self.dataframe = pd.read_csv(clean_path)
