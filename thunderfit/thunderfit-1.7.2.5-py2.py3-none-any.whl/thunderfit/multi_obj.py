import logging
from typing import Union
from copy import deepcopy
from glob import glob
from numpy import array, ndarray, round
from pandas.errors import ParserError
from tqdm import tqdm
from os.path import join

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

from . import utilities as utili
from .thundobj import Thunder
from . import map_scan_tools
from . import peak_fitting
from . import peak_finding
from .background import background_removal as bg_remove


# TODO
# make option of passing in many params files - one for each data file

class ThunderBag():
    """
    A 'bag' of thunder objects. these are collectively stored with some metadata in this object, so we can do some
    cool things like store a thunderfit object for each coordinate and make mapscans etc
    """

    def __init__(self, input):
        """
        initialise everything first
        :param input: a dictionary of parameters to create the bag object with
        """
        self.thunder_bag: {} = {}
        self.coordinates: {} = {}
        self.first: str = ''
        self.stats: {} = {}
        self.fit_params: {} = {}
        self.x_ind: Union[None, int] = None
        self.y_ind: Union[None, int] = None
        self.e_ind: Union[None, int] = None
        self.img_path: Union[None, str] = None
        self.map: Union[None, str] = None
        self.datapath: Union[None, str] = None
        self.x_coord_ind: Union[None, int] = None
        self.y_coord_ind: Union[None, int] = None

        if isinstance(input, Thunder):  # if only pass one but its already a thunder object then just use that
            # add all the details in depending on args
            self.thunder_bag[0] = Thunder(input)
        elif isinstance(input, dict):
            self.create_bag(input)  # add all the details in depending on args
        else:
            raise TypeError('Cannot convert input to ThunderBag object')

    def create_bag(self, inp):
        """
        create a bag object given an inp
        :param inp: this is a dictionary with all the necessary data on the bag
        :return:
        """
        logging.debug('creating bag object')
        self.x_ind = inp.get('x_ind', 2)
        self.y_ind = inp.get('y_ind', 3)
        self.e_ind = inp.get('e_ind', None)
        self.img_path = inp.get('imgpath', None)
        self.coordinates = inp.get('coords', {})

        # if user passes map as True then the file will be treated as a map
        # file
        self.map = inp.get('map', None)

        # note this must be a list of datapaths, even if its just one element
        self.datapath = inp.get('datapath', None)
        for i, data in tqdm(enumerate(self.datapath)):  # iterate through the datapaths for each file to be loaded
            if len(self.datapath) > 1:
                # if more than one datapath then we name them with i_j prefix.
                prefix = f'{i}_'
            else:# if not its just j
                prefix = ''
            if isinstance(data, Thunder):
                # then its already loaded so just assign it
                self.thunder_bag[i] = data
            elif isinstance(data, str):
                # then read the data file
                if self.map:  # then we have a map file with 4 columns and lots of individual runs in it
                    self.x_coord_ind, self.y_coord_ind = inp.get('x_coord_ind', 0), inp.get('y_coord_ind', 1)
                    # get the exact filepath to the data
                    map_path = glob(data)[0]
                    x_data, y_data, x_coords, y_coords = self.read_map(
                        map_path, self.x_ind, self.y_ind, self.x_coord_ind, self.y_coord_ind)  # read the
                    # map file into lists of x_data etc

                    for j in range(
                            len(x_data)):  # iterate through the list of data and coords
                        # the x and y data for each coordinate set
                        x_data_, y_data_ = x_data[j], y_data[j]
                        self.thunder_bag[f'{prefix}{j}'] = Thunder(
                            inp, x_data=x_data_, y_data=y_data_)  # make a thunder obj
                        # with this data
                        x_coords_, y_coords_ = x_coords[j], y_coords[j]
                        # for each i we will have a list of tuples of x and y
                        # coords
                        self.coordinates[f'{prefix}{j}'] = (
                            x_coords_, y_coords_)
                elif '*' in data:  # then we need to load all the files in the filepath
                    filematches = glob(data)  # this is a list of the matches
                    for j, file in enumerate(filematches):  # for each file
                        try:
                            self.thunder_bag[f'{prefix}{j}'] = self.create_thunder(
                                file, inp)  # make a thunder object for
                            # each file
                        except ParserError as e:
                            logging.warning(
                                f"A Thunder object could not be created for the datafile: {file}, skipping")
                else:  # its possible the user has passed in a list of thunder objects for us
                    try:
                        self.thunder_bag[str(i)] = self.create_thunder(
                            data, inp)
                    except ParserError as e:
                        logging.warning(
                            f"A Thunder object could not be created for the datafile: {file}, skipping")
            else:  # we can't load any other way
                logging.warning(
                    f"wrong format in data list detected for {i}th element: {data}. Skipping element")
                pass

    @staticmethod
    def create_thunder(file, inp):
        """
        create a thunder object given a path and an inp
        :param file: string
        :param inp: correct filetype for thunder obj, i.e. a dict or a thunder obj
        :return:
        """
        logging.debug('creating thunder object')
        arguments = deepcopy(inp)
        arguments['datapath'] = file
        thund_obj = Thunder(arguments)
        return thund_obj

    @staticmethod
    def read_map(file_address, x_ind, y_ind, x_coord_ind, y_coord_ind):
        """
        read a map file and return four lists for data and coordinates
        :param file_address: what is the path to the file
        :param x_ind: which column is x data
        :param y_ind: which column is y data
        :param x_coord_ind: which column is x coords
        :param y_coord_ind: which column is y coords
        :return:
        """
        logging.debug('reading in mapscan file')
        # load the data. note these drop nan rows but
        x_data, y_data, _ = utili.load_data(file_address, x_ind, y_ind)
        # does that for the whole filepath so will be consistent for data and
        # coordinates
        x_coords, y_coords, _ = utili.load_data(
            file_address, x_coord_ind, y_coord_ind)  # load the coordinates
        x_data, y_data, x_coords, y_coords = utili.map_unique_coords(
            x_data, y_data, x_coords, y_coords)  #

        return x_data, y_data, x_coords, y_coords

    @staticmethod
    def bag_iterator(bag, func, input_args, sett_args):
        """
        this is a generic method which will apply a func with arguments input_args to a bag one by one, and set the
        outputs to the sett_args attributes for each thunder object
        :param bag: bag should be a dictionary of thunder objects
        :param func: the function to apply
        :param input_args: the arguments for the function
        :param sett_args: what to set the output of the function as
        :return:
        """
        bagkeys = tqdm(bag.keys())  # progress bar
        bagkeys.set_description(
            f"Operating with: {func.__name__}, to find: {sett_args}")
        for key in bagkeys:
            thund = bag.get(key)  # bag[key] is the thunder object
            # get the input arg attributes from thunder obj
            kwargs_ = [getattr(thund, arg) for arg in input_args]
            # we return _ which we ignore and val which is a list of
            _, val = utili.apply_func((key, kwargs_), func)
            # output values
            for i, arg in enumerate(sett_args):
                try:
                    # set the data as an attribute to the thunder object
                    if len(sett_args) == 1:
                        setattr(thund, arg, val)
                    else:
                        setattr(thund, arg, val[i])
                except KeyError as e:
                    if isinstance(val, dict):
                        setattr(thund, arg, val)
                    else:
                        print(f'Weird KeyError encountered: {e}')

    def choose_spectrum(self):
        """
        when doing user guided routines e.g. clipping data or background removal, run this to choose which data in the
        bag will be the piece its based on
        :return:
        """
        logging.debug(
            'choosing which thunder object will be the user specified data for bg etc')
        # then we have to choose which spectrum we want
        # changed from list to iter
        first = next(iter(self.thunder_bag.keys()))
        while True:  # keep going until we break
            try:
                first_thunder = self.thunder_bag[first]
                fig, ax = plt.subplots()
                ax.plot(
                    getattr(
                        first_thunder, 'x_data'), getattr(
                        first_thunder, 'y_data'))
                print(
                    f"Need a decision on which plot is representitive of data, the following is for index {first}")
                plt.show(block=True)
                ans = input(
                    "If you are happy with using this data file, type y, otherwise enter a new index")
                if ans == 'y':
                    break
                else:
                    try:
                        first = str(ans)
                    except ValueError:
                        print("You entered an incorrect answer! Trying again...")
            except KeyError:
                print('incorrect key, please enter a lower index value')
                first = next(iter(self.thunder_bag.keys()))
        self.first = first  # save the user decision

    def clip_data(self, clips=None):
        """
        method to clip the data for each thunder object
        :param clips: if none wil do a user guided routine, if a list of two elements will use those elements as the clips
        :return:
        """
        logging.debug('clipping data based on user specified plot')
        first_thunder = self.thunder_bag[self.first]
        clip_left, clip_right = utili.clip_data(
            getattr(
                first_thunder, 'x_data'), getattr(
                first_thunder, 'y_data'), clips)
        for thund in self.thunder_bag.values():
            setattr(
                thund, 'x_data', getattr(
                    thund, 'x_data')[
                    clip_left:clip_right])
            setattr(
                thund, 'y_data', getattr(
                    thund, 'y_data')[
                    clip_left:clip_right])

    def cosmic_rays(self):
        print(
            'cosmic ray removal is not yet implemented. If this is an issue I recommend first smoothing the data elsewhere/ '
            'if you can select a range to delete any troublesome cosmic rays then do that')
        self.bag_iterator(getattr(self,'thunder_bag'), utili.cosmic_rays, ('y_data',), ('y_data',))

    def smoother(self):
        self.bag_iterator(getattr(self,'thunder_bag'), utili.smoother, ('y_data','x_data'), ('y_data','x_data'))


    def bg_param_setter(self):
        """
        method for setting the parameters for the background for all the thunder objects in the bag
        :return:
        """
        logging.debug(
            'setting backgrounds for all based on background of user specified plot')
        # add step to find bg parameters for first one and use for the rest.
        first_thunder = self.thunder_bag[self.first]
        if isinstance(
                getattr(
                    first_thunder,
                    'background'),
                str) and getattr(
                first_thunder,
                'background') == "SCARF":
            _, _, params = bg_remove.background_finder(
                getattr(
                    first_thunder, 'x_data'), getattr(
                    first_thunder, 'y_data'), getattr(
                    first_thunder, 'background'), getattr(
                    first_thunder, 'scarf_params'))
            # we want to find b each time so don't set it for all others
            [param.pop('b', None) for param in params]
            for thund in self.thunder_bag.values():
                # set all the values to this
                setattr(thund, 'scarf_params', params)

    def remove_backgrounds(self):
        """
        method to remove the background for each object, and save the output as y_data_bg_rm in each
        :return:
        """
        # do some checks
        self.bag_iterator(
            getattr( self,'thunder_bag'),
            bg_remove.background_finder,
            ('x_data','y_data','background','scarf_params'),
            ('background', 'y_data_bg_rm', 'params')
        )

    def normalise_data(self):
        """
        method to normalise the data and save the normalised data
        :return:
        """
        self.bag_iterator(
            getattr(
                self,
                'thunder_bag'),
            utili.normalise_all,
            ('y_data_bg_rm',
             'background',
             'y_data'),
            ('y_data_bg_rm',
             'background',
             'y_data'))

    def find_peaks(self):
        """
        method to find peaks using a peakfinder routine and then set peak attributes
        :return:
        """
        logging.debug(
            'setting peak no, centres and types based on user specified plot details')
        # add step to find bg parameters for first one and use for the rest.
        first_thunder = self.thunder_bag[self.first]
        no_peaks, peak_info_dict, prominence = peak_finding.find_peak_details(
            getattr(
                first_thunder, 'x_data'), getattr(
                first_thunder, 'y_data_bg_rm'), getattr(
                first_thunder, 'no_peaks'), getattr(
                    first_thunder, 'peak_finder_type', 'auto'))
        for thund in self.thunder_bag.values(
        ):  # set these first values for all of them
            setattr(thund, 'no_peaks', no_peaks)  # set values
            center_indices = utili.find_closest_indices(
                thund.x_data, peak_info_dict['center'])  # get the indices from the x centres
            center_indices = peak_finding.match_peak_centres(
                center_indices, thund.y_data)  # match to the peakfinding cents
            # convert back to x values
            peak_centres = thund.x_data[center_indices]
            peak_info_dict['center'] = peak_centres  # set values
            thund.peak_info_dict = peak_info_dict

    def peaks_adj_params(self):
        """
        method to adjust the input peak centres by finding peaks in the data and matching the closest ones to the input centres to speed up fitting
        :return:
        """
        for thund in self.thunder_bag.values(
        ):  # set these first values for all of them
            center_indices = utili.find_closest_indices(
                thund.x_data, thund.peak_info_dict['center'])  # get the indices from the x centres
            center_indices = peak_finding.match_peak_centres(
                center_indices, thund.y_data)  # match to the peakfinding cents
            # convert back to x values
            peak_centres = thund.x_data[center_indices]
            thund.peak_info_dict['center'] = peak_centres  # set values

    def bound_setter(self, bounds=None):
        """
        set bounds for all the thunder objects, if no bounds are given then will use a bound finding routine
        :param bounds: a dicitonary on bounds on the data
        :return:
        """
        logging.debug(
            'setting bounds based on user provided bounds or found for user specified plot')
        if not bounds:
            first_thunder = self.thunder_bag[self.first]
            bounds = peak_finding.make_bounds(
                getattr(
                    first_thunder, 'x_data'), getattr(
                    first_thunder, 'y_data'), getattr(
                    first_thunder, 'no_peaks'), first_thunder.peak_info_dict)
        for thund in self.thunder_bag.values(
        ):  # set these first values for all of them
            setattr(thund, 'bounds', bounds)  # set values

    def fit_peaks(self):
        """
        fit the peaks for each of the thunder objects
        :return:
        """
        self.bag_iterator(
            getattr(
                self,
                'thunder_bag'),
            peak_fitting.fit_peaks,
            ('x_data',
             'y_data_bg_rm',
             'peak_info_dict',
             'bounds',
             'method',
             'tol'),
            ('specs',
             'model',
             'peak_params',
             'peaks'))  # fit peaks

    def make_map_matrices(self):
        """
        once the data has been fit for all the thunder objects, make a map matrix from the coordinates of each of the thunder objects
        :return:
        """
        if not isinstance(self.coordinates, ndarray):
            coordinates_array = array(
                list(getattr(self, 'coordinates').values()))
        else:
            coordinates_array = self.coordinates
        coordinates_array = map_scan_tools.shift_map_matr(coordinates_array)
        for i, key in enumerate(getattr(self, 'coordinates')):
            getattr(self, 'coordinates')[key] = coordinates_array.tolist()[
                i]  # reassign in the correct format
        map_matrices = {}
        X_dict = {}
        Y_dict = {}
        fit_iter = tqdm(self.fit_params.keys())
        fit_iter.set_description("making map matrices")
        for p in fit_iter:
            data_mat, X_, Y_ = map_scan_tools.map_scan_matrices_from_dicts(
                getattr(self, 'coordinates'), self.fit_params.get(p))
            map_matrices[p] = data_mat
            X_dict[p] = X_
            Y_dict[p] = Y_

        self.map_matrices = map_matrices
        self.X_coords = X_dict
        self.Y_coords = Y_dict

    @staticmethod
    def histograms(map_matrices, path, keys=None, gmm=False, bins='auto'):
        if isinstance(map_matrices, dict):
            if not keys:
                keys = map_matrices.keys()
            keys1 = tqdm(keys)
            keys1.set_description("making histograms for each parameter")
            for key1 in keys1:
                map_lvl_1 = map_matrices.get(key1) # this should now be a np array or could still be a dict
                if isinstance(map_lvl_1, dict):
                    keys2 = tqdm(map_lvl_1)
                    keys2.set_description("making histograms for each sub parameter")
                    for key2 in keys2:
                        map_lvl_2 = map_lvl_1[key2] # this should now be an nd array
                        assert isinstance(map_lvl_2, ndarray), "The dictionary contains a dictionary whose values " \
                                                               "aren't np arrays!"
                        f, ax, bins_ = utili.histogram_func(map_lvl_2.flatten(), x_label=f'{key2}_value', gmm=gmm,
                                                           bins=bins)
                        f.savefig(join(path, f"{key1}_{key2}s_histogram.svg"), transparent=True, format='svg')
                        plt.close('all')
                elif isinstance(map_lvl_1, ndarray):
                    f, ax, bins_ = utili.histogram_func(map_lvl_1.flatten(),x_label=f'{key1}_value', gmm=gmm,
                                                 bins=bins)
                    f.savefig(join(path, f"{key1}s_histogram.svg"), transparent=True,
                                format='svg')
                    plt.close('all')
        else:
            raise TypeError("The map matrices object supplied is the incorrect type. Must be a dictionary")


    def make_fit_params(self):
        """
        fit_params is a dictionary with the details of the fits, make map matrices will use this dictionary to make maps of e.g. amplitude at each coordinate
        :return:
        """
        logging.debug('generating fit params')
        fit_params = {}
        first_thunder = self.thunder_bag.get(self.first)
        params = set([key.split('__')[1]
                      for key in getattr(first_thunder, 'peak_params').keys()])
        param_iter = tqdm(params)
        param_iter.set_description('making fit parameters')
        for param in param_iter:
            fit_params[param] = {}  # e.g. 'center'
            for key in self.thunder_bag.keys():
                fit_details = getattr(self.thunder_bag.get(key), 'peak_params')
                fit_details = {key_.split('__')[0]: fit_details.get(
                    key_) for key_ in fit_details.keys() if key_.split('__')[1] == param}
                fit_params[param][key] = fit_details
        self.fit_params = fit_params

    def get_fit_stats(self):
        """
        make a fit statistics dictionary with chisq etc for each thunder obj
        :return:
        """
        logging.debug('generating fit stats')
        stats = {'chisq': {}, 'reduced_chi_sq': {}, 'free_params': {}}
        dict_iter = tqdm(self.thunder_bag.items())
        dict_iter.set_description('making stats dict')
        for key, thund in dict_iter:
            chisq = getattr(getattr(thund, 'peaks'), 'chisqr')
            reduced_chi_sq = getattr(getattr(thund, 'peaks'), 'redchi')
            free_params = round(chisq / reduced_chi_sq)
            stats['chisq'][key] = chisq
            stats['reduced_chi_sq'][key] = reduced_chi_sq
            stats['free_params'][key] = free_params
        self.stats = stats

    def save_failed_plots(self, dirname):
        """
        If any of the thunderobjects failed to fit then this will save those in dirname directory
        :param dirname: directory to save in
        :return:
        """
        logging.debug('saving failed plots')
        dict_iter = tqdm(self.thunder_bag.items())
        dict_iter.set_description('saving failed plots')
        for key, thund in dict_iter:
            if not getattr(getattr(thund, 'peaks'), 'success'):
                thund.plot_all()
                utili.save_plot(
                    thund.plot,
                    path=dirname,
                    figname=f"failed_plot_{key}_at_position_{self.coordinates.get(key)}.svg")
                thund.plot.close()  # close so memory is conserved.

    def save_all_plots(self, dirname, plot_unc=True):
        """
        method to save all the plots
        :param dirname: directory to save in
        :param plot_unc: bool, if True then also plots uncertainty
        :return:
        """
        dict_iter = tqdm(self.thunder_bag.items())
        dict_iter.set_description('saving all plots')
        for key, thund in dict_iter:
            thund.plot_all(plot_unc=plot_unc)
            utili.save_plot(
                thund.plot,
                path=dirname,
                figname=f"plot_no_{key}_at_position_{self.coordinates.get(key)}.svg")
            thund.plot.close()  # close so memory is conserved.


def main(arguments):
    """
    function to build a thunderbag objects
    :param arguments:
    :return:
    """
    bag = ThunderBag(deepcopy(arguments))  # load object
    return bag
