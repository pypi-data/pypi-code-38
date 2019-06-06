import pprint
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import statsmodels
import collections
import re


def test_value(value):

    ref_assert_var = False

    try:
        SRE_MATCH_TYPE = type(re.match("", ""))
        value_type = type(value)
        user_ns = tuple(get_ipython().user_ns.items())

        if value_type == int:
            for name, value2 in user_ns:
                if type(value2) == int and value == value2:
                    return True

        elif value_type == float:
            for name, value2 in user_ns:
                if type(value2) == float and value == value2:
                    return True

        elif value_type == str:
            for name, value2 in user_ns:
                if type(value2) == str and value == value2:
                    return True

        elif value_type == list:
            for name, value2 in user_ns:
                if type(value2) == list and value == value2:
                    return True

        elif value_type == np.float64:
            for name, value2 in user_ns:
                if type(value2) == np.float64 and value == value2:
                    return True

        elif value_type == pd.DataFrame:
            from pandas.util.testing import assert_frame_equal
            for name, value2 in user_ns:
                if type(value2) == value_type:
                    try:
                        assert_frame_equal(value, value2)
                    except:
                        continue
                    return True

        elif value_type == collections.deque:
            for name, value2 in user_ns:
                if type(value2) == value_type:
                    if(value == value2):
                        return True

        elif value_type is SRE_MATCH_TYPE:
            for name, value2 in user_ns:
                if type(value2) == value_type and value.group(0) == value2.group(0):
                    return True

        elif value_type == dict:
            for name, value2 in user_ns:
                if value_type == type(value2) and value == value2:
                    return True

        elif value_type == tuple:
            for name, value2 in user_ns:
                if type(value2) == tuple and value == value2:
                    return True

        elif value_type == np.int64:
            for name, value2 in user_ns:
                if type(value2) == np.int64 and value == value2:
                    return True

        elif value_type == np.ndarray:
            for name, value2 in user_ns:
                if type(value2) == np.ndarray and np.array_equal(value,value2):
                    return True


        if not ref_assert_var:
            print('Please follow the instructions given and use the same variables provided in the instructions.')
        return ref_assert_var

    except Exception:
        print('Please follow the instructions given and use the same variables provided in the instructions.')
        return False


def test_variable(variable,value):

    try:
        ret_var = False
        value_type = type(value)
        user_ns = tuple(get_ipython().user_ns.items())

        #if value_type == int:
        for name, value2 in user_ns:
            if variable == name and value == value2:
                return True

        if not ret_var:
            print('ERR1:Please follow the instructions given and use the same variables provided in the instructions.')
        return ret_var

    except Exception:
        print(Exception)
        print('ERR2:Please follow the instructions given and use the same variables provided in the instructions.')
        return False


def test_plot(value):

    try:
        value_type = type(value)
        user_ns = tuple(get_ipython().user_ns.items())


        ref_assert_var = False
        if value_type == sns.axisgrid.JointGrid:
            for name, value2 in user_ns:
                if type(value2) == value_type:
                    if (np.array_equal(value.y,value2.y) and np.array_equal(value.x,value2.x)):
                        ref_assert_var = True
                        return True

                    continue

        elif issubclass(value_type, matplotlib.axes.SubplotBase):
            for name, value2 in user_ns:
                if type(value2) == value_type:
                    if (value.get_xlabel() == value2.get_xlabel() and value.get_ylabel() == value2.get_ylabel()):
                        ref_assert_var = True
                        return True
                    continue

        if not ref_assert_var:
            print('Please follow the instructions given and use the same variables provided in the instructions.')
        return ref_assert_var

    except Exception:
        print('Please follow the instructions given and use the same variables provided in the instructions.')
        return False


def test_model(value):

    try:

        value_type = type(value)
        user_ns = tuple(get_ipython().user_ns.items())
        ref_assert_var = False
        if value_type == statsmodels.regression.linear_model.RegressionResultsWrapper:
            for name, value2 in user_ns:
                if type(value2) == value_type:
                    if (value.model.formula == value2.model.formula):
                        ref_assert_var = True
                        return True
                    continue

        if not ref_assert_var:
            print('Please follow the instructions given and use the same variables provided in the instructions.')
        return ref_assert_var

    except Exception:
        print('Please follow the instructions given and use the same variables provided in the instructions.')
        return False


def test_output(output):
    assert False, 'Wrong answer!'
