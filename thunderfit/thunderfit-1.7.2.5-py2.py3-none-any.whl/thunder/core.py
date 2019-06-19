import logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
import os
import json
import dill
import operator
import difflib
import re
from typing import Dict, Union
import copy

from scipy.signal import find_peaks as peak_find
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.optimize import least_squares
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import lmfit
from lmfit import models

import utilities as utili


# TODO: need to fail if peak fitting doesn't work!
# fix peak finder
# add argument for number of peaks to use pick these based on some paramter e.g. prominence
# sort peaks in this order
# add try for matplotlib and set interactive background to not run if it fails

class Thunder():
    """
    thunder object with all the methods we love inside it. Name generated using WuTang Clan name generator.
    """
    def __init__(self, input):
        self.input: Union[Thunder, Dict] = input
        self.data: pd.DataFrame = pd.DataFrame([])  # this is what we will create later
        self.data_bg_rm: pd.DataFrame = pd.DataFrame([]) # later we will fill this with background remove data
        self.x_ind: int = 0
        self.y_ind: int = 1
        self.e_ind: Union[int, None] = None
        self.x_label: str = 'x_axis'
        self.y_label: str = 'y_axis'
        self.e_label: Union[str, None] = None
        self.datapath: str = 'data.txt'
        self.peaks: lmfit.model.ModelResult
        self.plot: plt = None
        self.fit_data: {} = {}

        self.user_params: Dict = {'yfit': None, 'background': None, 'peak_types': [], 'peak_centres': [], 'peak_widths':[],
                                'peak_amps': [], 'chisq': None, 'free_params': None, 'p_value':None, 'tightness':None,
                                'bounds' : {'centers':None, 'widths':None, 'amps':None}}

        if isinstance(input, Thunder):  # if only pass one but its already a thunder object then just use that
            self.overwrite_thunder(input)  # add all the details in depending on args
        elif isinstance(input, dict):
            self.create_thunder(input)  # add all the details in depending on args
        else:
            raise TypeError('Cannot convert input to Thunder object')

        self.data = self.load_data(self.datapath, self.x_ind, self.y_ind, self.x_label, self.y_label, self.e_ind,
                                   self.e_label) # load the data

        self.tightness = self.tightness_setter(self.user_params['tightness'])

    #### loading data and thunder object
    def overwrite_thunder(self, inp):
        thun = inp
        self.x_ind = thun.x_ind
        self.y_ind = thun.y_ind
        self.e_ind = thun.e_ind
        self.x_label = thun.x_label
        self.y_label = thun.y_label
        self.datapath = thun.datapath
        self.user_params = thun.user_params

    def create_thunder(self, inp: Dict):
        """
        Used to create a thunder object given different input types
        :param args: a,b,c depending on type of input and
        :return: None, we modify the object unless a spec1d object is passed, in which case we return that
        """
        self.x_label = inp.get('x_label', self.x_label)  # if the key exists then set as that, otherwise make it
        self.y_label = inp.get('y_label', self.y_label)
        self.e_label = inp.get('e_label', self.e_label)
        try:
            self.x_ind = inp['x_ind']
            self.y_ind = inp['y_ind']
            self.e_ind = inp['e_ind']
            self.datapath = inp['datapath']
        except KeyError as e:
            LOGGER.info(f"KeyError: Missing field in the data dictionary: {e}")
        self.user_params = inp.get('fit_params', self.user_params)

    @staticmethod
    def load_data(datapath, x_ind, y_ind, x_label, y_label, e_ind=None, e_label=None):
        """
        load in data as a pandas df - save by modifying self.data, use object params to load
        :return: None
        """
        if '.h5' in datapath: # if the data is already stored as a pandas df
            store = pd.HDFStore(datapath)
            keys = store.keys()
            if len(keys) > 1:
                LOGGER.warning("Too many keys in the hdfstore, will assume all should be concated")
                LOGGER.warning("not sure this concat works yet")
                data = store.concat([store[key] for key in keys]) # not sure this will work! concat all keys dfs together
            else:
                data = store[keys[0]] # if only one key then we use it as the datafile
        else: # its a txt or csv file
            data = pd.read_csv(datapath, header=None, sep='\t') # load in, works for .txt and .csv
            # this needs to be made more flexible/user defined

        col_ind = [x_ind, y_ind]
        col_lab = [x_label, y_label]
        if e_ind: # if we have specified this column then we use it, otherwise just x and y
            assert (len(data.columns) >= 2), "You have specified an e_ind but there are less than 3 columns in the data"
            col_ind.append(e_ind)
            col_lab.append(e_label)
        data = data[col_ind]  # keep only these columns, don't want to waste memory
        data.columns = col_lab   # rename the columns
        data.dropna() # drop any rows with NaN etc in them
        return data

    @staticmethod
    def tightness_setter(tightness):
        tight_dict = {}
        if tightness == None:
            tight_dict['width'] = 10
            tight_dict['centre_bounds'] = 10
            tight_dict['width_bounds'] = (10, 3)

        elif tightness == 'low':
            tight_dict['width'] = 2
            tight_dict['centre_bounds'] = 20
            tight_dict['width_bounds'] = (100, 10)

        elif tightness == 'med':
            tight_dict['width'] = 10
            tight_dict['centre_bounds'] = 10
            tight_dict['width_bounds'] = (10, 3)

        elif tightness == 'high':
            tight_dict['width'] = 20
            tight_dict['centre_bounds'] = 5
            tight_dict['width_bounds'] = (5, 2)

        else:
            logging.warning(
                'The tightness defined was incorrect format, use low, med or high. Using default med settings')
            tight_dict['width'] = 10
            tight_dict['centre_bounds'] = 10
            tight_dict['width_bounds'] = (10, 3)

        return tight_dict
    #### end loading

    #### background
    def background_finder(self):
        y_label = self.y_label
        x_label = self.x_label
        y_data = self.data[y_label]
        x_data = self.data[x_label]
        bg = self.user_params['background']
        data_bg_rm = self.data_bg_rm

        if bg == 'no':  # then user doesn't want to make a background
            LOGGER.warning(
                "Warning: no background specified, so not using a background,"
                " this may prevent algorithm from converging")
            bg = np.array([0 for _ in y_data])  # set the background as 0 everywhere
            data_bg_rm[y_label] = y_data # no background subtracted
            data_bg_rm[x_label] = x_data

        elif bg == 'SCARF':
            bg = np.array([0 for _ in y_data], dtype=np.float64)
            rad = 20
            b = 0
            window_length, poly_order = 51, 3
            L_sg = 0
            data_bg_rm[y_label] = y_data

            while True:
                while True:
                    D = utili.rcf(data_bg_rm[y_label], rad)
                    fig, ax = plt.subplots()
                    ax.plot(x_data, D)
                    ax.plot(x_data, data_bg_rm[y_label])
                    print(f"SCARF background removal requires user input. Please look at the following bg with rad={rad}")
                    plt.show(block=True)
                    ans = input("If you are happy with the plot, type y. if not then please type a new rad")
                    if ans == 'y':
                        break
                    else:
                        try:
                            rad = int(ans)
                        except ValueError:
                            print("You entered an incorrect answer! Trying again...")

                L = D + b
                while True: # now estimate a baseline to add to D to get L
                    fig, ax = plt.subplots()
                    ax.plot(x_data, L)
                    ax.plot(x_data, data_bg_rm[y_label])
                    print(f"Please look at the following bg with a shift={b}")
                    plt.show(block=True)
                    ans = input("If you are happy with the plot, type y. if not then please type a new background value. \n"
                                "Please note that the background should NOT intercept the data. Ideally it would pass through"
                                "the mean of the noise for the correct bg already fit")
                    if ans == 'y':
                        L = D + b
                        break
                    else:
                        try:
                            b = int(ans)
                            L = D + b
                        except ValueError:
                            print("You entered an incorrect answer! Trying again...")

                # then apply SG filter to L
                while True:
                    try:
                        L_sg = utili.smooth(L, window_length, poly_order)
                        fig, ax = plt.subplots()
                        ax.plot(x_data, L_sg)
                        ax.plot(x_data, data_bg_rm[y_label])
                        print(f"Please look at the following bg with Sg filter parameters (window length, polynomial order): "
                              f"{window_length}, {poly_order}")
                        plt.show(block=True)
                    except ValueError as e:
                        print(
                            "Incorrect values for window_length and poly_order have been entered. Poly order must be less than window length and window length must be odd")
                    ans = input("please enter y if you are happy with these values, or enter two integers with a space "
                                    "for window_length and poly_order")
                    if ans == 'y':
                        L = L_sg
                        break
                    else:
                        try:
                            ans = ans.split(' ')
                            if len(ans) != 2:
                                raise ValueError("The tuple was more than two elements long")
                            window_length = int(ans[0])
                            poly_order = int(ans[1])
                        except ValueError:
                            print("You entered an incorrect answer! Trying again...")

                # final question before exiting
                fig, ax = plt.subplots()
                ax.plot(x_data, L)
                ax.plot(x_data, data_bg_rm[y_label])
                print(f"Please look at the following bg with selected parameters")
                plt.show(block=True)
                ans = input("Are you happy with this bg? If yes, type y, else type n. n will restart the fitting. \n"
                            "typing repeat will add an additional bg subtraction to this one")
                if ans == 'y':
                    bg += L
                    break
                elif ans == 'n':
                    pass
                elif ans =='repeat':
                    bg += L
                    print("apply two bg removal steps, this will mean the background just specified will be removed "
                          "from the data")
                    data_bg_rm[y_label] -= L # remove the bg found here from the original data and go again
                else:
                    print("You entered an incorrect answer! Trying whole fitting routine again...")

            data_bg_rm[y_label] -= L  # subtract background from the data
            data_bg_rm[x_label] = x_data

        elif isinstance(bg, np.ndarray):
            assert len(self.user_params['background']) == len(y_data), \
                    "the background generated or passed is of incorrect length"
            data_bg_rm[y_label] = y_data - bg # subtract user supplied background from the data
            data_bg_rm[x_label] = x_data

        elif bg == 'OLD':
            bg = self.find_background(y_data) # find a background the old way
            data_bg_rm[y_label] = y_data - bg  # subtract background from the data
            data_bg_rm[x_label] = x_data

        else:  # then it is the incorrect type
            raise TypeError('the background passed is in the incorrect format, please pass as type np array')

        #y_min = data_bg_rm[y_label].min()
        #if y_min < 0:
        #    data_bg_rm[y_label] += abs(y_min)  # then shift all the data up so no points are below zero
        #    bg -= abs(y_min)  # and lower the bg we have calculated by that shift too

        self.user_params['background'] = bg
        self.data_bg_rm = data_bg_rm

    # old
    def find_background(self, data):
        params = np.array([0.01, 10 ** 5])
        bounds = [np.array([0.001, 10 ** 5]), np.array([0.1, 10 ** 9])]
        baseline_values = least_squares(self.residual_baseline, params[:], args=(data.values,),
                                  bounds=bounds)

        p, lam = baseline_values['x']
        baseline_values = self.baseline_als(data.values, lam, p, niter=10)
        return baseline_values
    # old
    def residual_baseline(self, params, y):
        p, lam = params
        niter = 10
        baseline = self.baseline_als(y, lam, p, niter)
        residual = y - baseline
        return residual
    #old
    @staticmethod
    def baseline_als(y, lam, p, niter=10):
        L = len(y)
        D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
        w = np.ones(L)
        if niter < 1:
            raise ValueError("n iter is too small!")
        for i in range(niter):
            W = sparse.spdiags(w, 0, L, L)
            Z = W + lam * D.dot(D.transpose())
            z = spsolve(Z, w * y)
            w = p * (y > z) + (1 - p) * (y < z)
        return z
    ##### background end

    #### normalise
    @staticmethod
    def normalisation(y_data):
        """normalise using std variance normalisation"""
        mean_y_data = np.mean(y_data)
        shifted_y_data = y_data - mean_y_data
        std_dev = np.std(y_data)
        normalised_y = shifted_y_data / std_dev
        return normalised_y

    #### normalise end

    ##### peak finding
    def peaks_unspecified(self, specified_dict):
        x_data = self.data_bg_rm[self.x_label]
        # fix this up since only cents_specified works now

        if not specified_dict['cents_specified']:

            #width_ranges = [50, len(x_data) / 2]  # these are index widths TODO make this a variable...
            prominence = 1.6
            # do question asking routine for picking prominence to find peaks
            peak_info = self.peak_finder(self.data_bg_rm[self.y_label],
                                                    prominence)  # find the peak centers

            # use peak info dict and store the heights and widths of peaks
            self.user_params['peak_centres'] = x_data[peak_info['center_indices']].values  # these are the indices of the centres
            self.user_params['peak_widths'] = x_data[peak_info['right_edges']].values - x_data[peak_info['left_edges']].values
            self.user_params['peak_amps'] = peak_info['amps']
            import ipdb
            ipdb.set_trace()

            # set bounds from these too


        if not specified_dict['amps_specified']: # find a faster way to do this
            xcents = self.user_params['peak_centres'] # this is x data
            peak_centres_indices = [self.data_bg_rm[self.x_label].iloc[(self.data_bg_rm[self.x_label] - xval)
                                 .abs().argsort()[:1]].index for xval in xcents] #find the indices for these xvalues
            peak_centres_indices = [ind.tolist()[0] for ind in peak_centres_indices] # stupid pandas index type

            y_peaks = self.data_bg_rm[self.y_label][peak_centres_indices]  # get the y values from the indices
            self.user_params['peak_amps'] = list(y_peaks)  # all peak amps are the order of mag of largest y

        if not specified_dict['widths_specified']:
            width = x_data.max() - x_data.min()
            self.user_params['peak_widths'] = [(width / self.tightness['width']) * np.random.random() for _ in self.user_params['peak_centres']]

        if not specified_dict['types_specified']:
            self.user_params['peak_types'] = ['LorentzianModel' for _ in
                                              self.user_params['peak_centres']]  # we assume all the types are gaussian


        len_ord_specified = sorted(specified_dict.items(), key=operator.itemgetter(1))  # get the shortest
        len_ord_specified = filter(lambda tup: tup[1] > 0, len_ord_specified)
        try:
            shortest_specified = next(len_ord_specified)[0]  # this is the dict key with the shortest specified data

            for param in ['peak_amps', 'peak_centres', 'peak_widths', 'peak_types']:
                if len(self.user_params[param]) > specified_dict[shortest_specified]: # then we need to trim it
                    LOGGER.warning("Some of the specified peak parameters differ in length. Choosing peak paramters"
                                   "as the first n parameters where n is the length of the shortest set of parameters")
                    self.user_params[param] = self.user_params[param][:specified_dict[shortest_specified]]
        except StopIteration:
            pass

    @staticmethod
    def peak_finder(data, prominence):
        # do a routine looping through until the right number of peaks is found

        peaks, properties = peak_find(data, prominence=prominence) # find the peak positions in the data

        peaks = list(peaks) # convert to a list
        amps = list(properties['prominences']) # store the heights

        peak_info = {'center_indices':peaks, 'right_edges':list(properties['right_bases']),
                     'left_edges':list(properties['left_bases']), 'amps':amps}
        return peak_info
    ##### peak finding end

    ##### peak fitting
    def fit_peaks(self):
        self.user_params = self.make_bounds(self.data_bg_rm, self.user_params, self.y_label)
        self.specs = self.build_specs(self.data_bg_rm[self.x_label].values, self.data_bg_rm[self.y_label].values, self.user_params)

        self.model, self.peak_params = self.generate_model(self.specs)
        self.peaks = self.model.fit(self.specs['y_bg_rm'], self.peak_params, x=self.specs['x_bg_rm'])
        if not self.peaks.success:
            logging.warning('The fitting routine failed! exiting programme. Try lowering tightness settings or manually '
                         'inputting a background, peak bounds and peak info.')
        self.peak_params = self.peaks.best_values

    def make_bounds(self, data_bg_rm, user_params, y_label):
        if user_params['bounds']['centers'] is None:
            l_cent_bounds = [cent - self.tightness['centre_bounds'] *
                             user_params['peak_widths'][i] for i, cent in enumerate(user_params['peak_centres'])]
            u_cent_bounds = [cent + self.tightness['centre_bounds'] *
                             user_params['peak_widths'][i] for i, cent in enumerate(user_params['peak_centres'])]
            cent_bounds = list(zip(l_cent_bounds, u_cent_bounds))
            user_params['bounds']['centers'] = cent_bounds

        if user_params['bounds']['widths'] is None:
            peak_widths = user_params['peak_widths']
            l_width_bounds = [width / self.tightness['width_bounds'][0] for width in peak_widths]
            u_width_bounds = [width * self.tightness['width_bounds'][1] for width in peak_widths]
            width_bounds = list(zip(l_width_bounds, u_width_bounds))
            user_params['bounds']['widths'] = width_bounds

        if user_params['bounds']['amps'] is None:
            peak_amps = user_params['peak_amps']
            amps_lb = data_bg_rm[y_label].mean() # maybe change this to min
            amps_ub = data_bg_rm[y_label].max()
            l_amp_bounds = [amps_lb for _ in peak_amps]
            u_amp_bounds = [amps_ub for _ in peak_amps]
            amp_bounds = list(zip(l_amp_bounds, u_amp_bounds))
            user_params['bounds']['amps'] = amp_bounds

        # todo currently our bounds are set by the data ranges. It may make sense to define
        # narrower ranges around the peaks themselves
        return user_params

    @staticmethod
    def build_specs(x_bg_rm, y_bg_rm, user_params):
        specs = {'x_bg_rm':x_bg_rm, 'y_bg_rm':y_bg_rm,
                'model': [
                    {'type': user_params['peak_types'][i],
                    'params': {'center': user_params['peak_centres'][i], 'amp': user_params['peak_amps'][i],
                               'sigma': user_params['peak_widths'][i], 'gamma':user_params['peak_widths'][i]},
                     'bounds': {'centers': user_params['bounds']['centers'][i], 'amps': user_params['bounds']['amps'][i],
                                'widths': user_params['bounds']['widths'][i]}
                    }
                for i, _ in enumerate(user_params['peak_centres'])]
                }
        return specs

    @staticmethod
    def generate_model(spec):
        """
        https://chrisostrouchov.com/post/peak_fit_xrd_python/
        :param spec:
        :return:
        """
        composite_model = None
        params = None
        for i, basis_func in enumerate(spec['model']):
            prefix = f'm{i}_'
            model = getattr(models, basis_func['type'])(prefix=prefix)
            if basis_func['type'] in ['GaussianModel', 'LorentzianModel','VoigtModel']:
                # for now VoigtModel has gamma constrained to sigma
                w_min = basis_func['bounds']['widths'][0]
                w_max = basis_func['bounds']['widths'][1]
                x_min = basis_func['bounds']['centers'][0]
                x_max = basis_func['bounds']['centers'][1]
                y_min = basis_func['bounds']['amps'][0]
                y_max = basis_func['bounds']['amps'][1]

                model.set_param_hint('sigma', min=w_min, max=w_max)
                model.set_param_hint('center', min=x_min, max=x_max)
                model.set_param_hint('height', min=y_min, max=1.1 * y_max)
                model.set_param_hint('amplitude', min=1e-6)

                # default guess is horrible!! do not use guess()
                default_params = {
                    prefix + 'center': basis_func['params']['center'],
                    prefix + 'height': basis_func['params']['amp'],
                    prefix + 'sigma': basis_func['params']['sigma']
                }
            else:
                raise NotImplemented(f'model {basis_func["type"]} not implemented yet')

            model_params = model.make_params(**default_params, **basis_func.get('params', {}))

            if params is None: # first loop
                params = model_params
                composite_model = model
            else: # subsequent loops
                params.update(model_params)
                composite_model = composite_model + model

        return composite_model, params
    ##### peak fitting end

    ##### plotting
    #todo fix the assertions in these
    @staticmethod
    def plot_data(x, y, ax=False, line='r-', linethickness=0.5):
        if ax:
            #assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
                                                                 " an axes object"
        else:
            fig, ax = plt.subplots()

        ax.plot(x, y, line, linewidth=linethickness, alpha=0.5)
        return ax

    @staticmethod
    def plot_fits(x, peaks, ax=False, linethickness=0.5):
        if ax:
            #assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
                                                                " an axes object"
        else:
            fig, ax = plt.subplots()

        for i, peak in enumerate(peaks):
            ax.plot(x, peaks[peak], linewidth=linethickness)
        return ax

    @staticmethod
    def plot_background(x, background_data, ax=False, line='b--', linethickness=0.5):
        if ax:
            #assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
                                                                 " an axes object"
        else:
            fig, ax = plt.subplots()

        ax.plot(x, background_data, line, linewidth=linethickness)
        return ax

    @staticmethod
    def plot_fit_sum(x, peak_sum, background, ax=False, line='k-', linethickness=0.5): # option of including background
        if ax:
            #assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
                                                                 " an axes object"
        else:
            fig, ax = plt.subplots()

        sum = peak_sum + background

        ax.plot(x, sum, line, linewidth=linethickness)
        return ax

    @staticmethod
    def plot_uncertainty_curve(x, eval_unc, peak_sum, ax=False, color="#ABABAB"):
        if ax:
            #assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
                                                                 " an axes object"
        else:
            fig, ax = plt.subplots()

        ax.fill_between(x, peak_sum - eval_unc, peak_sum + eval_unc, color=color) #plot a grey band of uncertainty

        return ax

    def plot_all(self):
        ax = self.plot_fits(self.data[self.x_label], self.peaks.eval_components()) # plot each component of the model
        ax = self.plot_background(self.data[self.x_label], self.user_params['background'], ax) #plot the background supplied by user
        ax = self.plot_fit_sum(self.data[self.x_label], self.peaks.best_fit, self.user_params['background'], ax) # plot the fitted data
        try:
            ax = self.plot_uncertainty_curve(self.data[self.x_label], self.peaks.eval_uncertainty(sigma=3),
                                         self.peaks.best_fit, ax) #plot a band of uncertainty
        except TypeError:
            logging.warning('There are not uncertainties available for some reason - '
                         'try lowering the tightness of automatic bounds')
        ax = self.plot_data(self.data[self.x_label], self.data[self.y_label], ax)  # plot the raw data

        ax.minorticks_on()
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)

        self.plot = plt
    ##### plotting end


    def fit_report(self):
        self.fit_data = {mod_no:{} for mod_no in range(len(self.user_params['peak_types']))}

        ## total fit data
        chi_sq = self.peaks.chisqr
        reduced_chi_sq = self.peaks.redchi
        free_params = round(chi_sq / reduced_chi_sq)

        ## individual parameter data
        param_info = {"center":"centers", "amplitude":"amps", "sigma":"widths", "fwhm":False, "height":False}
        for parameter, param_obj in self.peaks.params.items():
            model_no = int(re.findall(r'\d+', parameter)[0])
            param_type = param_info[difflib.get_close_matches(parameter, param_info.keys())[0]]

            if param_type:
                value =param_obj.value
                err = param_obj.stderr
                type = self.user_params['peak_types'][model_no]
                bounds = self.user_params['bounds'][param_type][model_no]

                fit_info = {"value":value,
                            "stderr":err,
                            "peak_type":type,
                            "bounds":bounds}

                self.fit_data[model_no][param_type] = fit_info


