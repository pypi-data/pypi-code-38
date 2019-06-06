# import matplotlib
# # matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import numpy as np
# import seaborn as sns
# import colours

plt.style.use('ggplot')

class Results:
    """
    
    This class defines a results object that is created at the end of running a genetic algorithm simulation.

    
    """
    def __init__(self):
        
    

        self.trial_N = None
        self.results_folder = None
        self.gene_names = None

        self.epochs = 0

        # saves additional data that is defined in the evaluation function
        self.data = {"history": [],
                     "fitness": [],
                     "genes": [],
                     "diversity": [],
                     "average_diversity": []}
        # All are lists of lists. The inner list will contain the values, and the outer list will represent each epoch
        # history: the individuals at each epoch
        # genes: a dictionary with each gene as a key. The corresponding values are that of the genes at each epoch
        # fitness: the fitness scores of each individual at each epoch

    def __gene_mins(self, gene):
        return [min(g[gene]) for g in self.data["genes"]]

    def __gene_maxs(self, gene):
        return [max(g[gene]) for g in self.data["genes"]]

    def gene_median(self, gene):
        """
         Returns a list of the median value of the specified gene in each generation
        """
        return [np.median(g[gene]) for g in self.data["genes"]]

    def gene_global_min(self, gene):
        """
        Returns the minimum value of the specified gene across all individuals in the genetic algorithm
        """
        return min(self.__gene_mins(gene))

    def gene_global_max(self, gene):
        """
        Returns the maximum value of the specified gene across all individuals in the genetic algorithm
        """
        return max(self.__gene_maxs(gene))

    def fitness_maxs(self):
        """
        Returns a list with the maximum fitness in each generation
        """
        return [max(f) for f in self.data["fitness"]]

    def fitness_mins(self):
        """
        Returns a list with the minimum fitness in each generation
        """
        return [min(f) for f in self.data["fitness"]]

    def fitness_global_min(self):
        """
        Returns the minimum fitness across all individuals in the genetic algorithm
        """
        return min(self.fitness_mins())

    def fitness_global_max(self):
        """
        Returns the maximum fitness across all individuals in the genetic algorithm
        """
        return max(self.fitness_maxs())

    def index_mins(self):
        return np.argmin(self.data['fitness'], axis = 1)

    def index_maxs(self):
        return np.argmax(self.data['fitness'], axis = 1)

    def create_fitness_df(self):
        pass

    def __calculate_limits(self, gene, margin = 0, i = 0):
        center = self.gene_median(gene)[-1]

        gene_maxs = max(self.__gene_maxs(gene)[i:])
        gene_mins = min(self.__gene_mins(gene)[i:])

        diameter = max(abs(gene_maxs - center), abs(gene_mins - center))
        if not isinstance(margin, int):
            margin = margin[i]

        min_val = center - (1 + margin) * diameter
        max_val = center + (1 + margin) * diameter

        return min_val, max_val


    def __draw(self, i, ax, x_gene, y_gene, s, alpha, cmap, fmin, fmax, bounds, optimum, os, o_front, om, oc):
        x = self.data["genes"][i][x_gene]
        y = self.data["genes"][i][y_gene]
        fitness_score = self.data["fitness"][i]

        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylim(bounds[2], bounds[3])

        ax.scatter(x, y, c = fitness_score, s = s, alpha = alpha, cmap = cmap, vmin = fmin, vmax = fmax)

        if len(optimum) > 0 and o_front is True:
            ax.scatter(optimum[0], optimum[1], s=os, marker=om, c=oc,)


    def __draw_inset(self, i, ax1, ax2, x_gene, y_gene, s, alpha, cmap, fmin, fmax, bounds, optimum, os, o_front, om, oc, inset, scale = 0.1):

        self.__draw(i, ax1, x_gene, y_gene, s, alpha, cmap, fmin, fmax, bounds, optimum, os, o_front, om, oc)
        # set up the bounds for the inset
        if inset is True:
            x_min, x_max = self.__calculate_limits(x_gene, margin = [scale - 1])
            y_min, y_max = self.__calculate_limits(y_gene, margin = [scale - 1])
        else:
            x_min = inset[0]
            x_max = inset[1]
            y_min = inset[2]
            y_max = inset[3]

        ax2.set_xlim(x_min, x_max)
        ax2.set_ylim(y_min, y_max)

        x = self.data["genes"][i][x_gene]
        y = self.data["genes"][i][y_gene]
        fitness_score = self.data["fitness"][i]

        mark_inset(ax1, ax2, loc1=2, loc2=3, ec='k')

        ax2.scatter(x, y, c=fitness_score, s=s, alpha=alpha, cmap=cmap, vmin = fmin, vmax = fmax)
        if len(optimum) > 0 and o_front is True:
            ax1.scatter(optimum[0], optimum[1], s=os, marker=om, c=oc,)
            ax2.scatter(optimum[0], optimum[1], s=os, marker=om, c=oc, )


    def animate(self, x_gene, y_gene, s = 5, alpha = 0.5, fps = 30, bounds = None, log_scale = False, fmin = None, fmax = None, cmap = cm.rainbow, optimum = [], os = 100, o_front = True, om = '*', oc = 'k', inset = False, scale = 0.1, filename = None):

        """

            **x_gene: string**
                The name of the gene to be plotted on the x axis.

            **y_gene: string**
                The name of the gene to be plotted on the y axis.

            **s: int, (default = 5)**
                Marker size

            **alpha: float, (default = 0.5)**
                Marker transparency

            **fps: int, (default = 30)**
                Frames per second

            **bounds: (default = None)**

            **log_scale: Boolean, (default = False)**
                If true, plots the fitness scores on a log scale.

                .. seealso::

                    :ref:`Fitness on a logscale <fitness_logscale>`

            **fmin: int or float, (default = None)**
                Minimum fitness value shown on the colorbar.

                .. seealso::

                    :ref:`fmin and fmax <fmin-fmax>`

            **fmax: int or float, (default = None)**
                Maximum fitness value shown on the colorbar.

                .. seealso::

                    :ref:`fmin and fmax <fmin-fmax>`

            **cmap: matplotlib colormap, (default = cm.rainbow)**
                Colormap used for the animation.

                .. seealso::

                    :ref:`Colormap <colormap>`


            **optimum: list, (default = [])**
                Allows you to specify and mark optima on the animation.

                .. seealso::

                    :ref:`Marking the optimum <optima>`

            **os: float, (default = 100)**
                Size of markers used to mark the optima.

            **o_front: boolean, (default = True)**

                * if true, the markers used to mark the optima will be in the foreground.

                * if false, the markers will be in the background.

            **om: char, (default = '*')**
                Style of markers used to mark the optima.

            **oc: char, (default = 'k')**
                Color of markers used to mark the optima.

            **inset: boolean or list, (default = False)**

                * if false, there will be no inset

                * if true, there will be an inset marked around the median individual of the final population

                * if list, there will be an inset marked around the bounds [xmin, xmax ymin, ymax]

                .. seealso::

                    :ref:`Inset <inset>`

            **scale: float, (default = 0.1)**
                Only used for a default inset. Dictates the zoom of the inset.

            **filename: string, (default = None)**
                Name the gif will be saved to. By default it is saved as ``<x_gene>_<y_gene>_animation.gif``

                .. note::
                    Specify the name without the ``.gif`` extension.
        """

        plt.clf()

        if inset is False:
            fig = plt.figure(figsize=(6, 5))
            ax1 = fig.add_subplot(111)
        else:
            fig = plt.figure(figsize=(6, 3))
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            ax2.set_xlabel(x_gene)
            ax2.set_ylabel(y_gene)

        fig.subplots_adjust(left=0.12, bottom=0.2, right=0.92, top=0.93, wspace=0.4, hspace=None)
        ax1.set_xlabel(x_gene)
        ax1.set_ylabel(y_gene)

        # Set the bounds of the image
        if bounds is None:
            x_range = self.gene_global_max(x_gene) - self.gene_global_min(x_gene)
            y_range = self.gene_global_max(y_gene) - self.gene_global_min(y_gene)

            bounds = [self.gene_global_min(x_gene) - 0.1 * x_range,
                      self.gene_global_max(x_gene) + 0.1 * x_range,
                      self.gene_global_min(y_gene) - 0.1 * y_range,
                      self.gene_global_max(y_gene) + 0.1 * y_range]

        ax1.set_xlim(bounds[0], bounds[1])
        ax1.set_ylim(bounds[2], bounds[3])

        # plot optimum
        if len(optimum) > 0:
            ax1.scatter(optimum[0], optimum[1], s=os, marker=om, c=oc,)
        if inset:
            ax2.scatter(optimum[0], optimum[1], s=os, marker=om, c=oc, )

        # Set up the colorbar range
        if fmin is None:
            fmin = self.fitness_global_min()

        if fmax is None:
            fmax = self.fitness_global_max()

        if log_scale:
            fmin = np.log(fmin)
            fmax = np.log(fmax)

        # plot invisible points to establish a colorbar
        scat = ax1.scatter([0, 0], [0, 0], c = [fmin, fmax], s = 0, vmin=fmin, vmax=fmax, cmap=cmap)


        cb = plt.colorbar(scat)
        cb.solids.set_edgecolor("face")
        if log_scale:
            cb.set_label("Fitness score (log scale)")
        else:
            cb.set_label("Fitness score")

        if inset is False:
            ani = animation.FuncAnimation(fig, self.__draw, fargs = (ax1, x_gene, y_gene, s, alpha, cmap, fmin, fmax, bounds, optimum, os, o_front, om, oc), frames = self.epochs, interval = 5, repeat = True)
        else:
            ani = animation.FuncAnimation(fig, self.__draw_inset, fargs=(ax1, ax2, x_gene, y_gene, s, alpha, cmap, fmin, fmax, bounds, optimum, os, o_front, om, oc, inset, scale), frames=self.epochs,
                                      interval=5, repeat=True)
        if filename is not None:
            ani.save("{}/{}.gif".format(self.results_folder, filename), writer='imagemagick', fps=fps)
        else:
            ani.save("{}/{}_{}_animation.gif".format(self.results_folder, x_gene, y_gene),
                 writer='imagemagick', fps=fps)

        return ani

    def plot_fitness(self, fname = None):

        """
        Plots the minimum fitness at each generation.

        .. seealso::

            :ref:`sphere demo <sphere-results>`

        """
        plt.figure()
        plt.title("Minimum fitness score")
        plt.xlabel("Epoch")
        plt.ylabel("fitness")
        plt.plot(self.fitness_mins())
        if fname is None:
            plt.savefig(fname = "{}fitness".format(self.results_folder))
        else:
            plt.savefig(fname="{}{}".format(self.results_folder, fname))
        plt.show()

    def plot_diversity(self, gene = None):
        plt.figure()
        plt.title("Diversity")
        plt.plot(self.data["average_diversity"], label = "Average", linewidth = 0.5)
        for gene in self.gene_names:
            gene_div = [div[gene] for div in self.data["diversity"]]
            plt.plot(gene_div, label = gene, linewidth = 0.5)
        plt.legend()
        plt.savefig(fname="{}_diversity".format(self.results_folder))
        plt.show()

    def plot_3d(self, x_gene, y_gene, z_gene):
        pass

    def print_best(self, minimise = True):
        """
        Prints the genes and the fitness score of the best individual.

        .. seealso::

            :ref:`sphere demo <sphere-results>`
        """
        best = False
        for epoch in self.data["history"]:
            for ind in epoch:

                if best == False:
                    best = ind
                else:
                    if minimise:
                        if ind.fitness_score < best.fitness_score:
                            best = ind
                    else:
                        if ind.fitness_score > best.fitness_score:
                            best = ind
        for gene in self.gene_names:
            print(gene + ": {0:4e}".format(best.genes[gene]))
        print("fitness score: {0:4e}".format(best.fitness_score))

    def __draw_correlate(self, i, ax, VAMP_data, Stokes, baseline_colours, bar_colour):

        plt.cla()
        ind = self.index_mins()
        ax.set_xlim([0.97, 1.04])
        ax.set_ylim([0.97, 1.04])
        plt.plot([0.97, 1.04], [0.97, 1.04])

        if 'Q' in Stokes:
            obs_data = VAMP_data.vhvv
            sim_data = self.data["data_Q"][i][ind[i]]
            errors = VAMP_data.vhvverr
            title = "Correlation (Stokes Q)"
            error = self.data["reduced_chi2err_Q"][i][ind[i]]
            ax.scatter(sim_data, obs_data, c=baseline_colours)
            ax.errorbar(sim_data, obs_data, yerr=errors, marker='', linestyle='', alpha=0.8, capsize=0, zorder=0,
                        ecolor=bar_colour)
        if 'U' in Stokes:
            obs_data = VAMP_data.vhvvu
            sim_data = self.data["data_U"][i][ind[i]]
            errors = VAMP_data.vhvvuerr
            error = self.data["reduced_chi2err_U"][i][ind[i]]
            title = "Correlation (Stokes U)"
            ax.scatter(sim_data, obs_data, c=baseline_colours)
            ax.errorbar(sim_data, obs_data, yerr=errors, marker='', linestyle='', alpha=0.8, capsize=0, zorder=0,
                        ecolor=bar_colour)

        if 'Q' in Stokes and 'U' in Stokes:
            title = 'Correlation'
            error = self.data["reduced_chi2err"][i][ind[i]]

        # place a text box in upper left in axes coords
        ax.text(0.05, 0.95, '$\chi^2$ Error: {0:.4f}'.format(error), transform=ax.transAxes, fontsize=14, verticalalignment='top')
        ax.set_title(title)
        ax.set_xlabel("Model Visibility Ratio")
        ax.set_ylabel("Observed Visibility Ratio")

    def correlate(self, VAMP_data, filename=None, Stokes="QU", fps=30):

        fig = plt.figure(figsize=(6, 5))
        ax = fig.add_subplot(111)

        baselines = VAMP_data.blengths
        # only select the baselines that are smaller than the maximum baseline
        baseline_colours = baselines[baselines <= 8]

        scatter_plot = ax.scatter(VAMP_data.vhvv, VAMP_data.vhvv, alpha=0, c=baseline_colours)
        clb = plt.colorbar(scatter_plot, label="Baseline length (m)")
        bar_colour = clb.to_rgba(baseline_colours)

        ani = animation.FuncAnimation(fig, self.__draw_correlate,
                                      fargs=(ax, VAMP_data, Stokes, baseline_colours, bar_colour),
                                      frames=self.epochs, interval=5, repeat=True)
        if filename is not None:
            ani.save("{}/{}.gif".format(self.results_folder, filename), writer='imagemagick', fps=fps)
        else:
            ani.save("{}/Correlation_{}.gif".format(self.results_folder, Stokes),
                     writer='imagemagick', fps=fps)

    def __draw_vis(self, i, ax, VAMP_data, Stokes, baseline_colours, bar_colour, ylim):

        plt.cla()
        ind = self.index_mins()
        ax.set_ylim(ylim)

        if 'Q' in Stokes:
            obs_data = VAMP_data.vhvv
            sim_data = self.data["data_Q"][i][ind[i]]
            errors = VAMP_data.vhvverr
            title = "Correlation (Stokes Q)"
            error = self.data["reduced_chi2err_Q"][i][ind[i]]

        if 'U' in Stokes:
            obs_data = VAMP_data.vhvvu
            sim_data = self.data["data_U"][i][ind[i]]
            errors = VAMP_data.vhvvuerr
            title = "Correlation (Stokes U)"
            error = self.data["reduced_chi2err_U"][i][ind[i]]

        scatter_plot = ax.scatter(VAMP_data.bazims, obs_data, marker='x', c=baseline_colours, label='observed')
        scatter_plot = ax.scatter(VAMP_data.bazims, sim_data, marker='o', c=baseline_colours, label='model')
        ax.errorbar(VAMP_data.bazims, obs_data, yerr=errors, marker='', linestyle='', alpha=0.8, capsize=0, zorder=0,
                    ecolor=bar_colour)

        # place a text box in upper left in axes coords
        ax.text(0.05, 0.95, '$\chi^2$ Error: {0:.4f}'.format(error), transform=ax.transAxes, fontsize=14, verticalalignment='top')
        ax.set_title(title)
        ax.set_xlabel("Polarised Visibility Ratio")
        ax.set_ylabel("Baseline Azimuth Angle (radians)")

    def vis(self, VAMP_data, filename=None, Stokes="Q", fps=30, ylim=[0.96, 1.04]):

        fig = plt.figure(figsize=(6, 5))
        ax = fig.add_subplot(111)

        baselines = VAMP_data.blengths
        # only select the baselines that are smaller than the maximum baseline
        baseline_colours = baselines[baselines <= 8]

        scatter_plot = ax.scatter(VAMP_data.vhvv, VAMP_data.vhvv, alpha=0, c=baseline_colours)
        clb = plt.colorbar(scatter_plot, label="Baseline length (m)")
        bar_colour = clb.to_rgba(baseline_colours)

        ani = animation.FuncAnimation(fig, self.__draw_vis,
                                      fargs=(ax, VAMP_data, Stokes, baseline_colours, bar_colour, ylim),
                                      frames=self.epochs, interval=5, repeat=True)
        if filename is not None:
            ani.save("{}/{}.gif".format(self.results_folder, filename), writer='imagemagick', fps=fps)
        else:
            ani.save("{}/visibilities_{}.gif".format(self.results_folder, Stokes),
                     writer='imagemagick', fps=fps)