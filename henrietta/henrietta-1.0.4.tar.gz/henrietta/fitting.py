'''
This module contains functions and class definitions to extend the
astropy.modeling toolkit to be visualizeable.
'''

from __future__ import print_function
from .imports import *
from .optimizers import *
from .modeling import BATMAN
from .utilities import decide_writer
from .goodnesses import *

from astropy.modeling import models, fitting, optimizers, statistic, custom_model


# define a custom model, based off our BATMAN function
BatmanTransit = custom_model(BATMAN)

@custom_model
def TrapezoidTransit(t, delta=0.01, P=1, t0=0, T=0.1, tau=0.01, baseline=1.0):

    """
    One dimensional Trapezoid Transit model,
    using the symbols defined for a circular
    transit approximation in Winn (2010).

    This is a fittable astropy model.

    Parameters
    ----------
    delta : float
        The depth of the transit, as a fraction of the out-of-transit flux.
    P : float
        The perio of the planet, in days.
    t0 : float
        Mid-transit time of the transit, in days.
    T : float
        The duration of the transit (from mid-ingress to mid-egress), in days.
    tau : float
        The duration of ingress/egress, in days.

    See Also
    --------
    astropy.modeling.models.Trapezoid1D

    Examples
    --------
    .. plot::
        :include-source:

        import numpy as np
        import matplotlib.pyplot as plt

        from henrietta.fitting import TrapezoidTransit

        plt.figure()
        model = TrapezoidTransit()
        t = np.arange(-5, 5, .01)

        for x in np.linspace(0.02, 0.2, 4):
            model.delta = x
            model.T = x
            plt.plot(t, model(t), lw=2)

        plt.show()
    """

    # calculate a phase-folded time (still in units of days)
    x = (t-t0 + 0.5*P) % P - 0.5*P

    # Compute the four points where the trapezoid changes slope
    # x1 <= x2 <= x3 <= x4

    if tau > T:
        x1 = -tau
        x2 = 0
        x3 = 0
        x4 = tau
    else:
        x1 = - (T+tau)/2.0
        x2 = - (T-tau)/2.0
        x3 = (T-tau)/2.0
        x4 = (T+tau)/2.0

    # Compute model values in pieces between the change points
    range_a = np.logical_and(x >= x1, x < x2)
    range_b = np.logical_and(x >= x2, x < x3)
    range_c = np.logical_and(x >= x3, x < x4)

    if tau == 0:
        slope = np.inf
    else:
        slope = delta/tau
    val_a = 1 - slope * (x - x1)
    val_b = 1 - delta
    val_c = 1 - slope * (x4 - x)
    result = np.select([range_a, range_b, range_c], [val_a, val_b, val_c], default=1)*baseline
    return result

def setup_transit_model(period=1.58,
                        t0=0.0,
                        radius=[0.0, 0.5],
                        a=[3.0, 50.0],
                        b=0.385,
                        baseline=1.0,
                        ld1=0.1, ld2=0.3):
    '''
    This function sets up an astropy transit model, which can then be used for fitting.

    Parameters that are fed in as single values will be held fixed.

    Parameters that are fed in as two-element lists will be varied,
    using the two values as their allowable bounds.

    Parameters
    ----------
    (same as we've seen in other transit modeling)
    '''
    inputs = {}
    names = ['period', 't0', 'radius', 'a', 'b', 'baseline', 'ld1', 'ld2']

    # set up the initial values
    for k in names:
        inputs[k] = np.mean(locals()[k])

    # decide which parameters are fixed and which are not
    model = BatmanTransit(**inputs)
    for k in names:
        if len(np.atleast_1d(locals()[k])) == 2:
            model.fixed[k] = False
            model.bounds[k] = locals()[k]
        else:
            model.fixed[k] = True

    return model

def setup_line_model(slope=[0, 5], intercept=[-10, 10]):
    '''
    This function sets up an astropy line model, which can then be used for fitting.

    Parameters that are fed in as single values will be held fixed.

    Parameters that are fed in as two-element lists will be varied,
    using the two values as their allowable bounds.

    Parameters
    ----------
    slope : float, or 2-element list
        The
    
    '''
    inputs = {}
    names = ['slope', 'intercept']

    # set up the initial values
    for k in names:
        inputs[k] = np.mean(locals()[k])

    # decide which parameters are fixed and which are not
    model = models.Linear1D(**inputs)
    for k in names:
        if len(np.atleast_1d(locals()[k])) == 2:
            model.fixed[k] = False
            model.bounds[k] = locals()[k]
        else:
            model.fixed[k] = True

    return model


