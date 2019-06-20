import pandas as pd
import numpy as np


def append_times(df, st, et):
    df.insert(0, 'START_TIME', st)
    df.insert(1, 'STOP_TIME', et)
    df = df.set_index(['START_TIME', 'STOP_TIME'])
    return df


def offset(df, offset_in_secs, start_time_col=0, stop_time_col=None):
    df_copy = df.copy(deep=True)
    if start_time_col is not None:
        start_time_col = df_copy.columns[start_time_col]
        df_copy[start_time_col] = df_copy[start_time_col] + \
            pd.Timedelta(offset_in_secs, unit='s')
    if stop_time_col is not None:
        stop_time_col = df_copy.columns[stop_time_col]
        df_copy[stop_time_col] = df_copy[stop_time_col] + \
            pd.Timedelta(offset_in_secs, unit='s')
    return df_copy


def segment(df, start_time=None, stop_time=None, start_time_col=0,
            stop_time_col=None):
    if stop_time_col is None:
        stop_time_col = start_time_col
    if start_time is None:
        start_time = df.iloc[0, start_time_col]
    if stop_time is None:
        stop_time = df.iloc[-1, stop_time_col]

    if start_time_col == stop_time_col:
        mask = (df.iloc[:, start_time_col] >= start_time) & (
            df.iloc[:, stop_time_col] < stop_time)
        return df[mask].copy(deep=True)
    else:
        mask = (df.iloc[:, start_time_col] <= stop_time) & (
            df.iloc[:, stop_time_col] >= start_time)
        subset_df = df[mask].copy(deep=True)

        start_time_col = df.columns[start_time_col]
        stop_time_col = df.columns[stop_time_col]

        subset_df.loc[subset_df.loc[:, start_time_col] <
                      start_time, start_time_col] = start_time
        subset_df.loc[subset_df.loc[:, stop_time_col] >
                      stop_time, stop_time_col] = stop_time
        return subset_df


def segment_sensor(df, start_time=None, stop_time=None):
    return segment(df, start_time=start_time, stop_time=stop_time)


def segment_annotation(df, start_time=None, stop_time=None):
    return segment(df, start_time=start_time, stop_time=stop_time,
                   start_time_col=1, stop_time_col=2)


def start_time(df, start_time_col=0):
    return df.iloc[0, start_time_col]


def end_time(df, stop_time_col=0):
    return df.iloc[-1, stop_time_col]


def get_annotation_labels(df):
    labels = df.iloc[:, 3].unique()
    return np.sort(labels)


def append_edges(df, before_df=None, after_df=None, duration=120,
                 start_time_col=0, stop_time_col=0):
    lbound_time = df.iloc[0, start_time_col]
    rbound_time = df.iloc[-1, stop_time_col]

    if before_df is not None:
        ledge_df = segment(before_df,
                           start_time=lbound_time -
                           pd.Timedelta(duration, unit='s'),
                           stop_time=lbound_time,
                           start_time_col=start_time_col,
                           stop_time_col=stop_time_col)
    else:
        ledge_df = pd.DataFrame()

    if after_df is not None:
        redge_df = segment(after_df,
                           start_time=rbound_time,
                           stop_time=rbound_time +
                           pd.Timedelta(duration, unit='s'),
                           start_time_col=start_time_col,
                           stop_time_col=stop_time_col)
    else:
        redge_df = pd.DataFrame()

    return pd.concat((ledge_df, df, redge_df))
