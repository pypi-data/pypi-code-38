import logging
import numpy as np
import math
import pyproj
import datetime

from scipy.signal import savgol_filter

import tec_embrace.settings as settings
import tec_embrace.helper as helper


class TECEstimation:
    """
    Comprises the full workflow to calculate/estimate local TEC. The workflow consists in TEC relative, absolute,
    and vertical estimation, besides the slant factor, which gives the ionopheric point where the TEC has been estimated
    """
    tec_resolution = ""
    tec_resolution_value = ""

    def __init__(self, tec_resolution=None, tec_resolution_value=None):
        self.tec_resolution = tec_resolution
        self.tec_resolution_value = tec_resolution_value

    def relative(self, tec, obs, factor_glonass, dcb, p1_or_c1_col, p2_or_c2_col):
        """
        Calculate the pseudo-range or pseudo-distance, which is the first TEC calculation, called relative TEC or simply
        R TEC. The R TEC includes, then, not only the TEC, but also all the extra influences, such as atmosphere
        attenuations, and eletronic errors

        :param tec: Dict with TEC python object
        :param obs: The measures of the current rinex
        :param factor_glonass: The channels values of each GLONASS PRNs to calc the selective factor
        :param dcb: The parsed DCB object, with the satellites bias, in order to
        subtract from relative TEC (in nanosecs)
        :param p1_or_c1_col: Either the P1 or C1 measures might be used. Here, a string defined the name of the column
        of the measure used
        :param p2_or_c2_col: Either the P2 or C2 measures might be used. Here, a string defined the name of the column
        of the measure used
        :return: The python relative TEC object, which will content all the TEC calculations along the process
        """
        tec_r = {}
        utils = helper.Utils()

        # logging.info(">>>> Converting DCB nanoseconds in TEC unit...")
        # dcb_tecu = helper.Utils.convert_dcb_ns_to_tecu(dcb, factor_glonass)

        # logging.info(">> Correcting DCB values...")
        # dcb_corrected = helper.Utils.correct_dcb_values(dcb, factor_glonass)

        logging.info(">>>> Calculating relative TEC and removing satellite DCB...")
        for prn in obs.sv.values:
            p2_or_c2 = obs[p2_or_c2_col[prn[0:1]]].sel(sv=prn).values
            p1_or_c1 = obs[p1_or_c1_col[prn[0:1]]].sel(sv=prn).values

            factor, dcb_compensate = utils.check_availability(factor_glonass, dcb, prn)

            relative = utils.check_arc_gaps(tec, factor, p2_or_c2, p1_or_c1, prn)

            tec_r[prn] = (relative - dcb_compensate).tolist()

            # utils.plot_relative(prn, tec['relative-l1-l2'][prn][0], tec_r[prn])

        return tec_r

    def slant(self, hdr, obs, orbit, type):
        """
        Consists in a more accurate acquirement of each satellite's slant in the ionospheric point regarding a specific
        receiver.

        :param hdr: The header the current rinex
        :param obs: The measures of the current rinex
        :param orbit: The python orbit object, with the daily and updated satellite locations
        :param type: Type of parameters to be calculated (For DTEC (0) or bias estimation (1))
        :return: The updated TEC object, now, with slant factor calculated. The tec['slant'] dict:
            tec['slant'] = {
                    'G01' = [
                              [SLANT_FACTOR_OVER_THE_DAY], [ZENITAL_ANGLE_OVER_THE_DAY],
                              [ELEVATION_OVER_THE_DAY], [LATITUDE_PP_OVER_THE_DAY], [LONG_PP_OVER_THE_DAY]
                            ],
                    'G02' = [
                              [SLANT_FACTOR_OVER_THE_DAY], [ZENITAL_ANGLE_OVER_THE_DAY],
                              [ELEVATION_OVER_THE_DAY], [LATITUDE_PP_OVER_THE_DAY], [LONG_PP_OVER_THE_DAY]
                            ],
                    ...
            }
        """
        tec_s = {}
        utils = helper.Utils()
        geodesy = helper.Geodesy()

        rec_x = hdr['position'][0]
        rec_y = hdr['position'][1]
        rec_z = hdr['position'][2]

        ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
        lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
        lon, lat, alt = pyproj.transform(ecef, lla, rec_x, rec_y, rec_z, radians=False)

        degrad = float(math.pi / 180.0)
        dpi = float('{:.16f}'.format(math.pi))

        lon = (lon + 360) * degrad
        lat *= degrad

        sin_rec_x = math.sin(lon)
        sin_rec_y = math.sin(lat)
        cos_rec_x = math.cos(lon)
        cos_rec_y = math.cos(lat)

        for prn in obs.sv.values:
            if prn not in orbit.keys():
                continue

            sat_x = utils.array_dict_to_array(orbit[prn], 'x')
            sat_x = [x * 1000 for x in sat_x]

            sat_y = utils.array_dict_to_array(orbit[prn], 'y')
            sat_y = [y * 1000 for y in sat_y]

            sat_z = utils.array_dict_to_array(orbit[prn], 'z')
            sat_z = [z * 1000 for z in sat_z]

            if type is 0:
                diff_x = np.array([item - rec_x for item in sat_x])
                diff_y = np.array([item - rec_y for item in sat_y])
                diff_z = np.array([item - rec_z for item in sat_z])

                term1 = -cos_rec_x * sin_rec_y * diff_x
                term2 = sin_rec_x * sin_rec_y * diff_y
                term3 = cos_rec_y * diff_z
                term4 = -sin_rec_x * diff_x
                term5 = cos_rec_x * diff_y
                term6 = cos_rec_x * cos_rec_y * diff_x
                term7 = sin_rec_x * cos_rec_y * diff_y
                term8 = sin_rec_y * diff_z

                north = term1 - term2 + term3
                east = term4 + term5
                vertical = term6 + term7 + term8
                vertical_norm = np.sqrt(np.power(cos_rec_x * cos_rec_y, 2) +
                                        np.power(sin_rec_x * cos_rec_y, 2) +
                                        np.power(sin_rec_y, 2))

                r = np.sqrt(np.power(diff_x, 2) + np.power(diff_y, 2) + np.power(diff_z, 2))

                ang_zenital = np.arccos(vertical / (r * vertical_norm))
                ang_elev = ((dpi / 2) - ang_zenital) / degrad
                slant_factor = np.arcsin((settings.EARTH_RAY / (settings.EARTH_RAY + settings.AVERAGE_HEIGHT)) *
                                              np.cos(ang_elev * degrad))
                slant_factor = np.cos(slant_factor)

                azimute = np.arctan2(east, north)
                azimute[azimute < 0] += (2 * math.pi)
                azimute = azimute / degrad

                var1 = ang_elev * degrad
                w = (dpi / 2) - var1 - np.arcsin(
                    settings.EARTH_RAY / (settings.EARTH_RAY + settings.AVERAGE_HEIGHT) * np.cos(var1))

                var2 = sin_rec_y * np.cos(w)
                var3 = cos_rec_y * np.sin(w) * np.cos(azimute * degrad)
                lat_pp = np.arcsin(var2 + var3)

                var4 = np.sin(w) * np.sin(azimute * degrad)
                long_pp = lon + np.arcsin(var4 / np.cos(lat_pp))

                lat_pp = lat_pp / degrad
                long_pp = long_pp / degrad

                lat_pp = lat_pp.tolist()
                long_pp = long_pp.tolist()

            elif type is 1:
                ion_x, ion_y, ion_z = geodesy.sub_ion_point(settings.ALT_IONO, sat_x, sat_y, sat_z, rec_x, rec_y, rec_z)
                top_ion_x, top_ion_y, top_ion_z = geodesy.sub_ion_point(settings.ALT_IONO_TOP, sat_x, sat_y, sat_z,
                                                                        rec_x, rec_y, rec_z)
                bot_ion_x, bot_ion_y, bot_ion_z = geodesy.sub_ion_point(settings.ALT_IONO_BOTTOM, sat_x, sat_y, sat_z,
                                                                        rec_x, rec_y, rec_z)

                lat_pp, long_pp, alt_pp = geodesy.car_2_pol(ion_x, ion_y, ion_z)

                ang_zenital = geodesy.calc_zenital_angle(sat_x, sat_y, sat_z, rec_x, rec_y, rec_z)

                ang_elev = ((dpi / 2) - ang_zenital) / degrad

                slant_factor = pow(np.array(top_ion_x) - np.array(bot_ion_x), 2) + \
                                    pow(np.array(top_ion_y) - np.array(bot_ion_y), 2) + \
                                    pow(np.array(top_ion_z) - np.array(bot_ion_z), 2)
                slant_factor = np.sqrt(slant_factor) / (settings.ALT_IONO_TOP - settings.ALT_IONO_BOTTOM)
            else:
                logging.error(">>>> Type of slant factor calculation is incorrect. The procedure will be "
                              "interrupted for this file!")
                raise Exception(">>>> Type of slant factor calculation is incorrect. The procedure will be "
                                "interrupted for this file!")

            slant_factor = slant_factor.tolist()
            ang_zenital = ang_zenital.tolist()
            ang_elev = ang_elev.tolist()

            # utils.plot_slant(prn, slant_factor, ang_zenital, ang_elev, lat_pp, long_pp)

            tec_s[prn] = [slant_factor, ang_zenital, ang_elev, lat_pp, long_pp]

        return tec_s

    def detrended(self, tec, factor_glonass, l2_channel):
        """
        Calculate the Detrended TEC

        :param tec: Dict with TEC python object
        :param factor_glonass: The channels values of each GLONASS PRNs to calc the selective factor
        :param l2_channel: A True value means that L2 was present at the file, then, used for the calculus. By using
        this measure, the frequency 2 should be used. If False, the frequency 3 is used.
        :return: The updated TEC object, now, with detrended TEC calculated
        """
        tec_d = {}
        input = helper.InputFiles()

        for prn in tec['relative-l1-l2']:
            l1 = np.array(tec['relative-l1-l2'][prn][1])
            l2_or_l3 = np.array(tec['relative-l1-l2'][prn][2])

            f1, f2, f3, factor_1, factor_2, factor_3 = input.frequency_by_constellation(prn, factor_glonass)

            if l2_channel:
                term1 = ((l1 / f1) - (l2_or_l3 / f2)) * settings.C
            else:
                term1 = ((l1 / f1) - (l2_or_l3 / f3)) * settings.C

            sTEC_diff = factor_3 * term1
            savgol = savgol_filter(sTEC_diff, 121, 2, mode='nearest')

            tec_d[prn] = (sTEC_diff - savgol).tolist()

            # utils = helper.Utils()
            # utils.plot_dtrended(prn, l1, l2_or_l3, sTEC_diff, savgol, tec_d[prn])

        return tec_d

    def absolute(self, tec, constellations):
        """
        The absolute TEC consists in the TEC without the contribution of bias. In this method, the Python TEC object
        is updated with the subtraction of bias.

        :param tec: Dict with TEC python object
        :param constellations: Which constellations was eligible to be used during the calculus
        :return: The updated TEC object, now, with absolute TEC calculated
        """
        tec_a = {}
        b = tec['bias']['B']
        bias_receiver = b[len(b)-len(constellations):len(b)]

        if len(bias_receiver) != len(constellations):
            logging.warning(">>>> Number of bias estimated ({}) is different of constellations considered ({})!".
                            format(len(bias_receiver), len(constellations)))

        for c, const in enumerate(constellations):
            for prn, values in tec['relative'].items():
                if prn[0:1] is not const:
                    continue

                absolute = np.array(tec['relative'][prn]) - bias_receiver[c]
                tec_a[prn] = absolute.tolist()

        return tec_a

    def vertical(self, tec, orbit):
        """
        When calculated, the TEC is function of satellites incident angles, sometimes, in the horizon. The vertical
        TEC is the process to remove this influence, bringing the TEC perpendicular to the receiver, called vertical
        TEC -> Vertical = Absolute / Slant. At the first part of this method, the slant variable is reduce to the
        range of the rinex, in a way that both cover the same range of datetime over the day. The vertical TEC is then
        calculated.

        :param tec: Dict with TEC python object
        :param orbit: The Orbit dict, with all the informations of satellites, including x, y, z locations, and time
        :return: The updated TEC object, now, with vertical TEC calculated
        """
        tec_v = {}

        for prn, values in tec['absolute'].items():
            if prn not in tec['slant'].keys():
                continue

            absolute_np = np.array(tec['absolute'][prn])
            slant_np = np.array(tec['slant'][prn][0])

            if absolute_np.shape[0] != slant_np.shape[0]:
                slant_np_aux = []

                for i, item in enumerate(orbit['date']):
                    if item in tec['time']:
                        slant_np_aux.append(slant_np[i])

                slant_np = np.array(slant_np_aux)

            tec_v[prn] = (absolute_np / slant_np).tolist()

            # utils = helper.Utils()
            # utils.plot_absolute_vertical(prn, tec['absolute'][prn], tec_v[prn])

        return tec_v


