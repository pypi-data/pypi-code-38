# -*- coding: utf-8 -*-
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2019-, Dilawar Singh"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"

# These are helper functions to store metadata to HDF5.
# Snippets originally from https://stackoverflow.com/a/29130146/1805129
def h5store(filename, df, key = 'mydata', **kwargs):
    import pandas as pd
    store = pd.HDFStore(filename)
    store.put(key, df)
    store.get_storer(key).attrs.metadata = kwargs
    store.close()

def h5load(store, key='mydata'):
    data = store[key]
    metadata = store.get_storer(key).attrs.metadata
    return data, metadata