class VisualizedStatistic:
    '''
    Objects that inherit from VisualizedStatistic should be a drop-in
    replacement for the astropy.modeling.statistic.leastsq. The simplest
    class definiton that modifies this would simply be to redefine the
    `.name` attribute and the `.goodness()` method.
    '''

    # this may appear in labels
    #name = 'sumofsquares'

    def __init__(self, goodness=sumofsquares, fitter=None):
        '''
        Initialize a visualized statistic, which is connected to a fitter.
        '''
        self.goodness = goodness
        self.name = goodness.__name__
        self.fitter = fitter

    def __call__(self, measured_vals, updated_model, weights, x, y=None):
        """
        Generic goodness-of-fit statistic.

        Parameters
        ----------
        measured_vals : `~numpy.ndarray`
            Measured data values.
        updated_model : `~astropy.modeling.Model`
            Model with parameters set by the current iteration of the optimizer.
        weights : `~numpy.ndarray`
            Array of weights to apply to each residual.
        x : `~numpy.ndarray`
            Independent variable "x" to evaluate the model on.
        y : `~numpy.ndarray`, optional
            Independent variable "y" to evaluate the model on, for 2D models.

        Returns
        -------
        res : float
            The sum of least squares.
        """


        if y is None:
            model_vals = updated_model(x)
        else:
            model_vals = updated_model(x, y)
        if weights is None:
            residuals = (model_vals - measured_vals)
        else:
            residuals = (weights * (model_vals - measured_vals))

        gof = self.goodness(residuals)

        #print(self.fitter._iterations, gof)

        # plot the updated model on the data
        plt.sca(self.fitter.ax['data'])

        # make the previous models fade more, then add a new model
        for l in self.fitter.plotted['data']['models']:
            l.set_alpha(0.95*l.get_alpha())
        newline = plt.plot(x, updated_model(x), zorder=-1, color=l.get_color(), alpha=l.get_alpha(), linewidth=l.get_linewidth())[0]
        self.fitter.plotted['data']['models'].append(newline)

        if len(self.fitter._gof) == 0:
            best = True
        else:
            best = gof < np.min(self.fitter._gof)

        if best:

            # update the best model
            self.fitter.plotted['data']['best'].set_data(x, updated_model(x))

            # update the title
            plt.suptitle('Best Model ({} = {:.4})\n{}'.format(self.name, gof, repr(updated_model)))

            # update the goodness plot
            self.fitter.plotted['gof']['best'].set_data(self.fitter._iterations, gof)



        # plot the current step number and goodness of fit
        plt.sca(self.fitter.ax['gof'])
        self.fitter._iterations += 1
        self.fitter._gof.append(gof)
        self.fitter.plotted['gof']['all'].set_data(np.arange(self.fitter._iterations), self.fitter._gof)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.fitter.ax['gof'].set_xlim(0, self.fitter._iterations+1)
            self.fitter.ax['gof'].set_ylim(np.min(self.fitter._gof), np.max(self.fitter._gof))

        # update the parameters (kludge?)
        interesting = list(self.fitter.plotted['params'].keys())
        for i, p in enumerate(updated_model.param_names):
            if p in interesting:
                self.fitter._parameters[p].append(updated_model.parameters[i])
        # update the goodness
        self.fitter._parameters[self.name] = self.fitter._gof

        # update the plots
        for i, pi in enumerate(interesting):
            for j, pj in enumerate(interesting):
                x = self.fitter._parameters[pj]
                y = self.fitter._parameters[pi]
                if i>j:
                    #print(pj, x)
                    #print(pi, y)
                    #print('---')
                    self.fitter.plotted['params'][pi][pj]['all'].set_data((x, y))
                    if best:
                        self.fitter.plotted['params'][pi][pj]['best'].set_data((x[-1], y[-1]))

                    if pi == self.name:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            self.fitter.ax['params'][pi][pj].set_ylim(np.nanmin(y), np.nanmax(y))



        if self.fitter.animate:
            self.fitter.writer.grab_frame()
            print('Saving frame {} to {}.'.format(self.fitter._iterations, self.fitter.writer.outfile), end='\r')
        else:
            print('Calculating test model #{}.'.format(self.fitter._iterations), end='\r')
        return self.goodness(residuals)

