"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

import pandas as pd
import numpy as np

from maracatu.src.statistics.base.confidence_inverval import ConfidenceInterval
from maracatu.src.statistics.base.correlation import Correlation
import multiprocessing


class Joint:

    def __init__(self):
        pass

    @staticmethod
    def func_l(df, x, y, xvar, yvar):
        num = df[(df[xvar] > x) & (df[yvar] <= y)].shape[0]
        den = df[df[xvar] > x].shape[0]
        return num, den


    @staticmethod
    def calculate_joint_ccdf(df, x, y, xvar='X', yvar='Y'):
        # df.loc[:, 'X'] = df[xvar]
        # df.loc[:, 'Y'] = df[yvar]
        num, den = Joint.func_l(df, x, y, xvar, yvar)
        p, ci_l, ci_u = ConfidenceInterval.proportion_ci_wilson(num, den)
        return num, den, p, ci_l, ci_u

    @staticmethod
    def calculate_freq(row, df, x_callback=None, y_callback=None):
        x = row.name[0]
        y = row.name[1]
        num, den, p, ci_l, ci_u = Joint.calculate_joint_ccdf(df, x, y)
        row['num'] = num
        row['den'] = den
        row['p'] = p
        row['ci_l'] = ci_l
        row['ci_u'] = ci_u
        return row

    @staticmethod
    def get_hist(df=None,
                 x_bins=1,
                 y_bins=1,
                 y_callback=None,
                 x_callback=None):
        if df is None:
            raise ('df is none')

        df_freq = pd.DataFrame(index=pd.MultiIndex.from_product([x_bins, y_bins], names=['X', 'Y']),
                               columns=['num', 'den'])

        df_freq = df_freq.apply(Joint.calculate_freq,
                                axis=1,
                                df=df,
                                x_callback=x_callback,
                                y_callback=y_callback)


        # df_freq = util.apply_by_multiprocessing(df_freq, )

        return df_freq

    @staticmethod
    def get_hist2d(df=None,
                   xvar=None,
                   xbins=None,
                   xcallback=None,
                   yvar=None,
                   ybins=None,
                   ycallback=None):
        '''
        get_hist2d -> pd.DataFrame
        :param df:
        :param xvar:
        :param xbins:
        :param xcallback:
        :param yvar:
        :param ybins:
        :param ycallback:
        :return:
        '''

        df_freq = df.copy(deep=True)

        df_freq.loc[:, 'X'] = df_freq[xvar]
        df_freq.loc[:, 'Y'] = df_freq[yvar]

        df_freq = Joint.get_hist(df=df_freq,
                                 x_bins=xbins,
                                 x_callback=xcallback,
                                 y_bins=ybins,
                                 y_callback=ycallback)
        return df_freq

    #
    # @staticmethod
    # def get_bins(df, name, bin_size, f_max=max):
    #     if df is None:
    #         raise ('df is none')
    #
    #     max_value = int(np.ceil(f_max(df[name])))
    #     bins = np.round(np.arange(0, max_value + bin_size, bin_size), 2)
    #     return bins



def apply_by_multiprocessing(df, func, **kwargs):
    workers = kwargs.pop('workers')

    with multiprocessing.Pool(processes=workers) as pool:
        result = pool.map(_apply_df, [(d, func, kwargs)
                                      for d in np.array_split(df, workers)])
        return pd.concat(list(result))
    # pool = multiprocessing.Pool(processes=workers)
    #     return
    # pool.close()


def _apply_df(args):
    df, func, kwargs = args
    return df.apply(func, **kwargs)



