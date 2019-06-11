import pandas as pd
from typing import List

def most_related_columns(df: pd.DataFrame, target: str, number: int) -> List[str]:
    return list(df.corr()[target].abs().sort_values(ascending=False)[:number].index.values)

def all_cols_except(df: pd.DataFrame, targets: List[str]) -> List[str]:
    return list(set(df.columns.values) - set(targets))

def merged(traindf: pd.DataFrame, testdf: pd.DataFrame, targets: List[str]) -> pd.DataFrame:
        all_data = pd.concat((traindf, testdf), sort=False).reset_index(drop=True)
        all_data.drop(targets, axis=1, inplace=True)

        return all_data