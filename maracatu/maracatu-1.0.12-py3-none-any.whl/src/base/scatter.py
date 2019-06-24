"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

from maracatu.src.base.plot_base import PlotBase
# from dataintensive.src import BinsDataFrame
# from dataintensive.src import Parameter
# from dataintensive.src import Correlation


class Scatter(PlotBase):

    def __init__(self):
        super().__init__()

    def plot(self, df, par_plot=None, fig=None, ax=None, **kwargs):
        fig, ax, par_plot = super().plot(df, par_plot, fig, ax, **kwargs)

        par_alpha = self.get_par(par_plot, 'alpha', 1)
        ax.set_alpha(par_alpha)

        par_xvar = self.get_par(par_plot, 'xvar', 'X')
        par_yvar = self.get_par(par_plot, 'yvar', 'Y')

        ax.scatter(df[par_xvar], df[par_yvar], alpha=par_alpha)

        # ax.scatter(df['X'], df['Y'], alpha=par_alpha)

        self.configure_ax(ax, par_plot)
        self.configure_fig(fig, par_plot)

        return fig, ax, par_plot
#
#
# class ScatterDataFrame(Scatter):
#
#     def __init__(self):
#         super().__init__()
#
#     def plot(self, df, par=None, fig=None, ax=None, **kwargs):
#         par_xvar = par['xvar']
#         par_yvar = par['yvar']
#
#         # df = df.rename(columns={par_xvar: 'X', par_yvar: 'Y'})
#         # df.loc[:, 'X'] = df[par_xvar]
#         # df.loc[:, 'Y'] = df[par_yvar]
#
#         return super().plot(df, par, fig, ax, **kwargs)
#
#
# class ScatterResiduals(object):
#
#     def __init__(self):
#         super().__init__()
#         self.plotter = ScatterDataFrame()
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
#             'alpha': .2,
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