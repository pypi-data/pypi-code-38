import datetime
import logging
import math
import os
import re

from datetime import timedelta

import georinex as gr
import numpy as np
import scipy.interpolate as interp
import dateparser

import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

import tec_embrace.settings as settings

from tec_embrace.app.downloads import DownloadDCB, DownloadOrbit, DownloadGlonassChannel
from tec_embrace.app.parser import ParserChannels, ParserRinexChannels, ParserOrbit, ParserDCB


class Utils:
    """
    Python utils, converting and dealing with variable types
    """

    @staticmethod
    def plot_absolute_vertical(prn, absolute, vertical):
        fig, ax = plt.subplots(2, 1)

        ax[0].set_title(prn)

        ax[0].plot(absolute)
        ax[0].set_ylabel('absolute')
        ax[0].grid(True)

        ax[1].plot(vertical)
        ax[1].set_ylabel('vertical')
        ax[1].grid(True)

        fig.savefig(prn + "_absolute_vertical.pdf")

    @staticmethod
    def plot_relative(prn, cycle_slip, rtec):
        fig, ax = plt.subplots(2, 1)

        ax[0].set_title(prn)

        ax[0].plot(cycle_slip)
        ax[0].set_ylabel('rTEC-cycle_slip')
        ax[0].grid(True)

        ax[1].plot(rtec)
        ax[1].set_ylabel('rTEC')
        ax[1].grid(True)

        fig.savefig(prn + "_rTEC.pdf")

    @staticmethod
    def plot_dtrended(prn, l1, l2, array1, array2, array3):
        fig, axs = plt.subplots(5, 1)

        axs[0].set_title(prn)

        axs[0].plot(array1)
        axs[0].set_ylabel('sTEC')
        axs[0].grid(True)

        axs[1].plot(array2)
        axs[1].set_ylabel('savgol')
        axs[1].grid(True)

        axs[2].plot(array3)
        axs[2].set_ylabel('dtec')
        axs[2].grid(True)

        axs[3].plot(l1)
        axs[3].set_ylabel('l1')
        axs[3].grid(True)

        axs[4].plot(l2)
        axs[4].set_ylabel('l2')
        axs[4].grid(True)

        fig.savefig(prn + "_dTEC.pdf")

    @staticmethod
    def plot_slant(prn, slant_factor, ang_zenital, ang_elev, lat_pp, long_pp):
        fig, axs = plt.subplots(5, 1)

        axs[0].plot(slant_factor)
        axs[0].set_title(prn)
        axs[0].set_ylabel('slant_factor')
        axs[0].grid(True)

        axs[1].plot(ang_zenital)
        axs[1].set_ylabel('ang_zenital')
        axs[1].grid(True)

        axs[2].plot(ang_elev)
        axs[2].set_ylabel('ang_elev')
        axs[2].grid(True)

        axs[3].plot(lat_pp)
        axs[3].set_ylabel('lat_pp')
        axs[3].grid(True)

        axs[4].plot(long_pp)
        axs[4].set_ylabel('long_pp')
        axs[4].grid(True)

        fig.savefig(prn + "_slant.pdf")

    @staticmethod
    def plot_lat_lon_pp_over_map(plt, lat, long, elevation, prn):
        """

        :param lat:
        :param long:
        :param elevation:
        :param prn:
        :return:
        """
        lat_30 = []
        long_30 = []
        elevation_30 = []

        fig, ax = plt.subplots(figsize=(12, 7))

        pos_elv_30 = [i for i, x in enumerate(elevation) if x >= 30]

        for pos in pos_elv_30:
            lat_30.append(lat[pos])
            long_30.append(long[pos])
            elevation_30.append(elevation[pos])

        zoom_scale = 1
        bbox = [np.min(lat_30) - zoom_scale, np.max(lat_30) + zoom_scale, \
                np.min(long_30) - zoom_scale, np.max(long_30) + zoom_scale]

        # m = Basemap(projection='merc', llcrnrlat=bbox[0], urcrnrlat=bbox[1], llcrnrlon=bbox[2], urcrnrlon=bbox[3],
        #             lat_ts=10, resolution='i')
        m = Basemap(projection='ortho', lon_0=bbox[2], lat_0=bbox[0], resolution='l')

        m.drawcoastlines()
        m.fillcontinents(color='#CCCCCC', lake_color='lightblue')

        m.drawparallels(np.arange(bbox[0], bbox[1], (bbox[1] - bbox[0]) / 5), labels=[1, 0, 0, 0])
        m.drawmeridians(np.arange(bbox[2], bbox[3], (bbox[3] - bbox[2]) / 5), labels=[0, 0, 0, 1], rotation=15)
        m.drawmapboundary(fill_color='lightblue')

        alt_min = np.min(elevation_30)
        alt_max = np.max(elevation_30)
        cmap = plt.get_cmap('gist_earth')
        normalize = matplotlib.colors.Normalize(vmin=alt_min, vmax=alt_max)

        for ii in range(0, len(elevation_30)):
            x, y = m(long_30[ii], lat_30[ii])
            color_interp = np.interp(elevation_30[ii], [alt_min, alt_max], [50, 200])
            plt.plot(x, y, markersize=1, marker='o', color=cmap(int(color_interp)))

        cax, _ = matplotlib.colorbar.make_axes(ax)
        cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, label='Elevation')

        plt.savefig('latlon_pp_' + prn + '.pdf', dpi=90, transparent=True)

    @staticmethod
    def array_timestamp_to_datetime(array_timestamp):
        """
        Convert an array with string timestamp to an array of datetimes

        :param array_timestamp: Array with string date in timestamp format
        :return: Array with datetime format elements
        """
        array = []

        for item in array_timestamp.values:
            array.append(dateparser.parse(str(item)))

        return array

    @staticmethod
    def restrict_datearray(date_array, initial, final):
        """
        Create a new array of dates, based only in the interval initial to final

        :param date_array: Array with string date in timestamp format
        :param initial: Initial date
        :param final: Final date
        :return: A restricted date_array based in the range initial to final
        """
        restricted_date_array = [x for x in date_array if initial <= x <= final]

        return restricted_date_array

    @staticmethod
    def array_dict_to_array(array_dict, key):
        """
        Get all values from a specific key in a dictionary array, and transform in a simple array

        :param array_dict: Array of dictionaries
        :param key: Interest key, based on this key that the values in array_dict will be extracted
        :return: Array, with values based on the key passed on
        """
        array = []

        for item in array_dict:
            array.append(item[key])

        return array

    @staticmethod
    def rinex_str_date_to_datetime(hdr):
        """
        From rinex string timestamps, return the right datetime

        :param hdr: Rinex header informations
        :return: A date in datetime format
        """
        string_date = hdr[str(settings.TIME_LAST_OBS[str(hdr['version'])])]

        m = re.search(settings.REGEX_RINEX_DATE, string_date)
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        hour = int(m.group(4))
        minute = int(m.group(5))
        second = int(float(m.group(6)))

        if hdr['version'] == 2.11:
            date = datetime.datetime(year, month, day, 23, 59, (60 - int(hdr['interval'])))
        else:
            date = datetime.datetime(year, month, day, hour, minute, second)

        return date

    @staticmethod
    def interpolate_orbit(orbit, hdr):
        """
        Interpolate X, Y, Z values as sampling on the Rinex file. Thus, both measures have the same precision

        :param orbit: The python orbit object less precise than rinex
        :param hdr: Rinex header, to extract rinex precision, first and last acquisition
        :return: The python orbit object with the same precise than rinex, with interpolated values
        """
        orbit_interpolated = {}
        rinex_last_obs_time = Utils.rinex_str_date_to_datetime(hdr)

        sat_date = orbit['date']
        date_array_interpolated = np.array([])

        aux_date = sat_date[0]
        date_array_interpolated = np.append(date_array_interpolated, sat_date[0])
        while aux_date < rinex_last_obs_time:
            aux_date += timedelta(seconds=float(hdr['interval']))
            date_array_interpolated = np.append(date_array_interpolated, aux_date)

        orbit_interpolated['date'] = date_array_interpolated

        for prn, data in orbit.items():
            if prn is 'date' or prn is 'path':
                continue

            x_aux = np.array([])
            y_aux = np.array([])
            z_aux = np.array([])

            for item in data:
                x_aux = np.append(x_aux, item['x'])
                y_aux = np.append(y_aux, item['y'])
                z_aux = np.append(z_aux, item['z'])

            x_interp = interp.CubicSpline(np.arange(x_aux.size), x_aux)
            x_interp = x_interp(np.linspace(0, x_aux.size - 1, date_array_interpolated.size))

            y_interp = interp.CubicSpline(np.arange(y_aux.size), y_aux)
            y_interp = y_interp(np.linspace(0, y_aux.size - 1, date_array_interpolated.size))

            z_interp = interp.CubicSpline(np.arange(z_aux.size), z_aux)
            z_interp = z_interp(np.linspace(0, z_aux.size - 1, date_array_interpolated.size))

            pos_aux = []
            for i in range(len(date_array_interpolated)):
                pos_aux.append({'x': x_interp[i], 'y': y_interp[i], 'z': z_interp[i]})

            orbit_interpolated[prn] = pos_aux

        return orbit_interpolated

    @staticmethod
    def detect_gap(initial_date, final_date):
        """
        Compare two dates, verify if they are too distant from each other

        :param initial_date: Initial date to be compared
        :param final_date: Final date to be compared
        :return: True for gaps, False if the dates are close
        """
        t1 = initial_date.hour / 24.0 + initial_date.minute / 1440.0 + initial_date.second / 86400.0
        t2 = final_date.hour / 24.0 + final_date.minute / 1440.0 + final_date.second / 86400.0

        if t2 - t1 > settings.ARC_GAP_TIME:
            return True
        else:
            return False

    @staticmethod
    def check_arc_gaps(tec, factor, p2_or_c2, p1_or_c1, prn):
        """
        Calculate the ambiguous phase bias, and subtract it from the relative TEC

        :param tec: The dict python object, with all TEC parameters calculated
        :param factor: The factor TEC
        :param p2_or_c2: The column name for P2 or C2
        :param p1_or_c1: The column name for P1 or C1
        :param prn: The current string PRN: e.g. 'PRN'
        :return:
        """
        p_relative = np.array(tec['relative-l1-l2'][prn][0])
        p_relative_without_nan = p_relative[~np.isnan(p_relative)]

        p_relative_pos = np.where(np.isnan(p_relative))[0]
        p1_c1_nan_pos = np.where(np.isnan(p1_or_c1))[0]
        p2_c2_nan_pos = np.where(np.isnan(p2_or_c2))[0]

        c = np.concatenate([p_relative_pos, p1_c1_nan_pos, p2_c2_nan_pos], axis=0)
        unique_pos = np.unique(c)

        p_relative[unique_pos] = np.nan
        p1_or_c1[unique_pos] = np.nan
        p2_or_c2[unique_pos] = np.nan

        p1_or_c1_without_nan = p1_or_c1[~np.isnan(p1_or_c1)]
        p2_or_c2_without_nan = p2_or_c2[~np.isnan(p2_or_c2)]

        time = np.array(tec['time'])
        time_without_nan = time[~np.isnan(p_relative)]

        narc = 1
        jlast = 0
        a_without_nan = p2_or_c2_without_nan - p1_or_c1_without_nan
        b = p_relative_without_nan[0] - a_without_nan[0]

        for j in range(1, len(a_without_nan)):
            if Utils().detect_gap(time_without_nan[j-1], time_without_nan[j]):
                b /= narc
                for k in range(jlast, j):
                    p_relative_without_nan[k] = factor * (p_relative_without_nan[k] - b)

                jlast = j
                narc = 1
                a_without_nan[j] = p2_or_c2_without_nan[j] - p1_or_c1_without_nan[j]
                b = p_relative_without_nan[j] - a_without_nan[j]
            else:
                narc += 1
                a_without_nan[j] = p2_or_c2_without_nan[j] - p1_or_c1_without_nan[j]
                b += p_relative_without_nan[j] - a_without_nan[j]

        b /= narc
        for k in range(jlast, len(a_without_nan)):
            p_relative_without_nan[k] = factor * (p_relative_without_nan[k] - b)

        nan_pos_in_p_relative = np.where(np.isnan(p_relative))
        nan_pos_in_p_relative = np.array(nan_pos_in_p_relative).flatten().tolist()
        for i in range(len(nan_pos_in_p_relative)):
            nan_pos_in_p_relative[i] -= i

        p_relative = np.insert(p_relative_without_nan, nan_pos_in_p_relative, np.nan)

        return p_relative

    @staticmethod
    def correct_dcb_values(dcb, factor_glonass):
        """

        :param dcb: The original DCB parsed file, with nanoseconds values
        :param factor_glonass:
        :return: The updated DCB parsed file, with the values of bias updated to meters
        """
        dcb_corrected = {}

        if not dcb:
            logging.info(">>>> DCB is empty. Skipping convertion!")
            return

        for key, dcb_type in dcb.items():
            if key is 'path':
                continue

            dcb_corrected[key] = {}
            dcb_aux = {}

            for prn, value in dcb_type.items():
                p1p2_dcb = value
                p1c1_dcb = value
                factor = Utils.frequency_by_constellation(prn, factor_glonass)[5]

                dcb_aux[prn] = ((-p1p2_dcb + p1c1_dcb) * (settings.C / pow(10, 9))) * factor

            dcb_corrected[key].update(dcb_aux)

        return dcb_corrected

    @staticmethod
    def convert_dcb_ns_to_meter(dcb):
        """
        DCB files originally store values in nanoseconds unit. In order to use those values to remove ou correct another
        files or calculation. The units has to be the same. Here, these values are converted to meters unit

        :param dcb: The original DCB parsed file, with nanoseconds values
        :return: The updated DCB parsed file, with the values of bias updated to meters
        """
        dcb_ns = {}

        if not dcb:
            logging.info(">>>> DCB is empty. Skipping convertion!")
            return

        for key, dcb_type in dcb.items():
            if key is 'path':
                continue

            dcb_ns[key] = {}
            dcb_aux = {}
            for prn, value in dcb_type.items():
                ns_to_meter = settings.C * pow(10, -9)
                new_value = [x * ns_to_meter for x in value]
                dcb_aux[prn] = [new_value[0], value[1]]

            dcb_ns[key].update(dcb_aux)

        return dcb_ns

    @staticmethod
    def convert_dcb_ns_to_tecu(dcb, factor_glonass):
        """
        DCB files originally store values in nanoseconds unit. In order to use those values to remove ou correct another
        files or calculation. The units has to be the same. Here, these values are converted to TEC unit (TECU)

        :param dcb: The original DCB parsed file, with nanoseconds values
        :param factor_glonass: Python object with GLONASS factors
        :return: The updated DCB parsed file, with the values of bias updated to TEC Unit
        """
        dcb_tecu = {}
        input = InputFiles()

        for key, dcb_type in dcb.items():
            if key is 'path':
                continue

            dcb_tecu[key] = {}
            dcb_aux = {}
            for prn, value in dcb_type.items():
                ns_to_meter = settings.C * pow(10, -9)
                f1, f2, f3, factor_1, factor_2, factor_3 = input.frequency_by_constellation(prn, factor_glonass)
                new_value = [(x * ns_to_meter * factor_3) for x in value]
                dcb_aux[prn] = [new_value[0], value[1]]

            dcb_tecu[key].update(dcb_aux)

        return dcb_tecu

    @staticmethod
    def check_availability(factor_glonass, dcb, prn):
        """
        Sometimes, the GLONASS factor or DCB array values, might not be available for some specific PRN. Thus, this
        method apply default values for both variables for such cases

        :param factor_glonass: GLONASS factor, with factors values for GLONASS constellation
        :param dcb: Dict object with bias of C1-P1 and P2-P1
        :param prn: The satellite code (PRN) verified: '01', '02', etc
        :return: In case the data are not available, it returns the default values. For instance, the value of 0 for DCB
        indicates it has no compensation under a respective equation
        """
        input = InputFiles()

        dcb_compensate = 0.0
        f1, f2, f3, factor_1, factor_2, factor_3 = input.frequency_by_constellation(prn, factor_glonass)

        if prn not in dcb['P1-P2']:
            logging.info(">>>>>> Relative TEC for {} constellation, was not compensate due to "
                         "the lack of DCB/factor GLONASS for PRN {}".format(prn[0:1], prn))
            return factor_3, dcb_compensate

        if prn not in dcb['C1-P1']:
            logging.info(">>>>>> Relative TEC for {} constellation, was not compensate due to "
                         "the lack of DCB/factor GLONASS for PRN {}".format(prn[0:1], prn))
            return factor_3, dcb_compensate

        if prn[0:1] is 'R' and prn[1:] not in factor_glonass:
            logging.info(">>>>>> Relative TEC for {} constellation, was not compensate due to "
                         "the lack of DCB/factor GLONASS for PRN {}".format(prn[0:1], prn))
            return factor_3, dcb_compensate

        p1p2_dcb = dcb['P1-P2'][prn][0]
        c1p1_dcb = dcb['C1-P1'][prn][0]
        dcb_compensate = ((-p1p2_dcb - c1p1_dcb) * (settings.C / pow(10, 9))) * factor_3

        return factor_3, dcb_compensate


