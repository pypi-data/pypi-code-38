'''
Various plotting functions
'''
import re
import os
from collections import OrderedDict, defaultdict
import warnings

import numpy as np
from numpy import meshgrid
import scipy.optimize
from matplotlib import cm, patches
from matplotlib.colors import LightSource
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
from matplotlib.pyplot import savefig
import matplotlib2tikz
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # @UnresolvedImport. Axes3D is needed for projection = '3d' below @UnusedImport

from swutil.files import path_from_keywords
from swutil.np_tools import weighted_median, grid_evaluation
from swutil.validation import Float, Dict, List, Tuple, Bool, String, Integer,Function
from swutil.collections import unique

def save(*name, pdf=True, tex=False, png = False, figs = None):
    if len(name)==1:
        name = name[0]
    else:
        if len(name) % 2 == 1:
            raise ValueError('Number of arguments must be even')
        properties=OrderedDict()
        for j in range(len(name)//2):
            properties[name[2*j]]=name[2*j+1]
        name = path_from_keywords(properties,into='file')
    if tex:
        if figs is not None:
            raise ValueError('tex only supports saving current figure')
        matplotlib2tikz.save(name + '.tex')
    if pdf or png:
        def save(format):
            nonlocal figs
            if figs=='current':
                savefig(name + '.' +format, bbox_inches='tight')
            else:
                if figs is None or figs=='all':
                    figs = plt.get_fignums()
                savenames = {n:name+('_{:d}'.format(n) if len(figs)>1 else '')+'.'+format for n in figs}
                for n in figs:
                    plt.figure(n)
                    savefig(savenames[n],bbox_inches='tight')
                if format=='pdf' and len(figs)>1:
                    from PyPDF2 import PdfFileMerger
                    merger = PdfFileMerger()
                    for n in figs:
                        merger.append(open(savenames[n], 'rb'))
                    with open(name+'.'+format, "wb") as fout:
                        merger.write(fout)
                    for n in figs:
                        try:
                            os.remove(savenames[n])
                        except:
                            pass
        if pdf: save('pdf')
        if png: save('png')

def plot_indices(mis, dims=None, weights=None, groups=1,legend = True,index_labels=None, colors = None,axis_labels = None,size_exponent=0.1,ax=None):
    '''
    Plot multi-index set
    
    :param mis: Multi-index set
    :type mis: Iterable of SparseIndices
    :param dims: Which dimensions to use for plotting
    :type dims: List of integers.
    :param weights: Weights associated with each multi-index
    :type weights: Dictionary
    :param quantiles: Number of groups plotted in different colors
    :type quantiles: Integer>=1 or list of colors
    
    TODO: exchange index_labels and dims, exchange quantiles and dims
    '''
    if weights is None:
        weights = {mi: 1 for mi in mis}
    if Function.valid(weights):
        weights = {mi:weights(mi) for mi in mis}
    values = list(weights.values())
    if Integer.valid(groups):
        N_g = groups
        groups = [[mi for mi in mis if (weights[mi] > np.percentile(values, 100/groups*g) or g==0) and weights[mi] <= np.percentile(values, 100/groups*(g+1))] for g in range(N_g)]
        group_names = ['{:.0f} -- {:.0f} percentile'.format(100/N_g*(N_g-i-1),100/N_g*(N_g-i)) for i in reversed(range(N_g))]
    else:
        if Function.valid(groups):
            groups = {mi:groups(mi) for mi in mis}
        group_names = unique(list(groups.values()))
        groups = [[mi for mi in mis if groups[mi]==name] for name in group_names]
        N_g = len(group_names)
    if colors is None: 
        colors = matplotlib.cm.rainbow(np.linspace(0, 1, N_g))  # @UndefinedVariable
    if Dict.valid(mis):
        if index_labels is None or weights is None:
            temp = list(mis.keys())
            if (List|Tuple).valid(temp[0]):
                if not (index_labels is None and weights is None):
                    raise ValueError('mis cannot be dictionary with tuple entries if both index_labels and weights are specified separately')
                weights = {mi:mis[mi][0] for mi in mis}
                index_labels=  {mi:mis[mi][1] for mi in mis}
            else:
                if weights is None:
                    weights = mis
                else:
                    index_labels = mis
            mis = temp
        else:
            raise ValueError('mis cannot be dictionary if index_labels are specified separately')
    if dims is None:
        try:
            dims = len(mis[0])
        except TypeError:
            dims = sorted(list(set.union(*(set(mi.active_dims()) for mi in mis))))   
    if len(dims) > 3:
        raise ValueError('Cannot plot in more than three dimensions.')
    if len(dims) < 1:
        warnings.warn('Sure you don\'t want to plot anything?')
        return
    if ax is None:
        fig = plt.figure() # Creates new figure, because adding onto old axes doesn't work if they were created without 3d
        if len(dims) == 3:
            ax = fig.gca(projection='3d')
        else:
            ax = fig.gca()
    size_function = lambda mi: sum([weights[mi2] for mi2 in mis if mi.equal_mod(mi2, lambda dim: dim not in dims)]) 
    sizes = {mi: np.power(size_function(mi), size_exponent) for mi in mis}
    for i,plot_indices in enumerate(groups):
        X = np.array([mi[dims[0]] for mi in plot_indices])
        if len(dims) > 1:
            Y = np.array([mi[dims[1]] for mi in plot_indices])
        else:
            Y = np.array([0 for mi in plot_indices])
        if len(dims) > 2:
            Z = np.array([mi[dims[2]] for mi in plot_indices])
        else:
            Z = np.array([0 for mi in plot_indices])   
        sizes_plot = np.array([sizes[mi] for mi in plot_indices])
        if weights:
            if len(dims) == 3:
                ax.scatter(X, Y, Z, s = 50 * sizes_plot / max(sizes.values()), color=colors[i], alpha=1)            
            else:
                ax.scatter(X, Y, s = 50 * sizes_plot / max(sizes.values()), color=colors[i], alpha=1)
        else:
            if len(dims) == 3:
                ax.scatter(X, Y, Z,color = colors[i],alpha=1)
            else:
                ax.scatter(X, Y,color=colors[i],alpha=1)
        if True:
            if len(dims)==3:
                axs='xyz'
            else:
                axs='xy'
            extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in axs])
            sz = extents[:,1] - extents[:,0]
            maxsize = max(abs(sz))
            for dim in axs:
                getattr(ax, 'set_{}lim'.format(dim))(0, maxsize)
    if axis_labels is not None:
        ax.set_xlabel(axis_labels[0])
        if len(dims)>1:
            ax.set_ylabel(axis_labels[1])
        if len(dims)>1:
            ax.set_zlabel(axis_labels[2])
    else:
        ax.set_xlabel('$k_' + str(dims[0])+'$',size=20)
        if len(dims) > 1:
            ax.set_ylabel('$k_' + str(dims[1])+'$',size=20)
        if len(dims) > 2:
            ax.set_zlabel('$k_' + str(dims[2])+'$',size=20)
        plt.grid()
    x_coordinates = [mi[dims[0]] for mi in mis]
    xticks=list(range(min(x_coordinates),max(x_coordinates)+1))
    ax.set_xticks(xticks)
    if len(dims)>1:
        y_coordinates = [mi[dims[1]] for mi in mis]
        ax.set_yticks(list(range(min(y_coordinates),max(y_coordinates)+1)))
    if len(dims)>2:
        z_coordinates = [mi[dims[2]] for mi in mis]
        ax.set_zticks(list(range(min(z_coordinates),max(z_coordinates)+1)))
    if index_labels:
        for mi in index_labels:
            ax.annotate('{:.3g}'.format(index_labels[mi]),xy=(mi[0],mi[1]))
    if legend and len(group_names)>1:
        ax.legend([patches.Patch(color=color) for color in np.flipud(colors)],group_names)
    return ax

    
