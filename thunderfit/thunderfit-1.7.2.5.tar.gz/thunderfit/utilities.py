import logging
from json import dump as j_dumps
from json import load as j_load
from os import mkdir
from os.path import join, abspath
from time import strftime

import pandas as pd
from dill import dump as d_dump
from dill import load as d_load
from numpy import vstack, pad, diff, frombuffer, round, nanmean, ndarray, nanstd, histogram, exp, nanpercentile, count_nonzero, isnan
from sklearn.mixture import GaussianMixture
from tqdm import tqdm

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

from . import normalisation

# tools
def save_thunder(obj, path, filename='thunder.d'):
    """
    save a thunder object to a path using the dill package
    :param obj:
    :param path:
    :param filename:
    :return:
    """
    logging.debug(f'saving using dill {filename}')
    d_dump(obj, open(abspath(join(path, filename)), 'wb'))


def load_thunder(path):
    """
    load a dill dumped object
    :param path:
    :return:
    """
    logging.debug('loading using dill')
    obj = d_load(open(path, 'rb'))
    return obj


def save_plot(plot, path='.', figname='figure.svg'):
    """
    save a plot as a svg
    :param plot:
    :param path:
    :param figname:
    :return:
    """
    logging.debug(f'saving figure {figname}')
    plot.savefig(join(path, figname), transparent=True, format='svg')


def save_fit_report(obj, path, filename="report.json"):
    """
    save a fit report dictionary as a json
    :param obj:
    :param path:
    :param filename:
    :return:
    """
    logging.debug(f'saving report {filename}')
    j_dumps(obj, open(abspath(join(path, filename)), 'w'), indent=4)


def find_closest_indices(list1, list2):
    """
    given two lists returns list of indices indicating which indices in list 1 match each index in list 2. i.e. index 0
    of the returned list indicates which index in list 1 matches index 0 in list 2
    :param list1: a list of numbers
    :param list2: a list of numbers
    :return: a list of indices of matches
    """
    try:
        list_of_matching_indices = [min(range(len(list1)), key=lambda i: abs(
            list1[i] - cent)) for cent in list2]  # the lambda function is what min uses
    except ValueError:
        print('this dataset has no values!')
        return
    return list_of_matching_indices


def normalise_all(y_bg_rem, bg, y_raw):
    """
    given data with background removed, a background and the raw data, normalise the data with the bg removed and then
    normalise the others according to this normalisation (i.e. use the mean and std from that)
    :param y_bg_rem: np array of data after bg removed
    :param bg: np array of bg
    :param y_raw: np array of data before bg removed
    :return: data np arrays normalised by svn normalisaiton
    """
    logging.debug('normalising many objects')
    y_data_bg_rm, (mean_y_data, std_dev) = normalisation.svn(
        y_bg_rem)  # normalise the data
    # normalise with data from bg subtracted data
    background, _ = normalisation.svn(bg, mean_y_data, std_dev)
    # normalise with data from bg subtracted data
    y_data_norm, _ = normalisation.svn(y_raw, mean_y_data, std_dev)

    return y_data_bg_rm, background, y_data_norm


def safe_list_get(l, idx, default):
    """fetch items safely from a list, if it isn't long enough return a default value"""
    try:
        return l[idx]
    except IndexError:
        return default


def sharpening_routine(x_data, y_data):
    """
    a function to run a user guided routine to sharpen data using peak_sharpening function
    :param x_data: np array of x data
    :param y_data: np array of y data
    :return: y_data sharpened by user chosen factors
    """
    sharpening_factor = (0, 0)
    res_enhanced = y_data
    while True:
        plt.plot(x_data, res_enhanced)
        print(
            f"Do you want to sharpen the peaks to help find components? Note this will not edit the actual data. "
            f"Current sharpening factor is: {sharpening_factor}")
        plt.show()
        ans = input(
            "Please enter the method (either 'power' or 'deriv'), then a comma, then a new sharpening factors "
            "(comma seperated if mutliple i.e. for derivative), "
            "or type y to continue with the current factor")
        if ans == 'y':
            plt.close()
            return y_data
        else:
            try:
                ans = ans.split(',')
                _type = ans[0]
                ans = ans[1:]
                sharpening_factor = [float(fac) for fac in ans]
                res_enhanced = peak_sharpening(
                    y_data, _type, sharpening_factor)
            except BaseException:
                print("You entered an incorrect answer! Trying again...")