class InputFiles:
    """
    Complementary methods to download all the input files needed for TEC and Bias estimation procedures
    """

    rinex_folder = ""
    path_dcb = ""
    path_orbit = ""
    path_glonass_channel = ""
    min_requeried_version = ""
    constelations = ""
    tec_resolution = ""
    tec_resolution_value = ""
    keys_save = ""

    def __init__(self, rinex_folder=None, path_dcb=None, path_orbit=None, path_glonass_channel=None,
                 min_requeried_version=None, constelations=None, tec_resolution=None, tec_resolution_value=None,
                 keys_save=None):
        self.rinex_folder = rinex_folder
        self.path_dcb = path_dcb
        self.path_orbit = path_orbit
        self.path_glonass_channel = path_glonass_channel
        self.min_requeried_version = min_requeried_version
        self.constelations = constelations
        self.tec_resolution = tec_resolution
        self.tec_resolution_value = tec_resolution_value
        self.keys_save = keys_save      
        
    def setup_rinex_name(self, rinex_folder, rinex_name):
        """
        Test if rinex name is in the old fashion way or in another formats. In case the format is newer or older, the
        method will always return the values needed
            Example of formats name accept:
                2.11: ALMA1520.18O
                3.03: ALMA00BRA_R_20181520000_01D_30S_MO.rnx

        :param rinex_folder: Absolute path to the rinexes folder
        :param rinex_name: String rinex filename
        :return: Returns the String rinex absolute path, and the year, month and doy related
        """
        if rinex_name.endswith(".rnx"):
            day_i, day_f = 16, 19
            year_i, year_f, year_type = 12, 16, "%Y"
            extens = "[rR][nN][xX]$"
        elif bool(re.match("[oO]$", rinex_name[-1:])):
            day_i, day_f = 4, 7
            year_i, year_f, year_type = -3, -1, "%y"
            extens = "[\\d]{2}[oO]$"
        else:
            logging.error(">>>> Error during rinex file reading. Check it and try again!\n")
            raise Exception(">>>> Error during rinex file reading. Check it and try again!\n")

        if len(rinex_name) == 0:
            logging.error('>> Something wrong with parameter \'rinex_name\'!. Empty name!\n')
            raise Exception('>> Something wrong with parameter \'rinex_name\'!. Empty name!\n')
        elif not rinex_name[0:4].isalpha():
            logging.error('>> Something wrong with parameter \'rinex_name\'!. IAGA code not well format!\n')
            raise Exception('>> Something wrong with parameter \'rinex_name\'!. IAGA code not well format!\n')
        elif not rinex_name[day_i:day_f].isdigit() or int(rinex_name[day_i:day_f]) > 366:
            logging.error('>> Something wrong with parameter \'rinex_name\'!. Invalid day of the year!\n')
            raise Exception('>> Something wrong with parameter \'rinex_name\'!. Invalid day of the year!\n')
        elif not bool(re.match(extens, rinex_name[-3:])):
            logging.error('>> Something wrong with parameter \'rinex_name\'!. Wrong extension or not well format!\n')
            raise Exception('>> Something wrong with parameter \'rinex_name\'!. Wrong extension or not well format!\n')

        path = os.path.join(rinex_folder, rinex_name)
        doy = rinex_name[day_i:day_f]
        year = datetime.datetime.strptime(rinex_name[year_i:year_f], year_type).strftime('%Y')
        month = datetime.datetime.strptime(doy, '%j').strftime('%m')

        return path, year, month, doy

    def setup_file_and_download(self, hdr, **kwargs):
        """
        Prepare the inputs, such as the correct name and paths before actually download it. The files, in this case,
        can only be DCB or Orbit

        :param hdr: Current rinex header. If there is at least one constellation without L1P column, the DCB is
        then downloaded. Otherwise, the L1P measures are already sufficient and the download is skipped
        :param year: String year [YYYY]
        :param month: String month [mm]
        :param day: String day [dd]
        :param file_type: The file type to be downloaded. It might be 'DCB' or 'Orbit'
        :return: Python object with a parsed file
        """
        obj = {}
        year = kwargs.get('year')
        month = kwargs.get('month')
        day = kwargs.get('day')
        file_type = kwargs.get('file_type')

        col_var = settings.COLUMNS_IN_RINEX[str(hdr['version'])]

        if file_type == "DCB":
            l1p_present = True

            for item in hdr['fields']:
                if item not in self.constelations:
                    continue

                if col_var[item]['P1'] not in hdr['fields'][item]:
                    l1p_present = False
                    break

            if l1p_present:
                logging.info(">>>> P1 present in all columns!")

            dcb = DownloadDCB(year, day, self.path_dcb)
            dcb.download()

            dcb_parsed = ParserDCB(dcb.file_uncompressed)
            dcb_parsed.parser()

            obj = dcb_parsed.parsed

        elif file_type == "Orbit":

            logging.info(">> Searching " + file_type + " file...")

            orbit = DownloadOrbit(year, month, day, self.path_orbit)
            orbit.download()

            orbit_parsed = ParserOrbit(orbit.file_uncompressed)
            orbit_parsed.parser()

            return orbit_parsed.parsed

        return obj
    
    def compensating_c1_c2(self, hdr, obs, dcb_m, columns, constellations):
        """
        Update the rinex C1 measures, converting it to P1 values, corresponding to P1 = C1 + DCB_P1-C1, and DCB in
        meters unit

        :param hdr: Current rinex header
        :param obs: The current rinex measures to be updated
        :param dcb_m: DCB values in meter unit
        :param columns: The string columns names, according to each existent constellation
        :param constellations: Which constellations was eligible to be used during the calculus
        :return: The updated current rinex with P1 values calculated through C1 and DCB
        """
        if not dcb_m:
            logging.info(">>>> DCB is empty. Skipping compensation!")
            return

        cols_var = settings.COLUMNS_IN_RINEX[str(hdr['version'])]

        for const in constellations:
            if cols_var[const]['P1'] not in columns:
                logging.info(">>>> Compensating {} for constellation {}...".format(cols_var[const]['C1'], const))
                for prn in obs.sv.values:
                    obs[cols_var[const]['C1']].sel(sv=prn).values -= (dcb_m['C1-P1'][prn][0] * -1)

            if cols_var[const]['P2'] not in columns:
                logging.info(">>>> Compensating {} for constellation {}...".format(cols_var[const]['C2'], const))
                for prn in obs.sv.values:
                    obs[cols_var[const]['C2']].sel(sv=prn).values -= dcb_m['C2-P2'][prn][0]

        return obs
    
    def validate_version(self, hdr, file):
        """
        Check if the current rinex version obey the required one

        :param hdr: Current header file
        :param file: String name file
        :return: If the current rinex version is smaller than required, the process will throw an exception
        """
        if hdr['version'] < float(self.min_requeried_version):
            logging.error(">>>>>> Version {} required. Current version {}. "
                          "Process stopped for rinex {}!".format(self.min_requeried_version, hdr['version'], file))
            raise Exception(">>>>>> Version {} required. Current version {}. "
                            "Process stopped for rinex {}!".format(self.min_requeried_version, hdr['version'], file))

    def frequency_by_constellation(self, prn, factor_glonass):
        """
        Check values and factors according to the GNSS constellation

        :param prn: The current PRN: e.g. 'G01'
        :param factor_glonass: Dict with all channels and' factors (by PRN) of GLONASS
        :return: Returns the respective frequencies F1, F2, F3, and factors 1, 2, and 3
        according to the GNSS constellation
        """
        f1 = 0
        f2 = 0
        f3 = 0
        factor_1 = 0.0
        factor_2 = 0.0
        factor_3 = 0.0
        if prn[0:1] == 'R':
            if prn[1:] in factor_glonass:
                f1 = factor_glonass[prn[1:]][0]
                f2 = factor_glonass[prn[1:]][1]
                f3 = factor_glonass[prn[1:]][2]
                factor_1 = factor_glonass[prn[1:]][3]
                factor_2 = factor_glonass[prn[1:]][4]
                factor_3 = factor_glonass[prn[1:]][5]
        elif prn[0:1] == 'G' or prn[0:1] == 'E' or prn[0:1] == 'C':
            f1 = settings.FREQUENCIES[prn[0:1]][0]
            f2 = settings.FREQUENCIES[prn[0:1]][1]
            f3 = settings.FREQUENCIES[prn[0:1]][2]
            factor_1 = (f1 - f2) / (f1 + f2) / settings.C
            factor_2 = (f1 * f2) / (f2 - f1) / settings.C
            factor_3 = pow(f1 * f2, 2) / (f1 + f2) / (f1 - f2) / settings.A / settings.TECU
        else:
            logging.warning('>>>> This constellation ({}), does not have frequencies and '
                            'factors defined. Default values will be assigned (all zeros)'.format(prn[0:1]))

        return f1, f2, f3, factor_1, factor_2, factor_3
    
    def which_data_to_load(self, hdr):
        """
        The rinex file is an extensive file, sometimes, with a lot of measures that are not interesting for this present
        work. Said that, in this method is selected only the columns used during the EMBRACE TEC and Bias estimation,
        such as L1, L2, P1, P2, C1 and C2. This method validate the availability of each of these columns regarding
        each desired constellation. If there is any missing columns, that constellation is remove from calculus

        :param hdr: Rinex header
        :return: The columns and constellations available to load in the rinex
        """
        aux_columns = []
        data_to_be_load = {}

        cols_desired_in_rinex = settings.COLUMNS_IN_RINEX[str(hdr['version'])]
        cols_available_in_rinex = hdr['fields']

        # TODO: ainda falha quando a versão é 2.11, na qual diz que todos as constelações desejadas
        #  (settings.CONSTELATIONS), estao presentes no rinex, o que nem sempre é verdadeiro. Ao final,
        #  "constellations" (variavel que guarda somente as constelacoes que possuem medidas) ainda mostrará
        #  constelações que na verdade não possuem medidas no corpo do arquivo
        for const in cols_desired_in_rinex:
            if const in self.constelations:
                for col in cols_desired_in_rinex[const]:

                    if hdr['version'] == 2.11:
                        if col not in cols_available_in_rinex:
                            continue

                        if cols_desired_in_rinex[const][col] not in cols_available_in_rinex:
                            continue
                    else:
                        if const not in cols_available_in_rinex.keys():
                            continue

                        if cols_desired_in_rinex[const][col] not in cols_available_in_rinex[const]:
                            continue

                    aux_columns.append(cols_desired_in_rinex[const][col])

                data_to_be_load[const] = aux_columns
                aux_columns = []

        data_to_be_load_copy = data_to_be_load.copy()
        
        for const in data_to_be_load_copy:
            if cols_desired_in_rinex[const]['L1'] not in data_to_be_load[const]:
                logging.info(">>>>>> Column {} is not available for constellation {}. "
                             "TEC wont be consider for this constellation!".format(cols_desired_in_rinex[const]['L1'],
                                                                                   const))
                del data_to_be_load[const]
                continue

            if cols_desired_in_rinex[const]['L2'] not in data_to_be_load[const] and \
                    cols_desired_in_rinex[const]['L3'] not in data_to_be_load[const]:
                logging.info(">>>>>> Column {} and {} are not available for constellation {}. "
                             "TEC wont be consider for this constellation!".format(cols_desired_in_rinex[const]['L2'],
                                                                                   cols_desired_in_rinex[const]['L3'],
                                                                                   const))
                del data_to_be_load[const]
                continue

            if cols_desired_in_rinex[const]['P1'] not in data_to_be_load[const] and \
                    cols_desired_in_rinex[const]['C1'] not in data_to_be_load[const]:
                logging.info(">>>>>> Column {} and {} are not available for constellation {}. "
                             "TEC wont be consider for this constellation!".format(cols_desired_in_rinex[const]['P1'],
                                                                                   cols_desired_in_rinex[const]['C1'],
                                                                                   const))
                del data_to_be_load[const]
                continue

            if cols_desired_in_rinex[const]['P2'] not in data_to_be_load[const] and \
                    cols_desired_in_rinex[const]['C2'] not in data_to_be_load[const]:
                logging.info(">>>>>> Column {} and {} are not available for constellation {}. "
                             "TEC wont be consider for this constellation!".format(cols_desired_in_rinex[const]['P2'],
                                                                                   cols_desired_in_rinex[const]['C2'],
                                                                                   const))
                del data_to_be_load[const]
                continue

            if cols_desired_in_rinex[const]['L2'] in data_to_be_load[const] and \
                    cols_desired_in_rinex[const]['L3'] in data_to_be_load[const]:
                data_to_be_load[const].remove('L3')

            # Based in some rinex, the column P1 is described in header rinex versions 2.11, but, in fact,
            # the measures of P1 does not exist in the body. So, if the version is 2.11, C1 is always used
            if hdr['version'] == 2.11 and cols_desired_in_rinex[const]['P1'] in data_to_be_load[const] and \
                    cols_desired_in_rinex[const]['C1'] not in data_to_be_load[const]:
                del data_to_be_load[const]

            if hdr['version'] == 2.11 and cols_desired_in_rinex[const]['P1'] in data_to_be_load[const] and \
                    cols_desired_in_rinex[const]['C1'] in data_to_be_load[const]:
                data_to_be_load[const].remove('P1')

        constellations = list(data_to_be_load.keys())
        flattened_columns = [y for x in list(data_to_be_load.values()) for y in x]

        l2_channel = True
        l1_col = {}
        l2_or_l3_col = {}
        p1_or_c1_col = {}
        p2_or_c2_col = {}
        for const in constellations:
            l1_col[const] = cols_desired_in_rinex[const]['L1']

            if cols_desired_in_rinex[const]['L2'] in flattened_columns:
                l2_or_l3_col[const] = cols_desired_in_rinex[const]['L2']
            else:
                l2_channel = False
                l2_or_l3_col[const] = cols_desired_in_rinex[const]['L3']

            if cols_desired_in_rinex[const]['P1'] in flattened_columns:
                p1_or_c1_col[const] = cols_desired_in_rinex[const]['P1']
            else:
                p1_or_c1_col[const] = cols_desired_in_rinex[const]['C1']

            if cols_desired_in_rinex[const]['P2'] in flattened_columns:
                p2_or_c2_col[const] = cols_desired_in_rinex[const]['P2']
            else:
                p2_or_c2_col[const] = cols_desired_in_rinex[const]['C2']

        return flattened_columns, constellations, l1_col, l2_or_l3_col, p1_or_c1_col, p2_or_c2_col, l2_channel

    def _prepare_rinex(self, complete_path):
        """
        Prepare the rinexs, such as checking if it is a valid file and if it has all the information need for the
        calculation

        :param complete_path: The absolute path to the rinex
        :return: The Python objects after to successful read the prev and rinex, it includes the header
        and measures of both files
        """
        if not os.path.isfile(complete_path):
            logging.error(">>>> Rinex {} does not exist. Process stopped!\n".format(complete_path))
            raise Exception(">>>> Rinex {} does not exist. Process stopped!\n".format(complete_path))

        logging.info(">> Validating file and measures...")
        hdr = gr.rinexheader(complete_path)
        logging.info(">>>> Rinex version {}!".format(hdr['version']))

        self.validate_version(hdr, complete_path)
        columns, constellations, l1_col, l2_or_l3_col, p1_or_c1_col, p2_or_c2_col, l2_channel = self.which_data_to_load(hdr)

        if not constellations:
            logging.info(">>>> This rinex ({}) does not have the measures required for the TEC and bias estimation.\n".
                         format(complete_path))
            raise Exception(">>>> This rinex ({}) does not have the measures required for the TEC and "
                            "bias estimation.\n".format(complete_path))
        else:
            logging.info(">> Reading rinex measures... Only constellation(s) {} will "
                         "be considered!".format(constellations))
            obs = gr.load(complete_path, meas=columns, use=constellations)

        return hdr, obs, columns, constellations, l1_col, l2_or_l3_col, p1_or_c1_col, p2_or_c2_col, l2_channel

    def _prepare_factor(self, hdr, year, day, month):
        """
        The factors is used as a weight during the first estimate (relative TEC). For the GLONASS constellation, the
        factors are selective, per PRN, then, this values can be download from the own rinex or a URL

        :param hdr: The current rinex header, which brings the information of GLONASS channels
        :param year: Year of the current rinex
        :param month: Month of the current rinex
        :param day: Day of the current rinex
        :return: The GLONASS factors, already multiply by the frequencies F1 and F2
            GLONASS factor Python object. Format example:
                    factor_glonass = {
                                '01': VALUE_1, VALUE_2, VALUE_3
                                '02': VALUE_1, VALUE_2, VALUE_3
                                '03': VALUE_1, VALUE_2, VALUE_3
                                '04': VALUE_1, VALUE_2, VALUE_3
                                '05': ...
                        }
        """
        logging.info(">> Downloading GLONASS channels in " + settings.URL_GLONASS_CHANNELS
                     + " for pseudorange calculation...")

        if "GLONASS SLOT / FRQ #" not in hdr:
            glonnas_channel = DownloadGlonassChannel(year, day, month, self.path_glonass_channel)
            glonnas_channel.download()

            glonass_channels_parser = ParserChannels(glonnas_channel.file_uncompressed)
            glonass_channels_parser.parser()
        else:
            glonass_channels_parser = ParserRinexChannels(hdr['GLONASS SLOT / FRQ #'])
            glonass_channels_parser.parser()

        return glonass_channels_parser.parsed

    def _prepare_orbit(self, hdr, year, month, day):
        """
        Construct the Orbit file and Python object. The file has to be downloaded from a remote repository. As soon it
        is guaranteed, the Python object can then be constructed.

        :param hdr: The current rinex header
        :param year: Year of the current rinex
        :param month: Month of the current rinex
        :param day: Day of the current rinex
        :return: The Python orbit object, with the right location of every satellite
                 Orbit Python object. Format example:
                    orbit = {
                        'G01': [{'date': VALUE, 'x': VALUE, 'y': VALUE, 'z': VALUE}, {...}}
                        'G02': [{'date': VALUE, 'x': VALUE, 'y': VALUE, 'z': VALUE}, {...}}
                        'G03': [{'date': VALUE, 'x': VALUE, 'y': VALUE, 'z': VALUE}, {...}}
                        ...
                        'R01': [{'date': VALUE, 'x': VALUE, 'y': VALUE, 'z': VALUE}, {...}}
                        'R02': [{'date': VALUE, 'x': VALUE, 'y': VALUE, 'z': VALUE}, {...}}
                        'R03': [{'date': VALUE, 'x': VALUE, 'y': VALUE, 'z': VALUE}, {...}}
                        ...
                    }
        """
        logging.info(">> Downloading Orbit files...")
        orbit = self.setup_file_and_download(hdr, year=year, month=month, day=day, file_type='Orbit')

        logging.info(">> Checking precision in time of both files, rinex and orbit...")
        if not math.isnan(hdr['interval']):
            rinex_interval = float(hdr['interval'])

        orbit_diff = orbit['date'][1] - orbit['date'][0]
        orbit_interval = orbit_diff.total_seconds()

        if rinex_interval < orbit_interval:
            logging.info(">>>> Orbit is less precise ({}) than rinex ({}) in seconds. Interpolation will be applied!".
                         format(orbit_interval, rinex_interval))

            orbit_aux = Utils.interpolate_orbit(orbit, hdr)
            orbit.update(orbit_aux)
        elif rinex_interval == orbit_interval:
            logging.info(">>>> Rinex and orbit with same time precision, {} and {} in seconds. "
                         "Interpolation is not required!".format(rinex_interval, orbit_interval))

        return orbit

    def _prepare_dcb(self, hdr, year, month, day):
        """
        Construct the DCB file and Python object. The file has to be downloaded from a remote repository. As soon it
        is guaranteed, the Python object can then be constructed. Finally, the DCB values are converted from nanosecs to
        TEC units

        :param hdr: The current rinex header
        :param year: Year of the current rinex
        :param month: Month of the current rinex
        :param day: Day of the current rinex
        :return: The Python DCB object, with the converted TEC units satellites errors
            DCB Python object. Format example:
                    dcb = {
                        'C1-P1':
                            {'G01': [BIAS_VALUE, STD_VALUE],
                            'G02': [BIAS_VALUE, STD_VALUE],
                            'G03': [BIAS_VALUE, STD_VALUE],
                            ...
                            'G32': [BIAS_VALUE, STD_VALUE],
                            'R01': [BIAS_VALUE, STD_VALUE],
                            'R02': [BIAS_VALUE, STD_VALUE],
                            ...
                            'R24': [BIAS_VALUE, STD_VALUE]}
                        'P1-P2':
                            {'G01': [BIAS_VALUE, STD_VALUE],
                            'G02': [BIAS_VALUE, STD_VALUE],
                            'G03': [BIAS_VALUE, STD_VALUE],
                            ...
                            'G32': [BIAS_VALUE, STD_VALUE],
                            'R01': [BIAS_VALUE, STD_VALUE],
                            'R02': [BIAS_VALUE, STD_VALUE],
                            ...
                            'R24': [BIAS_VALUE, STD_VALUE]}
                    }
        """
        logging.info(">> Downloading DCB files...")
        dcb = self.setup_file_and_download(hdr, year=year, month=month, day=day, file_type='DCB')

        return dcb

    def prepare_inputs(self, file):
        """
        Prepare the inputs needed to the TEC and bias receptor estimation. It includes the current and previous day rinex,
        the orbit file, the DCBs, and the GLONASS channels

        :param folder: Absolute path to the rinex file
        :param file_prev: The previous rinex according to the current day
        :param file: Name of the file in order to extract the corresponding year and month values: ssssdddd.yyo
        :return: The rinex header and measures objects, orbit object, dcb object, and factor_glonass object
        """
        path, year, month, doy = self.setup_rinex_name(self.rinex_folder, file)

        hdr, obs, columns, constellations, l1_col, l2_or_l3_col, \
        p1_or_c1_col, p2_or_c2_col, l2_channel = self._prepare_rinex(path)
        factor_glonass = self._prepare_factor(hdr, year, month, doy)
        orbit = self._prepare_orbit(hdr, year, month, doy)
        dcb = self._prepare_dcb(hdr, year, month, doy)

        logging.info(">> Converting DCB nanoseconds in meter unit...")
        dcb_m = Utils.convert_dcb_ns_to_meter(dcb)

        logging.info(">> Checking the availability of P1 and P2...")
        obs = self.compensating_c1_c2(hdr, obs, dcb_m, columns, constellations)

        return hdr, obs, orbit, dcb, factor_glonass, l1_col, l2_or_l3_col, p1_or_c1_col, \
               p2_or_c2_col, l2_channel, constellations


