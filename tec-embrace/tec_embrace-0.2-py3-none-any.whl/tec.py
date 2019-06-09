import time
import os
import logging
import datetime
import csv

import tec_embrace.settings as settings
import tec_embrace.helper as helper
import tec_embrace.estimate as calc
import tec_embrace.cycleslip.cycleslip as cs


class TEC:
    """
    Class with the main calls for TEC estimation (by station)
    """
    input_files = ""
    utils = ""
    cycle_slip = ""
    tec_estimation = ""
    bias_estimation = ""
    quality_control = ""

    rinex_folder = ""
    path_dcb = ""
    path_orbit = ""
    path_glonass_channel = ""
    min_requeried_version = ""
    constelations = ""
    tec_resolution = ""
    tec_resolution_value = ""
    keys_save = ""

    def __init__(self, rinex_folder, path_dcb, path_orbit, path_glonass_channel, 
                 min_requeried_version, constelations, tec_resolution, tec_resolution_value, keys_save):
        self.rinex_folder = rinex_folder
        self.path_dcb = path_dcb
        self.path_orbit = path_orbit
        self.path_glonass_channel = path_glonass_channel
        self.min_requeried_version = min_requeried_version
        self.constelations = constelations
        self.tec_resolution = tec_resolution
        self.tec_resolution_value = tec_resolution_value
        self.keys_save = keys_save      

        self.input_files = helper.InputFiles(rinex_folder, path_dcb, path_orbit, path_glonass_channel, min_requeried_version, 
                                        constelations, tec_resolution, tec_resolution_value, keys_save)
        self.utils = helper.Utils()
        self.cycle_slip = cs.CycleSlip()
        self.tec_estimation = calc.TECEstimation(self.tec_resolution, self.tec_resolution_value)
        self.bias_estimation = calc.BiasEstimation(self.tec_resolution, self.tec_resolution_value)
        self.quality_control = calc.QualityControl()

    def simplify_dict(self, dict_var, list_keys):
        """
        According to args, select and save in dict_var, specific keys among many other

        :param dict_var: Dict with all the TEC estimates
        :param list_keys: Brings the right keys to simplify the dict
        :return: A simplified dict_var based on the args
        """
        dict_var_simplified = {}

        for item in list_keys:
            dict_var_simplified[item] = dict_var[item]

        return dict_var_simplified

    def write_csv(self, path, tec, key):
        """
        Based on a dict (TEC), select the 'key' for printing all PRNs in columns in a CSV file format
        :param path: Path to save the CSV file
        :param tec: Dict object
        :param key: Key to be printed
        :return:
        """
        time = tec['time']

        f = csv.writer(open(path, "w+"))

        columns = []
        columns.append('time')
        for prn in tec[key]:
            columns.append(prn)

        f.writerow(columns)

        prns = list(tec[key].keys())
        elements = len(tec[key][prns[0]])
        for element in range(elements):
            row = []
            row.append(time[element])
            for prn in tec[key]:
                row.append(tec[key][prn][element])
            f.writerow(row)

    def process_tec_file(self, file):
        """
        TEC workflow, with the calculus of the whole day. At the end of this workflow, the

        :param rinex_folder: Absolute folder with a set of rinex files
        :param file: the rinex name file        
        :return: All the TEC estimative, including the piercing points, slant factor, daily TEC, bias receiver,
        detrended, relative, absolute and, finally, vertical TEC
        """
        tec = {}
        start = time.perf_counter()

        logging.info("- {} - TEC by fractions of {} {} a day, and bias receiver estimation".
                     format(file, self.tec_resolution_value, self.tec_resolution))

        logging.info("Preparing inputs...")        
        hdr, obs, orbit, dcb, factor_r, l1_col, l2_or_l3_col, p1_or_c1_col, p2_or_c2_col, l2_channel, \
        constellations = self.input_files.prepare_inputs(file)

        tec['metadata'] = {
            'creation-date': datetime.datetime.utcnow(),
            'modification-date': datetime.datetime.utcnow(),
            'rinex-file': file,
            'rinex-path': os.path.join(self.rinex_folder, file),
            'rinex-date': self.utils.rinex_str_date_to_datetime(hdr),
            'rinex-precision': hdr['interval'],
            'keys-saved': self.keys_save,
            'constellations-desired': self.constelations,
            'constellations-used-in-the-calc': constellations,
            'min-elev-angle': settings.MIN_ELEVATION_ANGLE,
            'station': hdr['MARKER NAME'].strip(),
            'orbit-name': orbit['path'],
            'dcb-name': dcb['path']
        }

        logging.info("Converting timestamp str in datetimes...")
        tec['time'] = self.utils.array_timestamp_to_datetime(obs.time)

        try:
            logging.info("Calculating slant factor for DTEC calculation...")
            tec['slant-dtec'] = self.tec_estimation.slant(hdr, obs, orbit, 0)

            logging.info("Calculating slant factor for TEC estimation...")
            tec['slant'] = self.tec_estimation.slant(hdr, obs, orbit, 1)

            logging.info("Correcting Cycle-Slip...")
            tec['relative-l1-l2'] = self.cycle_slip.cycle_slip_analysis(obs, tec, factor_r, l1_col, l2_or_l3_col,
                                                                        p1_or_c1_col, p2_or_c2_col, l2_channel)

            logging.info("Calculating dTEC...")
            tec['detrended'] = self.tec_estimation.detrended(tec, factor_r, l2_channel)

            logging.info("Calculating relative TEC...")
            tec['relative'] = self.tec_estimation.relative(tec, obs, factor_r, dcb, p1_or_c1_col, p2_or_c2_col)

            logging.info("Estimating TEC and Bias with daily measurements...")
            tec['matrixes'], tec['bias'] = self.bias_estimation.estimate_bias(tec, constellations)

            logging.info("Quality control - calculating the quality of the estimates...")
            tec['quality'] = self.quality_control.quality_control(tec['matrixes'], tec['bias'])

            # TODO: Incluir leitura de obs (parcial): em somente parte do dia
            # TODO: Concluir controle de qualidade por análise residual
            logging.info("Filtering - filtering measures and error detection...")
            # tec['bias'] = quality_control.check_quality(obs, tec, constellations, rinex_folder, file)

            logging.info("Calculating absolute TEC...")
            tec['absolute'] = self.tec_estimation.absolute(tec, constellations)

            logging.info("Calculating vertical TEC...")
            tec['vertical'] = self.tec_estimation.vertical(tec, orbit)

            # utils.write_csv(tec, 'absolute.csv', tec[absolute])

        except Exception as e:
            logging.error(':::: EXCEPTION thrown during {} processing: {}! File skipped!\n'.format(file, e))

        stop = time.process_time()
        logging.info("Processing done for {}! Time: {} minutes".format(file, float((start - stop) / 60)))
        logging.info("-----------------------------------------------------------------------------------")

        tec_to_be_stored = self.simplify_dict(tec, settings.KEYS_SAVE)

        return tec_to_be_stored

