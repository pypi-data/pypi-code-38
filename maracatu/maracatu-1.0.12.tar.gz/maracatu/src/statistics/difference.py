"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

from src.util.parameters import Parameter
from src.statistics.base.bins import BinsDataFrame
from src.statistics.base.joints import Joint


class Difference(object):

    def __init__(self):
        pass

    @staticmethod
    def _calculate_diff(row, df):
        xs = df.index.get_level_values(0)[0]

        x = row.name[0]
        y = row.name[1]
        row['diff'] = df.loc[x, y]['p'] - df.loc[xs, y]['p']
        return row

    def get_ref(self, df, par):
        xvar = Parameter.get_par(par, 'xvar')
        yvar = Parameter.get_par(par, 'yvar')
        xbins = Parameter.get_par(par, 'xbins')
        ybins = Parameter.get_par(par, 'ybins')

        df_freq = Joint.get_hist2d(df, xvar=xvar, xbins=xbins, yvar=yvar, ybins=ybins)
        xs = df_freq.index.get_level_values(0)[0]
        # df_freq2 = Joint.get_hist2d(df2, xvar=xvar, xbins=xbins, yvar=yvar, ybins=ybins)

        # df_freq1 = df_freq1['p']
        # df_freq = df_freq
        # df_freq['ref'] = df_freq.loc[xs, :]['p']
        # df_diff = df_freq['p'] - df_freq['ref']

        df_diff = df_freq.apply(Difference._calculate_diff, axis=1, df=df_freq)

        return df_diff['diff']

    def get(self, df1, df2, par):
        xvar = Parameter.get_par(par, 'xvar')
        yvar = Parameter.get_par(par, 'yvar')
        xbins = Parameter.get_par(par, 'xbins')
        ybins = Parameter.get_par(par, 'ybins')

        df_freq1 = Joint.get_hist2d(df1, xvar=xvar, xbins=xbins, yvar=yvar, ybins=ybins)
        df_freq2 = Joint.get_hist2d(df2, xvar=xvar, xbins=xbins, yvar=yvar, ybins=ybins)

        df_freq1 = df_freq1['p']
        df_freq2 = df_freq2['p']

        df_diff = df_freq1 - df_freq2

        return df_diff


from src.organ_transplantation.common import TransplantCommon


def calculate_diff(xvar, yvar, organ):
    global par_base, diff
    par_base = {
        'organ': organ,
        'donor_type': TransplantCommon.DONOR_TYPE_DECEASED,
        'waiting_list': yvar == TransplantCommon.VAR_WLT_NM_WAIT,
        'xvar': xvar,
        'yvar': yvar,
        'binning': [
            {
                'var': xvar,
                'binning_type': 'quantile',
                'bin_sample': 50,
                'bin_min': .1,
                'bin_min_quantile': True,
                'bin_max': .9,
                'bin_max_quantile': True,
            },
            {
                'var': yvar,
                'binning_type': 'quantile',
                # 'step': 1,
                'bin_sample': 50,
                'bin_min': .1,
                'bin_min_quantile': True,
                'bin_max': .9,
                'bin_max_quantile': True,
            }
        ],
        # 'legend': ['BLACK', 'HISPANIC', 'ASIAN']
    }
    from src.organ_transplantation.curation.curation_equity import CurationEquity
    import matplotlib.pyplot as plt
    from src.plotting.base.histogram import Histogram
    curation = CurationEquity()
    df = curation.curate(par_base)
    # df.columns
    # df = df[df.TRR_DT_TRANSPLANT >= '2005']
    # df1 = df[df.PAT_CH_RACE == 'WHITE']
    # df2 = df[df.PAT_CH_RACE == 'BLACK']
    # df3 = df[df.PAT_CH_RACE == 'HISPANIC']
    # df4 = df[df.PAT_CH_RACE == 'ASIAN']
    #
    xbins, ybins = BinsDataFrame().get(df, par_base)
    par = {
        'xbins': xbins,
        'ybins': ybins
    }
    par_base.update(par)
    diff = Difference()

    return diff.get_ref(df, par_base)


def lambda_diff_get(params):
    xvar, yvar, organ = params
    df_diff = calculate_diff(xvar, yvar, organ)
    df_diff.to_hdf(f'datalink/demographic_environments/data_output/equity/difference/df_{organ}_{xvar}_{yvar}.hdf',
                   'df')

def main():
    list_xvar = ['RAC_WHITE', 'RAC_BLACK', 'RAC_HISPANIC', 'RAC_ASIAN',
                 'TRA_WHITE', 'TRA_BLACK', 'TRA_HISPANIC', 'TRA_ASIAN',
                 'EDU_ELEMENTAR', 'EDU_HIGH', 'EDU_COLLEGE', 'EDU_BACHELOR',
                 'TRA_ELEMENTAR', 'TRA_HIGH', 'TRA_COLLEGE', 'TRA_BACHELOR',
                 ]
    list_yvar = [TransplantCommon.VAR_TRR_NM_GRAFT_SURVIVAL, TransplantCommon.VAR_WLT_NM_WAIT]
    list_organ = TransplantCommon.LIST_ORGANS
    import itertools as it
    params = it.product(list_xvar, list_yvar, list_organ)



    from src.util.util_multiprocessing import MyPool
    df_diffs = []
    with MyPool(processes=10) as pool:
        pool.map(lambda_diff_get, params)

if __name__ == "__main__":
    main()



# #
# # df_diff1 = diff.get(df1, df2, par_base)
# # df_diff2 = diff.get(df1, df3, par_base)
# # df_diff3 = diff.get(df1, df4, par_base)
#
# plt_hist = Histogram()
# # fig, ax, par = plt_hist.plot([df_diff1, df_diff2, df_diff3], par_base)
# fig, ax, par = plt_hist.plot(df_diffs, par_base)
#
# plt.show()
#
#
# import numpy as np
# x = df_diffs[0]
# n = len(x)
# reps = 10000
# xb = np.random.choice(x, (n, reps))
# mb = xb.mean(axis=0)
# mb.sort()
# np.percentile(mb, [2.5, 97.5])
#
#
# plt_hist = Histogram()
# # fig, ax, par = plt_hist.plot([df_diff1, df_diff2, df_diff3], par_base)
# fig, ax, par = plt_hist.plot(mb, par_base)
#
# from src.organ_transplantation.organ_transplantation import OrganTransplantation
# #
# # ot = OrganTransplantation.get_organ_transplantation_helper()
# # df_transplants = ot.organ_transplantation
# #
# #
# # df = df_transplants[df_transplants.TRR_CH_ORGAN == organ]


import pandas as pd
from src.organ_transplantation.common import TransplantCommon
organ = TransplantCommon.ORGAN_KIDNEY
xvar = 'RAC_BLACK'
yvar = TransplantCommon.VAR_WLT_NM_WAIT

df = pd.read_hdf(f'datalink/demographic_environments/data_output/equity/difference/df_{organ}_{xvar}_{yvar}.hdf', 'df')


df

import numpy as np
x = df
n = len(x)
reps = 10000
xb = np.random.choice(x, (n, reps))
mb = xb.mean(axis=0)
mb.sort()
np.percentile(mb, [2.5, 97.5])