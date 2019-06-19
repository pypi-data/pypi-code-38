from . import utilities as utili
import logging
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib
import matplotlib.pyplot as plt
from numpy import unique, round, array, nanmin, nanmax, nan, nanpercentile, nanmean
from scipy.sparse import coo_matrix
from tqdm import tqdm

matplotlib.use('TkAgg')


# funcs for plotting
def shift_map_matr(coordinates_array):
    """
    function to shift all the coordinates in a coordinates array so that it start from zero.
    :param coordinates_array: an np array of mxn with the coordinates of each scan at each position
    :return: the shifted coordinates array
    """
    logging.debug('shifting coordinates array')
    coordinates_array[:, 0] = coordinates_array[:, 0] - \
        min(coordinates_array[:, 0])
    coordinates_array[:, 1] = coordinates_array[:, 1] - \
        min(coordinates_array[:, 1])
    return coordinates_array


def generate_map_matrix(coordinates, peak_label_vals):
    """
    function to generate a map matrix based on a dictionary of coordinates and peak_label_vals. both have matching keys
    and the coordinates values are (x,y) tuples, peak_label_vals is a dictionary of values of what is being mapped.
    :param coordinates: dictionary of keys corresponding to thunder objects, values are (x,y)
    :param peak_label_vals: same keys as coordinates but with values which will be mapped to a matrix
    :return: a matrix of dimensions from coordinates. each
    element corresponds to a new scan, so assumes a uniform grid. the spacing of scans isn't coded in here, but can be
    accessed from the X and Y which are returned (lists of the coodinates)
    """
    X = []  # initialise these
    Y = []
    Z = []

    for key in peak_label_vals.keys():  # corresponding to a pixel
        x, y = coordinates[key]  # coordinates
        z = peak_label_vals[key]  # value at those coordinates
        if isinstance(z, str):  # not sure why this is here.
            return [], []  # probably will break if this happens. better to raise an error
        X.append(x)  # append to coordinates and values to the lists
        Y.append(y)
        Z.append(z)
    x_step = unique(X)[1] - unique(X)[0]  # what are the step sizes in x
    # turn the x coordinates into an array of integer steps
    xx = (round(X / x_step)).astype(int)
    y_step = unique(Y)[1] - unique(Y)[0]
    yy = round((Y / y_step)).astype(int)
    # build a dense array by using sparse array notation and converting
    data_ = coo_matrix((Z, (yy, xx))).toarray()
    # if its zero we assume thats because there was no data taken there.
    data_[data_ == 0] = nan

    return X, Y, data_


def map_scan_matrices_from_dicts(coordinates, values):
    """
    function to generate dictionaries of X and Y coordiantes, as well as dict of data matrices. does this for all
    the peak types in the passed in dictionaries. keys are the properties e.g. 'center' etc
    :param coordinates: dictionary of coordinates for each property (usually doesn't differ though so is a repeat of the same ones)
    :param values: dict of values for each property (key). e.g. 'center' has value which is a dict of run keys and values at that key
    :return: data dict, and X_, Y_ coordinate dicts. same keys as input
    """
    logging.debug('generating map matrices')
    peak_labels = list(values.values())[0].keys()
    data = {}
    X_ = {}
    Y_ = {}
    for peak_label in peak_labels:
        peak_label_vals = {
            key: values[key].get(
                peak_label,
                nan) for key in values.keys()}
        X, Y, data_ = generate_map_matrix(coordinates, peak_label_vals)
        data[peak_label] = data_
        X_[peak_label] = X
        Y_[peak_label] = Y
    return data, X_, Y_


def map_plotter(data, X, Y, colorbounds=[None,None]):
    """
    function to plot a mapscan given a data matrix and the actual coordinates to plot on the map
    :param data: np array of values
    :param X: x coordinates corresponding to each element in data in x direction
    :param Y: same as for x
    :return: figure and axis to be reused/saved etc later
    """
    f = plt.figure()
    ax = plt.gca()
    magma_cmap = matplotlib.cm.get_cmap('magma')
    magma_cmap.set_bad(color='green')

    # either set colorbounds or use user-supplied bounds
    if not colorbounds[0]:
        colorbounds[0] = nanpercentile(data, 3)
    if not colorbounds[1]:
        colorbounds[1] = nanpercentile(data, 97)

    im = plt.imshow(
        data,
        cmap=magma_cmap,
        vmin=colorbounds[0],
        extent=[min(X),max(X), max(Y), min(Y)],
        vmax=colorbounds[1])  # we plot the 99th percentile and 1st percentil as the max and min
    # colours
    plt.xlabel('x coordinates')
    plt.ylabel('y coordinates')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)

    return f, ax, colorbounds