def peak_details(params):
    cents_specified = len(params['peak_centres'])
    types_specified = len(params['peak_types'])
    widths_specified = len(params['peak_widths'])
    amps_specified = len(params['peak_amps'])

    return {'cents_specified':cents_specified,
            'types_specified': types_specified,
            'widths_specified': widths_specified,
            'amps_specified': amps_specified}

# TODO move bounds making into a new function in main
def main(arguments):
    thunder = Thunder(copy.deepcopy(arguments)) # load object

    thunder.background_finder() # then determine the background
    thunder.data_bg_rm[thunder.y_label] = thunder.normalisation(thunder.data_bg_rm[thunder.y_label]) # normalise the data

    specified_dict = peak_details(thunder.user_params)
    thunder.peaks_unspecified(specified_dict)

    # now fit peaks
    thunder.fit_peaks()
    thunder.plot_all()
    thunder.fit_report()

    return thunder


#### tools
def save_thunder(obj, path, filename='thunder.p'):
    dill.dump(obj, open(os.path.join(path, filename), 'wb'))

def load_thunder(path):
    obj = dill.load(open(path, 'rb'))
    return obj

def save_plot(plot, path='.', figname='figure.png'):
    plot.savefig(os.path.join(path, figname), transparent=True, format='svg')

def save_fit_report(obj, path, filename="report.json"):
    json.dump(obj, open(os.path.join(path, filename), 'w'))

