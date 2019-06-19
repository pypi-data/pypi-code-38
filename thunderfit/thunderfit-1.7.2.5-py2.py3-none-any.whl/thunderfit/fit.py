import peak_finding
import normalisation
import background.background_removal as bg_remove
import plotting
import utilities as utili
import background.scarf as scarf
from lmfit import models
import lmfit
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import copy
from typing import Dict, Union
import re
import difflib
import os
import logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


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
        self.data: pd.DataFrame = pd.DataFrame(
            [])  # this is what we will create later
        # later we will fill this with background remove data
        self.data_bg_rm: pd.DataFrame = pd.DataFrame([])
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

        self.user_params: Dict = {
            "no_peaks": None,
            'user_input': None,
            'yfit': None,
            'background': None,
            'peak_types': [],
            'peak_centres': [],
            'peak_widths': [],
            'peak_amps': [],
            'chisq': None,
            'free_params': None,
            'p_value': None,
            'tightness': None,
            'bounds': {
                'centers': None,
                'widths': None,
                'amps': None}}

        if isinstance(
                input,
                Thunder):  # if only pass one but its already a thunder object then just use that
            # add all the details in depending on args
            self.overwrite_thunder(input)
        elif isinstance(input, dict):
            # add all the details in depending on args
            self.create_thunder(input)
        else:
            raise TypeError('Cannot convert input to Thunder object')

        self.data = utili.load_data(
            self.datapath,
            self.x_ind,
            self.y_ind,
            self.x_label,
            self.y_label,
            self.e_ind,
            self.e_label)  # load the data

        self.tightness = utili.tightness_setter(self.user_params['tightness'])

    # loading thunder object
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
        self.x_label = inp.get(
            'x_label',
            self.x_label)  # if the key exists then set as that, otherwise make it
        self.y_label = inp.get('y_label', self.y_label)
        self.e_label = inp.get('e_label', self.e_label)
        try:
            self.x_ind = inp['x_ind']
            self.y_ind = inp['y_ind']
            self.e_ind = inp['e_ind']
            self.datapath = inp['datapath']
        except KeyError as e:
            LOGGER.info(f"KeyError: Missing field in the data dictionary: {e}")
        self.user_params = inp.get('user_params', self.user_params)
    # end loading

    # background
    @staticmethod
    def background_finder(
            y_data,
            y_label,
            x_data,
            x_label,
            bg,
            data_bg_rm,
            user_input):
        if bg == 'no':  # then user doesn't want to make a background
            LOGGER.warning(
                "Warning: no background specified, so not using a background,"
                " this may prevent algorithm from converging")
            # set the background as 0 everywhere
            bg = np.array([0 for _ in y_data])
            data_bg_rm[y_label] = y_data  # no background subtracted
            data_bg_rm[x_label] = x_data

        elif bg == 'SCARF':
            data_bg_rm, bg = scarf.perform_scarf(
                data_bg_rm, y_data, y_label, x_data, x_label, user_input)

        elif isinstance(bg, np.ndarray):
            assert len(bg) == len(y_data), \
                "the background generated or passed is of incorrect length"
            # subtract user supplied background from the data
            data_bg_rm[y_label] = y_data - bg
            data_bg_rm[x_label] = x_data

        elif bg == 'OLD':
            bg = bg_remove.find_background(
                y_data,
                bg_remove.residual_baseline,
                bg_remove.baseline_als)  # find a background the old way
            # subtract background from the data
            data_bg_rm[y_label] = y_data - bg
            data_bg_rm[x_label] = x_data

        else:  # then it is the incorrect type
            raise TypeError(
                'the background passed is in the incorrect format, please pass as type np array')

        return bg, data_bg_rm
    # background end

    # peak finding
    # maybe tidy this up a bit?
    @staticmethod
    def peaks_unspecified(
            data_bg_rm,
            x_label,
            y_label,
            tightness,
            user_params):

        peak_no = user_params["no_peaks"]
        # pass in prominence x2 values

        if len(user_params['peak_centres']) == 0 or len(
                user_params['peak_centres']) < peak_no:
            if peak_no and len(
                    user_params['peak_centres']) < peak_no and len(
                    user_params['peak_centres']):
                logging.warning(
                    "you specified less peak centers than peak_numbers."
                    " Currently only finding all peaks based on tightness criteria or using all supplied is possible")
            prominence = 1.6
            if not peak_no:  # then they don't know so we can find everything in one go and save some time
                peak_info = peak_finding.find_cents(
                    prominence, data_bg_rm[y_label], find_all=True)
                center_indices = peak_info['center_indices']
                peak_amps = peak_info['amps']
                peak_left_edges, peak_right_edges = peak_info['left_edges'], peak_info['left_edges']
                peak_widths = data_bg_rm[x_label][peak_right_edges].values - \
                    data_bg_rm[x_label][peak_left_edges].values  # the xvalues can be indexed from the data

                user_params['peak_centres'] = data_bg_rm[x_label][center_indices].values
                user_params['peak_amps'] = peak_amps
                user_params['peak_widths'] = peak_widths
                user_params["no_peaks"] = len(center_indices)

            else:  # just find the centers
                center_indices = peak_finding.find_cents(
                    prominence, data_bg_rm[y_label])
                # take the first n as user has specified how
                center_indices = center_indices[:peak_no]
                # many peaks they want
                # need to pick the correct amount of peaks
                user_params['peak_centres'] = data_bg_rm[x_label][center_indices].values
        elif len(user_params['peak_centres']) > peak_no:
            logging.warning(
                "specified more peak centers than no_peaks. cutting the peaks supplied as [:no_peaks]")
            user_params['peak_centres'] = user_params['peak_centres'][:peak_no]

        if len(user_params['peak_amps']) == 0 or len(
                user_params['peak_amps']) < peak_no:
            if peak_no and len(
                    user_params['peak_amps']) < peak_no and len(
                    user_params['peak_amps']):
                logging.warning(
                    "you specified less peak amps than peak_numbers."
                    " Currently only finding all peaks based on tightness criteria or using all supplied is possible")
            center_x_values = user_params['peak_centres']
            peak_amps = peak_finding.find_peak_properties(
                1, center_x_values, data_bg_rm[y_label], 'amps')
            user_params['peak_amps'] = peak_amps
        elif len(user_params['peak_amps']) > peak_no:
            logging.warning(
                "specified more peak amps than no_peaks. cutting the peaks supplied as [:no_peaks]")
            user_params['peak_amps'] = user_params['peak_amps'][:peak_no]

        if len(user_params['peak_widths']) == 0 or len(
                user_params['peak_widths']) < peak_no:
            if peak_no and len(
                    user_params['peak_widths']) < peak_no and len(
                    user_params['peak_widths']):
                import ipdb
                ipdb.set_trace()
                logging.warning(
                    "you specified less peak widths than peak_numbers."
                    " Currently only finding all peaks based on tightness criteria or using all supplied is possible")
            center_x_values = user_params['peak_centres']
            peak_left_edges, peak_right_edges = peak_finding.find_peak_properties(
                1, center_x_values, data_bg_rm[y_label], 'widths')  # get the indices of edges
            peak_widths = data_bg_rm[x_label][peak_right_edges].values - \
                data_bg_rm[x_label][peak_left_edges].values  # the xvalues can be indexed from the data
            user_params['peak_widths'] = peak_widths
        elif len(user_params['peak_widths']) > peak_no:
            logging.warning(
                "specified more peak widths than no_peaks. cutting the peaks supplied as [:no_peaks]")
            user_params['peak_widths'] = user_params['peak_widths'][:peak_no]

        if len(user_params['peak_types']) == 0 or len(
                user_params['peak_types']) < peak_no:
            if peak_no and len(
                    user_params['peak_types']) < peak_no and len(
                    user_params['peak_types']):
                logging.warning(
                    "you specified less peak types than peak_numbers."
                    " Currently only finding all peaks based on tightness criteria or using all supplied is possible")
            # we assume all the types are gaussian
            user_params['peak_types'] = [
                'LorentzianModel' for _ in user_params['peak_centres']]
        elif len(user_params['peak_types']) > peak_no:
            logging.warning(
                "specified more peak types than no_peaks. cutting the peaks supplied as [:no_peaks]")
            user_params['peak_types'] = user_params['peak_widths'][:peak_no]

        return user_params
    # peak finding end

    # peak fitting
    def fit_peaks(self, data_bg_rm, user_params, y_label, x_label):

        specs = self.build_specs(
            data_bg_rm[x_label].values,
            data_bg_rm[y_label].values,
            user_params)

        model, peak_params = self.generate_model(specs)
        peaks = model.fit(specs['y_bg_rm'], peak_params, x=specs['x_bg_rm'])
        if not peaks.success:
            logging.warning(
                'The fitting routine failed! exiting programme. Try lowering tightness settings or manually '
                'inputting a background, peak bounds and peak info.')
        peak_params = peaks.best_values

        return user_params, specs, model, peak_params, peaks

    @staticmethod
    def make_bounds(user_params, tightness):
        bounds = {}
        peaks = user_params['no_peaks']

        if not user_params['bounds']['centers'] or len(
                user_params['bounds']['centers']) != peaks:
            l_cent_bounds = [
                cent -
                tightness['centre_bounds'] *
                user_params['peak_widths'][i] for i,
                cent in enumerate(
                    user_params['peak_centres'])]
            u_cent_bounds = [
                cent +
                tightness['centre_bounds'] *
                user_params['peak_widths'][i] for i,
                cent in enumerate(
                    user_params['peak_centres'])]
            cent_bounds = list(zip(l_cent_bounds, u_cent_bounds))
            bounds['centers'] = cent_bounds

        if not user_params['bounds']['widths'] or len(
                user_params['bounds']['widths']) != peaks:
            peak_widths = user_params['peak_widths']
            l_width_bounds = [width / tightness['width_bounds'][0]
                              for width in peak_widths]
            u_width_bounds = [width * tightness['width_bounds'][1]
                              for width in peak_widths]
            width_bounds = list(zip(l_width_bounds, u_width_bounds))
            bounds['widths'] = width_bounds

        if not user_params['bounds']['amps'] or len(
                user_params['bounds']['amps']) != peaks:
            peak_amps = user_params['peak_amps']
            l_amp_bounds = [amp / tightness['amps_bounds'][0]
                            for amp in peak_amps]
            u_amp_bounds = [amp * tightness['amps_bounds'][1]
                            for amp in peak_amps]
            amp_bounds = list(zip(l_amp_bounds, u_amp_bounds))
            bounds['amps'] = amp_bounds

        return bounds

    @staticmethod
    def build_specs(x_bg_rm, y_bg_rm, user_params):
        specs = {'x_bg_rm': x_bg_rm,
                 'y_bg_rm': y_bg_rm,
                 'model': [{'type': user_params['peak_types'][i],
                            'params': {'center': user_params['peak_centres'][i],
                                       'amp': user_params['peak_amps'][i],
                                       'sigma': user_params['peak_widths'][i],
                                       'gamma':user_params['peak_widths'][i]},
                            'bounds': {'centers': user_params['bounds']['centers'][i],
                                       'amps': user_params['bounds']['amps'][i],
                                       'widths': user_params['bounds']['widths'][i]}} for i,
                           _ in enumerate(user_params['peak_centres'])]}
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
            if basis_func['type'] in [
                'GaussianModel',
                'LorentzianModel',
                    'VoigtModel']:
                # for now VoigtModel has gamma constrained to sigma
                w_min = basis_func['bounds']['widths'][0]
                w_max = basis_func['bounds']['widths'][1]
                x_min = basis_func['bounds']['centers'][0]
                x_max = basis_func['bounds']['centers'][1]
                y_min = basis_func['bounds']['amps'][0]
                y_max = basis_func['bounds']['amps'][1]

                model.set_param_hint('sigma', min=w_min, max=w_max)
                model.set_param_hint('center', min=x_min, max=x_max)
                model.set_param_hint('height', min=y_min, max=y_max)
                model.set_param_hint('amplitude', min=1e-6)

                # default guess is horrible!! do not use guess()
                default_params = {
                    prefix + 'center': basis_func['params']['center'],
                    prefix + 'height': basis_func['params']['amp'],
                    prefix + 'sigma': basis_func['params']['sigma']
                }
            else:
                raise NotImplemented(
                    f'model {basis_func["type"]} not implemented yet')

            model_params = model.make_params(
                **default_params, **basis_func.get('params', {}))

            if params is None:  # first loop
                params = model_params
                composite_model = model
            else:  # subsequent loops
                params.update(model_params)
                composite_model = composite_model + model

        return composite_model, params
    # peak fitting end

    def plot_all(self):
        # plot each component of the model
        ax = plotting.plot_fits(
            self.data_bg_rm[self.x_label], self.peaks.eval_components())
        # plot the background supplied by user
        ax = plotting.plot_background(
            self.data_bg_rm[self.x_label], self.user_params['background'], ax)
        ax = plotting.plot_fit_sum(self.data_bg_rm[self.x_label],
                                   self.peaks.best_fit,
                                   self.user_params['background'],
                                   ax)  # plot the fitted data
        try:
            ax = plotting.plot_uncertainty_curve(self.data[self.x_label], self.peaks.eval_uncertainty(
                sigma=3), self.peaks.best_fit, ax)  # plot a band of uncertainty
        except TypeError:
            logging.warning(
                'There are not uncertainties available for some reason - '
                'try lowering the tightness of automatic bounds')
        ax = plotting.plot_data(
            self.data[self.x_label], self.data[self.y_label], ax)  # plot the raw data

        ax.minorticks_on()
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)

        self.plot = plt

    # this needs some fixing
    def fit_report(self):
        self.fit_data = {mod_no: {}
                         for mod_no in range(len(self.user_params['peak_types']))}

        # total fit data
        chi_sq = self.peaks.chisqr
        reduced_chi_sq = self.peaks.redchi
        free_params = round(chi_sq / reduced_chi_sq)

        # individual parameter data
        param_info = {
            "center": "centers",
            "amplitude": "amps",
            "sigma": "widths",
            "fwhm": False,
            "height": False}
        for parameter, param_obj in self.peaks.params.items():
            model_no = int(re.findall(r'\d+', parameter)[0])
            param_type = param_info[difflib.get_close_matches(
                parameter, param_info.keys())[0]]

            if param_type:
                value = param_obj.value
                err = param_obj.stderr
                type = self.user_params['peak_types'][model_no]
                bounds = self.user_params['bounds'][param_type][model_no]

                fit_info = {"value": value,
                            "stderr": err,
                            "peak_type": type,
                            "bounds": bounds}

                self.fit_data[model_no][param_type] = fit_info


