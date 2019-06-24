"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

from itertools import cycle
import matplotlib.pyplot as plt
# import matplotlib as mpl
# mpl.use('agg')
# mpl.rc_params
# figure.max_open_warning

from maracatu.src.base.parameters import Parameter


class PlotBase(object):

    def __init__(self, par_plot=None):
        self.plt = plt
        self.par_plot = par_plot

    markers = ['D', 'o', 'x','s', '^', 'd', 'h', '+', '*', ',', '.', '1', 'p', '3', '2', '4', 'H', 'v', '8',
               '<', '>']
    # colors = ['g', 'y', 'r', 'b', 'k', 'm', 'c']\

    colors = ['#1f77b4', '#ff7f0e',  '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    def get_fig_ax(self):
        pass

    def plot(self, data, par_plot, fig, ax, **kwargs):
        if ax is None and fig is None:
            fig, ax = plt.subplots(1, 1)

        if par_plot is None:
            par_plot = dict()
        par_plot.update(self.get_par_plot())

        return fig, ax, par_plot

    def get_par_plot(self):
        par_plot = {

        }
        return par_plot

    def configure_ax(self, ax, par_plot):
        self.configure_axes_ticks(ax, par_plot)
        self.configure_axes_label(ax, par_plot)
        self.configure_grid(ax, par_plot)
        self.configure_title(ax, par_plot)
        self.configure_legend(ax, par_plot)

        par_xscale = self.get_par(par_plot, 'xscale')
        if par_xscale:
            ax.set_xscale(par_xscale)

        par_yscale = self.get_par(par_plot, 'yscale')
        if par_yscale:
            ax.set_yscale(par_yscale)

        par_xlim = self.get_par(par_plot, 'xlim')
        if par_xlim:
            ax.set_xlim(par_xlim)

        par_ylim = self.get_par(par_plot, 'ylim')
        if par_ylim:
            ax.set_ylim(par_ylim)

    def configure_label_name(self, ax, par_plot, name):
        par_label = PlotBase.get_par(par_plot, name)
        if par_label:
            par_labelsize = PlotBase.get_par(par_plot, '%s.size' % name, 25)
            f = getattr(ax, 'set_%s' % name)
            f(par_label, fontsize=par_labelsize)

    def configure_axes_label(self, ax, par_plot):
        self.configure_label_name(ax, par_plot, 'xlabel')
        self.configure_label_name(ax, par_plot, 'ylabel')

    def configure_legend(self, ax, par_plot):
        par_legend = self.get_par(par_plot, 'legend', transform=cycle)
        if par_legend:
            par_loc = self.get_par(par_plot, 'legend.loc')
            par_fontsize = self.get_par(par_plot, 'legend.fontsize', default=12)
            par_legent_title = self.get_par(par_plot, 'legend.title')
            ax.legend(title=par_legent_title, loc=par_loc, fontsize=par_fontsize)

    def configure_title(self, ax, par_plot):
        par_titles = self.get_par(par_plot, 'title')
        par_titlesize = self.get_par(par_plot, 'title.size', default=25)
        if par_titles:
            if type(par_titles) is cycle:
                ax.set_title(next(par_titles), fontsize=par_titlesize)
            else:
                ax.set_title(par_titles, fontsize=par_titlesize)

    def configure_grid(self, ax, par_plot):
        par_grid = self.get_par(par_plot, 'grid')
        if par_grid:
            par_grid_alpha = self.get_par(par_plot, 'grid.alpha', 1)
            par_grid_which = self.get_par(par_plot, 'grid.which', 'both')
            par_grid_axis = self.get_par(par_plot, 'grid.axis', 'both')
            par_grid_zorder = self.get_par(par_plot, 'grid.zorder', 1)
            ax.grid(alpha=par_grid_alpha, which=par_grid_which, axis=par_grid_axis, zorder=par_grid_zorder)

    def configure_axes_ticks(self, ax, par_plot):
        ax.xaxis.set_ticks_position('bottom')

        par_xticklabels = self.get_par(par_plot, 'xticklabels')
        par_xticklabels_heatmap = self.get_par(par_plot, 'xticklabels.heatmap')

        if par_xticklabels is not None:
            if par_xticklabels_heatmap:
                xticks = ax.get_xticks()
                xlabels = [0] + [par_xticklabels[int(xticks[i])] for i in range(len(xticks) - 1) if xticks[i] >= 0]
                xticklabels_formatter = self.get_par(par_plot, 'xticklabels.formatter')
                if xticklabels_formatter:
                    # print(xlabels)
                    xlabels = [xticklabels_formatter % l for l in xlabels]
                    ax.set_xticklabels([''] + list(xlabels))
                ax.set_xticklabels(xlabels, rotation='-45', minor=False)

            # else:
            #     xticks = ax.get_xticks()
            #     # xlabels = par_xticklabels
            #     # ax.set_xticks(xlabels)
            #     # xlabels = ax.get_xticks()
            #     # ax.set_xticklabels(xlabels, rotation='horizontal', minor=False)
            #     xticklabels_formatter = self.get_par(par_plot, 'xticklabels.formatter')
            #     if xticklabels_formatter:
            #         xlabels = ax.get_xticks(minor=False)
            #         xlabels = [xticklabels_formatter % l for l in xlabels]
            #         ax.set_xticklabels(xlabels, minor=False)

            par_xticklabels_maxnlocator = self.get_par(par_plot, 'xticklabels.maxnlocator')
            if par_xticklabels_maxnlocator:
                ax.xaxis.set_major_locator(plt.MaxNLocator(par_xticklabels_maxnlocator))

        par_yticklabels = self.get_par(par_plot, 'yticklabels')
        if par_yticklabels is not None:
            if par_xticklabels_heatmap:
                yticks = ax.get_yticks()
                ylabels = [0] + [par_yticklabels[int(yticks[i])] for i in range(len(yticks) - 1) if yticks[i] >= 0]
                yticklabels_formatter = self.get_par(par_plot, 'yticklabels.formatter')
                if yticklabels_formatter:
                    ylabels = [yticklabels_formatter % l for l in ylabels]
                    ax.set_yticklabels([''] + list(ylabels))
                ax.set_yticklabels(ylabels, rotation='0', minor=False)

        ax.tick_params(axis='both', which='major', labelsize=20)

    @staticmethod
    def set_par(par_plot, name, func, default=None, transform=None):
        Parameter.set_par(par_plot, name, func, default, transform)

    @staticmethod
    def get_par(par_plot, name, default=None, transform=None):
        return Parameter.get_par(par_plot, name, default, transform)

    def configure_fig(self, fig, par_plot):
        # Figure params
        self.configure_figure_title(fig, par_plot)
        self.configure_figure_tight_layout(fig, par_plot)
        par_figsize = PlotBase.get_par(par_plot, 'fig.figsize', (7, 5))
        fig.set_size_inches(par_figsize)
        file_output = self.get_par(par_plot, 'file_output')
        if file_output:
            self.plt.savefig(file_output)
            self.plt.close()

        # mpl.rcParams['pdf.use14corefonts'] = True
        # mpl.rcParams['pdf.fonttype'] = 42

    def configure_figure_title(self, fig, par_plot):
        par_figtitle = self.get_par(par_plot, 'fig.suptitle')
        if par_figtitle:
            par_figtitle_fontsize = self.get_par(par_plot, 'fig.suptitle.fontsize', 14)
            # TODO unused parameter
            par_figtitle_fontweight = self.get_par(par_plot, 'fig.suptitle.fontweight', 'normal')
            fig.suptitle(par_figtitle, fontsize=par_figtitle_fontsize)

    def configure_figure_tight_layout(self, fig, par_plot):
        par_figtight_layout = self.get_par(par_plot, 'fig.tight_layout', True)
        if par_figtight_layout:
            par_figrect = self.get_par(par_plot, 'fig.tight_layout.rect')
            par_figwpad = self.get_par(par_plot, 'fig.tight_layout.w_pad')
            par_fighpad = self.get_par(par_plot, 'fig.tight_layout.h_pad')
            par_figpad = self.get_par(par_plot, 'fig.tight_layout.pad', 0)
            fig.tight_layout(rect=par_figrect, w_pad=par_figwpad, h_pad=par_fighpad,
                             pad=par_figpad)