import numpy as np
import pandas as pd

from datasci.pandas import drop_uninformative_columns


def test_drop_uninformative_columns(n: int = 10):
    df = pd.DataFrame.from_dict({
        'repeated_string': np.repeat('abc', n),
        'repeated_float':  np.repeat(1.23, n),
        'repeated_int':    np.repeat(123, n),
        'repeated_nan':    np.repeat(np.nan, n),
        'random_float':    np.random.uniform(size=n),
        'int_range':       np.arange(n),
        'all_but_one':     np.concatenate([np.repeat(100, n - 1), [99]]),
        'all_but_one_2':   np.concatenate([[-1], np.repeat(0, n - 1)]),
    })
    for column in drop_uninformative_columns(df).columns:
        assert not column.startswith('repeated_'), f'Column {column} should have been dropped'
