"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

from lifelines import KaplanMeierFitter
from lifelines import CoxPHFitter
from lifelines.utils import survival_table_from_events

import pandas as pd


class Survival:

    def __init__(self):
        self.kmf = KaplanMeierFitter()


    def fit_groups(df, column):
        groups = np.sort(df[column].unique())
        fig, ax = plt.subplots(1,1)
        for g in groups:
    #         df_g = df[(df.TIME <= df.TIME.quantile(.94)) & (df[column] == g)]
            df_g = df[(df[column] == g)]
            if len(df_g) > 0:
                kmf.fit(df_g['TIME'] , df_g['EVENT'], label=g)
                kmf.plot(ax=ax)

    def plot_group_subgroup(df, group, subgroup1, subgroup2):
        groups = df.loc[pd.notnull(df[group]), group].unique()
        subgroups1 = df.loc[pd.notnull(df[subgroup1]), subgroup1].unique()
        subgroups2 = df.loc[pd.notnull(df[subgroup2]), subgroup2].unique()
        fig, axes = plt.subplots(len(groups), len(subgroups1))
        fig.set_size_inches(40, 40)
        for i, g in enumerate(groups):
            for j, s1 in enumerate(subgroups1):
                for k, s2 in enumerate(subgroups2):
                    #                 ax = plt.subplot(len(group), len(subgroup1), i+j+1)
                    ax = axes[i, j]
                    df_g = df[(df[group] == g) & (df[subgroup1] == s1) & (df[subgroup2] == s2)]
                    if len(df_g) > 0:
                        kmf.fit(df_g['TIME'], df_g['EVENT'], label=s2)
                        #                     kmf.fit(df_g['TIME'] , df_g['EVENT'], label=None)
                        ax.set_title('%s, %s' % (g, s1))
                        kmf.plot(ax=ax)
