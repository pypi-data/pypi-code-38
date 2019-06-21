import argparse
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas
import sys

from astropy.stats import sigma_clip
from astropy.modeling import models, fitting, Model
from ccdproc import CCDData
from ccdproc import ImageFileCollection
from scipy import signal

import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(levelname)s]: %(message)s',
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'rotate_file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'focus_finder.log',
            'encoding': 'utf8',
            'maxBytes': 100000,
            'backupCount': 1,
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'rotate_file'],
            'level': 'DEBUG',
        },
}
}

LOG_FORMAT = '[%(asctime)s][%(levelname)s]: %(message)s'
LOG_LEVEL = logging.INFO

DATE_FORMAT = '%H:%M:%S'

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

logging.config.dictConfig(LOGGING)

log = logging.getLogger(__name__)


def get_args(arguments=None):
    parser = argparse.ArgumentParser(
        description="Get best focus value using a sequence of images with "
                    "different focus value"
    )

    parser.add_argument('--data-path',
                        action='store',
                        dest='data_path',
                        default=os.getcwd(),
                        help='Folder where data is located')

    parser.add_argument('--file-pattern',
                        action='store',
                        dest='file_pattern',
                        default='*.fits',
                        help='Pattern for filtering files.')

    parser.add_argument('--obstype',
                        action='store',
                        dest='obstype',
                        default='FOCUS',
                        help='Only the files whose OBSTYPE matches what you '
                             'enter here will be used. The default should '
                             'always work.')

    parser.add_argument('--features-model',
                        action='store',
                        dest='features_model',
                        choices=['gaussian', 'moffat'],
                        default='gaussian',
                        help='Model to use in fitting the features in order to'
                             'obtain the FWHM for each of them')

    parser.add_argument('--debug',
                        action='store_true',
                        dest='debug',
                        help='Activate debug mode')

    args = parser.parse_args(args=arguments)

    if not os.path.isdir(args.data_path):
        parser.error("Data location {} does not exist".format(args.data_path))
    elif len(glob.glob(os.path.join(args.data_path, args.file_pattern))) == 0:
        parser.error("There are no files matching \"{}\" in the folder \"{}\"".format(args.file_pattern, args.data_path))

    return args


def get_peaks(ccd, file_name='', plots=False):
    """Identify peaks in an image

    For Imaging and Spectroscopy the images obtained for focusing have lines
    that in the first case is an image of the slit and for the second is the
    spectrum of lamp, strategically selected for a good coverage of lines across
    the detector.

    Args:
        ccd (object): Image to get peaks from
        file_name (str): Name of the file used. This is optional and is used
        only for debugging purposes.
        plots (bool): Show plots of the profile, background and
        background-subtracted profile

    Returns:
        A list of peak values, peak intensities as well as the x-axis and the
        background subtracted spectral profile. For Imaging is the same axis as
        the spectral axis.

    """
    width, length = ccd.data.shape

    low_limit = int(width / 2 - 50)
    high_limit = int(width / 2 + 50)

    raw_profile = np.median(ccd.data[low_limit:high_limit, :], axis=0)
    x_axis = np.array(range(len(raw_profile)))

    clipped_profile = sigma_clip(raw_profile, sigma=1, iters=5)

    _mean = np.mean(clipped_profile)

    clipped_x_axis = [i for i in range(len(clipped_profile)) if not clipped_profile.mask[i]]
    cleaned_profile = clipped_profile[~clipped_profile.mask]

    background_model = models.Linear1D(slope=0,
                                       intercept=np.mean(clipped_profile))

    fitter = fitting.SimplexLSQFitter()

    fitted_background = fitter(background_model,
                               clipped_x_axis,
                               cleaned_profile)

    profile = raw_profile - np.array(fitted_background(x_axis))

    filtered_data = np.where(
        np.abs(profile > profile.min() + 0.03 * profile.max()), profile,
        None)
    filtered_data = np.array(
        [0 if it is None else it for it in filtered_data])

    peaks = signal.argrelmax(filtered_data, axis=0, order=5)[0]


    if len(peaks) == 1:
        log.debug("Found {} peak in file".format(len(peaks)))
    else:
        log.debug("Found {} peaks in file".format(len(peaks)))

    values = np.array([profile[int(index)] for index in peaks])

    if plots:   # pragma: no cover
        plt.title("{} {}".format(file_name, np.mean(clipped_profile)))
        plt.axhline(0, color='k')
        plt.plot(x_axis, raw_profile, label='Raw Profile')
        plt.plot(x_axis, clipped_profile)
        plt.plot(x_axis, background_model(x_axis),
                 label='Background Level')
        plt.plot(x_axis, fitted_background(x_axis), label='Background Level')
        # plt.plot(x_axis, profile, label='Background Subtracted Profile')
        # plt.plot(x_axis, filtered_data, label="Filtered Data")
        # for _peak in peaks:
        #     plt.axvline(_peak, color='k', alpha=0.6)
        plt.legend(loc='best')
        plt.show()

    return peaks, values, x_axis, profile