def ezplot(f,xlim,ylim=None,ax = None,vectorized=True,N=None,contour = False,args=None,kwargs=None,dry_run=False,show=None,include_endpoints=False):
    '''
    Plot polynomial approximation.
    
    :param vectorized: `f` can handle an array of inputs
    '''
    kwargs = kwargs or {}
    args = args or []
    d = 1 if ylim is None else 2
    if ax is None:
        fig = plt.figure()
        show = show if show is not None else True
        ax = fig.gca() if (d==1 or contour) else fig.gca(projection='3d')
    if d == 1:
        if N is None:
            N = 200
        if include_endpoints:
            X = np.linspace(xlim[0],xlim[1],N)
        else:
            L = xlim[1] - xlim[0]
            X = np.linspace(xlim[0] + L / N, xlim[1] - L / N, N)
        X = X.reshape((-1, 1))
        if vectorized:
            Z = f(X)
        else:
            Z = np.array([f(x) for x in X])
        if not dry_run:
            C = ax.plot(X, Z,*args,**kwargs)
    elif d == 2:
        if N is None:
            N = 30
        T = np.zeros((N, 2))
        if include_endpoints:
            T[:,0]=np.linspace(xlim[0],xlim[1],N)
            T[:,1]=np.linspace(ylim[0],ylim[1],N)
        else:
            L = xlim[1] - xlim[0]
            T[:, 0] = np.linspace(xlim[0] + L / N, xlim[1] - L / N, N) 
            L = ylim[1] - ylim[0]
            T[:, 1] = np.linspace(ylim[0] + L / N, ylim[1] - L / N, N) 
        X, Y = meshgrid(T[:, 0], T[:, 1])
        Z = grid_evaluation(X, Y, f,vectorized=vectorized)
        if contour:
            if not dry_run:
                # C = ax.contour(X,Y,Z,levels = np.array([0.001,1000]),colors=['red','blue'])
                N=200
                colors=np.concatenate((np.ones((N,1)),np.tile(np.linspace(1,0,N).reshape(-1,1),(1,2))),axis=1)
                colors = [ [1,1,1],*colors,[1,0,0]]
                print('max',np.max(Z[:]))
                C = ax.contourf(X,Y,Z,levels = [-np.inf,*np.linspace(-20,20,N),np.inf],colors=colors)
        else:
            if not dry_run:
                C = ax.plot_surface(X, Y, Z)#cmap=cm.coolwarm, 
                # C = ax.plot_wireframe(X, Y, Z, rcount=30,ccount=30)
    if show:
        plt.show()
    return ax,C,Z
    