class BiasEstimation:
    """
    Comprises the methods responsible to the estimate of bias receiver. This includes all the process of discovering
    the unknown variables by the use of MMQ (Least-Square)
    """
    tec_resolution = ""
    tec_resolution_value = ""

    def __init__(self, tec_resolution=None, tec_resolution_value=None):
        self.tec_resolution = tec_resolution
        self.tec_resolution_value = tec_resolution_value

    def _split_datetime_array(self, array_datetime):
        """
        Split a datetime array in fractions of time, where each fractions corresponds a pre-determined period (delta).
        Thus, considering an array of 24h datetime, and a delta of 15 minutes, the return will be fractions of date
        indexes corresponding to every 15 minutes until the end of the day

        :param array_datetime: Array of datetimes
        :return: Fractions of date indexes corresponding to every delta in the day. The delta is set up by the
        TEC_RESOLUTION constant variable
        """
        indexes_fraction = []
        indexes_fraction_aux = []

        if self.tec_resolution == 'hours':
            delta = datetime.timedelta(hours=int(self.tec_resolution_value))
        elif self.tec_resolution == 'minutes':
            delta = datetime.timedelta(minutes=int(self.tec_resolution_value))
        else:
            delta = datetime.timedelta(hours=1)
            logging.info(">>>> TEC resolution estimation not declare. Hourly TEC was defined as default! Please, "
                         "check your .env and look for TEC_RESOLUTION and TEC_RESOLUTION_VALUE to set correctly!")

        fraction_limit = array_datetime[0] + delta

        for i, item in enumerate(array_datetime):
            if item < fraction_limit:
                indexes_fraction_aux.append(i)
            else:
                fraction_limit = item + delta
                indexes_fraction.append(indexes_fraction_aux)

                indexes_fraction_aux = []
                indexes_fraction_aux.append(i)

        indexes_fraction.append(indexes_fraction_aux)

        return indexes_fraction

    def _build_coefficients(self, tec, constellations):
        """
        Build the coefficients of the equation system. These terms are defined through a Least-Square Fitting method,
        which consist in the minimization of set of unknown variable, dispose in a set of equations, so called,
        equation system (see Otsuka et al. A new Technique for mapping of TEC using GPS network in Japan).
        The coefficients, are values organized by hours, each hour will receive a mean value of a specific PRN.
        For instance, for hour '0h' of group_1, will receive an array with TOTAL_OF_SATELLITES positions, each
        position corresponds to a mean value of 1 / tec slant, for group_2, the each position corresponds to a mean
        value of relative / tec slant

        :param tec: The TEC object, with relative and slant factor, calculated by PRN
        :param constellations: Which constellations was eligible to be used during the calculus
        :return: The group 1 and 2 of coefficients, which is hourly mean of 1 / slant_factor, and
        hourly mean of tec_relative / slant_factor, respectively
            For example:
                coefficients = {
                            'group_1':
                                        {
                                        'every_00.00.10_frac_0': [G01_mean, G02_mean, ..., N_sat_mean],
                                        'every_00.00.10_frac_1': [G01_mean, G02_mean, ..., N_sat_mean],
                                        'every_00.00.10_frac_2': [G01_mean, G02_mean, ..., N_sat_mean],
                                        ...
                                        'every_00.00.10_frac_INTERVAL_A_DAY': [G01_mean, G02_mean, ..., N_sat_mean],
                                        },
                            'group_2':
                                        {
                                        'every_00.00.10_frac_0': [G01_mean, G02_mean, ..., N_sat_mean],
                                        'every_00.00.10_frac_1': [G01_mean, G02_mean, ..., N_sat_mean],
                                        'every_00.00.10_frac_2': [G01_mean, G02_mean, ..., N_sat_mean],
                                        ...
                                        'every_00.00.10_frac_INTERVAL_A_DAY': [G01_mean, G02_mean, ..., N_sat_mean],
                                        }
                                }
        """
        coefficients = {}
        group_1 = {}
        group_2 = {}
        res = str(self.tec_resolution_value) + '_' + str(self.tec_resolution)

        indexes = self._split_datetime_array(tec['time'])

        for i, ind in enumerate(indexes):
            group_1_aux_dict = {}
            group_2_aux_dict = {}

            for const in constellations:
                group_1_aux = []
                group_2_aux = []

                for prn in tec['slant']:
                    if prn[0:1] is not const:
                        continue

                    # TODO: avaliar a construção da matriz. Apesar de estar construindo corretamente,
                    #  o valor de bais ainda difere da versão Java
                    #  arquivo exemplo: ango2220.14o - bias G: 40 (Goppe-Semalla (?))
                    #                   ango2220.14o - bias G: -17 (versão atual do TEC/EMBRACE)
                    #                   ango2220.14o - bias G: -42 (versão Java: SpaceWeatherTEC-GUI)
                    elements_slant = np.take(tec['slant'][prn][0], ind)
                    elements_relat = np.take(tec['relative'][prn], ind)

                    elements_slant[np.isnan(elements_slant)] = 0.0
                    elements_relat[np.isnan(elements_relat)] = 0.0

                    elements_slant_pos = np.where(~(elements_slant <= settings.SLANT_FACTOR_LIMIT))[0]
                    elements_slant = elements_slant[elements_slant <= settings.SLANT_FACTOR_LIMIT]
                    elements_relat = np.delete(elements_relat, elements_slant_pos)

                    if len(elements_slant) == 0:
                        avg_rel = 0.0
                        avg_sla = 0.0
                    else:
                        _1_slant = np.divide(1, elements_slant)
                        _relative_slant = np.divide(elements_relat, elements_slant)

                        avg_sla = np.mean(_1_slant, dtype=np.float32)
                        avg_rel = np.mean(_relative_slant, dtype=np.float32)

                    group_1_aux.append(avg_sla)
                    group_2_aux.append(avg_rel)

                group_1_aux_dict[const] = group_1_aux
                group_2_aux_dict[const] = group_2_aux

            group_1["every_" + res + "_frac_" + str(i)] = group_1_aux_dict
            group_2["every_" + res + "_frac_" + str(i)] = group_2_aux_dict

        coefficients['group_1'] = group_1
        coefficients['group_2'] = group_2

        return coefficients

    def _build_matrix_f(self, group1_coefficients):
        """
        Build part of the A matrix, which it is splited in matrix E and F. Matrix B is built on top of
        coefficients 1/slant_factor

        :param group1_coefficients:
        :return: Numpy matrix F
        """
        keys = list(group1_coefficients.keys())
        intervals_a_day = len(list(group1_coefficients.keys()))
        flattened_values = [y for x in list(group1_coefficients[keys[0]].values()) for y in x]
        total_n_prns = len(flattened_values)
        number_valid_constellations = len(group1_coefficients[keys[0]])
        rows = total_n_prns * intervals_a_day

        f = np.zeros([rows, number_valid_constellations], dtype=float)

        pivot = 0
        for element in group1_coefficients:
            for c, const in enumerate(group1_coefficients[element]):
                n_prns = len(group1_coefficients[element][const])
                f[pivot:pivot + n_prns, c] = group1_coefficients[element][const]
                pivot += n_prns

        return f

    def _build_matrix_e(self, group1_coefficients):
        """
        Build part of the A matrix, which it is splited in matrix E and F. Matrix E is simply a matrix with 1's, based
        on the number of PRNs observed

        :param group1_coefficients:
        :return: A numpy E matrix
        """
        keys = list(group1_coefficients.keys())
        intervals_a_day = len(list(group1_coefficients.keys()))
        flattened_values = [y for x in list(group1_coefficients[keys[0]].values()) for y in x]
        total_n_prns = len(flattened_values)

        e = np.zeros([total_n_prns * intervals_a_day, intervals_a_day], dtype=float)

        for f, frac in enumerate(group1_coefficients):
            initial_row = f * total_n_prns
            final_row = initial_row + total_n_prns
            e[initial_row:final_row, f] = 1

        return e

    def _build_matrix_a(self, group1_coefficients):
        """
        Build the A matrix, which is an union between matrix E and B

        :param group1_coefficients:
        :return: A numpy A matrix
        """
        e = self._build_matrix_e(group1_coefficients)
        f = self._build_matrix_f(group1_coefficients)

        #TODO: check if f matrix is all zero. If so, the matrix will be singular, so interrupt the process for the
        # current file

        a = np.concatenate((e, f), 1)

        return a

    def _build_matrix_p(self, group1_coefficients):
        """
        Build the P matrix, which is a eye matrix built on top of coefficients 1 / slant_factor, also
            based on the number of PRNs observed

        :param group1_coefficients:
        :return: A numpy P matrix
        """
        keys = list(group1_coefficients.keys())
        intervals_a_day = len(list(group1_coefficients.keys()))
        flattened_values = [y for x in list(group1_coefficients[keys[0]].values()) for y in x]
        total_n_prns = len(flattened_values)
        rows = total_n_prns * intervals_a_day

        pivot = 0
        p = np.zeros([rows, rows], dtype=float)
        for element in group1_coefficients:
            for c, const in enumerate(group1_coefficients[element]):
                n_prns = len(group1_coefficients[element][const])
                np.fill_diagonal(p[pivot:pivot + rows, pivot:pivot + rows], group1_coefficients[element][const])
                pivot += n_prns

        return p

    def _build_matrix_l(self, group2_coefficients):
        """
        Build the L matrix, which is a column matrix built on top of coefficients tec_relative / slant_factor, also
        based on the number of PRNs observed

        :param group2_coefficients:
        :return: A numpy L matrix
        """
        keys = list(group2_coefficients.keys())
        intervals_a_day = len(list(group2_coefficients.keys()))
        flattened_values = [y for x in list(group2_coefficients[keys[0]].values()) for y in x]
        total_n_prns = len(flattened_values)
        rows = total_n_prns * intervals_a_day

        pivot = 0
        l = np.zeros([rows, 1], dtype=float)
        for element in group2_coefficients:
            for c, const in enumerate(group2_coefficients[element]):
                n_prns = len(group2_coefficients[element][const])
                l[pivot:pivot + n_prns, 0] = group2_coefficients[element][const]
                pivot += n_prns

        return l

    def estimate_bias(self, tec, constellations):
        """
        The bias estimate comprises the resolution of a equation system, which can be represented by a set of matrixes.
        The unknowns are built over averages values over the day, as shown in Otsuka et al. 2002. The solution, however,
        is given by the resolution of an equation system, given by the matrixes A, P, and L, where the estimated TEC
        and receiver bias (B) is given by inv(A^T P A) * (A^T P L)

        :param tec: The measures of the current rinex
        :param constellations: Which constellations was eligible to be used during the calculus
        :return: The settings.INTERVAL_A_DAY elements corresponding to averages TEC over the day, more one last value,
        corresponding to the receptor/receiver bias
        """
        matrixes = {}
        bias = {}

        logging.info(">> Preparing coefficients...")
        coefficients = self._build_coefficients(tec, constellations)

        logging.info(">> Split intervals in each {} {}...".format(self.tec_resolution_value,
                                                                  self.tec_resolution))
        intervals_a_day = len(list(coefficients['group_1'].keys()))

        logging.info(">> Building matrix A...")
        a = self._build_matrix_a(coefficients['group_1'])
        at = np.transpose(a)

        logging.info(">> Building matrix P...")
        p = self._build_matrix_p(coefficients['group_1'])

        logging.info(">> Building matrix L...")
        l = self._build_matrix_l(coefficients['group_2'])
        l[np.isnan(l)] = 0

        np.savetxt("/home/lotte/Desktop/a.csv", a, delimiter=";")
        np.savetxt("/home/lotte/Desktop/p.csv", p, delimiter=";")
        np.savetxt("/home/lotte/Desktop/l.csv", l, delimiter=";")

        if a.shape[0] != p.shape[0]:
            logging.error(">>>> Matrix A dimension ({}) in row, does not match with P ({}). There is "
                          "something wrong! Process stopped!\n".format(a.shape, p.shape))
            raise Exception(">>>> Matrix A dimension ({}) in row, does not match with P ({}). There is "
                            "something wrong! Process stopped!\n".format(a.shape, p.shape))

        if p.shape[0] != l.shape[0]:
            logging.error(">>>> Matrix P dimension ({}) in row, does not match with L ({}) in row. There is "
                          "something wrong! Process stopped!\n".format(p.shape, l.shape))
            raise Exception(">>>> Matrix P dimension ({}) in row, does not match with L ({}) in row. There is "
                            "something wrong! Process stopped!\n".format(p.shape, l.shape))

        logging.info(">>>> Matrix A ({}), P ({}), and L ({}) successful built!".format(a.shape, p.shape, l.shape))
        logging.info(">> Estimating daily TEC and receiver bias...")

        term1 = np.dot(at, p)
        term2 = np.dot(term1, a)
        inv_atpa = np.linalg.inv(term2)

        atpl = np.dot(term1, l)
        b = np.dot(inv_atpa, atpl)

        if b.shape[0] != (intervals_a_day + len(constellations)):
            logging.error(">>>> Matrix B dimension, does not match with the number of TEC by day ({}) and "
                          "receiver bias estimation ({}). There is something wrong! "
                          "Process stopped!\n".format(b.shape, intervals_a_day, len(constellations)))
            raise Exception(">>>> Matrix B dimension, does not match with the number of TEC by day ({}) and "
                            "receiver bias estimation ({}). There is something wrong! "
                            "Process stopped!\n".format(b.shape, intervals_a_day, len(constellations)))
        else:
            logging.info(">>>> Matrix B successful calculated! TEC estimation every {} {} a day ({} fractions), plus,"
                         " {} receiver bias:".format(self.tec_resolution_value,
                                                     self.tec_resolution,
                                                     intervals_a_day, len(constellations)))
            for i, item in enumerate(b[len(b)-len(constellations):len(b)]):
                logging.info(">>>>>> {}: {}".format(constellations[i], item[0]))

        matrixes['A'] = a.tolist()
        matrixes['P'] = p.tolist()
        matrixes['L'] = l.tolist()
        matrixes['invATPA'] = inv_atpa.tolist()
        matrixes['ATPL'] = atpl.tolist()

        b = [y for x in b.tolist() for y in x]
        bias['B'] = b

        return matrixes, bias


