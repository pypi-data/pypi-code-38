__author__ = 'diegopinheiro'
__email__ = 'diegompin@gmail.com'
__github__ = 'https://github.com/diegompin'


import numpy as np
from maracatu.src.plotting.plot_base import PlotBase
from maracatu.src.base.parameters import Parameter
from maracatu.src.statistics.base.joints import Joint


class Heatmap(PlotBase):

    def __init__(self):
        super().__init__()

    def get_par_plot(self):
        par_plot = super().get_par_plot()
        return par_plot

    def plot(self, pyx, par_plot=None, fig=None, ax=None, **kwargs):
        fig, ax, par_plot = super().plot(pyx, par_plot, fig, ax)

        # xs = df.index.get_level_values(0).unique()
        # ys = df.index.get_level_values(1).unique()
        # pyx = df.values.reshape(len(xs), len(ys))
        # pyx = np.nan_to_num(pyx)
        # pyx = pyx.T

        par_plot_base = {
            'xticklabels.heatmap': True
        }
        par_plot_base.update(par_plot)

        par_cmap = self.get_par(par_plot_base, 'cmap', self.plt.get_cmap('jet'))
        # par_cmap = self.get_par(par_plot, 'cmap', self.plt.get_cmap('viridis'))
        mat = ax.matshow(pyx, aspect='auto', origin='lower', cmap=par_cmap)

        par_clim = self.get_par(par_plot_base, 'clim')
        if par_clim:
            mat.set_clim(par_clim[0], par_clim[1])

        pxy_max = pyx.max()
        pxy_min = pyx.min()

        tick_loc = [pxy_min, (pxy_max + pxy_min) / 2, pxy_max]
        c = fig.colorbar(mat, ax=ax, ticks=tick_loc, format='%.2f')
        c.ax.tick_params(labelsize=20)

        self.configure_ax(ax, par_plot_base)
        self.configure_fig(fig, par_plot_base)

        return fig, ax, mat, par_plot_base


class HeatmapDataFrame(Heatmap):

    def __init__(self):
        super().__init__()

    def plot(self, data, par_plot=None, fig=None, ax=None, **kwargs):
        par_xvar = par_plot['xvar']
        par_yvar = par_plot['yvar']
        par_xbins = par_plot['xbins']
        par_ybins = par_plot['ybins']
        xticklabels = Parameter.get_par(par_plot, 'xticklabels', par_xbins)
        yticklabels = Parameter.get_par(par_plot, 'yticklabels', par_ybins)

        df_freq = Joint.get_hist2d(data, xvar=par_xvar, xbins=par_xbins, yvar=par_yvar, ybins=par_ybins)
        df_freq = df_freq['p']
        # xs = df_freq.index.get_level_values(0).unique()
        # ys = df_freq.index.get_level_values(1).unique()
        #TODO CRITICAL!!! Not sure if it is solving the problem!!!
        xs = par_xbins
        ys = par_ybins
        # print(len(xs))
        # print(xs)
        # print(len(ys))
        # print(ys)

        pyx = df_freq.values.reshape(len(xs), len(ys))
        pyx = np.nan_to_num(pyx)
        pyx = pyx.T

        par_plot_base = {
            'xlabel.size': 25,
            'ylabel.size': 25,
            'fig.figsize': (7, 5),
            'ax.ticks.labelsize': 25,
            'xticklabels': xticklabels,
            'xticklabels.formatter': '%.2f',
            'yticklabels': yticklabels,
            'yticklabels.formatter': '%.2f',
        }

        par_plot_base.update(par_plot)

        fig, ax, mat, par_plot_base = super().plot(pyx, par_plot_base, fig, ax)

        return fig, ax, mat, par_plot_base
