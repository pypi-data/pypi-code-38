import pandas
import numpy
import re
from scipy import stats
import math
import warnings

from collections import Counter


def take_last(s: pandas.Series):
    return s.iloc[-1]


def take_first(s: pandas.Series):
    return s.iloc[0]


def count_unique(x: pandas.Series):
    return len(x.unique())


def bin_variable(s: pandas.Series, min_value, max_value, width, how, default=None, lower=None, upper=None, errors=None):
    """
    bin pandas Series
    :param s: pandas Series
    :param min_value: minimum bining value
    :param max_value: maximum binning value
    :param width: bin width
    :param how: function to use for binning. Use numpy.ceil, numpy.floor
    :param default: default value to replace nans
    :param lower: value to assign to values smaller than min_value
    :param upper: value to assign to values larger  than max_value
    :param errors: error values in the Series to be treated a if they where nans
    :return: binned series s_binned
    """
    s_binned = s.copy()
    nan_values = numpy.array(s_binned.isna()) | numpy.array((s_binned == errors))

    conditions = numpy.array([True for _ in range(len(s_binned))])

    if lower is not None:
        s_binned.loc[s_binned < min_value] = lower
        conditions = conditions & (s_binned != lower) & (min_value <= s_binned)

    if upper is not None:
        s_binned.loc[s_binned > max_value] = upper
        conditions = conditions & (s_binned != upper) & (s_binned <= max_value)

    s_binned.loc[conditions] = list(numpy.clip(how(s_binned.loc[conditions] / width) * width, min_value, max_value))
    s_binned = numpy.round(s_binned, 8)
    if default is not None:
        s_binned.loc[nan_values] = default

    return s_binned


def detect_outliers(df, n, features):
    """
    Takes a dataframe df of features and returns a list of the indices
    corresponding to the observations containing more than n outliers according
    to the Tukey method.
    """
    outlier_indices = []

    # iterate over features(columns)
    for col in features:
        # 1st quartile (25%)
        q1 = numpy.percentile(df[col].dropna(), 25)
        # 3rd quartile (75%)
        q3 = numpy.percentile(df[col].dropna(), 75)
        # Interquartile range (iqr)
        iqr = q3 - q1

        # outlier step
        outlier_step = 1.5 * iqr

        # Determine a list of indices of outliers for feature col
        outlier_list_col = df[(df[col] < q1 - outlier_step) | (df[col] > q3 + outlier_step)].index

        # append the found outlier indices for col to the list of outlier indices
        outlier_indices.extend(outlier_list_col)

    # select observations containing more than 2 outliers
    outlier_indices = Counter(outlier_indices)
    multiple_outliers = list(k for k, v in outlier_indices.items() if v > n)

    return multiple_outliers


def multiple_replace(s: pandas.Series, replacing_dict: dict, default=None):
    """
    replaces multiple values at once
    :param s: pandas Series to act on
    :param replacing_dict: dictionary with replacements. Has to be in the form: {'<replacing_value_1>' : [<list_of_values_to_replace], '<replacing_value_2>' : [<list_of_values_to_replace] ...}
    :param default: default value. used to fill values not in replacing_value_n
    :return:
    """
    for key, value in replacing_dict.items():
        s = s.replace(value, key)
    if default is not None:
        s = s.map(dict(zip(replacing_dict.keys(), replacing_dict.keys()))).fillna(default)
    return s


def find_regex(regex, value):
    if re.search(regex, value) is not None:
        return True
    else:
        return False


def fill_empty_with_distr(s: pandas.Series, values_to_fill: list, values_to_avoid: list = None):
    """
    :param s: pandas Series to be filled
    :param values_to_fill: value to fill
    :param values_to_avoid: values not valid for filling
    :return:
    """

    compl_values_to_avoid = [numpy.nan]
    if values_to_avoid is not None:
        compl_values_to_avoid += values_to_avoid

    filling_index = s.index[s.isin(values_to_fill)]

    distrib_data = s.value_counts()
    distrib_data = distrib_data[~distrib_data.index.isin(values_to_fill + compl_values_to_avoid)]
    distrib_data_dict = {k: v for k, v in enumerate(distrib_data.index)}

    xk, pk = list(distrib_data_dict.keys()), distrib_data.values / distrib_data.values.sum()
    distrib = stats.rv_discrete(values=(xk, pk))

    filled_s = s.copy()
    filled_s[filling_index] = [distrib_data_dict[distrib.rvs()] for _ in filling_index]

    return filled_s


def fill_str(s: pandas.Series, length, fill_value: str = '0', fillna=False):
    if s.isna().any() and not fillna:
        warnings.warn('{} NaNs found in input series. Mapping skipped'.format(sum(s.isna())), Warning)

    return s.astype(float).apply(lambda x: str(int(x)).rjust(length, fill_value) if not math.isnan(x) else ''.rjust(length, fill_value) if fillna else x)
