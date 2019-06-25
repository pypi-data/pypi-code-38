# Test case for PytorchCaffe
# common function for test: 
# 1. get environmnet for pytorch and python
# 2.

import sys, os

def get_env():
    from ptcaffe.utils.utils import torch_version_ge
    python_version = sys.version_info
    pytorch_version = '0.4.0' if torch_version_ge('0.4.0') else '0.3.0'
    return python_version, pytorch_version

def assertRaises(expected_exception, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except expected_exception as e:
        pass
    else:
        # Did not raise exception
        assert False, "%s did not raise %s" % (func.__name__, expected_exception.__name__)