# TODO move bounds making into a new function in main
def main(arguments):
    thunder = Thunder(copy.deepcopy(arguments))  # load object

    thunder.user_params['background'], thunder.data_bg_rm = thunder.background_finder(thunder.data[thunder.y_label],
                                                                                      thunder.y_label, thunder.data[thunder.x_label],
                                                                                      thunder.x_label, thunder.user_params['background'],
                                                                                      thunder.data_bg_rm, thunder.user_params['user_input'])  # then determine the background

    # thunder.data_bg_rm[thunder.y_label], (mean_y_data, std_dev) = \
    #                                        normalisation.svn(thunder.data_bg_rm[thunder.y_label]) # normalise the data
    # thunder.user_params['background'], _ = normalisation.svn(thunder.user_params['background'],
    #                                                mean_y_data, std_dev) #normalise with data from bg subtracted data
    # thunder.data[thunder.y_label], _ = normalisation.svn(thunder.data[thunder.y_label],
    # mean_y_data, std_dev) #normalise with data from bg subtracted data

    thunder.user_params = thunder.peaks_unspecified(
        thunder.data_bg_rm,
        thunder.x_label,
        thunder.y_label,
        thunder.tightness,
        thunder.user_params)
    thunder.user_params['bounds'] = thunder.make_bounds(
        thunder.user_params, thunder.tightness)

    # now fit peaks
    thunder.user_params, thunder.specs, thunder.model, thunder.peak_params, thunder.peaks = thunder.fit_peaks(
        thunder.data_bg_rm, thunder.user_params, thunder.y_label, thunder.x_label)

    thunder.plot_all()
    thunder.fit_report()

    return thunder


