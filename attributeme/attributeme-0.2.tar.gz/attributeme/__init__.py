import numpy as np

def get_time_line(df, col1, col2):
    df[col2] = df[col2].astype('datetime64[ns]')
    df['timedelta_hours'] = df.groupby(col1)[col2].apply(lambda x: x.shift(-1) - x)/np.timedelta64(1, 'h')
    df['timedelta_sec'] = df.groupby(col1)[col2].apply(lambda x: x.shift(-1) - x)/np.timedelta64(1, 's')
    df['timedelta_days'] = df.groupby(col1)[col2].apply(lambda x: x.shift(-1) - x)/np.timedelta64(1, 'D')
    return df