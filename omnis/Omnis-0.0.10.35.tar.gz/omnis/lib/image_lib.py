# -*- coding: utf-8 -*-
"""This module is a utility module for image preprocessing.
"""
import math
import os
import sys

import cv2
import numpy

IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg',)


def reshape_data(data_array, input_shape, cv_interpolation=cv2.INTER_LINEAR):
    """Changes an array of images to fit with input shape.
    Note that this method casts and rescales data to a range of [0, 1].

    Arguments:
        data_array {ndarray} -- An array of images.
        input_shape -- Shape of input

    Keyword Arguments:
        cv_interpolation {int} -- cv2 interpolation. (default: {cv2.INTER_LINEAR})

    Returns:
        [ndarray] -- Reshaped data array.
    """
    if data_array.shape[1:] != input_shape:
        reshaped_list = list()
        for i in range(data_array.shape[0]):
            resized_img = cv2.resize(
                data_array[i],
                (input_shape[1], input_shape[2]),
                interpolation=cv_interpolation)
            reshaped_list.append(resized_img)
        data_array = numpy.asarray(reshaped_list)
        reshaped_list = []  # empty list after use
    data_array = data_array.astype('float32')
    data_array /= 255
    return data_array


def resize_image(img, target_size, cv_interpolation=cv2.INTER_LINEAR):
    """Resizes image with specified target size and casts to float32.

    Arguments:
        img {ndarray} -- An opencv image array
        target_size {tuple} -- A tuple of two natural numbers. Two numbers represent the width and height, respectively.

    Keyword Arguments:
        cv_interpolation {int} -- cv2 interpolation. (default: {cv2.INTER_LINEAR})

    Returns:
        [ndarray] -- Resized image array.
    """
    resized_img = cv2.resize(img, target_size, interpolation=cv_interpolation)
    resized_img = resized_img.astype('float32')
    return resized_img