if __name__ == '__main__':
    # i.e. called from bash
    import argparse

    parser = argparse.ArgumentParser(
        description='fit peaks and background to the given data given a set of parameter')
    parser.add_argument(
        '--param_file_path',
        type=str,
        default='./params.txt',
        help='input filepath to param file, if you want to use it')
    parser.add_argument('--x_label', type=str, default='x_axis',
                        help='the label for independent variables')
    parser.add_argument('--y_label', type=str, default='y_axis',
                        help='the label for dependent variables')
    parser.add_argument('--e_label', type=str, default='y_error',
                        help='the label for uncertainties in y')
    parser.add_argument(
        '--x_ind',
        type=int,
        default=0,
        help='the column in data which is the independent data')
    parser.add_argument('--y_ind', type=int, default=1,
                        help='the column in data which is the dependent data')
    parser.add_argument('--e_ind',
                        type=Union[int,
                                   None],
                        default=None,
                        help='the column in data which is the independent data uncertainties')
    parser.add_argument(
        '--datapath',
        type=str,
        default='./data.txt',
        help='relative path to the datafile from where python script is called')
    parser.add_argument(
        '--user_params',
        type=Dict,
        default={
            'yfit': None,
            'background': None,
            'peak_types': [],
            'peak_centres': [],
            'peak_widths': [],
            'peak_amps': [],
            'chisq': None,
            'free_params': None,
            'p_value': None,
            'tightness': None},
        help='the fit data as specified in the Thunder __init__')
    args = parser.parse_args()  # this allows us to now use them all

    if args.param_file_path:  # if there is a params file then use it
        LOGGER.info('Using params file')
        arguments = utili.parse_param_file(args.param_file_path)  # parse it
    else:
        print('not using params file')
        # else use argparse but put in dictionary form
        arguments = utili.parse_args(args)

    curr_time = time.localtime(time.time())
    # make a dict for the processed data to be saved in
    dirname = utili.make_dir(f'analysed_{curr_time}')

    thunder = main(arguments)

    # save a plot of the figure and the thunder object
    dataname = os.path.basename(arguments['datapath'])
    utili.save_plot(thunder.plot, path=dirname, figname=f"{dataname}.svg")
    utili.save_thunder(thunder, path=dirname, filename=f"{dataname}.p")
    utili.save_fit_report(
        thunder.fit_data,
        path=dirname,
        filename=f"{dataname}_report.json")
