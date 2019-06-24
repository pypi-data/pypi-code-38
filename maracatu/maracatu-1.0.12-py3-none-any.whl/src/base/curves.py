"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

from itertools import cycle
from maracatu.src.base.plot_base import PlotBase
# import pandas as pd
# from dataintensive.src import Joint
# from dataintensive.src import BinsDataFrame
# from dataintensive.src import Parameter
# from dataintensive.src import Correlation


class Curves(PlotBase):
    '''

    '''

    def __init__(self):
        super().__init__()

    def get_par_plot(self):
        par_plot = super().get_par_plot()
        return par_plot

    def plot(self, data, par_plot=None, fig=None, ax=None, **kwargs):
        '''
        plot() -> fig, ax, par_plot
        :param data:
        :param par_plot:
        :param fig:
        :param ax:
        :param kwargs:
        :return:
        '''
        fig, ax, par_plot = super().plot(data, par_plot, fig, ax)

        if not isinstance(data, list):
            data = [data]

        par_color = self.get_par(par_plot, 'color', default=PlotBase.colors, transform=cycle)
        par_marker = self.get_par(par_plot, 'marker', default=PlotBase.markers, transform=cycle)
        par_legend = self.get_par(par_plot, 'legend', transform=cycle)
        for df in data:
            label = ''
            if par_legend:
                label = next(par_legend)

            par_linewidth = self.get_par(par_plot, 'linewidth', 2)
            par_linestyle = self.get_par(par_plot, 'linestyle', '-')
            par_alpha = self.get_par(par_plot, 'alpha', .8)

            ax.plot(df['X'], df['Y'],
                    linewidth=par_linewidth,
                    linestyle=par_linestyle,
                    alpha=par_alpha,
                    color=next(par_color),
                    marker=next(par_marker),
                    label=label,
                    **kwargs)

        self.configure_ax(ax, par_plot)
        self.configure_fig(fig, par_plot)

        return fig, ax, par_plot



#
#
# class CurvesDataFrame(Curves):
#
#     def __init__(self):
#         super().__init__()
#
#     def get_par_plot(self):
#         par_plot = super().get_par_plot()
#         return par_plot
#
#     def plot(self, df, par_plot=None, fig=None, ax=None, **kwargs):
#         # fig, ax, par_plot = super().plot(pyx, par_plot, fig, ax)
#         par_xvar = par_plot['xvar']
#         par_yvar = par_plot['yvar']
#         par_xbins = par_plot['xbins']
#         par_ybins = par_plot['ybins']
#
#         df_freq = Joint.get_hist2d(df, xvar=par_xvar, xbins=par_xbins, yvar=par_yvar, ybins=par_ybins)
#         df_freq = df_freq['p']
#
#         par_slices = self.get_par(par_plot, 'slices', par_ybins)
#         par_xbins = par_plot['xbins']
#
#         par_plot_base = {
#             # 'legend': ['$t$ = %d' % s for s in par_slices],
#             # 'legend.loc': 'upper left',
#             # 'legend.fontsize': 16,
#             # 'fig.figsize': (7,5),
#             'xticklabels.heatmap': False
#
#         }
#         par_plot.update(par_plot_base)
#
#         dfs = []
#         for s in par_slices:
#             dfs.append(pd.DataFrame({'x': par_xbins, 'y': df_freq.loc[:, s]}))
#
#         fig, ax, par_plot = super().plot(dfs, par_plot, fig, ax)
#         return fig, ax, par_plot
#
#
# class CurvesResiduals(object):
#
#     def __init__(self):
#         super().__init__()
#         self.plotter = CurvesDataFrame()
#
#     def plot(self, df, par_plot=None, fig=None, ax=None, **kwargs):
#         par_xvar = par_plot['xvar']
#         par_yvar = par_plot['yvar']
#
#         xbins, ybins = BinsDataFrame().get(df, par_plot)
#         xbins_label, ybins_label = xbins, ybins
#
#         df_ori = df
#         df = df_ori
#
#         par_residuals = Parameter.get_par(par_plot, 'residuals', False)
#         if par_residuals:
#             df = Correlation.get_df(df, x=par_xvar, y=par_yvar)
#
#             xbins_label, ybins_label = BinsDataFrame().get(df_ori, par_plot)
#
#         par_base = {
#             'xbins': xbins,
#             'ybins': ybins,
#             'xticklabels': xbins_label,
#             # 'xticklabels.formatter': '%.2f',
#             # 'xticklabels.maxnlocator': 4,
#             'yticklabels': ybins_label,
#             # 'yticklabels.formatter': '%d',
#             # 'yticklabels.maxnlocator': 4,
#         }
#
#         par_base.update(par_plot)
#
#         fig, ax, par = self.plotter.plot(df, par_base)
#
#         return fig, ax, par_base
