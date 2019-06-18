from uncertainties import ufloat, nominal_value, std_dev
from uncertainties.unumpy import uarray, nominal_values, std_devs
from pandas.testing import assert_frame_equal, assert_series_equal
from numpy.testing import assert_array_equal

# Uncertainties-aware version of pandas.testing functions
def u_assert_frame_equal(df1, df2):
    assert_frame_equal(df1.applymap(nominal_value),  df2.applymap(nominal_value))
    assert_frame_equal(df1.applymap(std_dev),  df2.applymap(std_dev))

def u_assert_series_equal(ser1, ser2):
    assert_series_equal(ser1.map(nominal_value),  ser2.map(nominal_value))
    assert_series_equal(ser1.map(std_dev), ser2.map(std_dev))

def u_assert_array_equal(arr1, arr2):
    assert_array_equal(nominal_values(arr1),  nominal_values(arr2))
    assert_array_equal(std_devs(arr1), std_devs(arr2))

