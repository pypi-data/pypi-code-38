"""This module is a custom module designed for general use in the Omnis project.
"""
import os

import numpy as np


def reverse_dict(input_dict):
    """This function returns a dictionary with input_dict's key, value is
    reversed. If input_dict has same value among different keys, some keys
    may be omitted.

    Arguments:
        input_dict {dict} -- Dictionary to reverse.

    Returns:
        [dict] -- Reversed dictionary.
    """
    return {value: key for key, value in input_dict.items()}


def get_n_largest_index_and_probs(probs_array, n):
    """This function returns array of top n index of probs

    Arguments:
        probs_array {array of array} -- Array of probs array
        n {int} -- top n

    Returns:
        [array of array] -- Array of Top n index array
        [array of array] -- Array of Top n probs array
    """
    if n > probs_array[0].size:
        raise ValueError("n should be smaller than classes number")

    indexes = np.argsort(-probs_array)[:, :n]
    sorted_probs = np.zeros((len(probs_array), n))
    for i, prob in enumerate(probs_array):
        for j in range(0, n):
            sorted_probs[i][j] = (int(prob[indexes[i][j]] * 10000)) / 10000

    return indexes, sorted_probs


def get_data_path_type(data_path):
    """This function returns type of data_path

    Arguments:
        data_path {string} -- name of data_path

    Returns:
        [string] -- return directory, image, csv decided by data_path type
    """
    if os.path.isdir(data_path):
        return "directory"

    _, file_extension = os.path.splitext(data_path)

    image_extension_list = ['.jpg', '.jpeg', '.png', '.bmp', '.ppm', '.tif',
                            '.tiff']

    if file_extension in image_extension_list:
        return "image"

    if file_extension == ".csv":
        return "csv"

    raise ValueError("We didn't provide %s type" % file_extension)


def get_area_by_polygons(all_points_x, all_points_y):
    """This function returns the area calculated by polygons.
    For more detailed explanation, refer to the Wikipedia article:
    https://en.wikipedia.org/wiki/Shoelace_formula

    Arguments:
        all_points_x {numpy array} -- np of x
        all_points_y {numpy array} -- np of y

    Returns:
        [float] -- return the area of polygons
    """
    return 0.5 * np.abs(
        np.dot(all_points_x, np.roll(all_points_y, 1))
        - np.dot(all_points_y, np.roll(all_points_x, 1))
    )


def divide_train_val_dataset(data_path):
    """This function returns lists of train data paths and validation
    data paths, with ratio of 9:1.

    Arguments:
        data_path {str} -- data path

    Returns:
        train {list} -- list of paths to train data
        val {list} -- list of paths to validation data
    """
    images = os.listdir(data_path)
    train = []
    val = []
    for i, image in enumerate(images):
        if i % 10 == 0:
            val.append(os.path.join(data_path, image))
        else:
            train.append(os.path.join(data_path, image))
    return train, val