def plot3D(X, Y, Z):
    '''
    Surface plot.
    
    Generate X and Y using, for example
          X,Y = np.mgrid[0:1:50j, 0:1:50j]
        or
          X,Y= np.meshgrid([0,1,2],[1,2,3]).
    
    :param X: 2D-Array of x-coordinates
    :param Y: 2D-Array of y-coordinates
    :param Z: 2D-Array of z-coordinates
    '''
    fig = plt.figure()
    ax = Axes3D(fig)
    light = LightSource(90, 90)
    illuminated_surface = light.shade(Z, cmap=cm.coolwarm)  # @UndefinedVariable
    Xmin = np.amin(X)
    Xmax = np.amax(X)
    Ymin = np.amin(Y)
    Ymax = np.amax(Y)
    Zmin = np.amin(Z)
    Zmax = np.amax(Z)
    ax.contourf(X, Y, Z, zdir='x', offset=Xmin - 0.1 * (Xmax - Xmin), cmap=cm.coolwarm, alpha=1)  # @UndefinedVariable
    ax.contourf(X, Y, Z, zdir='y', offset=Ymax + 0.1 * (Ymax - Ymin), cmap=cm.coolwarm, alpha=1)  # @UndefinedVariable
    ax.contourf(X, Y, Z, zdir='z', offset=Zmin - 0.1 * (Zmax - Zmin), cmap=cm.coolwarm, alpha=1)  # @UndefinedVariable
    ax.plot_surface(X, Y, Z, cstride=5, rstride=5, facecolors=illuminated_surface, alpha=0.5)
    plt.show()
    
def plot_divergence(times, values, name=None, title=None, divergence_type='algebraic', expect_values=None,
                    expect_times=None, plot_rate=None, p=2, preasymptotics=True, stagnation=False, marker=None, legend='lower right'):  
    plot_convergence(times, values, name, title, np.zeros(values[0].shape), divergence_type, expect_values, expect_times,
                     plot_rate, p, preasymptotics, stagnation, marker, legend)
    
