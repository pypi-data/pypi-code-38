import logging

from numpy import mean, std


def svn(y_data, mean_y_data=False, std_dev=False):
    """
    svn normalisation function
    :param y_data: np array of y data points
    :param mean_y_data: if you want to normalise relative to other data can pass in a mean
    :param std_dev: same as for mean but with std dev
    :return: svn normlaised data as np array, tuple of mean and std dev of data
    """
    logging.debug('normalising using svn normalisation')
    """normalise using std variance normalisation"""
    if not mean_y_data and not std_dev:
        mean_y_data = mean(y_data)
        std_dev = std(y_data)

    shifted_y_data = y_data - mean_y_data
    normalised_y = shifted_y_data / std_dev
    return normalised_y, (mean_y_data, std_dev)
