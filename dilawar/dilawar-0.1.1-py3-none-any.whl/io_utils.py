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

def h5load(filename, key='mydata'):
    import pandas as pd
    store = pd.HDFStore(filename)
    data = store[key]
    metadata = store.get_storer(key).attrs.metadata
    return data, metadata

def tests():
    import os
    import numpy as np
    import pandas as pd
    import tempfile
    storeName = os.path.join(tempfile.gettempdir(),'data.h5')
    data  = np.random.rand(100, 100)
    df = pd.DataFrame(data)
    h5store(storeName, df, me='dilawar', mynum = 301810)
    s, m = h5load(storeName)
    assert df.equals(s)
    assert m == dict(me ='dilawar', mynum=301810)

def main():
    tests()

if __name__ == '__main__':
    main()