class QualityControl:
    """
    Comprises the methods responsible to analyse the quality of the measures used to estimate the TEC and bias.
    """

    def _var(self, a, p, l, b, atpl):
        """
        Calculate the variance a posteriori for each estimated value, based on the bias matrixes used before

        :param a: Numpy A matrix: coefficients (group 1) mounted in a custom matrix
        :param p: Numpy P matrix: coefficients (group 1) mounted in a squared matrix
        :param l: Numpy L matrix: coefficients (group 2) mounted in a matrix column
        :param b: Numpy B matrix (bias)
        :param atpl: Numpy matrix - inverse of (A^T * P * L)
        :return: Numpy matrix with the calculated variance metric for each estimated value
        """
        lt = np.transpose(l)
        bt = np.transpose(b)

        mat1 = lt.dot(p).dot(l)
        mat2 = bt.dot(atpl)
        mat3 = mat1 - mat2

        a_rows = np.size(a, 0)
        b_rows = np.size(b, 0)

        degree_of_freedom = a_rows - b_rows
        var = mat3 / degree_of_freedom

        return var

    def _accuracy(self, inv_atpa):
        """
        Calculate the accuracy for each estimated value, based on the bias matrixes used before

        :param inv_atpa: inverse of (A^T * P * A)
        :return: Numpy matrix with the calculated accuracy metric for each estimated value
        """
        accuracy = np.sqrt(np.diag(inv_atpa))

        return accuracy

    def _quality(self, inv_atpa, var):
        """
        Calculate the quality for each estimated value, based on the inverse of (A^T * P * A) matrix

        :param inv_atpa: Numpy matrix - inverse of (A^T * P * A)
        :param var: Variance a posteriori
        :return: Numpy matrix with the calculated quality metric for each estimated value
        """
        quality = np.sqrt(np.diag(inv_atpa * var))

        return quality

    def _residuals(self, a, l, b):
        """
        Calculate the residuals for each estimated value

        :param a: Numpy A matrix
        :param l: Numpy L matrix
        :param b: Numpy B matrix
        :return: Numpy matrix with the calculated residuals for each estimated value
        """
        residuals = a.dot(b) - l

        return residuals

    def check_quality(self, obs, tec, constellations, folder, file):
        """
        From the quality metrics of each estimate value, check if the bias estimation is needed or not

        :param tec: Dict with the measures of the current rinex
        :param constellations: Which constellations was eligible to be used during the calculus
        :param folder: Absolute path to the rinex's folder
        :param file: Rinex filename
        :return: Returns the array of tec and bias, estimated after to consider possible noisy in rinex measures
        """
        restimated_bias = {}

        utils = helper.Utils()
        input_files = helper.InputFiles()
        bias_estimation = BiasEstimation()

        # 1o controle de qualidade a se aplicar ---------------------------
        if tec['quality']['var'] > settings.THRESHOLD_VARIANCE_BIAS:
            logging.info(">> Variance above limit (Limit: {}; Variance a posteriori = {}). The measures may "
                         "not be good. Using only part of the day: {}h until {}h...".
                         format(settings.THRESHOLD_VARIANCE_BIAS,
                                tec['quality']['var'],
                                settings.INITIAL_HOUR_RECALC_BIAS,
                                settings.FINAL_HOUR_RECALC_BIAS))

            path, year, month, doy = input_files.setup_rinex_name(folder, file)
            initial_date = datetime.datetime(int(year), 1, 1, settings.INITIAL_HOUR_RECALC_BIAS, 0) + \
                           datetime.timedelta(int(doy) - 1)
            final_date = datetime.datetime(int(year), 1, 1, settings.FINAL_HOUR_RECALC_BIAS, 0) + \
                         datetime.timedelta(int(doy) - 1)

            i = (obs.time >= initial_date) & (obs.time < final_date)
            obs_short = obs.isel(i)

            if obs_short is None:
                logging.info(">>>>>>>> No measures were made during this period of the day! Bias reestimation skipped!")
            else:
                tec['time'] = utils.restrict_datearray(tec['time'], initial_date, final_date)
                restimated_bias = bias_estimation.estimate_bias(tec, constellations)
        else:
            restimated_bias = tec['bias']

        # 2o controle de qualidade a se aplicar ---------------------------
        std_residuals = np.std(tec['quality']['residuals'])
        indexes_of_high_residuals = np.argwhere(np.std(tec['quality']['residuals']) >= (std_residuals * 2))
        if len(indexes_of_high_residuals) > 0:
            # TODO: Incluir 2o controle de qualidade neste ponto, que consiste na remoção dos resíduos
            logging.info(">> {} residuals found. Recalculation bias...".format(len(indexes_of_high_residuals)))
        else:
            restimated_bias = tec['bias']

        return restimated_bias

    def quality_control(self, matrixes, bias):
        """
        The quality control corresponds to the process of extracting metrics of quality, such as residuals, variance,
        and standard deviation. Through these metrics, it is possible to check if the estimates were made under a noisy
        scenario or not (ionosphere disturbed days over the year).

        :param matrixes: The resolution TEC problem matrixes
        :param bias: Object with the receptor estimate bias
        :return: The updated TEC object, now, with the quality of rinex measures, TEC, and bias estimation
        """
        quality_meas = {}

        A = np.array(matrixes['A'])
        L = np.array(matrixes['L'])
        P = np.array(matrixes['P'])
        B = np.array(bias['B'])
        ATPL = np.array(matrixes['ATPL'])
        invATPA = np.array(matrixes['invATPA'])

        var = self._var(A, P, L, B, ATPL)
        logging.info(">> Calculating variance a posteriori...")
        quality_meas['var'] = var.item()
        logging.info(">>>> Var: {}".format(quality_meas['var']))

        accuracy = self._accuracy(invATPA)
        logging.info(">> Calculating accuracy...")
        quality_meas['accuracy'] = accuracy.tolist()

        quality = self._quality(invATPA, quality_meas['var'])
        logging.info(">> Calculating quality...")
        quality_meas['quality'] = quality.tolist()

        residuals = self._residuals(A, L, B)
        logging.info(">> Calculating residuals...")
        quality_meas['residuals'] = residuals.tolist()

        return quality_meas
