import calendar
import datetime as dt
from typing import Any

import numpy as np
import pandas as pd

from bamboos.utils.dates import (
    DAYS_IN_MONTH,
    DAYS_IN_YEAR,
    MONTH_IN_YEAR,
    SECOND_IN_MINUTE,
    SECOND_IN_HOUR,
    MINUTE_IN_HOUR,
    HOUR_IN_DAY,
    BUSINESS_OPEN,
    BUSINESS_CLOSE,
    MIDNIGHT_START,
    MORNING_START,
    AFTERNOON_START,
    NIGHT_START,
    NIGHT_END,
    SATURDAY,
    SUNDAY,
)


def _get_max_day(row: pd.Series, col_name: str):
    """
    for each row in the pandas DataFrame, give the number of days in that month, given the year and month
    """
    if (pd.isnull(row[col_name + "_year"])) or (pd.isnull(row[col_name + "_year"])):
        return np.nan
    return calendar.monthrange(int(row[col_name + "_year"]), int(row[col_name + "_month"]))[1]


def _get_cyclical_sin(df: pd.Series, col_name: str, col_type: str, col_max: Any):
    """
    Perform cyclical encoding for the following col_type (month, days, hours, etc) by computing the cosine and sine
    """
    return np.sin(2. * np.pi * df["{}_{}".format(col_name, col_type)] / col_max)


def _get_cyclical_cos(df: pd.Series, col_name: str, col_type: str, col_max: Any):
    """
    Perform cyclical encoding for the following col_type (month, days, hours, etc) by computing the cosine and sine
    """
    return np.cos(2. * np.pi * df["{}_{}".format(col_name, col_type)] / col_max)


def date_single(input_df: pd.DataFrame, col_name: str, cur_time: dt.datetime = dt.datetime.now()):
    """
    Perform Feature Engineering on a single datetime column.
    """
    df = input_df[[col_name]].copy()
    df[col_name] = pd.to_datetime(df[col_name])
    df[col_name + "_age"] = cur_time.year - df[col_name].dt.year
    df[col_name + "_year"] = df[col_name].dt.year
    df[col_name + "_month"] = df[col_name].dt.month
    df[col_name + "_day"] = df[col_name].dt.day
    df[col_name + "_hour"] = df[col_name].dt.hour
    df[col_name + "_minute"] = df[col_name].dt.minute
    df[col_name + "_second"] = df[col_name].dt.second
    df[col_name + "_day_of_week"] = df[col_name].dt.dayofweek
    df[col_name + "_day_of_year"] = df[col_name].dt.dayofyear
    df[col_name + "_week_of_year"] = df[col_name].dt.weekofyear
    df[col_name + "_is_weekend"] = (df[col_name + "_day_of_week"] == SATURDAY) | (
        df[col_name + "_day_of_week"] == SUNDAY
    )
    df[col_name + "_year_elapsed"] = (cur_time - df[col_name]).dt.days / DAYS_IN_YEAR
    df[col_name + "_month_elapsed"] = (cur_time - df[col_name]).dt.days / DAYS_IN_MONTH
    df[col_name + "_day_elapsed"] = (cur_time - df[col_name]).dt.days
    df[col_name + "_month_sin"] = _get_cyclical_sin(df, col_name, "month", MONTH_IN_YEAR)
    df[col_name + "_month_cos"] = _get_cyclical_cos(df, col_name, "month", MONTH_IN_YEAR)
    df[col_name + "_day_sin"] = _get_cyclical_sin(df, col_name, "day", df[col_name + "_max_day"])
    df[col_name + "_day_cos"] = _get_cyclical_cos(df, col_name, "day", df[col_name + "_max_day"])
    df[col_name + "_hour_sin"] = _get_cyclical_sin(df, col_name, "hour", HOUR_IN_DAY)
    df[col_name + "_hour_cos"] = _get_cyclical_cos(df, col_name, "hour", HOUR_IN_DAY)
    df[col_name + "_minute_sin"] = _get_cyclical_sin(df, col_name, "minute", MINUTE_IN_HOUR)
    df[col_name + "_minute_cos"] = _get_cyclical_cos(df, col_name, "minute", MINUTE_IN_HOUR)
    df[col_name + "_second_sin"] = _get_cyclical_sin(df, col_name, "second", SECOND_IN_MINUTE)
    df[col_name + "_second_cos"] = _get_cyclical_cos(df, col_name, "second", SECOND_IN_MINUTE)
    df[col_name + "_is_year_start"] = df[col_name].dt.is_year_start
    df[col_name + "_is_year_end"] = df[col_name].dt.is_year_end
    df[col_name + "_is_quarter_start"] = df[col_name].dt.is_quarter_start
    df[col_name + "_is_quarter_end"] = df[col_name].dt.is_quarter_end
    df[col_name + "_is_month_start"] = df[col_name].dt.is_month_start
    df[col_name + "_is_month_end"] = df[col_name].dt.is_month_end
    df[col_name + "_is_business_hour"] = (df[col_name + "_hour"] > BUSINESS_OPEN) & (
        df[col_name + "_hour"] < BUSINESS_CLOSE
    )
    df[col_name + "_period"] = pd.cut(
        df[col_name + "_hour"],
        bins=[MIDNIGHT_START, MORNING_START, AFTERNOON_START, NIGHT_START, NIGHT_END],
        labels=["dawn", "morning", "afternoon", "night"],
    )
    return df.remove(columns=col_name)


def date_double(input_df: pd.DataFrame, begin_col: str, end_col: str):
    """
    Perform Feature Engineering on DataFrame with two connected Datetime columns. One specifying the start date
    of an event, and the other one specifying the end date of the event.
    """
    df = input_df[[begin_col, end_col]].copy()
    df[begin_col] = pd.to_datetime(df[begin_col])
    df[end_col] = pd.to_datetime(df[end_col])
    df["{}_{}_year".format(begin_col, end_col)] = (df[end_col] - df[begin_col]).dt.days / DAYS_IN_YEAR
    df["{}_{}_month".format(begin_col, end_col)] = (df[end_col] - df[begin_col]).dt.days / DAYS_IN_MONTH
    df["{}_{}_days".format(begin_col, end_col)] = (df[end_col] - df[begin_col]).dt.days
    df["{}_{}_hour".format(begin_col, end_col)] = (df[end_col] - df[begin_col]).dt.seconds / SECOND_IN_HOUR
    df["{}_{}_minute".format(begin_col, end_col)] = (df[end_col] - df[begin_col]).dt.seconds / SECOND_IN_MINUTE
    df["{}_{}_second".format(begin_col, end_col)] = (df[end_col] - df[begin_col]).dt.seconds
    return df.drop(columns=[begin_col, end_col])
