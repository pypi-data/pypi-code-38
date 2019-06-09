import pandas as pd


def _get_index_mask(dataframe, other, index, how):
    df_index = dataframe[index].set_index(index).index
    oth_index = other[index].set_index(index).index
    mask = df_index.isin(oth_index)
    if how == 'diff':
        return ~mask
    return mask


def _filter_by_index_mask(dataframe, index, mask):
    dataframe = dataframe.set_index(index)
    filterd = dataframe.loc[mask]
    dataframe = filterd.reset_index()
    return dataframe


def get_intersect_with(dataframe, other, index):
    mask = _get_index_mask(dataframe, other, index, 'intersect')
    dataframe = _filter_by_index_mask(dataframe, index, mask)
    return dataframe


def get_difference_from(dataframe, other, index):
    mask = _get_index_mask(dataframe, other, index, 'diff')
    dataframe = _filter_by_index_mask(dataframe, index, mask)
    return dataframe
