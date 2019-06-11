#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: violinsolo
# Created on 2019/4/19


def cnt_split(tar_list, cnt_per_slice):
    """
    Yield successive n-sized(cnt_per_slice) chunks from l(tar_list).

        >>> x = list(range(34))
        >>> for i in cnt_split(x, 5):
        >>>     print(i)
        <<< print result ...
        <<< [0, 1, 2, 3, 4]
        <<< [5, 6, 7, 8, 9]
        <<< [10, 11, 12, 13, 14]
        <<< [15, 16, 17, 18, 19]
        <<< [20, 21, 22, 23, 24]
        <<< [25, 26, 27, 28, 29]
        <<< [30, 31, 32, 33]

    The targetlist can be split into slices with a NAX size of 'cnt_per_slice' ...
    :param tar_list: target list to split
    :param cnt_per_slice: slice per max size...
    :return: yield one result.
    """
    for i in range(0, len(tar_list), cnt_per_slice):
        yield tar_list[i:i + cnt_per_slice]


def n_split(tar_list, n):
    """
    Yield successive n-sized(cnt_per_slice) chunks from l(tar_list).

        >>> x = list(range(33))
        >>> for i in n_split(x, 5):
        >>>     print(i)
        <<< print result ...
        <<< [0, 1, 2, 3, 4, 5, 6]
        <<< [7, 8, 9, 10, 11, 12, 13]
        <<< [14, 15, 16, 17, 18, 19, 20]
        <<< [21, 22, 23, 24, 25, 26]
        <<< [27, 28, 29, 30, 31, 32]

    The targetlist can be split into slices with a NAX size of 'cnt_per_slice' ...
    :param tar_list: target list to split
    :param n: slice counts ...
    :return: yield one result.
    """
    slice_len = int(len(tar_list) / n)
    slice_len_1 = slice_len + 1
    slice_remain = int(len(tar_list) % n)

    cur_idx = 0
    for i in range(n):
        # print(f'{i} < {slice_remain} : [{cur_idx}: {cur_idx+(slice_len_1 if i < slice_remain else slice_len)}]')
        yield tar_list[cur_idx: cur_idx+(slice_len_1 if i < slice_remain else slice_len)]
        cur_idx += slice_len_1 if i < slice_remain else slice_len


def n_split_idx(tar_list_len, n):
    """
    Yield successive n-sized(cnt_per_slice) chunks from l(tar_list).

        >>> x = list(range(33))
        >>> n_split_idx(len(x), 3)
        <<< [11, 11, 11]
        >>> n_split_idx(len(x), 4)
        <<< [9, 8, 8, 8]
        >>> n_split_idx(len(x), 5)
        <<< [7, 7, 7, 6, 6]
        >>> n_split_idx(len(x), 6)
        <<< [6, 6, 6, 5, 5, 5]
        >>> n_split_idx(len(x), 7)
        <<< [5, 5, 5, 5, 5, 4, 4]

    The targetlist can be split into slices with a NAX size of 'cnt_per_slice' ...
    :param tar_list_len: target list length to split
    :param n: slice counts ...
    :return: list of each slice length.
    """

    slice_len = int(tar_list_len / n)
    slice_remain = int(tar_list_len % n)

    res = []
    for i in range(n):
        if i<slice_remain:
            res.append(slice_len+1)
        else:
            res.append(slice_len)

    return res



