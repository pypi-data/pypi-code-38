import pandas as pd
import numpy as np
from padar_converter.mhealth.dataframe import segment_annotation, get_annotation_labels


def to_mutually_exclusive(data, res='s'):
    '''
    Combine overlapped labels and split them according to time

    :param pandas.DataFrame data: the mhealth annotation to split
    :param str res: the finest resolution to compare between timestamps
    '''
    def make_mutually_exclusive_row(df, start_time, stop_time):
        segmented = segment_annotation(
            df, start_time=start_time, stop_time=stop_time)
        labels = get_annotation_labels(segmented)
        return pd.Series([start_time, start_time, stop_time, ' '.join(labels).lower()],
                         index=['HEADER_TIME_STAMP',
                                'START_TIME',
                                'STOP_TIME',
                                'LABEL_NAME'])

    time_df = pd.concat(
        (data.iloc[:, 1], data.iloc[:, 2]), axis=0)
    time_df.sort_values(ascending=True, inplace=True)
    time_df = time_df.apply(lambda ts: ts.round(res)).drop_duplicates()
    time_df.reset_index(drop=True, inplace=True)
    start_times = time_df.iloc[:-1]
    stop_times = time_df.iloc[1:]
    result = pd.DataFrame({'HEADER_TIME_STAMP': start_times.values,
                           'START_TIME': start_times.values,
                           'STOP_TIME': stop_times.values})
    result = result.apply(lambda row:
                          make_mutually_exclusive_row(
                              data,
                              start_time=row['START_TIME'],
                              stop_time=row['STOP_TIME']),
                          axis=1,
                          result_type='expand')
    return result