def peak_sharpening(y_data, _type, sharpening_factor):
    """
    function to sharpen peaks. can use power or derivative methods
    :param y_data: np array of y data
    :param _type: the type of sharpening to be used
    :param sharpening_factor: the factors to sharpen with
    :return: the data sharpened
    """
    if _type == 'power':
        res_enhanced = y_data ** sharpening_factor[0]  # raise to the power
    elif _type == 'deriv':
        y_double_prime = pad(diff(y_data, n=2), (0, 2), 'constant')
        y_4_prime = pad(diff(y_data, n=4), (0, 4), 'constant')
        res_enhanced = y_data - sharpening_factor[0] * y_double_prime + sharpening_factor[
            1] * y_4_prime  # this is the original data minus its
        # derivative multiplied by some factor
    else:
        raise ValueError("enter a correct type")
    return res_enhanced

# tools

# user inputs and loading etc


def load_data(datapath, x_ind, y_ind, e_ind=None):
    """
    load in data as an np arra. can load from a csv or hs5 pandas
    :param datapath: where to get data from
    :param x_ind: which column to find x data
    :param y_ind: which column to find y data
    :param e_ind: optional, which column to find error data
    :return: np arrays of the data loaded with nan values dropped across all values (note might break with error values)
    """
    logging.debug('loading data')
    if '.h5' in datapath:  # if the data is already stored as a pandas df
        store = pd.HDFStore(datapath)
        keys = store.keys()
        if len(keys) > 1:
            logging.warning(
                "Too many keys in the hdfstore, will assume all should be concated")
            logging.warning("not sure this concat works yet")
            # not sure this will work! concat all keys dfs together
            data = store.concat([store[key] for key in keys])
        else:
            # if only one key then we use it as the datafile
            data = store[keys[0]]
    else:  # its a txt or csv file
        # load in, works for .txt and .csv
        data = pd.read_csv(datapath, header=None, sep='\t', dtype='float')
        if len(data.columns) < 2:
            # load in, works for .txt and .csv
            data = pd.read_csv(
                datapath,
                header=None,
                sep=r'\s+',
                dtype='float')
        # this needs to be made more flexible/user defined
    if e_ind:  # if we have specified this column then we use it, otherwise just x and y
        assert (len(data.columns) >=
                2), "You have specified an e_ind but there are less than 3 columns in the data"
        e_data = data[e_ind].values
    else:
        e_data = None

    data.dropna()  # drop any rows with NaN etc in them

    x_data = data[x_ind].values
    y_data = data[y_ind].values

    return x_data, y_data, e_data


def map_unique_coords(x_data, y_data, x_coords, y_coords):
    """
    function to get the unique coordinate values out from np arrays of data and coordinates
    :param x_data:np array of x data
    :param y_data: np array of y data
    :param x_coords: np array of x coordinates, index corresponds to x and y data
    :param y_coords: np array of y coordinates, index corresponds to x and y data
    :return: lists of np arrays, each element matches, x_coords and y_coords contain lists of numbers only. so e.g.
    index 0 of all has the x and y coordinates in coords lists at 0, and x and y data in those lists at 0 as np arrays
    """
    logging.debug('parsing coordinates')
    data = vstack((x_coords, y_coords, x_data, y_data)
                  ).transpose()  # now have columns as the data
    df = pd.DataFrame(
        data=data,
        columns=[
            'x_coords',
            'y_coords',
            'x_data',
            'y_data'])
    # get a dictionary of the unique values for
    unique_dict = dict(tuple(df.groupby(['x_coords', 'y_coords'])))
    # coordinates (as tuples of (x,y)) and then the whole df rows for these
    # values

    x_data, y_data, x_coords, y_coords = [], [], [], []
    for key in unique_dict.keys():
        x_data_ = unique_dict[key]['x_data'].values  # get the x_data
        x_data.append(x_data_)
        y_data_ = unique_dict[key]['y_data'].values
        y_data.append(y_data_)
        x_coords.append(key[0])
        y_coords.append(key[1])

    return x_data, y_data, x_coords, y_coords


def parse_param_file(filepath='./params.txt'):
    """
    parse a params file which we assume is a dictionary
    :param filepath: str: path to params file
    :return: dictionary of paramters
    """
    # maybe use json loads if you end up writing parameter files non-manually
    logging.debug('parsing params file')
    with open(filepath, 'r') as f:
        arguments = j_load(f)
        f.close()

    # TODO: add some checks to user passed data
    return arguments


