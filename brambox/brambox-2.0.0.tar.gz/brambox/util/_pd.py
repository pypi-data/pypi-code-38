#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Pandas specific bits and bops
#

import numpy as np
import pandas as pd
from pandas.api.types import union_categoricals

__all__ = ['concat', 'from_dict', 'new', 'np_col', 'remove_images', 'select_images', 'split_images']


def concat(dfs, **kwargs):
    """ Concatenate multiple dataframes, whilst keeping the categorical dtype of the `image` column.

    Args:
        dfs (list): List of dataframes to concatenate
        kwargs (dict, optional): Extra keyword arguments that are passed on to :func:`pandas.concat()`

    Returns:
        pandas.DataFrame: Combined dataframe that has a union of the categories for the image
    """
    img = union_categoricals([df.image for df in dfs], sort_categories=True)
    dfs = [df.drop(['image'], axis=1) for df in dfs]
    df = pd.concat(dfs, **kwargs)
    df.insert(0, 'image', img)

    return df


def from_dict(data, images=None):
    """ Create a brambox compatible dataframe from a dictionary.
    This function uses the `pandas.DataFrame.from_dict()` method, but also sets the correct dtypes on some of the columns.

    Args:
        data (dict): Dictionary containing data in column order
        images (list, optional): list of all images in the dataset, used to create the categorical; Default **infer from data**

    Returns:
        pandas.DataFrame: dataframe with the data

    Note:
        It is not recommended to use this function to create brambox annotation/detection dataframes,
        as only a few columns (that are common between both anno/det) are checked for dtype. |br|
        This function is mostly here for internal use, so use the parsers instead!

        The only columns that are checked for dtype are:
            - image: Setting as a categorical with the `images` argument
            - class_label: Setting as 'object' type
            - x_top_left: Setting as 'float' type
            - y_top_left: Setting as 'float' type
            - width: Setting as 'float' type
            - height: Setting as 'float' type


        These are also the only columns that are absolutely necessary to have in your data for this function to work!
        Any other columns are added as well, but the dtype is inferred by pandas automatically.

    Warning:
        If you give this function a list of images for the categorical, but the data contains an image not in this list,
        that value will be set to null in the dataframe.
    """
    if not {'image', 'class_label', 'x_top_left', 'y_top_left', 'width', 'height'}.issubset(set(data)):
        raise ValueError('data dict at least needs the following keys: (image, class_label, x_top_left, y_top_left, width, height)')
    if images is None:
        images = set(data['image'])

    df = pd.DataFrame.from_dict(data={**data, 'image': pd.Categorical(data['image'], categories=sorted(images))})
    df = df.sort_values('image').reset_index(drop=True)
    df['class_label'] = df['class_label'].astype('object')
    df[['x_top_left', 'y_top_left', 'width', 'height']] = df[['x_top_left', 'y_top_left', 'width', 'height']].astype('float')

    return df


def new(df_type, images=None):
    """ Create a new, empty dataframe according to the brambox annotation/detection specifications.

    Args:
        df_type (string): What type of dataframe to create ('anno[tation]' or 'det[ection]')
        images (list, optional): Images to use as the categorical values for the `image` column

    Returns:
        pandas.DataFrame: empty dataframe with the right columns and dtypes
    """
    df_type = df_type.lower()
    if df_type.startswith('anno'):
        data = {
            'image': [],
            'class_label': [],
            'id': [],
            'x_top_left': [],
            'y_top_left': [],
            'width': [],
            'height': [],
            'occluded': [],
            'truncated': [],
            'lost': [],
            'difficult': [],
            'ignore': [],
        }
    elif df_type.startswith('det'):
        data = {
            'image': [],
            'class_label': [],
            'id': [],
            'x_top_left': [],
            'y_top_left': [],
            'width': [],
            'height': [],
            'confidence': [],
        }
    else:
        raise ValueError(f'Unkown dataframe type [{df_type}]. Please choose one of [annotation, detection]')

    df = from_dict(data, images)
    if df_type.startswith('anno'):
        df[['lost', 'difficult', 'ignore']] = df[['lost', 'difficult', 'ignore']].astype('bool')

    return df


def np_col(df, name):
    """ A faster alternative than ``.values`` to access a pandas column as a numpy array.
    The speed benefits are only visible if accessing columns repeatedly (eg. loops),
    and as such might only be really usefull in internal parts of this package. |br|
    See https://github.com/pandas-dev/pandas/issues/10843 for more info.

    Args:
        df (pandas.DataFrame): Dataframe from which you want to access some column data
        name (string): Column name

    Returns:
        numpy.array: array with the column data

    Note:
        This function also works if `df` is already a dictionary of numpy arrays,
        making it really usefull in the cython portions of the codebase.
    """
    if isinstance(df, dict):
        return df[name]

    idx = df.columns.get_loc(name)
    bm = df._data
    return bm.blocks[bm._blknos[idx]].iget(bm._blklocs[idx])


def remove_images(df, removals):
    """ Remove images from the dataset.
    This function removes images from both the data and category.

    Args:
        df (pandas.DataFrame): brambox dataframe
        removals (list): images to remove

    Returns:
        pandas.DataFrame: brambox dataframe with the selected images removed
    """
    if df.image.isnull().values.any():
        log.error('Dataframe already has NaN values in the image column which will be filtered out')

    df = df.copy()
    df.image = df.image.cat.remove_categories(removals)
    return df[df.image.notnull()].reset_index(drop=True)


def select_images(df, selection):
    """ Select data from specific images in the dataset.
    This function only keeps the selected images in both the data and category

    Args:
        df (pandas.DataFrame): brambox dataframe
        selection (list): images to keep

    Returns:
        pandas.DataFrame: brambox dataframe with only the selected images
    """
    df = df.copy()
    df.image = df.image.cat.set_categories(selection)
    return df[df.image.notnull()].reset_index(drop=True)


def split_images(df, *splits, remainder=True):
    """ Split data in subsets based on images.

    Args:
        df (pandas.DataFrame): brambox dataframe
        *splits (list): different image splits you need
        remainder (optional): whether to return the remaining images as a last split; Default **True**

    Returns:
        list of [pandas.DataFrame]: the different splitted brambox dataframes

    Example:
        >>> # Split dataframe in even/odd
        >>> even, odd = bb.util.split_images(df, df.image.cat.categories[::2])

        >>> # Take specific subsets and discard whatever was not picked
        >>> images = df.image.cat.categories
        >>> train, test = bb.util.split_images(df, images[0:500], images[500:750], remainder=False)
    """
    dfs = []
    selected_images = set()
    for s in splits:
        data = df.copy()
        data.image = data.image.cat.set_categories(s)
        dfs.append(data[data.image.notnull()].reset_index(drop=True))

        df = df[data.image.isnull()]
        selected_images |= set(s)

    if remainder:
        df.image.cat.remove_categories(list(selected_images), inplace=True)
        dfs.append(df.reset_index(drop=True))

    return dfs
