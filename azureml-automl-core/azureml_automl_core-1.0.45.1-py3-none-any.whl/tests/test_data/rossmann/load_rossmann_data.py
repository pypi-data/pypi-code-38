import os

import pandas as pd

from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame

path_to_self = os.path.realpath(os.path.dirname(__file__))
ROSSMANN_DATA_PATH = path_to_self


def load_rossmann_dataset(data_path=ROSSMANN_DATA_PATH):
    """
    Returns the Rossmann's Store dataset (just the basic time series part) as a tuple, mostly for test purposes.
    """

    # Takes about 1s to load, per timeit. The run time is dominated (97+%) by load from disk,
    # and there is no way to read a csv partially, so skipped the "quick" option.
    train = pd.read_csv(os.path.join(data_path, 'train.csv'), low_memory=False)
    test = pd.read_csv(os.path.join(data_path, 'test.csv'), low_memory=False)

    # Convert the date column to numpy.datetime64 type
    train['Date'] = pd.to_datetime(train['Date'])
    test['Date'] = pd.to_datetime(test['Date'])

    # Convert sales column to float
    train['Sales'] = train['Sales'].astype('float')

    train_ts = TimeSeriesDataFrame(train, grain_colnames='Store',
                                   time_colname='Date', ts_value_colname='Sales')
    test_ts = TimeSeriesDataFrame(test, grain_colnames='Store',
                                  time_colname='Date')

    return train_ts, test_ts


if __name__ == '__main__':
    rossman_train_ts, rossman_test_ts = load_rossmann_dataset()
    print(rossman_train_ts.describe())
