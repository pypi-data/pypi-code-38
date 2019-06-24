"""
    In real world we deal with a lot of raw data. And that that has to ne in a certain format, weather it is used for
    building or predicting. Pre-Processing provides these utils for easy pre-processing of the data.

   ** Compatible with Pandas Data Frames
"""

from __future__ import print_function

from aitools.utils import util, constant, mathematics


def get_data_frame_as_list(data_frame, label_name):
    """
        This will help through out, Because training help with sudo list data frames, And this function provides
        sudo list data frames. Trick is to use it after all the pre-processing is complete.
    :param data_frame: Pandas DataFrame
    :param label_name: String for Label/Predictive Feature in data set
    :return: List of Lists. Containing the data and replacing the label to the -1 position.
    """
    cols = list(data_frame.columns.values)
    cols.pop(cols.index(label_name))

    return data_frame[cols + [label_name]].values.tolist()


def thresh_hold_binarization(feature_vector, thresh_hold):
    """
        Turn each value above or equal to the thresh hold 1 and values below the thresh hold 0.
    :param feature_vector: List of integer/float/double..
    :param thresh_hold: Thresh hold value for binarization
    :return: Process and binarized list of data.
    """
    return [1 if data >= thresh_hold else 0 for data in feature_vector]


def mean_value_binarization(feature_vector):
    """
        Turn each value above or equal to the mean value 1 and values below the mean 0.
    :param feature_vector: List of integer/float/double..
    :return: Process and binarized list of data.
    """

    mean = mathematics.mean(feature_vector)
    return [1 if data >= mean else 0 for data in feature_vector]


def mean_removal(feature_vector):
    """

    :param feature_vector:
    :return:
    """
    mean = mathematics.mean(feature_vector)
    return [data - mean for data in feature_vector]


def get_scaled_value(data, range_vector, input_vector):
    """

    :param data:
    :param range_vector:
    :param input_vector:
    :return:
    """
    min_input = min(input_vector)
    max_input = max(input_vector)
    max_range = max(range_vector)
    min_range = min(range_vector)
    return ((data - min_input) / (max_input - min_input)) * (max_range - min_range) + min_range


def scaling(feature_vector, min_max_vector=None):
    """

    :param feature_vector:
    :param min_max_vector:
    :return:
    """
    if min_max_vector is None:
        min_input = min(feature_vector)
        max_input = max(feature_vector)
        return [((data - min_input) / (max_input - min_input)) for data in feature_vector]
    else:
        return [
            get_scaled_value(data, min_max_vector, [max(feature_vector), min(feature_vector)])
            for data in feature_vector
        ]


def mean_value_normalization(feature_vector):
    """

    :param feature_vector:
    :return:
    """
    return [
        (data - mathematics.mean(feature_vector)) / mathematics.standard_deviation(feature_vector)
        for data in feature_vector
    ]
