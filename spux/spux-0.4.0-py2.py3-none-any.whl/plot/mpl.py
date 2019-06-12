# # # # # # # # # # # # # # # # # # # # # # # # # #
# Plotting class based on MatPlotLib (PyLab)
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from .mpl_utils import matplotlib, brighten, figname
from .mpl_palette_pf import palette
from ..io.formatter import plain
from ..io import loader
from ..io import dumper

import numpy
import scipy
import pylab
import pandas
import os
import textwrap
#import suftware

# register additional palette colors
for name, color in palette ['colors'] .items ():
    matplotlib.colors.ColorConverter.colors [name] = color

class MatPlotLib (object):
    """Plotting class based on MatPlotLib (PyLab)."""

    # constructor
    def __init__ (self, samples=None, infos=None,
                  prior=None, error=None, exact=None,
                  dataset=None, datasets=None,
                  configfile='config.dat', setupfile='setup.dat', reportdir='report',
                  burnin=None, tail=None, chains=None, replicates=False, names=None, deterministic=False, transform=None,
                  typesfiles={'parameters' : 'parameters.types', 'predictions' : 'predictions.types'},
                  title=False, legend=True, autosave=True, verbosity=0, formats=["eps", "png", "pdf", "svg"],
                  kdelib='scipy'):

        print (' :: Initializing MatPlotLib plotter...')

        # store loaded results
        self.samples = samples
        self.infos = infos

        # store auxiliary information
        self.exact = exact

        # plotting options
        self.title = title
        self.legend = legend
        self.autosave = autosave
        self.verbosity = verbosity
        self.kdelib = kdelib

        # store report directory
        self.reportdir = reportdir

        # load SPUX config from the specified 'configfile'
        if os.path.exists (os.path.join (reportdir, dumper.prefixname (configfile))):

            print ('  : -> Loading SPUX config from: %s' % dumper.prefixname (configfile))
            self.sampler = loader.load (dumper.prefixname (configfile), reportdir, self.verbosity)

            if hasattr (self.sampler, 'prior'):
                self._prior = self.sampler.prior
            else:
                self._prior = None

            self.replicates = self.sampler.likelihood.name == 'Replicates'
            if self.replicates:
                self.names = self.sampler.likelihood.names
                self._dataset = None
                self._datasets = self.sampler.likelihood.datasets
                self._error = self.sampler.likelihood.likelihood.error
            else:
                self.names = ['dataset']
                self._dataset = self.sampler.likelihood.dataset
                self._datasets = {'dataset' : self._dataset}
                self._error = self.sampler.likelihood.error
            self.deterministic = self.sampler.likelihood.name == 'Direct'
            self.chains = self.sampler.chains
            self.transform = self._error.transform if hasattr (self._error, 'transform') else None

        # if the specified 'configfile' does not exist, determite SPUX config from constructor arguments
        else:

            print ('  : -> Determine SPUX config from constructor arguments:')

            self.sampler = None
            self._prior = prior
            self._dataset = dataset
            self._datasets = datasets
            self._error = error
            self.replicates = replicates
            self.names = names
            self.deterministic = deterministic
            self.chains = chains
            self.transform = transform

        # types
        self.types = {}
        for key, typesfile in typesfiles.items ():
            self.types [key] = loader.read_types_of_keys (typesfile) if typesfile is not None else None

        # labels
        if prior is not None or self.samples is not None:
            self.labels = list (prior.labels if prior is not None else self.samples.columns.values)
        else:
            self.labels = None

        # load SPUX setup from the specified 'setupfile' (available only after sampling)
        if os.path.exists (os.path.join (reportdir, dumper.prefixname (setupfile))):

            print ('  : -> Loading SPUX setup from: %s' % dumper.prefixname (setupfile))
            self.setup = loader.load (dumper.prefixname (setupfile), reportdir, self.verbosity)

        else:

            self.setup = None

        # batches
        if self.infos is not None:
            self.batches = len (self.infos)
        elif self.samples is not None and self.chains is not None:
            self.batches = len (samples) // self.chains
        else:
            self.batches = None

        # determine burnin
        if self.samples is not None and burnin is None:
            self.burnin = self.samples.index [0] // self.chains
        else:
            self.burnin = burnin

        # determine tail
        if self.samples is not None and tail is None:
            self.tail = self.samples.index [0] // self.chains
        else:
            self.tail = tail

        # formats
        self.formats = formats

        # indices
        self.indices = self.tail + numpy.arange (self.batches) if self.batches is not None else None

        # infos structure
        if self.infos is not None and len (self.infos) > 0:
            dumper.infos (self.sampler, self.infos [-1], directory = self.reportdir)

        # MAP
        self._MAP = None

        # metrics
        self._metrics = {}

        print ('  : -> Samples:', len (self.samples) if self.samples is not None else 'none')
        print ('  : -> Chains:', self.chains)
        print ('  : -> Infos:', len (self.infos) if self.infos is not None else 'none')
        print ('  : -> Batches:', self.batches)
        if self.burnin is not None:
            print ('  : -> Burn-in:', self.burnin)
        if self.indices is not None:
            print ('  : -> Indices:', self.indices [0], '-', self.indices [-1])

    # plot line and range and return handles for legend
    def line_and_range (self, xs, lower, middle, upper, color="k", alpha=0.6, middlealpha=1, style="-", linewidth=1, marker=None, rangestyle='-', logx=0, logy=0, merged=1, fill=True):
        """Plot line and range and return handles for legend."""

        if fill:
            pylab.fill_between (xs, lower, upper, facecolor=brighten(color), edgecolor=brighten(color), alpha=alpha, linewidth=0)
        edgewidth = 0.3 * linewidth
        area, = pylab.plot (xs, lower, rangestyle, color=color, alpha=alpha, linewidth=edgewidth)
        pylab.plot (xs, upper, rangestyle, color=color, alpha=alpha, linewidth=edgewidth)
        if fill:
            area, = pylab.plot ([], [], color=brighten(color), alpha=alpha, linewidth=10)

        if middle is not None:
            line, = pylab.plot (xs, middle, style, color=color, linewidth=linewidth, marker=marker, markersize=10, alpha=middlealpha, markeredgewidth=linewidth)
        else:
            print(":: WARNING: MAP is likely None. Did we run plot.MAP()? Skipping line plot.")
            line = None

        if logx:
            pylab.xscale ("log")
        if logy:
            pylab.yscale ("log")

        if merged:
            handles = (area, line)
        else:
            handles = (line, area)

        return handles

    # custom legend handles (only, no plotting) for line and range plots
    def line_and_range_handles (self, color="k", alpha=0.6, middlealpha=1, style="-", linewidth=1, marker=None, rangestyle='-', merged=1, fill=True):
        """Plot line and range and return handles for legend."""

        if fill:
            area, = pylab.plot ([], [], color=brighten(color), alpha=alpha, linewidth=10)
        else:
            edgewidth = 0.3 * linewidth
            area, = pylab.plot ([], [], rangestyle, color=color, alpha=alpha, linewidth=edgewidth)
        line, = pylab.plot ([], [], style, color=color, linewidth=linewidth, marker=marker, markersize=10, alpha=middlealpha, markeredgewidth=linewidth)

        if merged:
            handles = (area, line)
        else:
            handles = (line, area)

        return handles

    # save figure
    def save (self, save, caption = None):
        """Save figure, additionally saving the optional caption in a corresponding .cap file."""

        if isinstance (self.formats, list):
            base_name = save [:-4]
            print ('  : -> Saving to:', base_name + '.{' + ','.join (self.formats) + '}')
            for format in self.formats:
                pylab.savefig (base_name + "." + format, bbox_inches="tight")
        else:
            print ('  : -> Saving to:', save)
            pylab.savefig (save, bbox_inches="tight")

        if caption is not None:
            print ('  : -> Saving caption to:', save [:-4] + '.cap')
            dumper.text (textwrap.dedent (caption), save [:-4] + '.cap', directory = None)

    # show figures
    def show (self):
        """Show figures."""

        pylab.show()

    # compute extents
    def extents (self, x, y, alpha=0.99, prior=True):
        """Compute extents."""

        xv = self.samples [x]
        yv = self.samples [y]

        # compute plotting extents
        xmin = xv.min ()
        xmax = xv.max ()
        ymin = yv.min ()
        ymax = yv.max ()

        # include prior support intervals, if available
        if prior and self._prior is not None:
            intervals = self._prior.intervals (alpha)
            xmin = min (intervals [x] [0], xmin)
            xmax = max (intervals [x] [1], xmax)
            ymin = min (intervals [y] [0], ymin)
            ymax = max (intervals [y] [1], ymax)

        return xmin, xmax, ymin, ymax

    def dataset (self, dataset=None, labels=None, name='dataset', legend=False, color='dimgray', scientific=True, columns=3, save=None, suffix='', frame=0):
        """Plot all specified labels of a single specified dataset in subplots."""

        if dataset is None:
            if self._dataset is not None:
                dataset = self._dataset
            else:
                print ('  : -> SKIPPING: No dataset is specified in arguments or in the constructor.')
                return

        if labels is None:
            labels = dataset.columns.values

        plots = len (labels)
        rows = numpy.ceil (plots / columns)
        if not frame:
            print (' :: Plotting dataset...')
            pylab.figure (figsize = (8 * columns, 6 * rows))

        for plot, label in enumerate (labels):

            if not frame:
                print ('  : For %s' % label)
                pylab.subplot (rows, columns, plot + 1)

            dataset = dataset [label] .dropna ()
            ylabel = label
            xlabel = dataset.index.name
            if len (dataset) <= 50:
                marker = "o"
                markeredgecolor = color
                markerfacecolor = 'none'
                markersize = 6
                markeredgewidth = 2
            else:
                marker = "."
                markeredgecolor = 'none'
                markerfacecolor = color
                markersize = 6
                markeredgewidth = 0
            handle, = pylab.plot (
                dataset.index, dataset,
                marker=marker,
                markeredgecolor=markeredgecolor, markerfacecolor=markerfacecolor,
                markersize=markersize, markeredgewidth=markeredgewidth, linewidth=0, alpha=0.8,
                label="dataset " + str (name)
                )

        pylab.ylabel (ylabel)
        pylab.xlabel (xlabel)
        if self.title:
            pylab.title ("dataset")

        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        if not frame:
            pylab.draw ()
            caption = "Observational dataset."
            self.save (figname (save, suffix="dataset%s" % suffix), caption)
        else:
            return handle

    # plot datasets
    def datasets (self, datasets=None, labels=None, legend=True, color=None, scientific=True, columns=3, save=None, suffix=''):
        """Plot all datasets on top of each other, splitting up all labels across multiple subplots."""

        if datasets is None:
            if self._datasets is not None:
                datasets = self._datasets
            else:
                print ("  : -> SKIPPING: Datasets not provided and not specified in the constructor.")
                return

        print (' :: Plotting datasets...')

        if labels is None:
            labels = list (datasets.values ()) [0] .columns.values

        names = sorted (list (datasets.keys ()))

        plots = len (labels)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (8 * columns, 6 * rows))

        for plot, label in enumerate (labels):

            print ('  : -> For %s' % label)
            pylab.subplot (rows, columns, plot + 1)

            for index, name in enumerate (names):
                if color is None:
                    datacolor = palette ['spaghetti'] [index]
                else:
                    datacolor = color
                self.dataset (datasets [name], labels = [label], name = name, color = datacolor, frame = 1)

            if self.legend and legend:
                pylab.legend (loc='best')
        pylab.draw ()
        caption = "Observational datasets (%d independent replicates)." % len (names)
        self.save (figname (save, suffix="datasets%s" % suffix), caption)

    # plot marginal distributions of all parameters
    def distributions (self, distribution, color='spux_blue', alpha=0.99, columns=3, scientific=True, samples=None, exact=False, cexcols=8, cexrows=5, title=False, save=None, suffix=''):
        """Plot marginal distributions of all parameters."""

        print (' :: Plotting distributions...')
        if len (self.types) > 0:
            print ('  : -> Using the specified types.')
        else:
            print ('  : -> Assuming all types are float.')

        plots = len (distribution.labels)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (cexcols * columns, cexrows * rows))

        intervals = distribution.intervals (alpha)
        for index, label in enumerate (sorted (distribution.labels)):
            print ('  : -> For %s...' % label)
            pylab.subplot (rows, columns, index + 1)
            interval = list (intervals [label])
            extent = interval [1] - interval [0]
            interval [0] -= 0.2 * extent
            interval [1] += 0.2 * extent
            if self.types is not None:
                if self.types ['parameters'] is not None and label in self.types ['parameters']:
                    group = 'parameters'
                elif self.types ['predictions'] is not None and label in self.types ['predictions']:
                    group = 'predictions'
                else:
                    group = None
            if self.types is not None and group is not None and self.types [group] [label] == 'int':
                x = numpy.arange (numpy.floor (interval [0]), numpy.ceil (interval [1]) + 1)
                pylab.plot (x, distribution.mpdf (label, x), marker=".", color=color, markersize=10, linewidth=0)
            else:
                x = numpy.linspace (interval [0], interval [1], 1000)
                pylab.plot (x, distribution.mpdf (label, x), color=color, linestyle='-', lw=5)
            ylim = list (pylab.ylim ())
            ylim [0] = 0
            ylim [1] *= 1.05
            pylab.ylim (ylim)
            if samples is not None:
                for name, sample in samples.items ():
                    pylab.axvline (sample [label], color='k', linestyle='-', lw=5, alpha=0.5, label=name)
            if exact and self.exact is not None:
                pylab.axvline (self.exact ['parameters'] [label], color='r', linestyle='--', lw=5, alpha=0.5, label='exact')
            pylab.ylim (ylim)
            pylab.xlabel (label)
            pylab.ylabel ('pdf of %s' % label)
            if scientific:
                pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
            if self.title:
                pylab.title ("prior")
            pylab.draw ()
        caption = "Marginal distributions%s."
        if suffix != '':
            caption = caption % (' (' + plain (suffix) + ')')
        else:
            caption = caption % ''
        if samples is not None:
            caption += ' Semi-transparent gray lines indicate the corresponding observed data points.'
        self.save (figname (save, suffix="distributions%s" % suffix), caption)

    # plot histogram
    def histogram (self, label, indices, densities, interval, color, colorbar=False, colorbarlabel=True, scale=None, centered=False, log=False, logextent=1e3, interpolation='hermite'):
        """Plot histogram instead of the provided densities for each index in indices."""

        vs = densities

        if log:
            if centered:
                vs = numpy.abs (vs)
            vs = numpy.where (vs == 0.0, 1e-16, vs)

        extent = (indices [0], indices [-1], interval [0], interval [1])
        x = numpy.linspace (indices [0], indices [-1], densities.shape [1])
        y = numpy.linspace (interval [0], interval [-1], densities.shape [1])

        if centered and not log:
            if scale is not None:
                vmax = scale
                vmin = - scale
            else:
                vmax = numpy.max ( numpy.abs (vs) )
                vmin = - numpy.max ( numpy.abs (vs) )
            cmap = 'seismic'
        else:
            vmax = scale if scale is not None else numpy.max (vs)
            vmin = 0.0
            colors = [ brighten (color, factor=1.0 ), color ]
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list ('gradient', colors)

        if log:
            from matplotlib.colors import LogNorm
            vmin = vmax / logextent
            norm = LogNorm (vmin=vmin, vmax=vmax)
        else:
            norm = None

        interpolant = scipy.interpolate.RectBivariateSpline (indices, y, vs)
        vs = interpolant (x, y)
        pylab.imshow (numpy.transpose (vs), cmap=cmap, origin='lower', aspect='auto', norm=norm, extent=extent, interpolation=interpolation, vmin=vmin, vmax=vmax)
        if colorbar:
            colorbar = pylab.colorbar ()
            if colorbarlabel:
                colorbar.set_label ('probability (density or mass)')

    # # plot histogram
    # def histogram (self, label, indices, densities, interval, color, colorbarlabel=True, scale=None, centered=False, log=False, logextent=1e3, interpolation='none'):
    #     """Plot histogram instead of the provided densities for each index in indices."""

    #     vs = densities

    #     if log:
    #         if centered:
    #             vs = numpy.abs (vs)
    #         vs = numpy.where (vs == 0.0, 1e-16, vs)

    #     gap = (indices [-1] - indices [0]) / (len (indices) - 1)
    #     extent = ( indices [0] - 0.5 * gap, indices [-1] + 0.5 * gap, interval [0], interval [1] )

    #     if centered and not log:
    #         if scale is not None:
    #             vmax = scale
    #             vmin = - scale
    #         else:
    #             vmax = numpy.max ( numpy.abs (vs) )
    #             vmin = - numpy.max ( numpy.abs (vs) )
    #         cmap = 'seismic'
    #     else:
    #         vmax = scale if scale is not None else numpy.max (vs)
    #         vmin = 0.0
    #         colors = [ brighten (color, factor=1.0 ), color ]
    #         cmap = matplotlib.colors.LinearSegmentedColormap.from_list ('gradient', colors)

    #     if log:
    #         from matplotlib.colors import LogNorm
    #         vmin = vmax / logextent
    #         norm = LogNorm (vmin=vmin, vmax=vmax)
    #     else:
    #         norm = None

    #     pylab.imshow (numpy.transpose (vs), cmap=cmap, origin='lower', aspect='auto', norm=norm, extent=extent, interpolation=interpolation, vmin=vmin, vmax=vmax)
    #     colorbar = pylab.colorbar ()
    #     if colorbarlabel:
    #         colorbar.set_label ('probability (density or mass)')

    # plot marginal prior distributions of all parameters
    def priors (self, prior=None, color='spux_blue', alpha=0.99, columns=3, scientific=True, samples=None, exact=True, cexcols=8, cexrows=5, title=False, save=None, suffix=''):
        """Plot marginal prior distributions of all parameters."""

        print (' :: Plotting priors...')

        if prior is None:
            if self._prior is not None:
                prior = self._prior
            else:
                print ('  : -> SKIPPING: Prior distribution not specified among the arguments and not available from config.')
                return

        self.distributions (prior, color, alpha, columns, scientific, samples, exact, cexcols, cexrows, title, save, '-prior' + suffix)

    # plot marginal error distributions
    def errors (self, error=None, datasets=None, parameters=None, labels=None, bins=200, percentiles=None, exact=True, color='spux_green', columns=3, scientific=True, title=False, save=None, suffix=''):
        """Plot marginal error distributions for the specified parameters and dataset(s) (or exact model predictions, if available).

        Include only plots for the specified labels - if not specified, include all plots."""

        print (" :: Plotting errors...")

        if error is None:
            if self._error is not None:
                error = self._error
            else:
                print ("  : -> WARNING: Error not provided and not specified in the constructor.")

        if self.replicates:

            if datasets is None:
                if self._datasets is not None:
                    datasets = self._datasets
                else:
                    print ("  : -> WARNING: Datasets not provided and not specified in the constructor.")

        else:

            if datasets is None:
                if self._dataset is not None:
                    datasets = {'dataset' : self._dataset}
                else:
                    print ("  : -> WARNING: Dataset not provided and not specified in the constructor.")

        exact_parameters = False
        if parameters is None:
            if self.exact is not None:
                print ("  : -> Using exact parameters.")
                parameters = self.exact ['parameters']
                exact_parameters = True
            else:
                print ("  : -> Parameters not specified, and exact parameters not specified in the constructor.")
                if self._prior is not None:
                    print ("  : -> Using random parameters from the prior distribution.")
                    parameters = self._prior.draw (rng = numpy.random.RandomState ())
        else:
            print ("  : -> Using specified parameters.")

        if exact and self.exact is not None and 'predictions' in self.exact and self.exact ['predictions'] is not None:
            print ("  : -> Using the specified exact model predictions...")
            exact_predictions = True
        else:
            exact_predictions = False
            print ("  : -> Using available datasets as model predictions (illustrative only)...")

        for name, dataset in datasets.items ():

            print ("  : -> For dataset", name)

            data_labels = list (dataset.columns.values)
            if hasattr (error, 'transform'):
                error_labels = list (error.transform (list (datasets.values ()) [0] .iloc [0], parameters) .index)
            else:
                error_labels = data_labels

            if labels is None:
                plot_labels = data_labels
            else:
                plot_labels = labels

            plots = len (plot_labels)
            rows = numpy.ceil (plots / columns)
            pylab.figure (figsize = (8 * columns, 5 * rows))

            for plot, label in enumerate (plot_labels):

                pylab.subplot (rows, columns, plot + 1)

                dataseries = dataset.copy (deep=1) [label] .dropna ()

                upper = numpy.empty (len (dataseries.index))
                middle = numpy.empty (len (dataseries.index))
                lower = numpy.empty (len (dataseries.index))

                interval = [float ('inf'), float ('-inf')]

                for index, time in enumerate (dataseries.index):

                    if exact_predictions:
                        if self.replicates:
                            prediction = self.exact ['predictions'] [name] .loc [time]
                        else:
                            prediction = self.exact ['predictions'] .loc [time]
                    else:
                        prediction = dataset.loc [time]

                    if hasattr (error, 'transform'):
                        prediction = error.transform (prediction, parameters)
                        dataseries.loc [time] = error.transform (dataset.loc [time], parameters) [error_labels [plot]]

                    distribution = error.distribution (prediction, parameters)

                    if percentiles is not None:
                        lower [index], upper [index] = distribution.intervals (1 - 2 * percentiles [error_labels [plot]] / 100) [error_labels [plot]]
                    middle [index] = prediction [error_labels [plot]]

                    percentile = min (percentiles [error_labels [plot]], 1) if percentiles is not None else 1
                    lowest, highest = distribution.intervals (1 - 2 * percentile / 100) [error_labels [plot]]
                    if not numpy.isinf (lowest) and lowest < interval [0]:
                        interval [0] = lowest
                    if not numpy.isinf (highest) and highest > interval [1]:
                        interval [1] = highest

                extent = interval [1] - interval [0]
                interval [0] -= 0.1 * extent
                interval [1] += 0.1 * extent

                if self.types ['predictions'] is not None and self.types ['predictions'] [label] == 'int':
                    locations = numpy.arange (numpy.floor (interval [0]), numpy.ceil (interval [1]) + 1)
                else:
                    locations = numpy.linspace (interval [0], interval [1], bins)
                densities = numpy.empty ((len (dataseries.index), len (locations)))

                for index, time in enumerate (dataseries.index):
                    if exact_predictions:
                        if self.replicates:
                            prediction = self.exact ['predictions'] [name] .loc [time]
                        else:
                            prediction = self.exact ['predictions'] .loc [time]
                    else:
                        prediction = dataset.loc [time]
                    if hasattr (error, 'transform'):
                        prediction = error.transform (prediction, parameters)
                    distribution = error.distribution (prediction, parameters)
                    densities [index] [:] = distribution.mpdf (error_labels [plot], locations)

                self.histogram (error_labels [plot], dataseries.index, densities, interval, color, log=False, logextent=1e2)
                handles = []
                legends = []
                if percentiles is not None:
                    percentiles_handles = self.line_and_range (dataseries.index, lower, None, upper, linewidth=2, color='dimgray', alpha=0.5, merged=False, fill=False)
                    handles += percentiles_handles [1]
                    legends += ["error percentiles (%s - %s)" % (str(percentiles [error_labels [plot]]), str(100 - percentiles [error_labels [plot]]))]
                if exact_predictions:
                    handles_exact, = pylab.plot (dataseries.index, middle, color='r', alpha=0.5, linewidth=2)
                    handles += [handles_exact]
                    legends += ["exact model predictions"]
                data_handle = self.dataset (pandas.DataFrame (dataseries), color='dimgray', frame=1)
                handles += [data_handle]
                legends += ["dataset"]
                pylab.ylabel (error_labels [plot])
                pylab.xlabel (dataset.index.name)
                pylab.ylim (interval)
                if scientific:
                    pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
                if self.legend:
                    pylab.legend (handles, legends, loc="best")

            if self.title:
                pylab.title ("errors")
            pylab.draw ()
            dataset_suffix = ('-%s' % name) if self.replicates else ''
            args = {'name' : (' %s' % name) if self.replicates else ''}
            if exact_parameters:
                args ['parameters'] = 'exact model parameters'
            else:
                args ['parameters'] = 'the specified or randomly generated (from prior distribution) model parameters'
            if exact_predictions:
                args ['predictions'] = 'exact model predictions'
                args ['line'] = ', the thick solid line indicates the model predictions used in the error model'
            else:
                args ['predictions'] = 'data points as predictions, for illustrative purposes only'
                args ['line'] = ''
            if percentiles is not None:
                args ['percentiles'] = ', and the thin solid lines indicate the %s%% - %s%% percentiles of the associated error model distribution' % (str (percentile), str (100 - percentile))
            else:
                args ['percentiles'] = ''
            caption = """\
                Observational dataset%(name)s and the associated error model,
                evaluated using %(predictions)s and %(parameters)s.
                The circles (or thick dots) indicate the dataset values%(line)s%(percentiles)s.
                The shaded green regions indicate the density of the error model distribution.
                """ % args
            self.save (figname (save, suffix="errors%s%s" % (dataset_suffix, suffix)), caption)

    # return maximum a posteriori (MAP) estimate of parameters and the associated posterior estimate
    def MAP (self):
        """Return maximum a posteriori (MAP) estimate of parameters and the associated posterior estimate."""

        print (' :: Computing MAP...')

        sample = None if not self.replicates else {}
        oLp = float ('-inf')

        # look through each batch and chain
        for index, batch in enumerate (self.indices):
            info = self.infos [index]
            for chain in range (len (info ['posteriors'])):

                # check if chain 'infos' is not None
                if info ['infos'] [chain] is None:
                    continue

                # no replicates - all straight forward
                if not self.replicates:

                    # check if likelihood was successful
                    if not info ['infos'] [chain] ['successful']:
                        continue

                    # get the MAP likelihood of the PF MAP, if available
                    if 'MAP' in info ['infos'] [chain]:
                        particles = True
                        predictions = info ['infos'] [chain] ['MAP'] ['predictions']
                        error = info ['infos'] [chain] ['MAP'] ['error']
                    else:
                        particles = False
                        predictions = info ['infos'] [chain] ['predictions']

                    # compute the joint posterior of parameter posterior and PF MAP error
                    #gposterior = info ['posteriors'] [chain]
                    # TODO: take into account prior the intial particle state
                    gposterior = (error if particles else 0) + info ['likelihoods'] [chain] + info ['priors'] [chain]

                # replicates - need predictions for each dataset
                else:

                    predictions = {}
                    error = {}

                    # check if replicate likelihood was successful
                    if not info ['infos'] [chain] ['successful']:
                        continue

                    successful = True
                    for name in info ['infos'] [chain] ['infos'] .keys ():

                        # check if likelihood was successful
                        if not info ['infos'] [chain] ['infos'] [name] ['successful']:
                            successful = False
                            break

                        if 'MAP' in info ['infos'] [chain] ['infos'] [name]:
                            particles = True
                            predictions [name] = info ['infos'] [chain] ['infos'] [name] ['MAP'] ['predictions']
                            error [name] = info ['infos'] [chain] ['infos'] [name] ['MAP'] ['error']
                        else:
                            particles = False
                            predictions [name] = info ['infos'] [chain] ['infos'] [name] ['predictions']

                    if not successful:
                        continue

                    # compute the joint posterior of parameter posterior and PF MAP error
                    # gposterior = info ['posteriors'] [chain]
                    gposterior = (numpy.sum (list (error.values ())) if particles else 0) + info ['likelihoods'] [chain] + info ['priors'] [chain]

                # check if the joint posterior is larger than current Lp
                if gposterior > oLp:
                    oLp = gposterior
                    sample = {}
                    sample ['parameters'] = info ['parameters'] .loc [chain]
                    sample ['predictions'] = predictions
                    sample ['posterior'] = info ['posteriors'] [chain]
                    sample ['index'] = index
                    sample ['batch'] = batch
                    sample ['chain'] = chain

        # print (' :: Estimated marginal MAP parameters:')
        # print (sample ['parameters'])
        # print (' :: -> Joint (parameters and realizations, if available) MAP log-posterior: %1.1e' % Lp)
        # Lp = self.infos [sample ['batch']] ['posteriors'] [sample ['chain']]
        # print (' :: -> Estimated marginal MAP parameters log-posterior: %1.1e' % Lp)
        # L = self.infos [sample ['batch']] ['likelihoods'] [sample ['chain']]
        # print (' :: -> Parameters MAP log-likelihood: %1.1e' % L)
        # p = self.infos [sample ['batch']] ['priors'] [sample ['chain']]
        # print (' :: -> Parameters MAP log-prior: %1.1e' % p)

        self._MAP = sample

        # add MAP posterior information to metrics
        label = 'Maximum A Posteriori (MAP) estimate'
        locations = (sample ['batch'], sample ['chain'], sample ['batch'] * self.chains + sample ['chain'])
        self._metrics [label] = 'batch:%d, chain:%d, sample:%d' % locations
        self._metrics [label] += ', log-posterior:%.2e' % sample ['posterior']

        # store MAP in a report
        headers = list (sample ['parameters'] .index)
        entry = dict (sample ['parameters'])
        entry = {key : '%.2e' % value for key, value in entry.items ()}
        title = 'Maximum A Posteriori (MAP) estimate parameters'
        dumper.report (self.reportdir, 'MAP', sample, title, [entry], headers, math = True, columns = 10)

    # plot evolution of all parameters samples
    def parameters (self, MAP=True, alpha=0.99, columns=3, merged=True, percentile=5, exact=True, burnin=True, example=0, legend=False, scientific=True, save=None, suffix=''):
        """Plot evolution of all parameters samples."""

        print (' :: Plotting parameters...')

        plots = len (self._prior.labels)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (8 * columns, 5 * rows))

        linewidth = 2 if plots == 1 else 4

        intervals = self._prior.intervals (alpha)

        for plot, label in enumerate (sorted (self._prior.labels)):
            pylab.subplot (rows, columns, plot + 1)
            support = list (intervals [label])
            interval = support [:]
            if not merged:
                for chain in range (self.chains):
                    samples = self.samples [label] .iloc [chain::self.chains]
                    pylab.plot (self.indices, samples, color=palette ['spaghetti'][chain], linestyle='-', lw=linewidth)
                    interval [0] = min (interval [0], numpy.min (samples))
                    interval [1] = max (interval [1], numpy.max (samples))
            else:
                median = numpy.empty (self.batches)
                upper = numpy.empty (self.batches)
                lower = numpy.empty (self.batches)
                for index, batch in enumerate (self.indices):
                    samples = self.samples [label] .loc [batch * self.chains : (batch + 1) * self.chains]
                    median [index] = numpy.median (samples)
                    lower [index] = numpy.percentile (samples, percentile)
                    upper [index] = numpy.percentile (samples, 100 - percentile)
                self.line_and_range (self.indices, lower, median, upper, color='spux_orange', linewidth=linewidth, alpha=0.9)
                interval [0] = min (interval [0], numpy.min (lower))
                interval [1] = max (interval [1], numpy.max (upper))
                if example is not None:
                    samples = self.samples [label] .iloc [example::self.chains]
                    pylab.plot (self.indices, samples, color = 'spux_orange', linewidth = linewidth / 2, alpha = 0.6)
            extent = interval [1] - interval [0]
            interval [0] -= 0.2 * extent
            interval [1] += 0.2 * extent
            pylab.ylim (interval)
            pylab.axhline (support [0], color='gray', linestyle='-', alpha=0.5, lw=5)
            pylab.axhline (support [1], color='gray', linestyle='-', alpha=0.5, lw=5)
            if MAP and self._MAP is not None:
                if not merged:
                    location = self._MAP ['batch']
                    value = self.samples [label] .loc [self._MAP ['batch'] * self.chains + self._MAP ['chain']]
                    pylab.plot (location, value, marker="o", color="brown", alpha=0.5, markerfacecolor='none', markersize=10, markeredgewidth=2, linewidth=0, label="approximate MAP")
                else:
                    pylab.axhline (self._MAP ['parameters'] [label], color='brown', linestyle=':', alpha=0.5, lw=5)
            if exact and self.exact is not None:
                pylab.axhline (self.exact ['parameters'] [label], color='r', linestyle='--', alpha=0.5, lw=5)
            if burnin and self.burnin is not None:
                pylab.axvline (self.burnin, color='deepskyblue', linestyle=':', alpha=0.5, lw=5)
            if scientific:
                pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
            pylab.ylabel (label)
            pylab.xlabel ('sample batch')
            if self.title:
                pylab.title("parameters")
        pylab.draw()
        args = {'lower' : str (percentile), 'upper' : str (100 - percentile)}
        # if self.burnin is not None and self.burnin > 0:
        #     args ['burnin'] = ' The burnin of the initial %d sample batches (%d samples) was removed.' % (self.burnin, self.burnin * self.chains)
        # else:
        #     args ['burnin'] = ''
        if exact and self.exact is not None:
            args ['exact'] = ' The red dashed line represents the exact parameter values.'
        else:
            args ['exact'] = ''
        if burnin and self.burnin is not None:
            args ['burnin'] = ' The vertical dotted blue line indicates the end of the specified burnin period.'
        else:
            args ['burnin'] = ''
        caption = """\
                Markov chain parameters samples.%(burnin)s
                The solid lines indicate the median and the semi-transparent spreads indicate the %(lower)s%% - %(upper)s%% percentiles
                accross multiple concurrent chains of the sampler.
                An auxiliary semi-transparent line indicates an example of such chain.
                The thick semi-transparent gray lines indicate the interval containing centererd 99%% mass of the respective prior distribution.
                The brown dotted line indicates the estimated maximum a postriori (MAP) parameters values.%(exact)s%(burnin)s
                """ % args
        self.save (figname (save, suffix="parameters%s" % suffix), caption)

    # evaluate 1D kde estimator
    def kde (self, samples, x, weights=None, percentile=None):
        """
        Evaluate 1D kde estimator.

        Use state-of-the-art 1-D estimator from https://doi.org/10.1103/PhysRevLett.121.160605.
        """

        if weights is not None:
            assert len (samples) == len (weights)
            samples = [sample for i, sample in enumerate (samples) for copy in range (weights [i])]

        # if self.kdelib == 'suft':
        #     density = suftware.DensityEstimator (samples, alpha=2)
        #     if percentile is None:
        #         return density.evaluate (x)
        #     else:
        #         MAP = density.evaluate (x)
        #         samples = density.evaluate_samples (x, resample=True)
        #         lower = numpy.nanpercentile (samples, percentile, axis=1)
        #         upper = numpy.nanpercentile (samples, 100 - percentile, axis=1)
        #         return lower, MAP, upper

        # elif self.kdelib == 'scipy':
        if self.kdelib == 'scipy':
            density = scipy.stats.gaussian_kde (samples)
            if percentile is None:
                return density (x)
            else:
                return None, density (x), None

        else:
            print (' :: ERROR: requested KDE is not available.')
            return

    # plot marginal posterior distributions of all parameters
    def posteriors (self, initial=True, MAP=True, alpha=0.99, columns=3, percentile=5, exact=True, prior=True, legend=False, scientific=True, save=None, suffix=''):
        """Plot marginal posterior distributions of all parameters."""

        print (' :: Plotting posteriors...')
        if self.types ['parameters'] is not None:
            print ('  : -> Using the specified types.')
        else:
            print ('  : -> Assuming all types are float.')

        plots = len (self._prior.labels)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (8 * columns, 5 * rows))

        percentile = (1 - alpha) / 2 * 100
        intervals = self._prior.intervals (alpha)

        for plot, label in enumerate (sorted (self._prior.labels)):
            pylab.subplot (rows, columns, plot + 1)
            interval = list (intervals [label])
            samples = self.samples [label] .values
            interval [0] = min (interval [0], numpy.percentile (samples, percentile))
            interval [1] = max (interval [1], numpy.percentile (samples, 100 - percentile))
            extent = interval [1] - interval [0]
            interval [0] -= 0.2 * extent
            interval [1] += 0.2 * extent
            if self.types ['parameters'] is not None and self.types ['parameters'] [label] == 'int':
                x = numpy.arange (numpy.floor (interval [0]), numpy.ceil (interval [1]) + 1)
                if prior:
                    pylab.plot (x, self._prior.mpdf (label, x), color='spux_blue', marker=".", markersize=10, linewidth=0)
                pylab.plot (x, self.kde (samples, x), color='spux_orange', alpha=0.9, marker=".", markersize=10, linewidth=0)
            else:
                x = numpy.linspace (interval [0], interval [1], 1000)
                if prior:
                    pylab.plot (x, self._prior.mpdf (label, x), color='spux_blue', linestyle='-', lw=5)
                lower, middle, upper = self.kde (samples, x, percentile = percentile)
                if lower is None or upper is None:
                    pylab.plot (x, self.kde (samples, x), color='spux_orange', alpha=0.9, linestyle='-', lw=5)
                else:
                    self.line_and_range (x, lower, middle, upper, color='spux_orange', middlealpha=0.9, style='-', linewidth=5)
            ylim = list (pylab.ylim ())
            ylim [0] = 0
            ylim [1] *= 1.05
            pylab.ylim (ylim)
            if MAP and self._MAP is not None:
                pylab.axvline (self._MAP ['parameters'] [label], color='brown', linestyle=':', alpha=0.5, lw=5)
            if exact and self.exact is not None:
                pylab.axvline (self.exact ['parameters'] [label], color='r', linestyle='--', alpha=0.5, lw=5)
            if scientific:
                pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
            pylab.ylim (ylim)
            pylab.xlabel (label)
            pylab.ylabel ('pdf of %s' % label)
            if self.title:
                pylab.title("posterior")
            pylab.draw()
        args = {}
        if exact and self.exact is not None:
            args ['exact'] = ' The red dashed line represents the exact parameter values.'
        else:
            args ['exact'] = ''
        caption = """\
            Marginal posterior (orange) and prior (blue) distributions of model parameters.
            The brown dotted line indicates the estimated maximum a postriori (MAP) parameters values.%(exact)s
            """ % args
        self.save(figname(save, suffix="posteriors%s" % suffix), caption)

    # # compute pairwise joint kde
    # def kde2d (self, xv, yv, xmin, xmax, ymin, ymax, points=100j):
    #     """Compute pairwise joint kde."""

    #     # estimate posterior PDF with a KDE
    #     xsg, ysg = numpy.mgrid[xmin:xmax:points, ymin:ymax:points]
    #     positions = numpy.vstack([xsg.ravel(), ysg.ravel()])
    #     values = numpy.vstack([xv, yv])
    #     kernel = scipy.stats.gaussian_kde(values)
    #     Z = numpy.reshape(kernel(positions).T, xsg.shape)
    #     return Z

    # plot pairwise joint posterior distributions of all parameters
    # with chains in superdiagonals and histograms in subdiagonals
    def posteriors2d (self, color="spux_orange", bins=30, initial=True, MAP=True, exact=True, legend=False, scientific=False, save=None, suffix=''):
        """Plot pairwise joint posterior distributions of all parameters."""

        print (' :: Plotting all pairwise joint posteriors...')

        plots = len (self.labels)

        if plots > 10:
            print(":: WARNING: Skipping posteriors2d as there are too many parameters (will likely segfault). Please, choose your pairwise parameters and use plot.posterior().")
            return

        canvas = pylab.figure (figsize = (6 * min (plots, 5), 6 * min (plots, 5)))
        canvas.subplots_adjust (hspace = 0, wspace = 0)

        for i, label_i in enumerate (sorted (self.labels)):
            for j, label_j in enumerate (sorted (self.labels)):
                pylab.subplot (plots, plots, i * plots + j + 1)
                if i == j:
                    xmin, xmax, ymin, ymax = self.extents (label_j, label_i)
                    pylab.xlim ([xmin, xmax])
                    pylab.ylim ([ymin, ymax])
                    pylab.gca().text (0.5, 0.5, label_i, fontsize=60, verticalalignment='center', horizontalalignment='center', transform=pylab.gca().transAxes)
                    if scientific:
                        pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
                else:
                    kde = (i > j)
                    chains = (i < j)
                    self.posterior2d_pair (label_j, label_i, color, kde, chains, initial, MAP, exact, legend, scientific, bins, save, suffix, frame=True)
                pylab.xlabel (None)
                pylab.ylabel (None)
                if i != 0 and i != (plots - 1):
                    pylab.gca().set_xticklabels ([])
                else:
                    if i == 0:
                        pylab.gca().xaxis.tick_top ()
                        if j % 2 == 0:
                            pylab.gca().set_xticklabels ([])
                    else:
                        if j % 2 == 1:
                            pylab.gca().set_xticklabels ([])
                if j != 0 and j != (plots - 1):
                    pylab.gca().set_yticklabels ([])
                else:
                    if j == 0:
                        if i % 2 == 0:
                            pylab.gca().set_yticklabels ([])
                    else:
                        pylab.gca().yaxis.tick_right ()
                        if i % 2 == 1:
                            pylab.gca().set_yticklabels ([])
                #pylab.gca().axis ('equal')

        args = {}
        if exact and self.exact is not None:
            args ['exact'] = ', red "x" - the exact parameters'
        else:
            args ['exact'] = ''
        args ['initial'] = ', blue "+" - initial parameters' if initial else ''
        args ['MAP'] = ', brown "o" - approximate MAP parameters' if MAP and self._MAP is not None else ''
        caption = """\
            Joint pairwise marginal posterior distribution of all model parameters,
            including the corresponding Markov chains from the sampler.
            Legend:
            thick semi-transparent gray lines -
            intervals containing centererd 99%% mass of the respective prior distribution%(initial)s%(MAP)s%(exact)s,
            thin semi-transparent gray lines and dots - concurrent chains,
            orange hexagons - histogram of the joint pairwise marginal posterior parameters samples.
            """ % args
        self.save (figname (save, suffix="posteriors2d" + suffix), caption)

    # plot pairwise joint posterior distribution for the specified pair of parameters
    # with chains in the left subplot and histogram in the right subplot
    def posterior2d (self, x, y, color="spux_orange", bins=30, initial=True, MAP=True, exact=True, legend=True, scientific=True, save=None, suffix=''):
        """Plot pairwise joint posterior distributions for the specified pair of parameters."""

        print (' :: Plotting joint posterior for %s and %s...' % (x, y))

        pylab.figure (figsize = (8 * 2, 6))

        pylab.subplot (1, 2, 1)
        kde = False
        chains = True
        self.posterior2d_pair (x, y, color, kde, chains, initial, MAP, exact, legend, scientific, bins, save, suffix, frame=True)
        #pylab.gca().axis ('equal')

        pylab.subplot (1, 2, 2)
        kde = True
        chains = False
        self.posterior2d_pair (x, y, color, kde, chains, initial, MAP, exact, legend, scientific, bins, save, suffix, frame=True)
        #pylab.gca().axis ('equal')

        args = {'x' : x, 'y' : y}
        if exact and self.exact is not None:
            args ['exact'] = ', red "x" - the exact parameters'
        else:
            args ['exact'] = ''
        args ['initial'] = ', blue "+" - initial parameters' if initial else ''
        args ['MAP'] = ', brown "o" - approximate MAP parameters' if MAP and self._MAP is not None else ''
        if self.burnin == 0 and self._prior is not None:
            args ['extents'] = ', thick semi-transparent gray lines - intervals containing centererd 99%% mass of the respective prior distribution'
        else:
            args ['extents'] = ''
        caption = """\
            Joint pairwise marginal posterior distribution of %(x)s and %(y)s,
            including the corresponding Markov chains from the sampler.
            Legend:
            thin semi-transparent gray lines and dots - concurrent chains,
            orange hexagons - histogram of the joint pairwise marginal posterior parameters samples%(extents)s%(initial)s%(MAP)s%(exact)s.
            """ % args
        self.save (figname (save, suffix="posterior2d-%s-%s%s" % (plain (x), plain (y), suffix)), caption)

    # plot pairwise joint posterior
    def posterior2d_pair (self, x, y, color="spux_orange", kde=True, chains=True, initial=True, MAP=True, exact=True, legend=False, scientific=True, bins=30, save=None, suffix="", frame=False):
        """Plot pairwise joint posterior."""

        print ('  : -> For %s and %s (%d chains)' % (x, y, self.chains))

        xv = self.samples [x]
        yv = self.samples [y]

        xmin, xmax, ymin, ymax = self.extents (x, y, prior=(self.burnin == 0))

        if not frame:
            pylab.figure ()

        # plot 2d KDE for posterior PDF
        if kde:
            colors = [brighten (color, factor=1.0 ), color]
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list ('gradient', colors)
            self.samples.plot.hexbin (x, y, gridsize=bins, colormap=cmap, xlim=(xmin, xmax), ylim=(ymin, ymax), colorbar=(not frame), ax=pylab.gca())
            # kde2d = self.kde2d (xv, yv, xmin, xmax, ymin, ymax)
            # pylab.imshow (numpy.transpose (kde2d), origin="lower", aspect="auto", extent=[xmin, xmax, ymin, ymax], cmap="YlOrBr")
            # if not frame:
            #     colorbar = pylab.colorbar()
            #     colorbar.set_label("probability density")

        # plot all posterior samples and paths of each chain
        if chains:
            for chain in range (self.chains):
                xs = xv.iloc [chain::self.chains]
                ys = yv.iloc [chain::self.chains]
                color = 'dimgray'
                pylab.plot (xs, ys, color=color, marker=".", markersize=10, markeredgewidth=0, alpha=0.2, label=str())
                # pylab.plot (xs, ys, color=color, marker=".", markersize=10, markeredgewidth=0, alpha=0.2, label="chain %d" % chain)

        # plot prior intervals region
        if self.burnin == 0 and self._prior is not None:
            intervals = self._prior.intervals (alpha=0.99)
            xpmin = intervals [x] [0]
            xpmax = intervals [x] [1]
            ypmin = intervals [y] [0]
            ypmax = intervals [y] [1]
            xs = [xpmin, xpmin, xpmax, xpmax, xpmin]
            ys = [ypmin, ypmax, ypmax, ypmin, ypmin]
            pylab.plot (xs, ys, color='gray', alpha=0.5, linewidth=3, label='prior support (99%)')

        # plot initial parameter set
        if initial and chains:
            x0 = self.samples [x] [0:self.chains]
            y0 = self.samples [y] [0:self.chains]
            pylab.plot (x0, y0, marker="+", color="spux_blue", markersize=10, markeredgewidth=2, linewidth=0, alpha=0.6, label="initial")

        # plot MAP
        if MAP and self._MAP is not None:
            xs = self._MAP ['parameters'] [x]
            ys = self._MAP ['parameters'] [y]
            pylab.plot (xs, ys, marker="o", color="brown", alpha=0.5, markerfacecolor='none', markersize=10, markeredgewidth=2, linewidth=0, label="approximate MAP")

        # plot exact parameter set
        if exact and self.exact is not None:
            pylab.plot (self.exact ['parameters'] [x], self.exact ['parameters'] [y], marker="x", color="r", alpha=0.5, markersize=10, markeredgewidth=3, linewidth=0, label="exact")

        # set axes extents
        pylab.xlim ([xmin, xmax])
        pylab.ylim ([ymin, ymax])

        # use scientific format for axes tick labels
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        # add legend
        if self.legend and legend:
            pylab.legend (loc="best", numpoints=1)

        if self.title:
            pylab.title("joint posterior")

        # add axes labels
        pylab.xlabel (x)
        pylab.ylabel (y)

        pylab.draw ()

        if not frame:
            self.save (figname (save, suffix="posterior2d_pair-%s-%s%s" % (plain (x), plain (y), suffix)))

    def _likelihoods (self, MAP, burnin, merged, percentile, columns, palette, scientific, save, suffix):
        """Internal plotting routine to plot likelihoods of all replicates."""

        print (' :: Plotting likelihoods for all replicates...')

        plots = len (self.names)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (8 * columns, 5 * rows))

        for plot, name in enumerate (self.names):

            print ('  : -> For dataset %s...' % name)
            pylab.subplot (rows, columns, plot + 1)
            pylab.title ('dataset %s' % name)

            if merged:

                L_means = numpy.empty (len (self.indices))
                L_lower = numpy.empty (len (self.indices))
                L_upper = numpy.empty (len (self.indices))

                for index, batch in enumerate (self.indices):
                    likelihood = [self.infos [index] ['infos'] [chain] ['evaluations'] [name] for chain in range (self.chains) if self.infos [index] ['infos'] [chain] is not None]
                    L_means [index] = numpy.nanmedian (likelihood)
                    L_lower [index] = numpy.nanpercentile (likelihood, percentile)
                    L_upper [index] = numpy.nanpercentile (likelihood, 100 - percentile)

                handles_likelihood = self.line_and_range (self.indices, L_lower, L_means, L_upper, linewidth=2, color=palette ['likelihood'], alpha=0.6)
                handles = [handles_likelihood]

            else:

                for chain in range (self.chains):
                    likelihood = [ info ['infos'] [chain] ['evaluations'] [name] for info in self.infos ]
                    variance = numpy.empty (len (self.infos))
                    for index, info in enumerate (self.infos):
                        if info ['infos'] [chain] is not None:
                            variance [index] = info ['infos'] [chain] ['infos'] [name] ['variance']
                        else:
                            variance [index] = float ('nan')
                    lower = likelihood - numpy.sqrt (variance)
                    upper = likelihood + numpy.sqrt (variance)
                    self.line_and_range (self.indices, lower, likelihood, upper, merged=0, linewidth=1, color=palette ['spaghetti'][chain], alpha=0.6, middlealpha=0.8)
                handles_likelihood = self.line_and_range_handles (merged=0, linewidth=2, color='dimgray', alpha=0.6, middlealpha=0.8)

            if MAP and self._MAP is not None:
                location = self._MAP ['batch']
                value = self.infos [self._MAP ['index']] ['infos'] [self._MAP ['chain']] ['evaluations'] [name]
                handle_map, = pylab.plot (location, value, marker="o", color="brown", alpha=0.5, markerfacecolor='none', markersize=10, markeredgewidth=2, linewidth=0)

            if burnin and self.burnin is not None:
                pylab.axvline (self.burnin, color='deepskyblue', linestyle=':', alpha=0.5, lw=2)

            pylab.xlabel("sample batch")
            pylab.ylabel("log-probability")
            if scientific:
                pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

            if merged:
                labels = ["log-likelihood estimate"]
            else:
                labels = ["log-likelihood estimate", "log-likelihood deviation"]
            if MAP and self._MAP is not None:
                handles += (handle_map,)
                labels += ["approximate MAP"]
            if self.legend:
                pylab.legend (handles, labels, loc="best")

        pylab.draw()
        args = {}
        args ['lower'] = str (percentile)
        args ['upper'] = str (100 - percentile)
        args ['MAP'] = 'The brown "o" symbol indicates the posterior estimate at the approximate MAP parameters.' if MAP and self._MAP is not None else ''
        if burnin and self.burnin is not None:
            args ['burnin'] = ' The vertical dotted blue line indicates the end of the specified burnin period.'
        else:
            args ['burnin'] = ''
        caption = """\
            Log-likelihood estimates for the sampled model posterior parameters for each replicate dataset.
            The solid lines indicate the median and the semi-transparent spreads indicate the %(lower)s%% - %(upper)s%% percentiles
            accross multiple concurrent chains of the sampler.
            The estimates from the rejected proposed parameters are also taken into account.%(MAP)s%(burnin)s
            """ % args
        self.save (figname (save, suffix="likelihoods-replicates" + suffix), caption)

    # plot likelihoods
    def likelihoods (self, MAP=True, burnin=True, merged=True, percentile=10, columns=3, palette=palette['likelihoods'], scientific=True, save=None, suffix=""):
        """Plot likelihoods (and acceptances or unsuccessfuls, if requested)."""

        print (' :: Plotting likelihoods...')

        pylab.figure ()

        # likelihoods
        if merged:

            L_means = numpy.empty (len (self.indices))
            L_lower = numpy.empty (len (self.indices))
            L_upper = numpy.empty (len (self.indices))
            Lp_means = numpy.empty (len (self.indices))
            Lp_lower = numpy.empty (len (self.indices))
            Lp_upper = numpy.empty (len (self.indices))

            for index, batch in enumerate (self.indices):
                likelihood = [ self.infos [index] ['likelihoods'] [chain] for chain in range (self.chains) ]
                posterior = [ self.infos [index] ['posteriors'] [chain] for chain in range (self.chains) ]
                L_means [index] = numpy.nanmedian (likelihood)
                L_lower [index] = numpy.nanpercentile (likelihood, percentile)
                L_upper [index] = numpy.nanpercentile (likelihood, 100 - percentile)
                Lp_means [index] = numpy.nanmedian (posterior)
                Lp_lower [index] = numpy.nanpercentile (posterior, percentile)
                Lp_upper [index] = numpy.nanpercentile (posterior, 100 - percentile)

            handles_likelihood = self.line_and_range (self.indices, L_lower, L_means, L_upper, linewidth=2, color=palette ['likelihood'], alpha=0.6)
            handles_likelihood = (handles_likelihood,)
            handle_posterior = self.line_and_range (self.indices, Lp_lower, Lp_means, Lp_upper, linewidth=2, color=palette ['posterior'], alpha=0.6, middlealpha=0.8)

        else:

            for chain in range (self.chains):
                likelihood = [ info ['likelihoods'] [chain] for info in self.infos ]
                posterior = [ info ['posteriors'] [chain] for info in self.infos ]
                if self.deterministic:
                    pylab.plot (self.indices, likelihood, lw=1, color=palette ['spaghetti'][chain], linestyle='-')
                else:
                    variance = numpy.empty (len (self.infos))
                    if not self.replicates:
                        for index, info in enumerate (self.infos):
                            if info ['infos'] [chain] is not None:
                                variance [index] = info ['infos'] [chain] ['variance']
                            else:
                                variance [index] = float ('nan')
                    else:
                        for index, info in enumerate (self.infos):
                            if info ['infos'] [chain] is not None:
                                variances = [ replicate ['variance'] for replicate in info ['infos'] [chain] ['infos'] .values () ]
                                variance [index] = numpy.sum (variances)
                            else:
                                if self.verbosity:
                                    print (' :: WARNING: NaN variance at', chain, index)
                                variance [index] = float ('nan')
                    lower = likelihood - numpy.sqrt (variance)
                    upper = likelihood + numpy.sqrt (variance)
                    self.line_and_range (self.indices, lower, likelihood, upper, merged=0, linewidth=1, color=palette ['spaghetti'][chain], alpha=0.6, middlealpha=0.8)
                pylab.plot (self.indices, posterior, lw=1, color=palette ['spaghetti'][chain], linestyle=':')
            if self.deterministic:
                handles_likelihood, = pylab.plot ([], [], lw=1, color='dimgray', linestyle='-')
            else:
                handles_likelihood = self.line_and_range_handles (merged=0, linewidth=2, color='dimgray', alpha=0.6, middlealpha=0.8)
            handle_posterior, = pylab.plot ([], [], lw=2, color='dimgray', linestyle=':')

        if MAP and self._MAP is not None:
            location = self._MAP ['batch']
            value = self.infos [self._MAP ['index']] ['posteriors'] [self._MAP ['chain']]
            handle_map, = pylab.plot (location, value, marker="o", color="brown", alpha=0.5, markerfacecolor='none', markersize=10, markeredgewidth=2, linewidth=0)

        if burnin and self.burnin is not None:
            pylab.axvline (self.burnin, color='deepskyblue', linestyle=':', alpha=0.5, lw=2)

        pylab.xlabel("sample batch")
        pylab.ylabel("log-probability")
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        handles = handles_likelihood
        if merged or self.deterministic:
            labels = ["log-likelihood estimate"]
        else:
            labels = ["log-likelihood estimate", "log-likelihood deviation"]
        handles += (handle_posterior,)
        labels += ["log-posterior estimate (scaled)"]
        if MAP and self._MAP is not None:
            handles += (handle_map,)
            labels += ["approximate MAP"]
        if self.legend:
            pylab.legend (handles, labels, loc="best")

        if self.title:
            pylab.title ("log-likelihood and log-posterior")
        pylab.draw()
        args = {}
        args ['lower'] = str (percentile)
        args ['upper'] = str (100 - percentile)
        args ['MAP'] = 'The brown "o" symbol indicates the posterior estimate at the approximate MAP parameters.' if MAP and self._MAP is not None else ''
        if burnin and self.burnin is not None:
            args ['burnin'] = ' The vertical dotted blue line indicates the end of the specified burnin period.'
        else:
            args ['burnin'] = ''

        caption = """\
            Log-likelihood and (scaled [TODO: estimate evidence and remove scaling])
            log-posterior estimates for the sampled model posterior parameters.
            The solid lines indicate the median and the semi-transparent spreads indicate the %(lower)s%% - %(upper)s%% percentiles
            accross multiple concurrent chains of the sampler.
            For log-likelihood, the estimates from the rejected proposed parameters are also taken into account.%(MAP)s%(burnin)s
            """ % args
        self.save (figname (save, suffix="likelihoods" + suffix), caption)

        if self.replicates:
            self._likelihoods (MAP, burnin, merged, percentile, columns, palette, scientific, save, suffix)

        try:
            self.fitscores (percentile, columns, palette, scientific, save, suffix)
            # self._max_avg_errs (percentile, columns, palette, scientific, save, suffix)
        except:
            print (" :: WARNING: fitscores plot failed!")

    def fitscores (self, percentile, columns, palette, scientific, save, suffix):
        """Internal: plot fitscores (for each replicate dataset)."""

        print (' :: Plotting fitscores...')

        plots = len (self.names)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (8 * columns, 5 * rows))

        for plot, name in enumerate (self.names):

            if self.replicates:
                print ('  : -> For dataset %s...' % name)
            pylab.subplot (rows, columns, plot + 1)
            if self.replicates:
                pylab.title ('dataset %s' % name)

            lower = numpy.empty (len (self.indices))
            upper = numpy.empty (len (self.indices))
            fitscore = numpy.empty (len (self.indices))

            for index, batch in enumerate (self.indices):
                if self.replicates:
                    #likelihoods = [chaininfo ['evaluations'] [name] if chaininfo is not None else float ('nan') for chaininfo in self.infos [index] ['infos']]
                    #chain = numpy.nanargmax (likelihoods)
                    fitscores = [chaininfo ['infos'] [name] ['fitscore'] if chaininfo is not None else float ('nan') for chaininfo in self.infos [index] ['infos']]
                    #fitscore [index] = fitscores [chain]
                else:
                    #likelihoods = self.infos [index] ['likelihoods']
                    #chain = numpy.nanargmax (likelihoods)
                    fitscores = [chaininfo ['fitscore'] if chaininfo is not None else float ('nan') for chaininfo in self.infos [index] ['infos']]
                    #fitscore [index] = fitscores [chain]
                fitscore [index] = numpy.nanmean (fitscores)
                upper [index] = numpy.nanmax (fitscores)
                lower [index] = numpy.nanmin (fitscores)

            if self.replicates:
                threshold = self.sampler.likelihood.likelihood.threshold
            else:
                threshold = self.sampler.likelihood.threshold

            # if numpy.all (fitscore < 0):
            #     pylab.semilogy (self.indices, -fitscore, linewidth=2, color=palette ['fitscore'], alpha=0.9)
            #     pylab.ylabel ("negative fitscore")
            #     pylab.axhline (-threshold, color='forestgreen', linestyle='--', lw=5, alpha=0.9)
            #     if scientific:
            #         pylab.gca().ticklabel_format (axis='x', style='sci', scilimits=(-2, 2))

            # else:
            self.line_and_range (self.indices, -lower, -fitscore, -upper, logy=True, merged=0, linewidth=2, color=palette ['fitscore'])
            # pylab.plot (self.indices, fitscore, linewidth=2, color=palette ['fitscore'], alpha=0.9)
            pylab.ylabel ("negative fitscore")
            pylab.axhline (-threshold, color='forestgreen', linestyle='--', lw=5, alpha=0.9)
            if scientific:
                pylab.gca().ticklabel_format (axis='x', style='sci', scilimits=(-2, 2))

            pylab.xlabel("sample batch")

        pylab.draw()
        args = {}
        args ['replicates'] = ' for each replicate dataset' if self.replicates else ''
        caption = """\
            Fitscores accross multiple concurrent chains of the sampler%(replicates)s.
            Fitscore is the log of the average (over snapshots and particles)
            normalized (with respect to maximum pdf value and the dimensions of the observations) posterior errors.
            The solid line indicates the mean
            and the semi-transparent spreads indicate the minimum and the maximum
            accross multiple concurrent chains of the sampler.
            The dashed green line indicates the threshold set in the adaptive PF likelihood.
            """ % args
        self.save (figname (save, suffix="fitscores" + suffix), caption)

    # def _max_avg_errs (self, percentile, columns, palette, scientific, save, suffix):
    #     """Internal: plot maximal average observational log-errors for each likelihood."""

    #     print (' :: Plotting average errors...')

    #     plots = len (self.names)
    #     rows = numpy.ceil (plots / columns)
    #     pylab.figure (figsize = (8 * columns, 5 * rows))

    #     for plot, name in enumerate (self.names):

    #         if self.replicates:
    #             print ('  : -> For dataset %s...' % name)
    #         pylab.subplot (rows, columns, plot + 1)
    #         if self.replicates:
    #             pylab.title ('dataset %s' % name)

    #         # L_lower = numpy.empty (len (self.indices))
    #         # L_upper = numpy.empty (len (self.indices))
    #         max_avg_err = numpy.empty (len (self.indices))

    #         for index, batch in enumerate (self.indices):
    #             if self.replicates:
    #                 likelihood = [self.infos [index] ['infos'] [chain] ['evaluations'] [name] for chain in range (self.chains) if self.infos [index] ['infos'] [chain] is not None]
    #             else:
    #                 likelihood = [self.infos [index] ['likelihoods'] [chain] for chain in range (self.chains) if self.infos [index] ['likelihoods'] [chain] is not None]
    #             # L_lower [index] = numpy.nanpercentile (likelihood, percentile)
    #             # L_upper [index] = numpy.nanpercentile (likelihood, 100 - percentile)
    #             max_avg_err [index] = numpy.nanpercentile (likelihood, 90)
    #             #max_avg_err [index] = numpy.nanmax (likelihood)

    #         if self.replicates:
    #             threshold = self.sampler.likelihood.likelihood.threshold
    #             snapshots = len (self._datasets [name] .index)
    #         else:
    #             threshold = self.sampler.likelihood.threshold
    #             snapshots = len (self._dataset.index)

    #         max_avg_err /= snapshots

    #         if numpy.all (max_avg_err < 0):
    #             pylab.semilogy (self.indices, -max_avg_err, linewidth=2, color=palette ['extent'], alpha=0.9)
    #             pylab.ylabel ("negative maximum average log-error")
    #             pylab.axhline (-threshold, color='forestgreen', linestyle='--', lw=5, alpha=0.9)
    #             if scientific:
    #                 pylab.gca().ticklabel_format (axis='x', style='sci', scilimits=(-2, 2))

    #         else:
    #             pylab.plot (self.indices, max_avg_err, linewidth=2, color=palette ['extent'], alpha=0.9)
    #             pylab.ylabel ("maximum average log-error")
    #             pylab.axhline (threshold, color='forestgreen', linestyle='--', lw=5, alpha=0.9)
    #             if scientific:
    #                 pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

    #         # pylab.semilogy (self.indices, L_upper - L_lower, linewidth=2, color=palette ['extent'], alpha=0.9)

    #         pylab.xlabel("sample batch")

    #     pylab.draw()
    #     args = {}
    #     args ['replicates'] = ' for each replicate dataset' if self.replicates else ''
    #     caption = """\
    #         Maximums of the average (over dataset snapshots) marginal observational log-errors
    #         accross multiple concurrent chains of the sampler%(replicates)s.
    #         The dashed green line indicates the threshold set in the adaptive PF likelihood.
    #         """ % args
    #     self.save (figname (save, suffix="max_avg_errs" + suffix), caption)

    def _unsuccessfuls (self, name, scientific):
        """Internal routine for unsuccessfuls plot."""

        succ = numpy.empty (self.batches)
        fail = numpy.empty (self.batches)
        skip = numpy.empty (self.batches)
        for index, info in enumerate (self.infos):
            if name is None:
                successful = [ info ['infos'] [chain] ['successful'] if info ['infos'] [chain] is not None else None for chain in range (self.chains) ]
            else:
                successful = [ info ['infos'] [chain] ['successful'] if info ['infos'] [chain] is not None else None for chain in range (self.chains) ]
            succ [index] = len ( [ state for state in successful if state is not False and state is not None ] )
            fail [index] = len ( [ state for state in successful if state is False ] )
            skip [index] = len ( [ state for state in successful if state is None ] )
        succ = numpy.where (succ != 0, succ, float ('nan'))
        fail = numpy.where (fail != 0, fail, float ('nan'))
        skip = numpy.where (skip != 0, skip, float ('nan'))
        width = 0.8 if self.batches < 101 else 1.0
        handle_succ = pylab.bar (self.indices, succ, color = "limegreen", width = width)
        handle_skip = pylab.bar (self.indices, skip, bottom = succ, color = "lightgray", width = width)
        handle_fail = pylab.bar (self.indices, fail, bottom = succ + skip, color = "firebrick", width = width)
        pylab.ylabel ("counts")
        pylab.ylim ((0, 1.05 * self.chains))
        pylab.xlabel ("sample batch")
        pylab.xlim ((self.indices [0] - 0.5, self.indices [-1] + 0.5))
        #pylab.axhline (self.chains, color='gray', linestyle='-', alpha=0.5, lw=5)
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        handles = (handle_succ, handle_skip, handle_fail)
        labels = ["successful (pass)", "zero prior (skip)", "NaN posterior (fail)"]
        if self.legend:
            pylab.legend (handles, labels, loc="best")

    # plot report for unsuccessful posteriors
    def unsuccessfuls (self, columns=3, scientific=True, save=None, suffix=""):
        """Plot report for unsuccessful posteriors."""

        print (' :: Plotting unsuccessful posteriors...')

        pylab.figure ()
        name = None
        self._unsuccessfuls (name, scientific)
        if self.title:
            pylab.title ("unsuccessful posteriors")

        pylab.draw ()
        caption = """\
            Diagnostics of the posterior sampler,
            indicating the successes and failures of the likelihood estmation procedures.
            Legend:
            green - successfully passed,
            gray - estimation skipped due to (numerically) zero prior,
            red - estimation failure due to failed model simulatios and/or failed PF filtering.
            """
        self.save (figname (save, suffix="unsuccessfuls" + suffix), caption)

        if self.replicates:

            print (' :: Plotting unsuccessful posteriors for each dataset...')

            plots = len (self.names)
            rows = numpy.ceil (plots / columns)
            pylab.figure (figsize = (8 * columns, 5 * rows))

            for plot, name in enumerate (self.names):
                print ('  : -> For dataset %s...' % name)
                pylab.subplot (rows, columns, plot + 1)
                self._unsuccessfuls (name, scientific)
                pylab.title ('dataset %s' % name)

            pylab.draw ()
            caption = """\
                Diagnostics of the posterior sampler,
                indicating the successes and failures of the likelihood estmation procedures for each replicate dataset.
                Legend:
                green - successfully passed,
                gray - estimation skipped due to (numerically) zero prior,
                red - estimation failure due to failed model simulatios and/or failed PF filtering.
                """
            self.save (figname (save, suffix="unsuccessfuls-replicates" + suffix), caption)

    # plot report for resets of stuck chains.
    def resets (self, scientific=True, save=None, suffix=""):
        """Plot report for resets of stuck chains."""

        print (' :: Plotting resets...')

        pylab.figure()

        resets = numpy.array ([info ['resets'] for info in self.infos])
        resets = numpy.where (resets != 0, resets, float ('nan'))
        width = 0.8 if self.batches < 101 else 1.0
        label = 'chain resets (cumulative: %.1f%%)' % (100 * numpy.nansum (resets) / (self.chains * self.batches))
        pylab.bar (self.indices, resets, color = "firebrick", width = width, label=label)
        pylab.ylabel ("counts")
        pylab.ylim ((0, 1.05 * self.chains))
        pylab.xlabel ("sample batch")
        pylab.xlim ((self.indices [0] - 0.5, self.indices [-1] + 0.5))
        pylab.axhline (self.chains, color='gray', linestyle='-', alpha=0.5, lw=5)
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        if self.legend:
            pylab.legend (loc="best")

        if self.title:
            pylab.title ("resets of stuck chains")
        pylab.draw()
        caption = """\
            The report for the number of resets (re-estimation of the marginal likelihood)
            for stuck Markov chains,
            including the cumulative percentage of resets relative to the total number of samples.
            """
        self.save (figname (save, suffix="resets" + suffix), caption)

    def _redraw (self, name, percentile, scientific):
        """Internal routine for 'redraw (...)' plot."""

        means = numpy.empty (len (self.infos))
        lower = numpy.empty (len (self.infos))
        upper = numpy.empty (len (self.infos))
        mins = numpy.empty (len (self.infos))
        maxs = numpy.empty (len (self.infos))

        for index, info in enumerate (self.infos):
            available = [ chain for chain in info ['infos'] if chain is not None ]
            if self.replicates:
                values = [redraw for chain in available for redraw in chain ['infos'] [name] ["redraw"] .values() if redraw is not None]
            else:
                values = [redraw for chain in available for redraw in chain ["redraw"] .values() if redraw is not None]
            means [index] = numpy.mean (values) if values != [] else float ('nan')
            lower [index] = numpy.percentile (values, percentile) if values != [] else float ('nan')
            upper [index] = numpy.percentile (values, 100 - percentile) if values != [] else float ('nan')
            mins [index] = numpy.min (values) if values != [] else float ('nan')
            maxs [index] = numpy.max (values) if values != [] else float ('nan')

        pylab.axhline (0, color='gray', linestyle='-', alpha=0.5, lw=5)
        pylab.axhline (1, color='gray', linestyle='-', alpha=0.5, lw=5)

        handles = self.line_and_range (self.indices, lower, means, upper, merged=0, linewidth=2, color="olivedrab")
        handles_range, = pylab.plot (self.indices, mins, 'k-', lw=2, alpha=0.5)
        pylab.plot (self.indices, maxs, 'k-', lw=2, alpha=0.5)
        handles += (handles_range,)

        if self.legend:
            pylab.legend (handles, ["mean", "percentiles (%s - %s)" % (str(percentile), str(100-percentile)), "range"], loc="best")

        if self.title:
            pylab.title("particle redraw rate")
        pylab.xlabel("sample batch")
        pylab.xlim((self.indices [0], self.indices [-1]))
        pylab.ylabel("redraw rate")
        pylab.ylim([-0.05, 1.05])
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

    # plot redraw rate
    def redraw (self, percentile=5, scientific=True, columns=3, save=None, suffix=""):
        """Plot redraw rate."""

        print (' :: Plotting redraw...')

        if self.deterministic:
            print (' :: ERROR: Redraw are not available for deterministic models.')
            return

        if self.replicates:

            if self.sampler.likelihood.likelihood.noresample:
                print (' :: ERROR: Redraw are not available for "noresample = 1".')
                return

            plots = len (self.names)
            rows = numpy.ceil (plots / columns)
            pylab.figure (figsize = (8 * columns, 5 * rows))

            for plot, name in enumerate (self.names):
                print ('  : -> For dataset %s...' % name)
                pylab.subplot (rows, columns, plot + 1)
                self._redraw (name, percentile, scientific)
                pylab.title ('dataset %s' % name)

        else:

            if self.sampler.likelihood.noresample:
                print (' :: ERROR: Redraw are not available for "noresample = 1".')
                return

            pylab.figure ()
            name = None
            self._redraw (name, percentile, scientific)

        pylab.draw ()
        args = {}
        args ['lower'] = str (percentile)
        args ['upper'] = str (100 - percentile)
        caption = """\
            Particle redraw rates (the fraction of surviving particles) in the PF likelihood estimator.
            The solid line indicates the mean,
            the semi-transparent spreads indicate the %(lower)s%% - %(upper)s%% percentiles,
            and the dotted lines indicate the range (minimum and maximum)
            accross multiple concurrent chains of the sampler.
            """ % args
        self.save (figname (save, suffix="redraw" + suffix), caption)

    def _accuracies (self, name, merged, percentile, palette, scientific):
        """Internal routine for 'accuracies (...)' plot."""

        if merged:

            means = numpy.empty (len (self.indices))
            lower = numpy.empty (len (self.indices))
            upper = numpy.empty (len (self.indices))

            for index, batch in enumerate (self.indices):
                deviation = numpy.empty (self.chains)
                # variance = numpy.empty (self.chains)
                for chain in range (self.chains):
                    if self.infos [index] ['infos'] [chain] is not None:
                        if name is None:
                            deviation [chain] = self.infos [index] ['infos'] [chain] ['avg_deviation']
                            # variance [chain] = self.infos [index] ['infos'] [chain] ['variance']
                        else:
                            deviation [chain] = self.infos [index] ['infos'] [chain] ['infos'] [name] ['avg_deviation']
                            # variance [chain] = self.infos [index] ['infos'] [chain] ['infos'] [name] ['variance']
                    else:
                        if self.verbosity:
                            print (' :: WARNING: NaN deviation at', chain, index)
                        deviation [chain] = float ('nan')
                # deviation = numpy.sqrt (variance)
                # likelihoods = self.infos [index] ['likelihoods']
                # extent = numpy.abs (numpy.nanmax (likelihoods))
                # extent = numpy.nanmax (likelihoods) - numpy.nanmin (likelihoods)
                # extent = 4 * numpy.nanstd (likelihoods, ddof=1)
                # extent = numpy.nanpercentile (likelihoods, 90) - numpy.nanpercentile (likelihoods, 10)
                # extent = numpy.abs (numpy.nanpercentile (likelihoods, 90))
                # deviation /= extent
                # arg = numpy.nanargmax (likelihoods)
                # means [index] = deviation [arg]
                means [index] = numpy.nanmean (deviation)
                lower [index] = numpy.nanmin (deviation)
                # lower [index] = numpy.nanpercentile (deviation, percentile)
                upper [index] = numpy.nanmax (deviation)
                # upper [index] = numpy.nanpercentile (deviation, 100 - percentile)

            self.line_and_range (self.indices, lower, means, upper, linewidth=2, color=palette)

        else:

            extents = numpy.empty (len (self.indices))
            for index, batch in enumerate (self.indices):
                likelihood = [ self.infos [index] ['likelihoods'] [chain] for chain in range (self.chains) ]
                extents [index] = numpy.nanmax (likelihood) - numpy.nanmin (likelihood)

            for chain in range (self.chains):
                variance = numpy.empty (len (self.infos))
                for index, info in enumerate (self.infos):
                    if info ['infos'] [chain] is not None:
                        if name is None:
                            variance [index] = info ['infos'] [chain] ['variance']
                        else:
                            variance [index] = info ['infos'] [chain] ['infos'] [name] ['variance']
                    else:
                        if self.verbosity:
                            print (' :: WARNING: NaN deviation at', chain, index)
                        variance [index] = float ('nan')
                pylab.plot (self.indices, numpy.sqrt (variance) / extents, lw=2, color=palette ['spaghetti'] [chain])

        if not self.replicates:
            likelihood = self.sampler.likelihood
        else:
            likelihood = self.sampler.likelihood.likelihood
        pylab.axhline (0, color='gray', linestyle='-', alpha=0.5, lw=5)
        middle = min (numpy.log (1 + likelihood.accuracy), - numpy.log (1 - likelihood.accuracy))
        upper = min (numpy.log (1 + likelihood.accuracy + likelihood.margin), - numpy.log (1 - likelihood.accuracy - likelihood.margin))
        lower = min (numpy.log (1 + likelihood.accuracy - likelihood.margin), - numpy.log (1 - likelihood.accuracy + likelihood.margin))
        pylab.axhline (middle, color='gray', linestyle='-', alpha=0.5, lw=5)
        pylab.axhline (upper, color='gray', linestyle='--', alpha=0.5, lw=3)
        pylab.axhline (lower, color='gray', linestyle='--', alpha=0.5, lw=3)

        pylab.xlabel ("sample batch")
        pylab.ylabel ("avg. std. deviation of log-error")
        # pylab.ylabel ("std. deviation of log-likelihood")
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
        pylab.xlim ((self.indices [0], self.indices [-1]))
        pylab.ylim ((-0.05 * pylab.ylim()[1], pylab.ylim()[1]))

    def accuracies (self, merged=True, percentile=5, palette=palette['accuracies'], columns=3, scientific=True, save=None, suffix=""):
        """Plot accuracies of the  marginal likelihood estimator (average (over dataset snapshots) standard deviations of the log-error estimates)."""

        if self.deterministic:
            print (' :: ERROR: Accuracies for log-likelihood are not available for deterministic models.')
            return

        print (' :: Plotting accuracies...')

        if self.replicates:

            plots = len (self.names)
            rows = numpy.ceil (plots / columns)
            pylab.figure (figsize = (8 * columns, 5 * rows))

            for plot, name in enumerate (self.names):
                print ('  : -> For dataset %s...' % name)
                pylab.subplot (rows, columns, plot + 1)
                self._accuracies (name, merged, percentile, palette, scientific)
                pylab.title ('dataset %s' % name)

        else:

            pylab.figure ()
            name = None
            self._accuracies (name, merged, percentile, palette, scientific)

        pylab.draw ()
        args = {}
        # args ['lower'] = str (percentile)
        # args ['upper'] = str (100 - percentile)
        args ['replicates'] = ' for each replicate dataset' if self.replicates else ''
        caption = """\
            Average (over dataset snapshots) standard deviations for the estimated marginal observational log-error
            using the PF%(replicates)s.
            The semi-transparent spread indicates the range (minimum and maximumum)
            and the solid line indicates the mean
            accross multiple concurrent chains of the sampler.
            The solid thick gray line above the same line for a zero value reference
            indicates the specified accuracy and
            the dashed thick gray lines indicate the specified margins -
            all specified within the adaptive PF likelihood.
            """ % args
        self.save (figname (save, suffix="accuracies" + suffix), caption)

    def _particles (self, name, particles_min, particles_max, palette, scientific):
        """Internal routine for 'particles (...)' plot."""

        feedbacks = numpy.empty (len (self.indices))
        particles = numpy.empty (len (self.indices))

        for index, batch in enumerate (self.indices):
            if name is None:
                feedbacks [index] = self.infos [index] ['feedback']
                # TODO: plot median and min/max here instead?
                particles [index] = numpy.nanmean ([info ['particles'] for info in self.infos [index] ['infos'] if info is not None])
            else:
                feedbacks [index] = self.infos [index] ['feedback'] [name]
                # TODO: plot median and min/max here instead?
                particles [index] = numpy.nanmean ([info ['infos'] [name] ['particles'] for info in self.infos [index] ['infos'] if info is not None and info ['infos'] [name] is not None])

        pylab.axhline (particles_min, color='gray', linestyle='-', alpha=0.2, lw=5)
        pylab.axhline (particles_max, color='gray', linestyle='-', alpha=0.2, lw=5)

        pylab.plot (self.indices [1:], feedbacks [:-1], linewidth=2, color=brighten(palette), label='feedback')
        pylab.plot (self.indices, particles, linewidth=2, color=palette, label='particles')

        if self.setup is not None and self.setup ['lock (batch)'] is not None:
            pylab.axvline (self.setup ['lock (batch)'], color='forestgreen', linestyle='--', lw=5, alpha=0.5)

        if self.burnin is not None:
            pylab.axvline (self.burnin, color='deepskyblue', linestyle=':', alpha=0.5, lw=5)

        pylab.xlabel ("sample batch")
        pylab.ylabel ("particles")
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
        pylab.xlim ((self.indices [0], self.indices [-1]))
        ylim_min = min (pylab.ylim()[0], particles_min)
        ylim_max = max (pylab.ylim()[1], particles_max)
        extent = ylim_max - ylim_min
        pylab.ylim ((ylim_min - 0.1 * extent, ylim_max + 0.1 * extent))
        if self.title:
            pylab.title ("adaptive number of particles" + (('(dataset %s)' % name) if name is not None else ''))
        pylab.legend (loc="best")

    # plot particles
    def particles (self, palette=palette['particles'], columns=3, scientific=True, save=None, suffix=""):
        """Plot the number of particles used in the marginal parameter likelihood estimation."""

        print (' :: Plotting adaptive particles...')

        if self.deterministic:
            print (' :: ERROR: Particles are not available for deterministic models.')
            return

        if self.replicates:

            particles_min = self.sampler.likelihood.likelihood.particles_min
            particles_max = self.sampler.likelihood.likelihood.particles_max
            plots = len (self.names)
            rows = numpy.ceil (plots / columns)
            pylab.figure (figsize = (8 * columns, 5 * rows))

            for plot, name in enumerate (self.names):
                print ('  : -> For dataset %s...' % name)
                pylab.subplot (rows, columns, plot + 1)
                self._particles (name, particles_min, particles_max, palette, scientific)
                pylab.title ('dataset %s' % name)

        else:

            pylab.figure ()
            name = None
            particles_min = self.sampler.likelihood.particles_min
            particles_max = self.sampler.likelihood.particles_max
            self._particles (name, particles_min, particles_max, palette, scientific)

        pylab.draw ()
        args = {}
        args ['replicates'] = ' for each replicate dataset' if self.replicates else ''
        if self.setup is not None and self.setup ['lock (batch)'] is not None:
            args ['lock'] = ' The vertical dashed green line indicates the sample batch, from which onwards the number of particles was locked.'
        else:
            args ['lock'] = ''
        if self.burnin is not None:
            args ['burnin'] = ' The vertical dotted blue line indicates the end of the specified burnin period.'
        else:
            args ['burnin'] = ''
        caption = """\
            The adaptavity of the number of particles in the PF likelihood%(replicates)s.
            The brighter line indicates the feedback (recommendation) of the adaptation algorithm,
            and the darker line indicates the actual number of used particles.
            The semi-transparent thick gray lines indicate the limits
            for minimum and the maximum number of allowed particles in the PF likelihood.%(lock)s%(burnin)s
            """ % args
        self.save (figname (save, suffix="particles" + suffix), caption)

    # plot acceptances
    def acceptances (self, merged=True, palette=palette['acceptances'], scientific=True, save=None, suffix="", start=None):
        """Plot acceptancess."""

        print (' :: Plotting acceptances...')

        # ignore the first batch if the burn-in was not removed
        if start is None:
            if not self.burnin:
                start = 1
            else:
                start = 0

        # check if available
        if 'accepts' not in self.infos [0]:
            print ('  -> Acceptances not available')
            return None

        pylab.figure()

        # plot acceptances

        acceptances = {}
        for chain in range (self.chains):
            acceptances [chain] = [ info ['accepts'] [chain] for info in self.infos [start:] ]

        if merged:

            means = numpy.empty (len (self.indices) - start)

            for index, batch in enumerate (self.indices [start:]):
                accept = [ acceptances [chain] [index] for chain in range (self.chains) ]
                means [index] = numpy.nanmean (accept)

            pylab.axhline (0, color='gray', linestyle='-', alpha=0.5, lw=5)
            pylab.axhline (1, color='gray', linestyle='-', alpha=0.5, lw=5)

            handles, = pylab.plot (self.indices [start:], means, linewidth=2, color=palette)

        else:

            pylab.axhline (0, color='gray', linestyle='-', alpha=0.5, lw=5)
            pylab.axhline (1, color='gray', linestyle='-', alpha=0.5, lw=5)
            for chain in range (self.chains):
                handles, = pylab.plot (self.indices [start:], acceptances [chain], color=palette ['spaghetti'][chain], linewidth=2)

        pylab.plot (self.indices [start:], means, linewidth=2, color=palette)

        pylab.ylabel("acceptance rate")
        pylab.xlabel ("sample batch")
        pylab.ylim((-0.05, 1.05))
        pylab.xlim((self.indices [0], self.indices [-1]))
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
        if self.title:
            pylab.title ("acceptance rate")
        pylab.draw ()
        caption = """\
            Acceptance rate (accross multiple concurrent chains of the sampler)
            for the proposed parameters samples.
            """
        self.save (figname (save, suffix="acceptances" + suffix), caption)

        return handles

    # plot autocorrelations
    def autocorrelations (self, columns=3, save=None, suffix='', minlength=3):
        """Plot autocorrelations."""

        print (' :: Plotting autocorrelations...')

        if self.batches < 3:
            print ('  : -> Autocorrelations plot requires at least 3 batches - skipping.')
            return None

        plots = len (self.samples.columns)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (8 * columns, 5 * rows))

        for plot, (label, series) in enumerate (self.samples.iteritems ()):
            print ('  : -> For %s...' % label)
            pylab.subplot (rows, columns, plot + 1)
            maxlag = self.batches // minlength
            upper = numpy.empty (maxlag + 1, dtype=float)
            means = numpy.empty (maxlag + 1, dtype=float)
            lower = numpy.empty (maxlag + 1, dtype=float)
            for lag in range (maxlag + 1):
                acors = [ series [chain::self.chains] .autocorr (lag = lag) for chain in range (self.chains) ]
                upper [lag] = numpy.nanmax (acors)
                means [lag] = numpy.nanmean (acors)
                lower [lag] = numpy.nanmin (acors)
            self.line_and_range (range (1, maxlag + 1), lower [1:], means [1:], upper [1:], color='r', linewidth = 2, rangestyle=':')
            pylab.axhline (-1, color='gray', linestyle='-', alpha=0.5, lw=5)
            pylab.axhline (1, color='gray', linestyle='-', alpha=0.5, lw=5)
            pylab.xlabel ('lag')
            pylab.ylabel ('autocorrelation of %s' % label)
            pylab.ylim ((-1.05, 1.05))
        pylab.draw ()
        caption = """\
            Autocorrelations of Markov chain parameters samples.
            The solid lines indicate the mean
            and the semi-transparent spreads indicate the range (minimum and maximum)
            accross multiple concurrent chains of the sampler.
            """
        self.save(figname(save, suffix="autocorrelations" + suffix), caption)

    def ESS (self):
        """
        Compute Effective Sample Size (ESS).

        Implementation based on:
        https://www.tensorflow.org/probability/api_docs/python/tfp/mcmc/effective_sample_size
        i.e.
        R_k := Covariance{X_1, X_{1+k}} / Variance{X_1}
        ESS(N) = N / [ 1 + 2 * ( (N - 1) / N * R_1 + ... + 1 / N * R_{N-1} ) ]
        """

        print (' :: Computing Effective Sample Size (ESS)...')

        if self.batches < 2:
            print ('  : -> ESS requires at least 2 batches - skipping.')
            return None

        thins = []
        ess = []
        for chain in range (self.chains):
            thin = {}
            for label, series in self.samples.iteritems ():
                acors = numpy.array ([ series [chain::self.chains] .autocorr (lag = lag) for lag in range (self.batches - 1) ])
                cutoff = min (numpy.argmax (acors < 0), numpy.argmax (numpy.isnan (acors)))
                thin [label] = int (numpy.round (1 + 2 * numpy.sum (acors [1:cutoff] * numpy.arange (self.batches - 1, self.batches - cutoff, -1) / self.batches )))
            max_thin = numpy.max (list (thin.values ()))
            thins += [max_thin]
            ess += [self.batches // max_thin]

        # store thin periods
        self.thins = thins

        # store metrics
        self._metrics ['Univariate thin period'] = '%d - %d (across chains), with mean %d' % (numpy.min (thins), numpy.max (thins), numpy.mean (thins))
        self._metrics ['Univariate Effective Sample Size (ESS)'] = '%d - %d (across chains), with average %d and sum %d' % (numpy.min (ess), numpy.max (ess), numpy.mean (ess), numpy.sum (ess))

        # compute multivariate version as well
        self.mESS ()

        return thins, ess

    def mESS (self):
        """
        Compute mutivariate Effective Sample Size (mESS).

        Implementation based on:
        https://stats.stackexchange.com/questions/49570/effective-sample-size-for-posterior-inference-from-mcmc-sampling
        https://arxiv.org/abs/1512.07713
        """

        print (' :: Computing multivariate Effective Sample Size (mESS)...')

        print ('  : -> not implemented.')

        self._metrics ['Multivariate thin period'] = 'not implemented'
        self._metrics ['Multivariate Effective Sample Size (mESS)'] = 'not implemented'

        return None, None

    # plot posterior model predictions including observations
    def predictions (self, datasets=None, labels=None, MAP=True, bins=200, kde=True, log=False, yrel_limits=[0.05, 99.95], percentile=None, exact=True, scientific=True, columns=3, save=None, suffix=""):
        """Plot posterior model predictions including observations."""

        print (' :: Plotting predictions for each dataset...')

        if datasets is None:
            if self._datasets is not None:
                datasets = self._datasets
            else:
                print ("  : -> WARNING: Datasets not provided and not specified in the constructor.")

        if labels is None:
            labels = list (list (datasets.values ()) [0] .columns.values)

        plots = len (labels)
        rows = numpy.ceil (plots / columns)

        for name, dataset in datasets.items ():

            print (' : -> For dataset', name)
            pylab.figure (figsize = (8 * columns, 5 * rows))

            if self.transform is not None:
                MAP_parameters = self._MAP ['parameters'] if self._MAP is not None else None
                transformed_labels = self.transform (dataset.iloc [0], MAP_parameters) .index

            for plot, label in enumerate (labels):

                times = dataset.index

                lower = numpy.empty (len (times))
                upper = numpy.empty (len (times))

                interval = [float ('inf'), float ('-inf')]
                values = {}
                weights = {}
                last = [ None for chain in range (self.chains) ]

                for index, time in enumerate (times):
                    values [time] = []
                    weights [time] = []
                    for sample, info in enumerate (self.infos):
                        if not self.replicates:
                            available = [ (chain, chaininfo) for chain, chaininfo in enumerate (info ['infos']) if chaininfo is not None and chaininfo ['successful'] ]
                            for chain, chaininfo in available:
                                if info ['accepts'] [chain]:
                                    last [chain] = []
                                    if self.deterministic:
                                        value = chaininfo ['predictions'] [time] [label]
                                        values [time] += [value]
                                        weights [time] += [1]
                                        last [chain] += [(1, value)]
                                    else:
                                        for i, value in enumerate (chaininfo ['predictions'] [time] [label] .values):
                                            weight = chaininfo ['weights'] [time] [i]
                                            values [time] += [value]
                                            weights [time] += [weight]
                                            last [chain] += [(weight, value)]
                                else:
                                    if last [chain] is None:
                                        for source in range (sample - 1, -1, -1):
                                            lastinfo = self.infos [source] ['infos'] [chain]
                                            if lastinfo is not None and lastinfo ['successful'] and self.infos [source] ['accepts'] [chain]:
                                                last [chain] = []
                                                if self.deterministic:
                                                    value = lastinfo ['predictions'] [time] [label]
                                                    values [time] += [value]
                                                    weights [time] += [1]
                                                    last [chain] += [(1, value)]
                                                else:
                                                    for i, value in enumerate (lastinfo ['predictions'] [time] [label] .values):
                                                        weight = lastinfo ['weights'] [time] [i]
                                                        values [time] += [value]
                                                        weights [time] += [weight]
                                                        last [chain] += [(weight, value)]
                                                break
                                    if last [chain] is not None:
                                        for weight, value in last [chain]:
                                            values [time] += [value]
                                            weights [time] += [weight]

                        else:
                            available = [ (chain, chaininfo) for chain, chaininfo in enumerate (info ['infos']) if chaininfo is not None and chaininfo ['infos'] [name] ['successful'] ]
                            for chain, chaininfo in available:
                                if info ['accepts'] [chain]:
                                    last [chain] = []
                                    if self.deterministic:
                                        value = chaininfo ['infos'] [name] ['predictions'] [time] [label]
                                        values [time] += [value]
                                        weights [time] += [1]
                                        last [chain] += [(1, value)]
                                    else:
                                        for i, value in enumerate (chaininfo ['infos'] [name] ['predictions'] [time] [label] .values):
                                            weight = chaininfo ['infos'] [name] ['weights'] [time] [i]
                                            values [time] += [value]
                                            weights [time] += [weight]
                                            last [chain] += [(weight, value)]
                                else:
                                    if last [chain] is None:
                                        for source in range (sample - 1, -1, -1):
                                            lastinfo = self.infos [source] ['infos'] [chain]
                                            if lastinfo is not None and lastinfo ['infos'] [name] ['successful'] and self.infos [source] ['accepts'] [chain]:
                                                last [chain] = []
                                                if self.deterministic:
                                                    value = lastinfo ['infos'] [name] ['predictions'] [time] [label]
                                                    values [time] += [value]
                                                    weights [time] += [1]
                                                    last [chain] += [(1, value)]
                                                else:
                                                    for i, value in enumerate (lastinfo ['infos'] [name] ['predictions'] [time] [label] .values):
                                                        weight = lastinfo ['infos'] [name] ['weights'] [time] [i]
                                                        values [time] += [value]
                                                        weights [time] += [weight]
                                                        last [chain] += [(weight, value)]
                                                break
                                    if last [chain] is not None:
                                        for weight, value in last [chain]:
                                            values [time] += [value]
                                            weights [time] += [weight]

                    replicated = [ value for i, value in enumerate (values [time]) for copy in range (weights [time] [i]) ]
                    if percentile is not None:
                        try:
                            lower [index] = numpy.percentile (replicated, percentile)
                            upper [index] = numpy.percentile (replicated, 100 - percentile)
                        except:
                            if self.verbosity:
                                print (' :: WARNING: percentiles failed for', label, name, time)
                            lower [index] = float ('nan')
                            upper [index] = float ('nan')
                    lowest = numpy.percentile (replicated, min (percentile, 1) if percentile is not None else 1)
                    highest = numpy.percentile (replicated, max (100 - percentile, 99) if percentile is not None else 99)
                    if label in list (dataset.columns.values):
                        lowest = min (lowest, dataset.loc [time] [label])
                        highest = max (highest, dataset.loc [time] [label])
                    if lowest < interval [0]:
                        interval [0] = lowest
                    if highest > interval [1]:
                        interval [1] = highest

                extent = interval [1] - interval [0]
                interval [0] -= 0.1 * extent
                interval [1] += 0.1 * extent

                processed = False
                if self.types ['predictions'] is not None and self.types ['predictions'] [label] == 'int':
                    start = int (numpy.floor (interval [0]))
                    end = int (numpy.ceil (interval [1]))
                    count = end + 1 - start
                    if count <= 50:
                        processed = True
                        densities = numpy.empty ((len (times), count))
                        for index, time in enumerate (times):
                            clipped = values [time] [values [time] >= start and values [time] <= end]
                            densities [index] [:] = numpy.bincount (clipped - start, weights = weights [time], minlength=count)

                if not processed:
                    densities = numpy.empty ((len (times), bins))
                    for index, time in enumerate (times):
                        if kde:
                            try:
                                x = numpy.linspace (interval [0], interval [1], bins)
                                densities [index] [:] = self.kde (values [time], x, weights = weights [time])
                            except:
                                print ('  : -> WARNING: kde failed for %s, falling back to historgram.' % label)
                                densities [index] [:], edges = numpy.histogram (values [time], weights=weights [time], bins=bins, range=interval, density=True)
                        else:
                            densities [index] [:], edges = numpy.histogram (values [time], weights=weights [time], bins=bins, range=interval, density=True)

                pylab.subplot (rows, columns, plot + 1)
                self.histogram (label, times, densities, interval, "spux_orange", log=log)

                handles = []
                legend = []

                # get MAP estimate and plot it
                if MAP and self._MAP is not None:
                    if self.replicates:
                        MAP_values = [ self._MAP ['predictions'] [name] [time] [label] for time in times ]
                    else:
                        MAP_values = [ self._MAP ['predictions'] [time] [label] for time in times ]
                    map_handle, = pylab.plot (times, MAP_values, color='brown', alpha=0.5)
                    handles += [map_handle]
                    legend += ["approximate MAP"]

                # plot exact predictions, if available
                exact_predictions = False
                if exact and self.exact is not None and 'predictions' in self.exact and self.exact ['predictions'] is not None:
                    exact_predictions = True
                    if self.replicates:
                        exact_series = self.exact ['predictions'] [name] [label]
                    else:
                        exact_series = self.exact ['predictions'] [label]
                    exact_handle, = pylab.plot (times, exact_series, color='red', alpha=0.5)
                    handles += [exact_handle]
                    legend += ["exact model predictions"]

                if percentile is not None:
                    middle = None
                    percentile_handle = self.line_and_range (times, lower, middle, upper, linewidth=2, color='dimgray', alpha=0.5, merged=False, fill=False)
                    handles += [percentile_handle [1]]
                    legend += ["posterior percentiles (%s - %s)" % (str(percentile), str(100-percentile))]

                if self.transform and label in transformed_labels:
                    transformed = {i : self.transform (dataset, MAP_parameters) [label] for i, dataset in dataset.iterrows ()}
                    single_dataset = pandas.DataFrame.from_dict (transformed, orient = 'index', columns = [label]).sort_index ()
                    dataset_handle = self.dataset (single_dataset, frame=1)
                    handles += [dataset_handle]
                    legend += ["dataset"]
                elif label in list (dataset.columns.values):
                    dataset_handle = self.dataset (dataset, labels=[label], frame=1)
                    handles += [dataset_handle]
                    legend += ["dataset"]

                pylab.ylabel (label)
                pylab.xlabel (dataset.index.name)
                pylab.ylim (interval)
                if self.title:
                    pylab.title ("posterior predictions for dataset " + name)
                if self.legend:
                    pylab.legend (handles, legend, loc="best")
                if scientific:
                    pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

                pylab.draw()

                args = {}
                args ['name'] = (' %s' % name) if self.replicates else ''
                args ['exact'] = ', the red line represents the exact model prediction values.' if exact_predictions else ''
                args ['MAP'] = ', the brown line indicates the approximate MAP model prediction.' if MAP and self._MAP is not None else ''
                if percentile is not None:
                    args ['percentiles'] = ', the thin gray lines indicate the %s%% - %s%% percentiles accross all posterior samples.' % (str (percentile), str (100 - percentile))
                else:
                    args ['percentiles'] = ''
                caption = """\
                    Posterior distribution of model predictions for the observational dataset%(name)s.
                    The shaded orange regions indicate
                    the log-density of the posterior model predictions distribution at the respective time points%(MAP)s%(percentiles)s%(exact)s
                    """ % args
                if self.replicates:
                    self.save (figname (save, suffix="predictions-posterior-%s%s" % (name, suffix)), caption)
                else:
                    self.save (figname (save, suffix="predictions-posterior%s" % suffix), caption)

    # plot quantile-quantile comparison of the error and residual distributions
    def QQ (self, error=None, datasets=None, columns=3, seed=1, scientific=True, save=None, suffix=""):
        """ Plot quantile-quantile comparison of the error and residual distributions."""

        print (' :: Plotting QQ for each observed quantity...')

        if error is None:
            if self._error is not None:
                error = self._error
            else:
                print ("  : -> SKIPPING: Error not provided and not specified in the constructor.")
                return

        if datasets is None:
            if self._datasets is not None:
                datasets = self._datasets
            else:
                print ("  : -> SKIPPING: Datasets not provided and not specified in the constructor.")
                return

        data_labels = list (datasets.values ()) [0] .columns.values

        plots = len (data_labels)
        rows = numpy.ceil (plots / columns)
        pylab.figure (figsize = (8 * columns, 5 * rows))

        rng = numpy.random.RandomState (seed=seed)

        parameters = self._MAP ['parameters']
        name = list (datasets.keys ()) [0]
        if self.replicates:
            predictions = list (self._MAP ['predictions'] [name] .values ()) [0]
        else:
            predictions = list (self._MAP ['predictions'] .values ()) [0]
        if hasattr (error, 'transform'):
            error_labels = list (error.transform (list (datasets.values ()) [0] .iloc [0], parameters) .index)
        else:
            error_labels = data_labels

        # compute residuals and draw theoretical random error samples
        residuals = {}
        errors = {}
        for plot, data_label in enumerate (data_labels):
            error_label = error_labels [plot]
            print (' : -> For', error_label)
            residuals [data_label] = numpy.array ([], dtype=float)
            errors [data_label] = numpy.array ([], dtype=float)
            for name, dataset in datasets.items ():
                if self.replicates:
                    predictions = self._MAP ['predictions'] [name]
                else:
                    predictions = self._MAP ['predictions']
                index = dataset [data_label] .dropna () .index
                if hasattr (error, 'transform'):
                    dt = lambda i : error.transform (dataset.loc [i], parameters)
                    pt = lambda i : error.transform (predictions [i], parameters)
                    r = [ dt (i) [error_label] - pt (i) [error_label] for i in index ]
                else:
                    r = [ dataset.loc [i] [data_label] - predictions [i] [data_label] for i in index ]
                residuals [data_label] = numpy.hstack ([residuals [data_label], r])
                if hasattr (error, 'transform'):
                    e = [ error.distribution (pt (i), parameters).draw (rng=rng) [error_label] - pt (i) [error_label] for i in index ]
                else:
                    e = [ error.distribution (predictions [i], parameters).draw (rng=rng) [error_label] - predictions [i] [error_label] for i in index ]
                errors [data_label] = numpy.hstack ([errors [data_label], e])
            pylab.subplot (rows, columns, plot + 1)
            pylab.plot (sorted (errors [data_label]), sorted (residuals [data_label]), marker='.', color='spux_orange', linewidth=0, markersize=10, markeredgewidth=0, alpha=0.8)
            lim0 = min (numpy.min (errors [data_label]), numpy.min (residuals [data_label]))
            lim1 = max (numpy.max (errors [data_label]), numpy.max (residuals [data_label]))
            lim = [lim0, lim1]
            pylab.plot (lim, lim, linestyle='--', color='gray', linewidth=2, alpha=0.8)
            pylab.xlabel ('theoretical error quantiles')
            pylab.ylabel ('posterior residual quantiles')
            pylab.title ('QQ plot for ' + error_label)
            pylab.gca().set_aspect ('equal')
            if scientific:
                pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        pylab.draw ()
        caption = """\
            Quantile-quantile distribution comparison between the prediction residuals and the specified error model.
            """
        self.save (figname (save, suffix="qq%s" % suffix), caption)

    # # plot predictive quantile-quantile comparison of the dataset and posterior model predictions distributions
    # def PQQ (self, error=None, datasets=None, columns=3, seed=1, scientific=True, save=None, suffix=""):
    #     """ Plot quantile-quantile comparison of the error and residual distributions."""

    #     print (' :: Plotting PQQ for each observed quantity and each dataset...')

    # make plots in log-quantities, if possible - this will allow to easily see scaling factor as well

    # compute Nash-Sutcliffe model efficiency
    def NSE (self, label, datasets=None):
        """Nash-Sutcliffe model efficiency."""

        print (' :: Computing Nash-Sutcliffe efficiency (NSE) for the model...')

        if datasets is None:
            if self._datasets is not None:
                datasets = self._datasets
            else:
                print ("  : -> SKIPPING: Datasets not provided and not specified in the constructor.")
                return

        NSE = {}
        for name, dataset in datasets.items ():
            data_values = numpy.array (dataset [label] .values)
            mean = numpy.nanmean (data_values)
            if self.replicates:
                MAP = self._MAP ['predictions'] [name]
            else:
                MAP = self._MAP ['predictions']
            prediction_values = numpy.array ([ MAP [time] [label] for time in dataset.index ])
            differences = data_values - prediction_values
            upper = numpy.nansum (differences ** 2)
            lower = numpy.nansum ((data_values - mean) ** 2)
            NSE [name] = 1 - (upper / lower)

        self._metrics ['Nash-Sutcliffe efficiency (NSE)'] = NSE

        return NSE

    def metrics (self):
        """Generate a metrics table, print it, and also dump it."""

        print (' :: Combining available metrics...')

        entries = [{'Metric' : header, 'Value' : self._metrics [header]} for header in sorted (list (self._metrics.keys ()))]
        headers = ['Metric', 'Value']
        title = 'Metrics for the inference efficiency.'
        dumper.report (self.reportdir, 'metrics', self._metrics, title, entries, headers)

    # plot traffic
    def traffic (self, keys=["move", "copy", "kill"], palette=palette['traffic'], scientific=True, save=None, suffix=""):
        """Plot traffic."""

        print (' :: Plotting traffic...')

        if keys is None:
            keys = palette ['keys']
        colors = palette ['colors']
        present = set ()

        pylab.figure ()
        handles = []

        for key in keys:

            means = numpy.empty (len (self.infos))
            lower = numpy.empty (len (self.infos))
            upper = numpy.empty (len (self.infos))

            for index, info in enumerate (self.infos):
                available = [ chain for chain in info ['infos'] if chain is not None ]
                values = [ traffic [key] for chain in available for replicate in chain ['infos'] .values () for traffic in replicate ["traffic"] .values() if key in traffic ]
                if values != []:
                    present = present | {key}
                means [index] = numpy.nanmedian (values) if values != [] else float ('nan')
                lower [index] = numpy.nanmin (values) if values != [] else float ('nan')
                upper [index] = numpy.nanmax (values) if values != [] else float ('nan')

            if key in present:
                handles.append (self.line_and_range (self.indices, lower, means, upper, linewidth=2, color=colors [key], rangestyle=':'))

        if self.legend:
            pylab.legend (handles, present, loc="best")
        if self.title:
            pylab.title ("traffic fractions")
        pylab.xlabel ("sample batch")
        pylab.xlim ((self.indices[0], self.indices[-1]))
        pylab.ylabel ("traffic [fraction]")
        if scientific:
            pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))
        pylab.ylim ([-0.05, 1.05])
        pylab.draw ()
        caption = """\
            Traffic of the model states within the resampling step of the PF likelihood.
            """
        self.save (figname (save, suffix="traffic" + suffix), caption)

    # plot runtimes
    def runtimes (self, keys=None, palette=palette['runtimes'], percentile=0, columns=3, legendpos="", scientific=True, save=None, suffix=""):
        """Plot runtimes."""

        print (' :: Plotting runtimes...')

        if not self.replicates or self.deterministic:
            print (' :: ERROR: runtimes plots are not yet implemented for non-replicates likelihood or non-stochatic model.')
            return

        if keys is None:
            keys = list (palette ['colors'])

        indices = numpy.arange ((len (self.infos)) * self.chains)

        if self.replicates:

            plots = len (self.names)
            rows = numpy.ceil (plots / columns)

            pylab.figure (figsize = (8 * columns, 5 * rows))

            for plot, name in enumerate (self.names):

                pylab.subplot (rows, columns, plot + 1)
                handles = {}
                present = []

                for key in keys:

                    timing = numpy.empty (len (indices))
                    # mean = numpy.empty (len (indices))
                    # lower = numpy.empty (len (indices))
                    # upper = numpy.empty (len (indices))

                    means = numpy.empty (len (indices))
                    lowers = numpy.empty (len (indices))
                    uppers = numpy.empty (len (indices))

                    scalar = False

                    for index, infos in enumerate (self.infos):
                        for chain, info in enumerate (infos ['infos']):

                            timings = []

                            if info is not None and info ['infos'] [name] is not None:
                                replicate = info ['infos'] [name]
                                if key in replicate ['timing'] .runtimes.keys ():
                                    if key not in present:
                                        present += [key]
                                    scalar = True
                                    timing [index * self.chains + chain] = replicate ['timing'] .runtimes [key]
                                else:
                                    for worker in replicate ['timings']:
                                        if key in worker.runtimes.keys ():
                                            if key not in present:
                                                present += [key]
                                            timings += [ worker.runtimes [key] ]
                            else:
                                timing [index * self.chains + chain] = float ('nan')

                            # mean [index * self.chains + chain] = numpy.nanmedian (timing) if timing != [] else float ('nan')
                            # lower [index * self.chains + chain] = numpy.nanpercentile (timing, percentile) if timing != [] else float ('nan')
                            # upper [index * self.chains + chain] = numpy.nanpercentile (timing, 100 - percentile) if timing != [] else float ('nan')

                            means  [index * self.chains + chain] = numpy.nanmedian (timings) if timings != [] else float ('nan')
                            lowers [index * self.chains + chain] = numpy.nanpercentile (timings, percentile) if timings != [] else float ('nan')
                            uppers [index * self.chains + chain] = numpy.nanpercentile (timings, 100 - percentile) if timings != [] else float ('nan')

                    color = palette ['colors'] [key]
                    style = ":" if any ([comm in key for comm in ["wait", "scatter", "sync", "gather"]]) else "-"

                    if scalar:
                        handles [key], = pylab.plot (indices, timing, style, color=color)
                    else:
                        handles [key] = self.line_and_range (indices, lowers, means, uppers, color=color, linewidth=2, style=style)

                legend_keys = [key for key in palette ['order'] if key in present]
                legend_handles = [handles [key] for key in legend_keys]

                pylab.legend (legend_handles, legend_keys, loc="best")
                # if len (legend_keys) <= 7:
                #     pylab.legend (legend_handles, legend_keys, loc="best")
                # else:
                #     pylab.legend (legend_handles, legend_keys, loc="center left", bbox_to_anchor=(1, 0.5))
                if self.title:
                    pylab.title ("runtimes")
                pylab.xlabel ("sample batch")
                pylab.xlim ((indices[0], indices[-1]))
                pylab.ylabel ("runtime [s]")
                if scientific:
                    pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        pylab.draw ()
        caption = """\
            Runtimes of key SPUX component methods.
            """
        self.save (figname (save, suffix="runtimes" + suffix), caption)

    # plot efficiency: (init + run + errors + kill + replicate) / evaluate
    def efficiency (self, palette=palette['efficiency'], percentile=0, columns=3, scientific=True, save=None, suffix=""):
        """Plot efficiency."""

        print (' :: Plotting efficiency...')

        if not self.replicates or self.deterministic:
            print (' :: ERROR: efficiency plots are not yet implemented for non-replicates likelihood or non-stochatic model.')
            return

        keys = ['init', 'run', 'errors', 'kill', 'clone']

        indices = numpy.arange ((len (self.infos)) * self.chains)

        if self.replicates:

            plots = len (self.names)
            rows = numpy.ceil (plots / columns)

            pylab.figure (figsize = (8 * columns, 5 * rows))

            for plot, name in enumerate (self.names):

                pylab.subplot (rows, columns, plot + 1)

                means = {}
                # upper = {}
                # lower = {}

                for key in keys:

                    means [key] = numpy.empty (len (indices))
                    # lower [key] = numpy.empty (len (indices))
                    # upper [key] = numpy.empty (len (indices))

                    for index, infos in enumerate (self.infos):
                        for chain, info in enumerate (infos ['infos']):

                            timings = []

                            if info is not None and info ['infos'] [name] is not None:
                                for worker in info ['infos'] [name] ['timings']:
                                    if key in worker.runtimes.keys ():
                                        timings += [ worker.runtimes [key] ]

                            means [key] [index * self.chains + chain] = numpy.nanmean (timings) if timings != [] else 0
                            # lower [key] [index * self.chains + chain] = numpy.nanpercentile (timings, percentile) if timings != [] else 0
                            # upper [key] [index * self.chains + chain] = numpy.nanpercentile (timings, 100 - percentile) if timings != [] else 0

                evaluate = numpy.empty (len (indices))
                for index, infos in enumerate (self.infos):
                    for chain, info in enumerate (infos ['infos']):
                        if info is not None:
                            replicate = info ['infos'] [name]
                            evaluate [index * self.chains + chain] = replicate ['timing'] .runtimes ['evaluate']
                        else:
                            evaluate [index * self.chains + chain] = float ('nan')

                efficiencies = numpy.zeros (len (indices))
                for key in keys:
                    efficiencies += means [key]
                efficiencies /= evaluate

                pylab.plot (indices, efficiencies, color = palette, lw=2)

                if self.title:
                    pylab.title ("parallelization efficiency")
                pylab.xlabel ("sample batch")
                pylab.xlim ((indices[0], indices[-1]))
                pylab.ylabel ("parallelization efficiency")
                pylab.ylim ([-0.05, 1.05])
                if scientific:
                    pylab.gca().ticklabel_format (axis='both', style='sci', scilimits=(-2, 2))

        pylab.draw ()
        caption = """\
            Efficiency of the parallel resampling within the PF likelihood.
            """
        self.save (figname (save, suffix="efficiency" + suffix), caption)

    # plot timestamps
    def timestamps (self, keys=None, sample=None, name=None, limit=None, palette=palette["runtimes"], scientific=True, save=None, suffix=""):

        print (' :: Plotting timestamps...')

        if self.replicates and name is None:
            name = self.names [0]

        if sample is None or sample == 'last':
            label = 'last'
            sample = len (self.samples) - 1
        elif sample == 'first':
            label = 'first'
            sample = self.indices [0]
        else:
            replicate = ('-R-%s' % str (name)) if self.replicates else ''
            label = 'S%05d%s' % (sample, replicate)

        if limit is None:
            limit = 20 if keys is None else (len (keys) + 4)

        index = sample // self.chains
        chain = sample - index * self.chains

        reference = self.infos [index] ['infos'] [chain]
        if self.replicates:
            reference = reference ['infos'] [name]
        if 'timing' not in reference:
            print (' :: SKIPPING: "timing" not found in infos.')
            print ('  : -> Did you accidentaly set "informative = 0" in sampler.setup (...)?')
            print ('  : -> If not, were all requested samples generated succesfully?')
            return
        start = reference ["timing"] .timestamps ["evaluate"] [0] [0]
        final = reference ["timing"] .timestamps ["evaluate"] [0] [1]

        if keys is None:
            keys = list (reference ['timing'] .timestamps.keys()) + list (reference ['timings'] [0] .timestamps.keys())

        keys = [key for key in palette ['order'] if key in keys]

        present = []

        offset = lambda timestamp: (timestamp [0] - start, timestamp [1] - start)
        linewidth = 0.6
        patch = lambda timestamp, level: (
            (timestamp [0], level - 0.5 * linewidth),
            timestamp [1] - timestamp [0],
            linewidth,
        )

        pylab.figure (figsize = (16, 10))
        handles = {}
        total = 1

        for key in keys:

            color = palette ['colors'] [key]
            alpha = 0.5 if any ([comm in key for comm in ["wait", "scatter", "sync", "gather"]]) else 1.0

            info = self.infos [index] ['infos'] [chain]
            if self.replicates:
                info = info ['infos'] [name]

            if key in info ['timing'] .runtimes.keys ():
                if key not in present:
                    present += [key]
                timestamps = info ['timing'] .timestamps [key]
                for timestamp in timestamps:
                    xy, w, h = patch (offset (timestamp), 0)
                    pylab.gca().add_patch (pylab.Rectangle (xy, w, h, color=color, alpha=alpha, linewidth=0))
                    handles [key], = pylab.plot ([], [], color=color, alpha=alpha, linewidth=10)

            else:
                total = min (limit, len (info ['timings']))
                for worker, timing in enumerate (info ['timings']):
                    if limit is not None and worker == limit:
                        break
                    if key in timing.timestamps.keys ():
                        if key not in present:
                            present += [key]
                        timestamps = timing.timestamps [key]
                        for timestamp in timestamps:
                            xy, w, h = patch (offset (timestamp), worker + 1)
                            pylab.gca().add_patch (pylab.Rectangle (xy, w, h, color=color, alpha=alpha, linewidth=0))
                            handles[key], = pylab.plot ([], [], color=color, alpha=alpha, linewidth=10)

        legend_keys = [key for key in palette ['order'] if key in present]
        legend_handles = [handles [key] for key in legend_keys]

        if self.legend:
            pylab.legend (legend_handles, legend_keys, loc = "center left", bbox_to_anchor = (1, 0.5))
        if self.title:
            pylab.title ("timestamps")
        pylab.xlabel ("time [s]")
        pylab.ylabel ("worker")
        pylab.xlim ((0, final - start))
        pylab.ylim ((-0.5, total + 0.5))
        if total <= 20:
            pylab.yticks (range (total + 1), ["M "] + ["%3d " % worker for worker in range (total)])
        pylab.gca().invert_yaxis ()
        pylab.setp (pylab.gca().get_yticklines(), visible = False)
        if scientific:
            pylab.gca().ticklabel_format (axis='x', style='sci', scilimits=(-2, 2))
        pylab.draw ()
        caption = """\
            Timestamps of key methods within a single estimation of the PF likelihood across all parallel workers.
            """
        self.save (figname (save, suffix = ("timestamps-" + label + suffix)), caption)

    # plot scaling and average efficiencies from multiple simulations
    def scaling (self, infosdict, factors={}, palette=palette['scaling'], save=None, suffix=""):
        """Plot scaling and average efficiencies from multiple simulations."""

        print (' :: Plotting scaling...')

        workerslist = list (infosdict.keys ())

        evaluate = {}
        efficiency = {}

        keys = ['init', 'run', 'errors', 'kill', 'clone']
        indices = numpy.arange ((len (self.infos)) * self.chains)

        for workers, infos in infosdict.items ():

            means = {}

            for key in keys:

                means [key] = numpy.empty (len (indices))

                for batch, infos in enumerate (self.infos):
                    for chain, info in enumerate (infos ['infos']):

                        timings = []

                        if info is not None and info ['infos'] [name] is not None:
                            for worker in info ['infos'] [name] ['timings']:
                                if key in worker.runtimes.keys ():
                                    timings += [ worker.runtimes [key] ]

                        means [key] [batch * self.chains + chain] = numpy.nanmean (timings) if timings != [] else 0

            evaluates = numpy.empty (len (indices))
            for batch, infos in enumerate (self.infos):
                for chain, info in enumerate (infos ['infos']):
                    if info is not None:
                        replicate = info ['infos'] [name]
                        evaluates [batch * self.chains + chain] = replicate ['timing'] .runtimes ['evaluate']
                    else:
                        evaluates [batch * self.chains + chain] = float ('nan')

            efficiencies = numpy.zeros (len (indices))
            for key in keys:
                efficiencies += means [key]
            efficiencies /= evaluates

            efficiency [workers] = numpy.nanmean (efficiencies)
            evaluate [workers] = numpy.nanmean (evaluates)

        # apply scaling factors if needed
        if factors != {}:
            for workers, runtime in evaluate.items():
                runtime *= factors [workers]

        pylab.figure ()

        # scaling
        means = [numpy.mean (evaluate [workers]) for workers in workerslist]
        lower = [numpy.percentile (evaluate [workers], 10) for workers in workerslist]
        upper = [numpy.percentile (evaluate [workers], 90) for workers in workerslist]
        linear, = pylab.plot (workerslist, [means[0] * workerslist[0] / workers for workers in workerslist], "--", color=palette ['linear'], linewidth=3, alpha=0.5)
        runtime = self.line_and_range (workerslist, lower, means, upper, color=palette ['runtime'], marker="+", linewidth=3, logx=1, logy=1)
        pylab.ylabel ("runtime [s]")
        pylab.ylim (0.5 * pylab.ylim()[0], 2 * pylab.ylim()[1])
        pylab.xlabel ("number of workers")

        # efficiencies
        pylab.sca (pylab.twinx ())
        means = [numpy.mean (efficiencies [workers]) for workers in workerslist]
        lower = [numpy.percentile (efficiencies [workers], 10) for workers in workerslist]
        upper = [numpy.percentile (efficiencies [workers], 90) for workers in workerslist]
        efficiency = self.line_and_range (workerslist, lower, means, upper, color=palette ['efficiency'], marker="+", linewidth=3, logx=1)
        pylab.ylabel ("efficiency")
        pylab.ylim ([-0.05, 1.05])

        pylab.xlim (0.5 * pylab.xlim()[0], 2 * pylab.xlim()[1])
        if self.title:
            pylab.title ("parallel scaling and efficiency")
        if self.legend:
            pylab.legend ([runtime, linear, efficiency], ["runtime", "linear scaling", "efficiency"], loc="best")
        pylab.draw ()
        caption = """\
            Parallel scaling and paralellization efficiency of the PF likelihood.
            """
        self.save (figname (save, suffix="scaling" + suffix), caption)
