_have_pandas = True
_have_numpy = True
_have_pyarrow = True
try:
    import pandas
except:
    _have_pandas = False
try:
    import numpy
except:
    _have_numpy = False
try:
    import pyarrow
except:
    _have_pyarrow = False

def have_numpy() -> bool:
    global _have_numpy
    return _have_numpy

def have_pandas() -> bool:
    global _have_pandas
    return _have_pandas

def have_pyarrow() -> bool:
    global _have_pyarrow
    return _have_pyarrow