def plot_convergence(times, values, name=None, title=None, reference='self', convergence_type='algebraic', expect_residuals=None,
                     expect_times=None, plot_rate='fit', base = np.exp(0),xlabel = 'x', p=2, preasymptotics=True, stagnation=False, marker='.',
                     legend='lower left',relative = False,ax = None):
    '''
    Show loglog or semilogy convergence plot.
    
    Specify :code:`reference` if exact limit is known. Otherwise limit is 
    taken to be last entry of :code:`values`.
    
    Distance to limit is computed as RMSE (or analogous p-norm if p is specified)
    
    Specify either :code:`plot_rate`(pass number or 'fit') or 
    :code:`expect_residuals` and :code:`expect_times` to add a second plot with
    the expected convergence.
    
    :param times: Runtimes
    :type times: List of positive numbers
    :param values: Outputs
    :type values: List of arrays
    :param reference: Exact solution, or 'self' if not available
    :type reference: Array or 'self'
    :param convergence_type: Convergence type
    :type convergence_type: 'algebraic' or 'exponential'
    :param expect_residuals: Expected residuals
    :type expect_residuals: List of positive numbers
    :param expect_times: Expected runtimes
    :type expect_times: List of positive numbers
    :param plot_rate: Expected convergence order
    :type plot_rate: Real or 'fit'
    :param preasymptotics: Ignore initial entries for rate fitting
    :type preasymptotics: Boolean
    :param stagnation: Ignore final entries from rate fitting
    :type stagnation: Boolean
    :param marker: Marker for data points
    :type marker: Matplotlib marker string
    :return: fitted convergence order
    '''
    name = name or ''
    self_reference = (isinstance(reference,str) and reference=='self') #reference == 'self' complains when reference is a numpy array
    ax = ax or plt.gca()
    color = next(ax._get_lines.prop_cycler)['color']
    ax.tick_params(labeltop=False, labelright=True, right=True, which='both')
    ax.yaxis.grid(which="minor", linestyle='-', alpha=0.5)
    ax.yaxis.grid(which="major", linestyle='-', alpha=0.6)
    c_ticks = 3
    ACCEPT_MISFIT = 0.1
    values, times = np.squeeze(values), np.squeeze(times)
    assert(times.ndim == 1)
    assert(len(times) == len(values))
    sorting = np.argsort(times)
    times = times[sorting]
    values = values[sorting]
    if plot_rate == True:
        plot_rate = 'fit'
    if plot_rate !='fit':
        plot_rate = plot_rate*np.log(base)#Convert to a rate w.r.t. exp
    if self_reference:
        if len(times) <= 2:
            raise ValueError('Too few data points')
        limit = values[-1]
        limit_time = times[-1]
        times = times[0:-1]
        values = values[0:-1]
    else:
        limit = np.squeeze(reference)
        limit_time = np.Inf
    residuals = np.zeros(len(times))
    N = limit.size
    for L in range(len(times)):
        if p < np.Inf:
            residuals[L] = np.power(np.sum(np.power(np.abs(values[L] - limit), p) / N), 1. / p)  #
        else:
            residuals[L] = np.amax(np.abs(values[L] - limit))
    if relative:
        if p<np.Inf:
            residuals /= np.power(np.sum(np.power(np.abs(limit),p)/N),1./p)
        else:
            residuals /= np.amax(np.abs(limit))
    try:
        remove = np.isnan(times) | np.isinf(times) | np.isnan(residuals) | np.isinf(residuals) | (residuals == 0) | ((times == 0) & (convergence_type == 'algebraic'))
    except TypeError:
        print(times,residuals)
    times = times[~remove]
    if sum(~remove) < (2 if self_reference else 1):
        raise ValueError('Too few valid data points')
    residuals = residuals[~remove]
    if convergence_type == 'algebraic':
        x = np.log(times)
        limit_x = np.log(limit_time)
    else:
        x = times
        limit_x = limit_time
    #min_x = min(x)
    max_x = max(x)
    y = np.log(residuals)
    try:
        rate, offset, min_x_fit, max_x_fit = _fit_rate(x, y, stagnation, preasymptotics, limit_x, have_rate=False if (plot_rate == 'fit' or plot_rate is None) else plot_rate)
    except FitError as e:
        warnings.warn(str(e))
        plot_rate = False
        rate = None
    if self_reference:
        if rate >= 0:
            warnings.warn('No sign of convergence')
        else:
            real_rate = _real_rate(rate, l_bound=min_x_fit, r_bound=max_x_fit, reference_x=limit_x)
            if (real_rate is None or abs((real_rate - rate) / rate) >= ACCEPT_MISFIT):
                warnings.warn(('Self-convergence strongly affects plot and would yield misleading fit.')
                              + (' Estimated true rate: {}.'.format(real_rate) if real_rate else '')
                              + (' Fitted rate: {}.'.format(rate) if rate else ''))      
    if plot_rate:
        name += 'Fitted rate: ' if plot_rate == 'fit' else 'Plotted rate: '
        if convergence_type == 'algebraic':
            name+='{:.2g})'.format(rate) 
        else:
            base_rate = rate/np.log(base)
            base_rate_str = f'{base_rate:.2g}'
            if base_rate_str=='-1':
                base_rate_str='-'
            if base_rate_str =='1':
                base_rate_str = ''
            name+=f'${base}^{{{base_rate_str}{xlabel}}}$'
        if convergence_type == 'algebraic':
            X = np.linspace(np.exp(min_x_fit), np.exp(max_x_fit), c_ticks)
            ax.loglog(X, np.exp(offset) * X ** rate, '--', color=color)
        else:
            X = np.linspace(min_x_fit, max_x_fit, c_ticks)
            ax.semilogy(X, np.exp(offset + rate * X), '--', color=color)
    max_x_data = max_x
    keep_1 = (x <= max_x_data)
    if convergence_type == 'algebraic':
        ax.loglog(np.array(times)[keep_1], np.array(residuals)[keep_1], label=name, marker=marker, color=color)
        ax.loglog(np.array(times), np.array(residuals), marker=marker, color=color, alpha=0.5)
    else:
        ax.semilogy(np.array(times)[keep_1], np.array(residuals)[keep_1], label=name, marker=marker, color=color)
        ax.semilogy(np.array(times), np.array(residuals), marker=marker, color=color, alpha=0.5)
    if expect_times is not None and expect_residuals is not None:
        ax.loglog(expect_times, expect_residuals, '--', marker=marker, color=color) 
    if name:
        ax.legend(loc=legend)
    if title:
        ax.set_title(title)
    return rate