def map_scan_plot_dicts(data_mat, X_coords, Y_coords, colorbounds={}):
    """
    plot all the data and save all the plots into dicts which are returned
    :param data_mat: data matrices as dicts. keys are for the properties for which each map matrix is the value
    :param X_coords: x coordinates as dicts. keys same as data_mat
    :param Y_coords: same as for x
    :return:
    """
    logging.debug('plotting mapscans')
    peak_labels = data_mat.keys()
    figs = {}
    axs = {}
    for peak_label in peak_labels:
        data = data_mat[peak_label]
        X = X_coords[peak_label]
        Y = Y_coords[peak_label]
        f, ax, colorbounds_ = map_plotter(data, X, Y, colorbounds=colorbounds.get(peak_label, [None,None]))
        colorbounds[peak_label] = colorbounds_
        figs[peak_label] = f
        axs[peak_label] = ax
    return figs, axs, colorbounds


def get_cent_mean(peak_label, fit_params):
    """
    function to return the mean center values from fit_params dict. isn't a great abstraction barrier though!
    :param peak_label: the label of the peak you want the mean center value for e.g. 'm0' for mdoel 0
    :param fit_params: fit params dict with keys of properties for peaks e.g. 'center' and 'amplitude'
     these have values which are dicts which include peak_label as a key. those values are the values for that property
     for each peak
    :return: the mean center value
    """
    cents = [
        cent.get(
            peak_label,
            0) for cent in fit_params.get(
            'center',
            {}).values()]
    cent_mean = nanmean(cents)
    return cent_mean


def save_mapscan(peak_label, fit_params, plot, dirname, p):
    """
    given a mapscan plot save it and add a title
    :param peak_label: the label of the peak the mapscan is for
    :param fit_params: the dicitonary of all peak properties and peaks values
    :param plot: the plot to save
    :param dirname: str: where to save it
    :param p: str: what is the peak being saved
    :return:
    """
    cent_mean = get_cent_mean(peak_label, fit_params)
    plot[peak_label].suptitle(
        f"{p}_{peak_label}_heatmap. peak {peak_label} is centered at:  {cent_mean}")
    utili.save_plot(
        plot[peak_label],
        path=dirname,
        figname=f"{p}_{peak_label}.svg")


def mapscans_for_parameter(
        map_matrices,
        X_coords,
        Y_coords,
        p,
        fit_params,
        dirname, colorbounds={}):
    """
    given the map matrices coordinates dictionaries and fit parameters, plot all the mapscans and then call them all to be saved
    :param map_matrices: a dict of map matrices, keys are the type of map to save e.g. 'center'. the values are dicts of
    actual data matrices as values and keys correspond to the model keys e.g. 'm0'
    :param X_coords: coordinates dict with keys same as map_matrices
    :param Y_coords: same as for x
    :param p: key for what mapscan to access
    :param fit_params: fit parameters dictionary as made by multi_obj method
    :param dirname: where to save the mapscans
    :return:
    """
    data_mat = map_matrices[p]
    plot, ax, colorbounds = map_scan_plot_dicts(data_mat, X_coords[p], Y_coords[p], colorbounds=colorbounds)
    for peak_label in plot.keys():
        save_mapscan(peak_label, fit_params, plot, dirname, p)
        plt.close('all')
    return colorbounds


def plot_all_maps(fit_params, map_matrices, X_coords, Y_coords, dirname):
    fit_params_iter = tqdm(fit_params.keys())
    fit_params_iter.set_description('plotting and saving all maps')
    for p in fit_params_iter:
        mapscans_for_parameter(map_matrices, X_coords, Y_coords, p, fit_params, dirname, colorbounds={})


def plot_map_scan(fit_params, map_matrices, X_coords, Y_coords, dirname, plot_all=False):
    """
    function to plot the mapscans given user input on what to plot for.
    :param fit_params: a dictionary of dicts. 1st keys are properties e.g. 'center' and second keys are for each model
    e.g. 'm0'. values are a dict of the actual values for each pixel in the map
    :param map_matrices: same as fit_params but the values are map matrices instead of dicts
    :param X_coords: same as map_matrices except the values are lists of X_coords
    :param Y_coords: same as x
    :param dirname: str: where to save the plots
    :return:
    """
    logging.debug(
        'runnning user input routine to generate/save user chosen variables in maps')
    if plot_all:
        plot_all_maps(fit_params, map_matrices, X_coords, Y_coords, dirname)
        return map_matrices
    while True:
        ans = input(
            "making map scans, please input which property you would like to scan. options are:"
            f"\n {[p_ for p_ in fit_params.keys()]}, or type 'all' to plot all, or type e to exit")
        if ans == 'e':
            break
        elif ans == 'all':
            plot_all_maps(fit_params, map_matrices, X_coords, Y_coords, dirname)
            break  # break the while loop
        else:
            try:
                p = ans
                mapscans_for_parameter(map_matrices, X_coords, Y_coords, p, fit_params, dirname)
            except KeyError:
                print('wrong answer entered, trying again!')
    plt.close('all')
#
    return map_matrices
