"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""
import numpy as np
import pandas as pd

from maracatu.src.base.plot_base import PlotBase
from itertools import cycle


class ErrorBar(PlotBase):

    def __init__(self):
        super().__init__()

    def plot(self, data, par=None, fig=None, ax=None, **kwargs):
        fig, ax, par = super().plot(data, par, fig, ax)

        if not isinstance(data, list):
            data = [data]

        par_color = self.get_par(par, 'color', default=PlotBase.colors, transform=cycle)
        par_marker = self.get_par(par, 'marker', default=PlotBase.markers, transform=cycle)
        par_legend = self.get_par(par, 'legend', transform=cycle)

        for df in data:
            # xs = df.index.get_level_values(0).unique()
            # ys = df.index.get_level_values(0).unique()
            # err_data = df.loc(axis=0)[xs, :]
            # err_data = df.loc(axis=0)[:'X']

            label = ''
            if par_legend:
                label = next(par_legend)

            par_linewidth = self.get_par(par, 'linewidth', 3)
            par_alpha = self.get_par(par, 'alpha', .7)

            plot = ax.errorbar(x=np.array(df.loc[:'X']),
                               y=np.array(df.loc[:, 'Y']),
                               yerr=[np.array(df.loc[:, 'Y_u']),  np.array(df.loc[:, 'Y_l'])],
                               fmt='o',
                               # ecolor='r',
                               color=next(par_color),
                               linewidth=par_linewidth,
                               # linestyle=':',
                               # mew=1,
                               ms=7,
                               alpha=par_alpha,
                               label=label,
                               capthick=2,
                               capsize=10
                               )


        self.configure_ax(ax, par)
        self.configure_fig(fig, par)

        return fig, ax, par

#
# class ErrorBar(PlotBase):
#
#     def __init__(self):
#         super().__init__()
#
#     def plot(self, data, par=None, fig=None, ax=None, **kwargs):
#         fig, ax, par = super().plot(data, par, fig, ax)
#
#         if not isinstance(data, list):
#             data = [data]
#
#         par_color = self.get_par(par, 'color', default=PlotBase.colors, transform=cycle)
#         par_marker = self.get_par(par, 'marker', default=PlotBase.markers, transform=cycle)
#         par_legend = self.get_par(par, 'legend', transform=cycle)
#
#         for df in data:
#             xs = df.index.get_level_values(0).unique()
#             # ys = df.index.get_level_values(0).unique()
#             err_data = df.loc(axis=0)[xs, :]
#
#             label = ''
#             if par_legend:
#                 label = next(par_legend)
#
#             par_linewidth = self.get_par(par, 'linewidth', 3)
#             par_alpha = self.get_par(par, 'alpha', .7)
#
#             plot = ax.errorbar(x=xs,
#                                y=err_data['p'],
#                                yerr=(err_data['ci_u'] - err_data['ci_l']) / 2,
#                                fmt='o',
#                                # ecolor='r',
#                                color=next(par_color),
#                                linewidth=par_linewidth,
#                                # linestyle=':',
#                                # mew=1,
#                                ms=7,
#                                alpha=par_alpha,
#                                label=label,
#                                capthick=2,
#                                capsize=10
#                                )
#
#
#         self.configure_ax(ax, par)
#         self.configure_fig(fig, par)
#
#         return fig, ax, par