def _keep(x, y, l_bound, r_bound):
    keep = (x >= l_bound) & (x <= r_bound)
    return x[keep], y[keep]

def _qof(x_original, y_original, l_bound, r_bound, have_rate, scale_x, scale_y, p=1, prefer_length=1):
    x, y = _keep(x_original, y_original, l_bound, r_bound)
    if len(x) >= 2:
        coeffs = _fit(x, y, l_bound, r_bound, have_rate)
        fitted_y = coeffs[1] + coeffs[0] * x
        w = _weights(x)
        return 5 * 2 ** (1 / p) * np.sum(w * np.abs((y - fitted_y) / scale_y) ** p) ** (1 / p) + prefer_length * (1 - (r_bound - l_bound) / scale_x)
    else:
        return np.Inf
    
def _truncate(x, y, where, l_bound, r_bound, have_rate, prefer_length, min_distance, max_move):
    min_x = min(x)
    max_x = max(x)
    bounds = np.linspace(min_x, max_x, 20)
    required_distance = min_distance * (max_x - min_x)
    bounds = bounds[(bounds > l_bound) & (bounds < r_bound)]
    if where == 'left':
        right_limit = min(r_bound - required_distance, min_x + max_move * (max_x - min_x))
        bounds = bounds[bounds < right_limit]
    if where == 'right':
        left_limit = max(l_bound + required_distance, max_x - max_move * (max_x - min_x))
        bounds = bounds[bounds > left_limit]
    scale_y = np.abs(max(y) - min(y))
    if bounds.size:
        scale_x = np.abs(max(x) - min(x))
        misfit = np.Inf * np.ones(bounds.shape)
        for i, bound in enumerate(bounds):
            if where == 'left':
                misfit[i] = _qof(x, y, bound, r_bound, have_rate, scale_x, scale_y, prefer_length=prefer_length)
            if where == 'right':
                misfit[i] = _qof(x, y, l_bound, bound, have_rate, scale_x, scale_y, prefer_length=prefer_length)
        i_min = np.argmin(misfit)
        if misfit[i_min] < np.Inf:
            return bounds[i_min]
    return l_bound if where == 'left' else r_bound

