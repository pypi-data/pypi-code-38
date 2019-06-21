import pandas as pd

def index_time(price_frame):
    if not isinstance(price_frame, pd.DataFrame):
        raise TypeError("Should be a dataframe")
    time_series = pd.to_datetime(price_frame['time'], unit='s')
    price_frame.drop('time', axis=1)
    price_frame.set_index(time_series, inplace=True)
    return price_frame