def parse_args(arg):
    """
    convert argparse arguments into a dictionary for consistency later
    :param arg: argparse parsed args
    :return: dictionary of parameters
    """
    logging.debug('parsing args')
    arguments = {}
    arguments['x_ind'] = arg.x_ind
    arguments['y_ind'] = arg.y_ind
    arguments['e_ind'] = arg.e_ind
    arguments['datapath'] = arg.datapath
    arguments['no_peaks'] = arg.no_peaks
    arguments['background'] = arg.background
    arguments['scarf_params'] = arg.scarf_params
    arguments['peak_types'] = arg.peak_types
    arguments['peak_centres'] = arg.peak_centres
    arguments['peak_widths'] = arg.peak_widths
    arguments['peak_amps'] = arg.peak_amps
    arguments['tightness'] = arg.tightness
    arguments['bounds'] = arg.bounds

    # TODO: add some checks to user passed data
    return arguments


def make_dir(dirname, i=1):
    """
    function to make a directory, recursively adding _new if that name already exists
    :param dirname: str: name of directory to create
    :param i: the run number we are on
    :return: str: the directory name which was available, and all subsequent data should be saved in
    """
    logging.debug('making dir')
    try:
        mkdir(f'{dirname}')
    except FileExistsError as e:
        dirname = make_dir(f'{dirname}_new', i + 1)
        if i == 1:
            print(e, f'. So I named the file: {dirname}')
        return dirname
    return dirname


def clip_data(x_data, y_data, clips=None):
    """
    given data either clip it or run a user guided routine to clip it
    :param x_data: np array of x data
    :param y_data: np array of y data
    :param clips: either none or a list of two values which are left and right clips in terms of x values
    :return: the indices of the clips to use
    """
    logging.debug('clipping data')
    if clips:
        clip_left, clip_right = clips
        clip_left = find_closest_indices(list(x_data), [clip_left])[0]
        clip_right = find_closest_indices(list(x_data), [clip_right])[0]
    else:
        clip_left, clip_right = 0, len(x_data) - 1
        while True:
            fig, ax = plt.subplots()
            ax.plot(x_data[clip_left:clip_right], y_data[clip_left:clip_right])
            print(
                f"Removing background, please type two x values seperated by a space for the clips. \n"
                f"Current values are: {x_data[clip_left]}, {x_data[clip_right]}. \n"
                f"PLEASE MAKE SURE YOU ENTER IN THE SAME ORDER AS HERE. i.e. if first value is larger than right then the "
                f"first value will be the large x_clip second small")
            plt.show(block=True)
            ans = input(
                "If you are happy with the clips type y. If not then please type a new pair of values ")
            if ans == 'y':
                break
            else:
                try:
                    ans = ans.split(' ')
                    if len(ans) != 2:
                        raise ValueError(
                            "The tuple was more than two elements long")
                    clip_left = float(ans[0])
                    clip_left = find_closest_indices(
                        list(x_data), [clip_left])[0]
                    clip_right = float(ans[1])
                    clip_right = find_closest_indices(
                        list(x_data), [clip_right])[0]
                except ValueError:
                    print("You entered an incorrect answer! Trying again...")

        plt.close()
    return clip_left, clip_right


def apply_func(key_kwargs_, func):
    """
    given some keywords and a function call the function
    :param key_kwargs_: a tuple of (key, args) to use
    :param func: function to call
    :return: the key for this and the value returned from calling the func
    """
    key = key_kwargs_[0]
    kwargs_ = key_kwargs_[1]
    val = func(*kwargs_)
    return key, val


def setup_logger(log_name):
    """
    function to setup a logger to save to file
    :param log_name:
    :return:
    """
    curr_time = strftime('%d_%m_%Y__%H;%M')
    log_filename = f"{log_name}_{curr_time}.log"
    logging.getLogger().setLevel(logging.DEBUG)
    logger = logging.getLogger('')
    logger.handlers = []
    logging.basicConfig(filename=log_filename, level=logging.DEBUG)
    logging.info('have read in user arguments')
    return log_filename


def gif_maker(bag, filename):
    """
    function to make a gif of all the plots (with no uncertainty) and save it at filename
    :param bag: a dictionary of the thunder objects which have been fit etc and are to be plotted
    :param filename: where to save the gif
    :return:
    """
    bags = iter(bag.values())

    def update(i):
        thund = next(bags)
        ax, fig = thund.plot_all(plot_unc=False)
        plt.text(
            0.1,
            0.9,
            f'PLOT_{i}',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes)
        fig.canvas.draw()
        img = frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close()
        return img

    import imageio
    print("Creating gif")
    imageio.mimsave(filename, tqdm([update(i) for i in range(len(bag))]), fps=2)
#