def _weights(x):
    w = 1 / 2 * ((x[1:-1] - x[0:-2]) + (x[2:] - x[1:-1]))
    if len(x) < 2:
        print(1)
    w = np.concatenate(((x[1] - x[0]).reshape(-1), w, (x[-1] - x[-2]).reshape(-1)))
    w = w / np.sum(w)
    return w

def _fit(x, y, l_bound, r_bound, have_rate):
    x, y = _keep(x, y, l_bound, r_bound)
    if len(x) < 2:
        raise FitError()
    if have_rate is False:
        coeffs = np.polyfit(x, y, deg=1, w=np.sqrt(_weights(x)))
    else:
        coeffs = have_rate, weighted_median(y - have_rate * x, _weights(x))
    return coeffs

class FitError(Exception):
    def __init__(self, cause=''):
        super().__init__(' '.join(['Could not fit rate.', cause]))
    
def _fit_rate(x, y, stagnation, preasymptotics, reference_x, have_rate):
    max_x = max(x)
    min_x = min(x)
    min_distance = 0.5 if len(x) > 10 else (0.5 if len(x) >= 5 else 0.8)
    attempts = 10
    l_bounds = {'init':min_x}
    r_bounds = {'init':max_x, 'selfconvergence':reference_x}
    r_bound = lambda : min(r_bounds.values())
    l_bound = lambda : max(l_bounds.values())
    for attempt in range(1, attempts + 1):
        if stagnation:
            r_bounds['stagnation'] = _truncate(x, y, 'right', l_bound=l_bound(), r_bound=max_x, have_rate=have_rate, prefer_length=0.5, min_distance=min_distance, max_move=1)
        if preasymptotics:
            l_bounds['preasymptotics'] = _truncate(x, y, 'left', r_bound=r_bound(), l_bound=min_x, have_rate=have_rate, prefer_length=2, min_distance=min_distance, max_move=attempt / attempts)
    observed_rate, offset = _fit(x, y, l_bound(), r_bound(), have_rate) 
    return observed_rate, offset, l_bound(), r_bound()
    
def _real_rate(observed_rate, l_bound, r_bound, reference_x):
    real_rate = None
    attempts = 10
    if observed_rate < -1e-12:
        def toy_residual(x, real_rate):  # -inf when x is too close to reference_x
            with np.errstate(divide='ignore'):
                return np.log(np.exp(real_rate * x) - np.exp(real_rate * reference_x))
        def observed_rate_fn(real_rate):
            observed_rate = (toy_residual(r_bound, real_rate) - toy_residual(l_bound, real_rate)) / (r_bound - l_bound)
            return observed_rate
        for _ in range(attempts):
            try:
                real_rate = scipy.optimize.bisect(lambda real_rate: observed_rate_fn(real_rate) - observed_rate, observed_rate, -1e-12, rtol=0.01)
                break
            except ValueError:  # Probably because r_bound is so close to reference_x that even the slowest rate would still give huge observed rates
                r_bound = max(l_bound + 0.1 * (r_bound - l_bound), r_bound / 2)
    return real_rate
        
def plot_nterm_convergence(coeffs):
    T = np.power(np.sort(coeffs, 0)[::-1], 2)
    times, values = range(1, len(T)), np.sqrt(np.sum(T) - np.cumsum(T)[:-1])
    return plot_convergence(times, values, reference=0, plot_rate='fit')