class VisualizedFitter(fitting.Fitter):
    '''
    Objects that inherit from a VisualizedFitter can do the normal
    stuff an astropy.fitting.Fitter can do, but they also visualize
    the process with panels that show what's happening.
    '''
    name = 'fitter'

    """
    def __init__(self, optimizer=optimizers.Simplex, goodness=sumofsquares, **kwargs):

        # shortcuts to make it easier to keep track of the optimizer and statistic
        self.optimizer = optimizer
        self.statistic = VisualizedStatistic(fitter=self, goodness=goodness)
        super().__init__(optimizer=self.optimizer, statistic=self.statistic)
    """

    def visualize(self, model, x, y, filename=None, animate=True, **kwargs):
        '''
        Yo
        '''

        self.animate = animate
        label = '{}-{}'.format(self.name, self.statistic.name)
        if self.animate:
            # make sure we have a filename set
            if filename is None:
                filename = '{}.mp4'.format(label)
            # figure out which animation writer to use
            self.writer = decide_writer(filename, fps=10)
            dpi = 200



        # restart our counter and goodness of fit score
        self._iterations = 0
        self._gof = []

        # set up a figure and some axes
        self.fi = plt.figure(figsize=(10, 7))
        gs = plt.matplotlib.gridspec.GridSpec(2, 2, height_ratios=[3, 1], hspace=0.25, wspace=0.25)

        # create some axes for our plot, and populate them with empty plots
        self.ax, self.plotted = {}, {}

        # create a space to plot the data vs. the model
        self.ax['data'] = plt.subplot(gs[0,0])

        allcolor = 'gray'
        bestcolor='mediumseagreen'
        self.plotted['data'] = dict(data=plt.plot(x, y, '.k', zorder=0),
                                    models=[plt.plot(x, model(x), zorder=-1, color=allcolor, alpha=1, linewidth=1)[0]],
                                    best=plt.plot(x, model(x), color=bestcolor, linewidth=3)[0])
        # (fuss with the axes)
        span = np.nanmax(y) - np.nanmin(y)
        self.ax['data'].set_ylim(np.nanmin(y)-span/2, np.nanmax(y)+span/2)
        self.ax['data'].set_xlabel('x')
        self.ax['data'].set_ylabel('y')


        # create a space to plot the goodness-of-fit vs time
        self.ax['gof'] = plt.subplot(gs[1,:])

        allkw = dict(marker='o', markersize=5, markeredgecolor='none', color=allcolor)
        bestkw = dict(marker='o', markersize=15, markeredgecolor='none', alpha=0.5, color=bestcolor)
        self.plotted['gof'] = dict(all=plt.plot([],[], **allkw)[0],
                                   best=plt.plot([],[], **bestkw)[0])
        # (fuss with the axes)
        self.ax['gof'].set_xlabel('# of Model Calculations')
        self.ax['gof'].set_ylabel('Goodness-of-Fit\n({})'.format(self._stat_method.name))

        # create a space for plotting the parameters
        interesting = [p for p in model.param_names if model.fixed[p] == False]
        # (include the goodness of fit values)
        interesting += [self._stat_method.name]
        N = len(interesting)-1
        # (grid a triangle of axes)
        gs_param = plt.matplotlib.gridspec.GridSpecFromSubplotSpec(N, N, gs[0,1])
        self.ax['params'] = {p:{} for p in interesting}
        self.plotted['params'] = {p:{} for p in interesting}

        # (decide the x/y limits for each box)
        limits = dict(**model.bounds)
        limits[self._stat_method.name] = (None, None)

        # loop through the triangle of parameter pairs
        for i, pi in enumerate(interesting):
            for j, pj in enumerate(interesting):
                if i>j:
                    # (create ax at this row/column)
                    ax = plt.subplot(gs_param[i-1,j])
                    self.ax['params'][pi][pj] = ax
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        ax.set_xlim(*limits[pj])
                        ax.set_ylim(*limits[pi])

                    #print(limits[pj], limits[pi])
                    if j == 0:
                        ax.set_ylabel(pi)
                    else:
                        plt.setp(ax.get_yticklabels(), visible=False)
                    if i == N:
                        ax.set_xlabel(pj)
                    else:
                        plt.setp(ax.get_xticklabels(), visible=False)

                    self.plotted['params'][pi][pj] = dict(all=plt.plot([],[], '.', **allkw)[0],
                                                          best=plt.plot([],[], '.', **bestkw)[0])

        # create a dictionary to store the parameter arrays in
        self._parameters = {p:[] for p in interesting}

        if self.animate:
            with self.writer.saving(self.fi, filename, dpi or figure.get_dpi()):
                fitted = self.__call__(model, x=x, y=y, **kwargs)
        else:
            fitted = self.__call__(model, x=x, y=y, **kwargs)
        return fitted


class VisualizedSimplexFitter(fitting.SimplexLSQFitter, VisualizedFitter):
    name = 'simplex'
    def __init__(self, goodness=sumofsquares, **kwargs):

        super().__init__(**kwargs)

        # shortcut to keep track of the optimizer and statistic
        self.optimizer = optimizers.Simplex
        self.statistic = VisualizedStatistic(goodness=goodness, fitter=self)

        # tell the optimizer which statistic to try to minimize
        self._stat_method = self.statistic


class VisualizedGuessNCheckFitter(VisualizedFitter):
    name = 'guessncheck'
    def __init__(self,  goodness=sumofsquares, **kwargs):

        # shortcut to keep track of the optimizer and statistic
        self.optimizer = guessncheck
        self.statistic = VisualizedStatistic(goodness=goodness, fitter=self)
        super().__init__(optimizer=self.optimizer, statistic=self.statistic, **kwargs)



    def __call__(self, model, x, y, N=100):
        '''
        Run the guess-n-check "optimization."
        '''

        # create a copy of the model
        model_copy = model.copy()

        # get the best fit parameters
        fitparams = self._opt_method(self._stat_method, model, x, y, N=N)
        model_copy.parameters = fitparams

        return model_copy

# write documentation that makes clear goodness must want to be minimized
# write wrapper that sets model bounds + fixed or not
# log axis for gof
# better default filename
# display mp4 in browswer
