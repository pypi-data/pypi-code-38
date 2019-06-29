import math as M
import numpy as np
# from mgpro import mgmat
# import matplotlib.pyplot as plt


def next_pow_2(i):
    """
    Find the next power of two

    >>> int(next_pow_2(5))
    8
    >>> int(next_pow_2(250))
    256
    """
    # do not use NumPy here, math is much faster for single values
    buf = M.ceil(M.log(i) / M.log(2))
    return int(M.pow(2, buf))


def expand(data):
    (len_row, len_col) = data.shape
    nft_row = next_pow_2(len_row)
    nft_col = next_pow_2(len_col)
    data_ex = np.zeros([nft_row, nft_col])
    row_begin = int(round((nft_row - len_row) / 2))
    row_end = row_begin + len_row - 1
    col_begin = int(round((nft_col - len_col) / 2))
    col_end = col_begin + len_col - 1
    data_ex[row_begin:row_end + 1, col_begin:col_end + 1] = data
    data_ex[row_begin:row_end + 1, 0: col_begin] = np.tile(data[:, 0], (col_begin, 1)).T \
                                                   * np.tile(np.cos(np.linspace(np.pi/2, np.pi, col_begin))**2, (len_row, 1))
    data_ex[row_begin:row_end + 1, col_end:] = np.tile(data[:, -1], (nft_col-col_end, 1)).T \
                                               * np.tile(np.cos(np.linspace(0, np.pi/2, nft_col - col_end))**2, (len_row, 1))
    data_ex[0:row_begin, :] = np.tile(data_ex[row_begin, :], (row_begin, 1))\
                              * np.tile(np.cos(np.linspace(np.pi/2, np.pi, row_begin))**2, (nft_row, 1)).T
    data_ex[row_end:, :] = np.tile(data_ex[row_end-1, :], (nft_row - row_end, 1)) \
                           * np.tile(np.cos(np.linspace(0, np.pi / 2, nft_row - row_end))**2, (nft_row, 1)).T
    return data_ex, row_begin, row_end, col_begin, col_end


if __name__ == '__main__':
    pass
    # filename = '/Users/xumj/Codes/MGPro/mag_test.dat'
    # mg = mgmat(filename)
    # data_ex, row_begin, row_end, col_begin, col_end = expand(mg.data)
    # plt.pcolormesh(data_ex)
    # plt.show()
