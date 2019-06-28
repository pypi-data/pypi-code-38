import pandas as pd


def locate_col(df: pd.DataFrame, col_name: str):
    """
    Return index after col_name within the dataframe df
    Args:
        df: DataFrame of interest
        col_name: Name of columns within the DataFrame

    Returns:
        (int): index of the column within the dataframe
    """
    idx = df.columns.get_loc(col_name) + 1
    return idx


def insert_df(input_outer_df: pd.DataFrame, input_inner_df: pd.DataFrame, loc: int):
    """
    Insert `input_inner_df` into `input_outer_df_df` at specified index, `loc`.

    Args:
        input_outer_df (pd.DataFrame): DataFrame which will be inserted by another DataFrame
        input_inner_df (pd.DataFrame): DataFrame to be inserted
        loc (int): location index of insertion

    Returns:
        (pd.DataFrame), `outer_df` with `inner_df` inserted in between according to the specified index
    """
    assert isinstance(input_outer_df, pd.DataFrame)
    assert isinstance(input_inner_df, pd.DataFrame)
    outer_df = input_outer_df.copy()
    inner_df = input_inner_df.copy()
    outer_df = outer_df.reset_index(drop=True)
    inner_df = inner_df.reset_index(drop=True)
    if len(outer_df) != len(inner_df):
        raise ValueError("len is not the same")
    return pd.concat([outer_df.iloc[:, :loc], inner_df, outer_df.iloc[:, loc:]], axis=1, join_axes=[outer_df.index])