def is_image_file(filename):
    """this function checks a file extension.

    Arguments:
        filename {str} -- A path of file.

    Returns:
        [bool] -- If an extension of the file is an image, returns True. Otherwise False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in IMAGE_EXTENSIONS


def get_current_directory_name(file_path):
    """This function returns a parent directory name of the file at the file_path.

    Arguments:
        file_path {str} -- A path of the file.

    Raises:
        ValueError -- If the file is not in a directory, then this function raises a ValueError.

    Returns:
        [str or unicode] -- A parent directory name.(The same as a label of the file.)
    """
    splitted_filename = None
    if sys.platform == "win32":
        splitted_filename = file_path.split('\\')
    else:
        splitted_filename = file_path.split('/')
    if len(splitted_filename) < 2:
        raise ValueError(
            'No parent directory found. You should put your image files inside '
            'a directory name which is the same as a label of them.'
        )

    return splitted_filename[-2]


def append_elem(path, img_list, label_list, target_size):
    """This function recursively iterates over files and directories.
    While iterating, if an image file found,
    this function appends an image as an array format to img_list and appends a label to label_list

    Arguments:
        path {str} -- A path of a current file or a director.
        img_list {list} -- A list of images.
        label_list {list} -- A list of labels.
        target_size {tuple} -- A tuple which specifies a target size of image array.(Image files are resized to target size.)
    """
    if os.path.isdir(path):
        child_list = os.listdir(path)
        for child in child_list:
            child_path = os.path.join(path, child)
            append_elem(child_path, img_list, label_list, target_size)
    else:
        if is_image_file(path):
            img = cv2.imread(path)
            resized_image = resize_image(img, target_size)
            label = get_current_directory_name(path)
            img_list.append(resized_image)
            label_list.append(label)


def directory_images_to_arrays(directory_path, target_size):
    """Recursively iterates over child files and directories of directory_path.
    Image files will be converted to an array of images with rescaled value.
    Parent directory names will be converted to array_of_labels.

    Arguments:
        directory_path {str} -- A root path of image files and directories.
        target_size {tuple} -- A tuple which specifies a target size of image
        array.(Image files are resized to target size.)

    Returns:
        array_of_images, array_of_labels [(ndarray, ndarray)] --
            array_of_images is a rescaled array of resized images.
            array_of_labels is a label array of images.
            You can find a label of an image at the same index of array_of_labels.
    """
    img_list = list()
    label_list = list()
    append_elem(directory_path, img_list, label_list, target_size)
    array_of_images = numpy.asarray(img_list)
    array_of_images /= 255
    array_of_labels = numpy.asarray(label_list)
    return array_of_images, array_of_labels


def get_image_names_in_directory(directory_path):
    """Iterates over files in directory_path.
    Return image file path lists of below directory_path.

    Arguments:
        directory_path {str} -- A root path of image files.
        target_size {tuple} -- A tuple which specifies a target size of image array.(Image files are resized to target size.)

    Returns:
        [str list] --
            list of image file paths inside given directory_path.
    """
    files = sorted(os.listdir(directory_path))
    return [os.path.join(directory_path, f) for f in files if is_image_file(f)]


def merge_image(img_list, images_area_index):
    """Merge images in img_list using images_area_index
    void area will be filled with 0 value
    Return image numpy array which merging given images

    Arguments:
        img_list {str list} -- Filenames of image files
        images_area_index {int[4] list} -- x1,y1,x2,y2 list of images

    Returns:
        [nparray] --
            array of merged image
    """
    boundary_xs = set()
    boundary_ys = set()

    for images_area in images_area_index:
        boundary_xs.add(images_area[2])
        boundary_ys.add(images_area[3])

    boundary_xs = list(boundary_xs)
    boundary_ys = list(boundary_ys)

    BG = numpy.zeros((max(boundary_ys), max(boundary_xs), 3), numpy.uint8)

    for index, image in enumerate(img_list):
        image_original_size = (
            images_area_index[index][2] -
            images_area_index[index][0],
            images_area_index[index][3] -
            images_area_index[index][1])
        image_after_resize = resize_image(image, image_original_size)

        # image_after_resize_blur = blur_boundary_area(image_after_resize, [2, image_original_size[0]-2], [2, image_original_size[1]-2], 2)
        BG[
            images_area_index[index][1]:images_area_index[index][3],
            images_area_index[index][0]:images_area_index[index][2]
        ] = image_after_resize

    # boundary_xs.remove(max(boundary_xs))
    # boundary_ys.remove(max(boundary_ys))
    # BG = blur_boundary_area(BG, boundary_xs, boundary_ys, 2)
    return BG


def blur_boundary_area(img, boundary_xs, boundary_ys, pixel_range):
    for y in boundary_ys:
        y_line = img[y - pixel_range:y + pixel_range, :]
        blur = cv2.GaussianBlur(y_line,
                                (2 * pixel_range + 1, 2 * pixel_range + 1), 0)
        img[y - pixel_range:y + pixel_range] = blur

    for x in boundary_xs:
        x_line = img[:, x - pixel_range:x + pixel_range]
        blur = cv2.GaussianBlur(x_line,
                                (2 * pixel_range + 1, 2 * pixel_range + 1), 0)
        img[:, x - pixel_range:x + pixel_range] = blur

    return img


def split_one_image(img, split_width, split_height):
    """Split images in img by split_width and split_height
    Return list of split image array and area_index for each image array

    Arguments:
        img {array} -- array of image files
        split_width {int} -- width you want to split in this size
        split_height {int} -- height you want to split in this size

    Returns:
        [list of array] -- list of image array
        [list] -- list of (x1, y1, x2, y2)
    """
    width, height = img.shape[1], img.shape[0]
    x_count = math.ceil(width / split_width)
    y_count = math.ceil(height / split_height)

    split_image_list = list()
    area_index = list()
    for i in range(0, x_count):
        for j in range(0, y_count):
            x_start = i * split_width
            x_end = min((i + 1) * split_width, width)
            y_start = j * split_height
            y_end = min((j + 1) * split_height, height)
            area = (x_start, y_start, x_end, y_end)
            cropped_img = img[y_start:y_end, x_start:x_end]
            split_image_list.append(cropped_img)
            area_index.append(area)

    return split_image_list, area_index


def save_image(image, file_path):
    directory = os.path.dirname(file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    cv2.imwrite(file_path, image)