def get_fwhm(peaks, values, x_axis, profile, model):
    """Finds FWHM for an image by fitting a model

    For Imaging there is only one peak (the slit itself) but for spectroscopy
    there are many. In that case a 3-sigma clipping 1-iteration is applied to
    clean the values and then the mean is returned. In case that a FWHM can't be
    obtained a `None` value is returned.

    This function allows the use of `Gaussian1D` and `Moffat1D` models to be
    fitted to each line. `Gaussian1D` produces more consistent results though
    `Moffat1D` usually fits better the whole line profile.

    Args:
        peaks (numpy.ndarray): An array of peaks present in the profile.
        values (numpy.ndarray): An array of values at peak location.
        x_axis (numpy.ndarray): X-axis for the profile, usually is equivalent to
        `range(len(profile))`.
        profile (numpy.ndarray): 1-dimensional profile of the image being
         analyzed.
        model (Model): A model to fit to each peak location. `Gaussian1D` and
        `Moffat1D` are supported.

    Returns:
        The FWHM, mean FWHM or `None`.

    """
    fitter = fitting.LevMarLSQFitter()
    all_fwhm = []
    for peak_index in range(len(peaks)):
        if model.__class__.name == 'Gaussian1D':
            model.amplitude.value = values[peak_index]
            model.mean.value = peaks[peak_index]
            # TODO (simon): stddev should be estimated based on binning and slit size
            model.stddev.value = 5
            log.debug(
                "Fitting {} with amplitude={}, mean={}, stddev={}".format(
                    model.__class__.name,
                    model.amplitude.value,
                    model.mean.value,
                    model.stddev.value))

        elif model.__class__.name == 'Moffat1D':
            model.amplitude.value = values[peak_index]
            model.x_0.value = peaks[peak_index]
            log.debug(
                "Fitting {} with amplitude={}, x_0={}".format(
                    model.__class__.name,
                    model.amplitude.value,
                    model.x_0.value))

        model = fitter(model,
                       x_axis,
                       profile)

        if not np.isnan(model.fwhm):
            all_fwhm.append(model.fwhm)

    if len(all_fwhm) == 1:
        log.info("Returning single FWHM value: {}".format(all_fwhm[0]))
        return all_fwhm[0]
    else:
        log.info("Applying sigma clipping to collected FWHM values."
                 " SIGMA: 3, ITERATIONS: 1")
        clipped_fwhm = sigma_clip(all_fwhm, sigma=3, iters=1)

        if np.ma.is_masked(clipped_fwhm):
            cleaned_fwhm = clipped_fwhm[~clipped_fwhm.mask]
            removed_fwhm = clipped_fwhm[clipped_fwhm.mask]
            log.info("Discarded {} FWHM values".format(len(removed_fwhm)))
            for _value in removed_fwhm.data:
                log.debug("FWHM {} discarded".format(_value))
        else:
            log.debug("No FWHM value was discarded.")
            cleaned_fwhm = clipped_fwhm

        if len(cleaned_fwhm) > 0:
            log.debug("Remaining FWHM values: {}".format(len(cleaned_fwhm)))
            for _value in cleaned_fwhm:
                log.debug("FWHM value: {}".format(_value))
            mean_fwhm = np.mean(cleaned_fwhm)
            log.debug("Mean FWHM value {}".format(mean_fwhm))
            return mean_fwhm
        else:
            log.error("Unable to obtain usable FWHM value")
            log.debug("Returning FWHM None")
            return None


