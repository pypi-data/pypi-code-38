"""
@author: magician
@file: pd_json.py
@date: 2019/06/05
"""
import pandas as pd


def read_json(file, **kwargs):
    """
    read json
    :param file:    json
    :param kwargs:
    :return: DataFrame
    """
    json_df = pd.read_json(file, **kwargs)

    return json_df


def write_json(df, **kwargs):
    """
    write json
    :param df:
    :param kwargs: orient
    :return: json
    """
    # orient: index, split, records, columns, values
    orient = kwargs.get('orient', 'index')
    json_df = df.to_json(orient=orient, force_ascii=False, **kwargs)

    return json_df