class Geodesy:
    """
    Complementary methods to calculate the right point of estimation, respect to receiver and satellites
    """

    def sub_ion_point(self, altitude, x_sat, y_sat, z_sat, x_rec, y_rec, z_rec):
        """
        Procedure to calculate the sub-ionospheric point through satellite and receiver positions

        :param altitude: Satellite altitude
        :param x_sat: X axis satellite position array
        :param y_sat: Y axis satellite position array
        :param z_sat: Z axis satellite position array
        :param x_rec: X axis receiver position value
        :param y_rec: Y axis receiver position value
        :param z_rec: Z axis receiver position value
        :return: Sub-ionospheric position array, corresponding to Lat, Long and Altitude, respectively
        """
        x_rec /= 1000
        y_rec /= 1000
        z_rec /= 1000

        x_sat = [x / 1000 for x in x_sat]
        y_sat = [y / 1000 for y in y_sat]
        z_sat = [z / 1000 for z in z_sat]

        x_sat = np.array(x_sat)
        y_sat = np.array(y_sat)
        z_sat = np.array(z_sat)
        diff_x = np.array([item - x_rec for item in x_sat])
        diff_y = np.array([item - y_rec for item in y_sat])
        diff_z = np.array([item - z_rec for item in z_sat])

        phi = (x_sat * y_rec) - (y_sat * x_rec)
        theta = (x_sat * z_rec) - (z_sat * x_rec)

        sqr_sum_1 = np.power(diff_y, 2) + np.power(diff_z, 2) + np.power(diff_x, 2)
        sqr_sum_2 = np.power(phi, 2) + np.power(theta, 2) - np.power(diff_x, 2) * np.power(altitude, 2)
        factor = np.power(diff_y * phi + diff_z * theta, 2) - sqr_sum_1 * sqr_sum_2

        factor = np.sqrt(factor)
        factor = np.nan_to_num(factor)

        dum = (-1 * (diff_y * phi + diff_z * theta) - factor) / sqr_sum_1

        term0 = (x_sat - dum) * (x_rec - dum)
        for i, item in enumerate(term0):
            if item > 0:
                dum[i] = (-1 * (diff_y[i] * phi[i] + diff_z[i] * theta[i]) + factor[i]) / sqr_sum_1[i]

        sub_ion_x = dum
        sub_ion_y = (diff_y * dum + phi) / diff_x
        sub_ion_z = (diff_z * dum + theta) / diff_x

        return sub_ion_x, sub_ion_y, sub_ion_z

    def calc_zenital_angle(self, array_x_sat, array_y_sat, array_z_sat, x_rec, y_rec, z_rec):
        """
        Procedure to calculate the zenital angle through satellite and receiver positions

        :param array_x_sat: X axis satellite position array
        :param array_y_sat: Y axis satellite position array
        :param array_z_sat: Z axis satellite position array
        :param x_rec: X axis receiver position value
        :param y_rec: Y axis receiver position value
        :param z_rec: Z axis receiver position value
        :return: The zenital angle based on the satellite and receiver positions
        """
        x_sat = np.array(array_x_sat)
        y_sat = np.array(array_y_sat)
        z_sat = np.array(array_z_sat)

        ang = ((x_sat - x_rec) * x_rec) + ((y_sat - y_rec) * y_rec) + ((z_sat - z_rec) * z_rec)
        aux1 = pow(x_sat - x_rec, 2) + pow(y_sat - y_rec, 2) + pow(z_sat - z_rec, 2)
        aux2 = pow(x_rec, 2) + pow(y_rec, 2) + pow(z_rec, 2)
        aux1_sqrt = np.sqrt(aux1)
        aux2_sqrt = np.sqrt(aux2)

        result_ang_zen = ang / aux1_sqrt / aux2_sqrt
        ang_zen = np.arccos(result_ang_zen)
        ang_zen *= 180 / math.pi

        return ang_zen

    def car_2_pol(self, array_x, array_y, array_z):
        """
        Convert the normal cartesian projection in polar projection

        :param array_x: Subionospheric coordinate in x
        :param array_y: Subionospheric coordinate in y
        :param array_z: Subionospheric coordinate in z
        :return: The converted triplice coordination array
        """
        array_x_pol = [0.0] * len(array_x)
        array_y_pol = [0.0] * len(array_y)
        array_z_pol = [0.0] * len(array_z)

        euclidian_distance = np.sqrt(np.power(array_x, 2) + np.power(array_y, 2))
        e = (2 - (1 / settings.ELLIPTICITY)) / settings.ELLIPTICITY

        for k, item in enumerate(euclidian_distance):
            if item != 0:
                array_x_pol[k] = np.arctan(array_z[k] / item)

                n = settings.RADIUS_EQUATOR / np.sqrt(1 - e * np.power(np.sin(array_x_pol[k]), 2))
                array_x_pol[k] = np.arctan(array_z[k] / (item - (e * n * np.cos(array_x_pol[k]))))

                if array_x[k] != 0:
                    array_y_pol[k] = np.arctan(array_y[k] / array_x[k])
                    if array_x[k] < 0:
                        array_y_pol[k] += math.pi
                else:
                    array_y_pol[k] = array_y[k] / abs(array_y[k]) * (math.pi / 2)

                array_z_pol[k] = item / np.cos(array_x_pol[k]) - n

            else:
                logging.info(">>>>>> Square root equal zero!")

        array_x_pol = [(180 / math.pi) * x for x in array_x_pol]
        array_y_pol = [(180 / math.pi) * y for y in array_y_pol]

        for k, item in enumerate(array_y_pol):
            if item > 180.0:
                aux = item - 180
                aux = -1 * (180 - aux)
            elif item < -180.0:
                aux = item + 180
                aux = 180 + aux
            else:
                aux = item

            array_y_pol[k] = aux

        return array_x_pol, array_y_pol, array_z_pol