def parse_param_file(filepath='./params.txt'):
    """
    parse a params file which we assume is a dictionary
    :param filepath: str: path to params file
    :return: dictionary of paramters
    """
    # maybe use json loads if you end up writing parameter files non-manually

    with open(filepath, 'r') as f:
        arguments = json.load(f)
        f.close()

    # TODO: add some checks to user passed data
    return arguments
#### tools


if __name__ == '__main__':
    ##### for saving and parsing
    def parse_args(arg):
        """
        convert argparse arguments into a dictionary for consistency later
        :param arg: argparse parsed args
        :return: dictionary of parameters
        """
        arguments = {}
        arguments['x_label'] = arg.x_label
        arguments['y_label'] = arg.y_label
        arguments['e_label'] = arg.y_label
        arguments['x_ind'] = arg.x_ind
        arguments['y_ind'] = arg.y_ind
        arguments['e_ind'] = arg.e_ind
        arguments['datapath'] = arg.datapath
        arguments['user_params'] = arg.user_params

        # TODO: add some checks to user passed data

        return arguments

    def make_dir(dirname, i=1):
        """
        function to make a directory, recursively adding _new if that name already exists
        :param dirname: str: name of directory to create
        :param i: the run number we are on
        :return: str: the directory name which was available, and all subsequent data should be saved in
        """
        try:
            os.mkdir(f'{dirname}')
        except FileExistsError as e:
            dirname = make_dir(f'{dirname}_new', i + 1)
            if i == 1:
                print(e, f'. So I named the file: {dirname}')
            return dirname
        return dirname
    #####

    # i.e. called from bash
    import argparse

    parser = argparse.ArgumentParser(
        description='fit peaks and background to the given data given a set of parameter'
    )
    parser.add_argument('--param_file_path', type=str, default='./params.txt',
                        help='input filepath to param file, if you want to use it')
    parser.add_argument('--x_label', type=str, default='x_axis',
                        help='the label for independent variables')
    parser.add_argument('--y_label', type=str, default='y_axis',
                        help='the label for dependent variables')
    parser.add_argument('--e_label', type=str, default='y_error',
                        help='the label for uncertainties in y')
    parser.add_argument('--x_ind', type=int, default=0,
                        help='the column in data which is the independent data')
    parser.add_argument('--y_ind', type=int, default=1,
                        help='the column in data which is the dependent data')
    parser.add_argument('--e_ind', type=Union[int, None], default=None,
                        help='the column in data which is the independent data uncertainties')
    parser.add_argument('--datapath', type=str, default='./data.txt',
                        help='relative path to the datafile from where python script is called')
    parser.add_argument('--user_params', type=Dict, default={'yfit': None, 'background': None, 'peak_types': [],
                            'peak_centres': [], 'peak_widths':[], 'peak_amps': [], 'chisq': None, 'free_params': None,
                                                          'p_value':None, 'tightness':None},
                        help='the fit data as specified in the Thunder __init__')
    args = parser.parse_args()  # this allows us to now use them all

    if args.param_file_path: # if there is a params file then use it
        LOGGER.info('Using params file')
        arguments = parse_param_file(args.param_file_path) # parse it
    else:
        print('not using params file')
        arguments = parse_args(args) # else use argparse but put in dictionary form

    dirname = make_dir('analysed')  # make a dict for the processed data to be saved in

    thunder = main(arguments)

    # save a plot of the figure and the thunder object
    dataname = os.path.basename(arguments['datapath'])
    save_plot(thunder.plot, path=dirname, figname=f"{dataname}.svg")
    save_thunder(thunder, path=dirname, filename=f"{dataname}.p")
    save_fit_report(thunder.fit_data, path=dirname, filename=f"{dataname}_report.json")