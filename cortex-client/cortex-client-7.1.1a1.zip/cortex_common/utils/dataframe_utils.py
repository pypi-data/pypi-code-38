"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from typing import List, TypeVar, Tuple, Type

import arrow
import attr
import pandas as pd

from .object_utils import tuples_with_nans_to_tuples_with_nones, head
from .time_utils import seconds_between_times
from .type_utils import pass_through_converter

T = TypeVar("T")

__all__ = [
    'list_of_attrs_to_df',
    'df_to_typed_list',
    'append_seconds_to_df',
    'split_df_into_files_based_on_date',
    'explode_column',
    'head_as_dict',
    'filter_time_column_after',
    'filter_time_column_before',
    'df_to_tuples',
    'parse_set_notation',
    'parse_string_set_notation',
    'parse_set_of_json_strings_notation',
    'df_to_records',
    'merge_list_of_dfs_similarly',
]


def list_of_attrs_to_df(l:List) -> pd.DataFrame:
    """
    Turns a list of attr based classes into a dataframe

    :param l:
    :return:
    """
    return pd.DataFrame([
        attr.asdict(x) for x in l
    ])


def append_seconds_to_df(df:pd.DataFrame, column_name_to_append:str, start_time_col:str, end_time_col:str) -> pd.DataFrame:
    """
    Appends an additional column that representes the duration between two other time oriented columns within the df.

    :param df:
    :param column_name_to_append:
    :param start_time_col:
    :param end_time_col:
    :return:
    """
    return df.assign(**{
        column_name_to_append: list(map(
            lambda x: seconds_between_times(arrow.get(x[0]), arrow.get(x[1])),
            df[[start_time_col, end_time_col]].itertuples(index=False, name=None)
        ))
    })


def split_df_into_files_based_on_date(df: pd.DataFrame, on_date: str, file_pattern: str) -> None:
    """
    Saves a dataframe into multiple files ... based on a date column.
    Records that occure on the same day with regards to the date column are saved into the same file .

    :param df: Dataframe to split
    :param on_date: Date column to split on
    :param file_pattern: The pattern to save the new files created, where {date} will be replaced with the actual date ...
    :return: Nothing, this function creates new files ...
    """
    for date, df_on_date in df.groupby(on_date):
        df_on_date.reset_index().to_csv(file_pattern.format(date=str(arrow.get(date).date())))


def explode_column(unindexed_df:pd.DataFrame, column:str) -> pd.DataFrame:
    """
    Expands a column where the value of each cell within a column is a list ...
    >>> len(explode_column(pd.DataFrame([{"name":"bob", "knows": ["jane", "jack"]}]))["knows"].unique())
    2
    Assumption:
        - df has no index ...
    :param df:
    :param column:
    :return:
    """
    if unindexed_df.empty:
        return unindexed_df
    id_columns = list(set(unindexed_df.columns).difference(set([column])))
    df = (unindexed_df.set_index(id_columns))[column].apply(pd.Series).stack().to_frame(column)
    for column in id_columns:
        df = df.reset_index(level=column)
    return df.reset_index(drop=True)

#  ------------------

def filter_time_column_after(df:pd.DataFrame, time_column:str, shifter:dict) -> pd.DataFrame:
    """
    Filters a dataframes rows based on the date in a specific column ...

    :param df: The Dataframe to filter
    :param time_column: The name of the time column to filter
    :param shifter: Arrow friendly dict to shift an arrow time ...
    :return:
    """
    return df[df[time_column].map(arrow.get) >= arrow.utcnow().shift(**shifter)].reset_index(drop=True)


def filter_time_column_before(df:pd.DataFrame, time_column:str, shifter:dict) -> pd.DataFrame:
    """
    Filters a dataframes rows based on the date in a specific column ...

    :param df: The Dataframe to filter
    :param time_column: The name of the time column to filter
    :param shifter: Arrow friendly dict to shift an arrow time ...
    :return:
    """
    return df[df[time_column].map(arrow.get) <= arrow.utcnow().shift(**shifter)].reset_index(drop=True)


#  ------------------


def parse_set_notation(string_series:pd.Series) -> pd.Series:
    """
    Turns a series into strings into a series of sets ...

    :param string_series:
    :return:
    """
    if string_series.empty:
        return pd.Series([])
    return string_series.map(parse_string_set_notation)


def parse_string_set_notation(string:str) -> pd.Series:
    """
    Splits comman seperated string into a pandas series ...

    :param string:
    :return:
    """
    return set(string[1:-1].split(","))


def parse_set_of_json_strings_notation(string_series: pd.Series) -> pd.Series:
    """
    Turns a series of strings into a series of json objects ...
    :param string_series:
    :return:
    """
    if string_series.empty:
        return []
    return string_series.map(
        pass_through_converter(
            (str,),
            lambda string: list(map(
                lambda x: json.loads(x),
                json.loads("[{}]".format(string[1:-1]))
            ))
        )
    )

#  ---------- DF Conversions ----------

def head_as_dict(df:pd.DataFrame) -> dict:
    """
    Returns the head of the dataframe into a dict ...
    :param df:
    :return:
    """
    if df.empty:
        return {}
    dict_as_head = head(df_to_records(df[0]))
    return dict_as_head if dict_as_head is not None else {}



def df_to_records(df:pd.DataFrame) -> List[dict]:
    """
    Turns a Dataframe into a list of dicts ...
    :param df:
    :return:
    """
    # return df.to_dict(orient="records")
    return df.to_dict('records')


def df_to_tuples(df:pd.DataFrame, columns:List[str]) -> List[Tuple]:
    """
    Turns a dataframe into a list of tuples ...
    :param df:
    :param columns: Names of columns to keep as tuples in order ...
    :return:
    """
    return tuples_with_nans_to_tuples_with_nones(df[columns].itertuples(index=False, name=None))


def df_to_typed_list(df:pd.DataFrame, t:Type[T]) -> List[T]:
    """
    Turns a dataframe into a list of a specific type ...
    :param df:
    :param t:
    :return:
    """
    return list(map(
        lambda rec: t(**rec),  # type: ignore # not a good way to do this with attr ...
        df_to_records(df)
    ))


#  ---------- DF Concatenation ----------

def merge_list_of_dfs_similarly(group_list:List[pd.DataFrame], **kwargs) -> pd.DataFrame:
    """
    Merged a list of Dataframes ... into a single Dataframe ... on the same criteria ...
    :param group_list:
    :param kwargs:
    :return:
    """
    if len(group_list) == 0:
        return pd.DataFrame(columns=[kwargs.get("on", kwargs.get("left_on"))])
    if len(group_list) == 1:
        return group_list[0]
    if len(group_list) == 2:
        return pd.merge(group_list[0], group_list[1], **kwargs)
    if len(group_list) >= 3:
        return merge_list_of_dfs_similarly(
            [merge_list_of_dfs_similarly(group_list[:2], **kwargs)] + group_list[2:]
        )
