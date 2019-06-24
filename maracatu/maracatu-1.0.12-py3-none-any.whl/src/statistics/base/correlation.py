"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

import statsmodels.api as sm
import scipy.stats as st
import numpy as np
import pandas as pd


class Correlation(object):

    def __init__(self):
        pass

    @staticmethod
    def corr_cint(r, n):
        z = np.arctanh(r)
        sigma = (1 / (n - 3) ** 0.5)
        cint = z + np.array([-1, 1]) * sigma * st.norm.ppf((1 + 0.95) / 2)
        return np.tanh(cint)

    @staticmethod
    def get_resid(df, x, y):
        control = set([x, y]) ^ set(df.columns)
        # formula_control = str.join('', [' %s +' % c for c in control])[:-1]
        # formula_x = '%s ~ 1 + %s' % (x, formula_control)
        # formula_y = '%s ~ 1 + %s' % (y, formula_control)
        formula_control = str.join('', [' + %s' % c for c in control])
        formula_x = '%s ~ 1 %s' % (x, formula_control)
        formula_y = '%s ~ 1 %s' % (y, formula_control)

        res_x = sm.OLS.from_formula(formula_x, data=df).fit().resid
        res_y = sm.OLS.from_formula(formula_y, data=df).fit().resid
        return res_x, res_y

    @staticmethod
    def get_df(df, x, y):
        res_x, res_y = Correlation.get_resid(df, x, y)
        df_new = pd.DataFrame()
        df_new[x] = res_x
        df_new[y] = res_y
        return df_new

    @staticmethod
    def get_correlation(df, x, y, partial=False):
        res_x, res_y = df[x], df[y]
        if partial:
            res_x, res_y = Correlation.get_resid(df, x, y)
        corr_x_y = st.pearsonr(res_x, res_y)
        return corr_x_y[0], corr_x_y[1], Correlation.corr_cint(corr_x_y[0], len(df))

#
# import pandas as pd
# from src.organ_transplantation.organ_transplantation import OrganTransplantation
# from src.organ_transplantation.common import TransplantCommon
# ot = OrganTransplantation.get_organ_transplantation_helper()
# df = ot.organ_transplantation
#
# df = df.loc[df.TRR_CH_ORGAN == 'HEART']

# df_new = Correlation.get_df(df, x=TransplantCommon.VAR_TRR_NM_DISTANCE, y=TransplantCommon.VAR_TRR_NM_GRAFT_SURVIVAL)

#
#
#
# cols = [TransplantCommon.VAR_TRR_NM_GRAFT_SURVIVAL, TransplantCommon.VAR_TRR_NM_DISTANCE, TransplantCommon.VAR_TRR_NM_GRAFT_ISCHEMIC]
# df = df[cols]
# df = df.dropna()
#
# res = Correlation.get_resid(df, x=TransplantCommon.VAR_TRR_NM_DISTANCE, y=TransplantCommon.VAR_TRR_NM_GRAFT_SURVIVAL)
#
# cor = Correlation.get_correlation(df, x=TransplantCommon.VAR_TRR_NM_DISTANCE, y=TransplantCommon.VAR_TRR_NM_GRAFT_SURVIVAL)


#
#
# control = set([x, y]) ^ set(df.columns)
# formula_control = str.join('', [' %s +' % c for c in control])[:-1]
# formula_x = '%s ~ %s' % (x, formula_control)
# formula_y = '%s ~ %s' % (y, formula_control)
#
# reg_x = sm.OLS.from_formula(formula_x, data=df).fit().resid
# reg_y = sm.OLS.from_formula(formula_y, data=df).fit().resid
#
# 'abs'[:-1]
#
# for c in control:
#     f = '%s +'