def cosmic_rays(y_data, width_threshold=3):
    """
    this currently fails if data is sloping and cosmic ray is below max values. change to sloping mad in future
    :param y_data: np array of data
    :return:
    """
    """
    import numpy as np
    from scipy.signal import find_peaks
    import ipdb
    ipdb.set_trace()
    peaks, properties = find_peaks(y_data, width=0, rel_height=0.8) # find peaks with a minimum prominence of zero -
    # finds widths at 0.8 the height of peaks - quick experiment shows this is optimal for a random example
    # - needs more testing
    prominences = properties['prominences']
    peak_ind = np.argwhere(prominences > np.percentile(prominences, 99))[:,0] # indices of peaks with prominence in 99th percentile
    y_data_peak_indices = np.take(peaks, peak_ind)

    widths = np.take(properties['widths'], peak_ind) # these are the widths with this peak prominence
    np.argwhere(widths < width_threshold) # this may fail often?

    """



    """
    mad = np.median(abs(y_data - np.median(y_data))) # median abs deviation of the data
    y_mad = abs(y_data - np.median(y_data)) / mad # abs mdeviation from median divided by mad to get ratio
    cutoff = np.percentile(y_mad, 99.5) # what values make up the 99th percentile, above this are rare!
    bad_indices = np.argwhere(y_mad > cutoff)
    for i in bad_indices[:,0]:
        y_data[i] = np.mean(y_data[i-10:i+10]) # set as the mean value in a window around the peak
    """
    #### ideas:
    ### detection:
    ## r-pca as from stanford - probably not good here. https://medium.com/netflix-techblog/rad-outlier-detection-on-big-data-d6b0494371cc : https://github.com/dganguli/robust-pca/blob/master/r_pca.py
    ## differentiate in time across multiple spectra, use that to detect spikes - for single spectra do user guided 'zap' function?
    ## just smoothing? or smoothing and then a residual threshold?
    ## find peaks using scipy and delete low width peaks, doesn't work if small though
    ## https://journals.sagepub.com/doi/pdf/10.1366/000370207781745847 - simulate the data and set a threshold for
    # residual, replace pixels with simulated. this would involve a cosmic spike removal step at the end of fitting.
    # if fitting has already failed then wouldn't work. could be a bit delicate
    ## asto guy: https://cosmicrayapp.com/2017/02/03/signal-processing-details/
    ## mad - also captures peaks in general so no bueno
    ## https://pureportal.strath.ac.uk/files-asset/38783720/Littlejohn_Automated_cosmic_spike_filter.pdf
    ## https://www.osti.gov/pages/servlets/purl/1334720
    ## https://www.researchgate.net/publication/233403614_Automated_Cosmic_Spike_Filter_Optimized_for_Process_Raman_Spectroscopy


    return y_data

def smoother(y_data, x_data):
    from scipy.signal import savgol_filter
    y_data = savgol_filter(y_data, 51, 9)
    return y_data, x_data


def hist_chooser(u_vals, bins, lower_per=1, upper_perc=99):
    range_l, range_h = nanpercentile(u_vals, lower_per), nanpercentile(u_vals, upper_perc)
    heights, edges = histogram(a=u_vals, bins=bins, range=(range_l, range_h))
    if len(edges) > 70:
        heights, edges = hist_chooser(u_vals, bins, lower_per + 2, upper_perc - 2)
    return heights, edges


def histogram_func(u_vals:ndarray, x_label, gmm=False, f=None, ax=None, bins='auto', color='r', label=''):
    assert(len(u_vals.shape) == 1), "The nd array passed to histogram func must be a 1d ndarray"
    if not ax or not f: # then create the figure
        f = plt.figure()
        ax = f.add_subplot(111)
    # get the hist
    heights, edges = hist_chooser(u_vals, bins)
    widths = [0.8*(edges[i+1] - edges[i]) for i in range(len(edges) - 1)]
    edges = edges[:-1]
    # plot it
    ax.bar(edges, heights, width=widths, color=color, align='edge', alpha=0.75)
    ax.grid(axis='y', alpha=0.75)
    ax.set(xlabel=x_label, ylabel='Frequency')
    mu = round(nanmean(u_vals), 3)
    mu_unc = round(nanstd(u_vals) / count_nonzero(~isnan(u_vals)), 3) # standard error
    sig = round(nanstd(u_vals), 3) # sigma

    plt.text(0.3, 0.9, f'{label}' + r'$\mu=$' + f'{mu}' + f'pm {mu_unc}' + ', ' + r'$\sigma=$' + f'{sig}' ,
             horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, color=color)
    if gmm: # then add gaussian mixture
        vals, bins = histogram(u_vals, bins='auto')
        gmm = GaussianMixture(n_components=3)
        gmm = gmm.fit(u_vals[:, None])
        plt.plot(bins[:None], exp(gmm.score_samples(bins[:, None])))
        plt.text(0.3, 0.8, r'GaussianMixture Components:', horizontalalignment='center',
                 verticalalignment='center', transform=ax.transAxes)
    return f, ax, bins