class GoodmanFocus(object):

    keywords = ['INSTCONF',
                'FOCUS',
                'CAM_TARG',
                'GRT_TARG',
                'CAM_FOC',
                'COLL_FOC',
                'FILTER',
                'FILTER2',
                'GRATING',
                'SLIT',
                'WAVMODE',
                'EXPTIME',
                'RDNOISE',
                'GAIN',
                'OBSTYPE',
                'ROI']

    def __init__(self, arguments=None):
        self.args = get_args(arguments=arguments)
        self.log = logging.getLogger(__name__)
        if self.args.debug:
            self.log.setLevel(level=logging.DEBUG)

        if self.args.features_model == 'gaussian':
            self.feature_model = models.Gaussian1D()
        elif self.args.features_model == 'moffat':
            self.feature_model = models.Moffat1D()

        self.__ccd = None
        self.file_name = None
        self.__best_focus = None
        self._fwhm = None

        self.polynomial = models.Polynomial1D(degree=5)
        self.fitter = fitting.LevMarLSQFitter()
        self.linear_fitter = fitting.LinearLSQFitter()

        if os.path.isdir(self.args.data_path):
            self.full_path = self.args.data_path
        else:
            sys.exit("No such directory")

        _ifc = ImageFileCollection(self.full_path, keywords=self.keywords)

        self.ifc = _ifc.summary.to_pandas()
        self.ifc = self.ifc[(self.ifc['OBSTYPE'] == self.args.obstype)]
        self.focus_groups = []
        configs = self.ifc.groupby(['CAM_TARG',
                                    'GRT_TARG',
                                    'FILTER',
                                    'FILTER2',
                                    'GRATING',
                                    'SLIT',
                                    'WAVMODE',
                                    'RDNOISE',
                                    'GAIN',
                                    'ROI']).size().reset_index().rename(
            columns={0: 'count'})
        # print(configs.to_string())
        for i in configs.index:
            focus_group = self.ifc[((self.ifc['CAM_TARG'] == configs.iloc[i]['CAM_TARG']) &
                                    (self.ifc['GRT_TARG'] == configs.iloc[i]['GRT_TARG']) &
                                    (self.ifc['FILTER'] == configs.iloc[i]['FILTER']) &
                                    (self.ifc['FILTER2'] == configs.iloc[i]['FILTER2']) &
                                    (self.ifc['GRATING'] == configs.iloc[i]['GRATING']) &
                                    (self.ifc['SLIT'] == configs.iloc[i]['SLIT']) &
                                    (self.ifc['WAVMODE'] == configs.iloc[i]['WAVMODE']) &
                                    (self.ifc['RDNOISE'] == configs.iloc[i]['RDNOISE']) &
                                    (self.ifc['GAIN'] == configs.iloc[i]['GAIN']) &
                                    (self.ifc['ROI'] == configs.iloc[i]['ROI']))]
            self.focus_groups.append(focus_group)

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        if value is not None:
            self._fwhm = value


    def __call__(self, *args, **kwargs):
        for focus_group in self.focus_groups:
            # print(focus_group)

            focus_dataframe = self.get_focus_data(group=focus_group)

            self._fit(df=focus_dataframe)
            self.log.info("Best Focus for {} is {}".format(self.file_name,
                                                           self.__best_focus))
            if True:   # pragma: no cover
                # TODO (simon): Do properly using matplotlib or pandas alone
                # fig = plt.subplots()
                focus_dataframe.plot(x='focus', y='fwhm', marker='x')
                plt.axvline(self.__best_focus)
                plt.title("Best Focus: {}".format(self.__best_focus))
                focus_list = focus_dataframe['focus'].tolist()
                new_x_axis = np.linspace(focus_list[0], focus_list[-1], 1000)
                plt.plot(new_x_axis,
                         self.polynomial(new_x_axis), label='Model')
                plt.show()

    def _fit(self, df):
        focus = df['focus'].tolist()
        fwhm = df['fwhm'].tolist()

        max_focus = np.max(focus)
        min_focus = np.min(focus)
        self.polynomial = self.fitter(self.polynomial, focus, fwhm)
        self._get_local_minimum(x1=min_focus, x2=max_focus)
        return self.polynomial

    def _get_local_minimum(self, x1, x2):
        x_axis = np.linspace(x1, x2, 2000)
        modeled_data = self.polynomial(x_axis)
        derivative = []
        for i in range(len(modeled_data) - 1):
            derivative.append(modeled_data[i+1] - modeled_data[i]/(x_axis[i+1]-x_axis[i]))

        self.__best_focus = x_axis[np.argmin(np.abs(derivative))]

        return self.__best_focus

    def get_focus_data(self, group):
        """Collects all the relevant data for finding best focus

        It is important that the data is not very contaminated because there is
        no built-in cleaning process.


        Args:
            group (DataFrame): The `group` refers to a set of images obtained
            most likely in series and with the same configuration.

        Returns:
            a `pandas.DataFrame` with three columns. `file`, `fwhm` and `focus`.

        """
        focus_data = []
        for self.file_name in group.file.tolist():
            self.log.debug("Processing file: {}".format(self.file_name))
            self.__ccd = CCDData.read(os.path.join(self.full_path,
                                                   self.file_name),
                                      unit='adu')

            peaks, values, x_axis,  profile = get_peaks(
                ccd=self.__ccd,
                file_name=self.file_name,
                plots=self.args.debug)

            self.fwhm = get_fwhm(peaks=peaks,
                                 values=values,
                                 x_axis=x_axis,
                                 profile=profile,
                                 model=self.feature_model)

            self.log.info("File: {} Focus: {} FWHM: {}"
                          "".format(self.file_name,
                                    self.__ccd.header['CAM_FOC'],
                                    self.fwhm))
            if self.fwhm:
                focus_data.append([self.file_name, self.fwhm, self.__ccd.header['CAM_FOC']])
            else:
                self.log.warning("File: {} FWHM is: {} FOCUS: {}"
                                 "".format(self.file_name,
                                           self.fwhm,
                                           self.__ccd.header['CAM_FOC']))

        focus_data_frame = pandas.DataFrame(
            focus_data,
            columns=['file', 'fwhm', 'focus']).sort_values(by='focus')

        return focus_data_frame


def run_goodman_focus(args=None):   # pragma: no cover
    """Entrypoint

    Args:
        args (list): (optional) a list of arguments and respective values.

    """

    goodman_focus = GoodmanFocus(arguments=args)
    goodman_focus()


if __name__ == '__main__':   # pragma: no cover
    # full_path = '/user/simon/data/soar/work/focus2'
    get_focus = GoodmanFocus()
    get_focus()

