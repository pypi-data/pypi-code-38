_have_pandas = True
_have_numpy = True
try:
    import pandas
except:
    _have_pandas = False
try:
    import numpy
except:
    _have_numpy = False

def have_numpy() -> bool:
    global _have_numpy
    return _have_numpy

def have_pandas() -> bool:
    global _have_pandas
    return _have_pandas
