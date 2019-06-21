# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

from PyQt5.QtWidgets import QApplication
from pandas import concat, DataFrame
from pyIMD.configuration.config import Settings
from pyIMD.ui.settings import SettingsDialog
from pyIMD.io.read_from_disk import read_from_text, read_from_file
from pyIMD.io.write_to_disk import write_to_disk_as
from pyIMD.analysis.calculations import calculate_mass
from pyIMD.analysis.calculations import calculate_resonance_frequencies, calculate_position_correction
from pyIMD.configuration.defaults import *
from PyQt5.QtCore import pyqtSlot, QObject
import matplotlib
matplotlib.use('Qt5Agg')
from pyIMD.plotting.figures import plot_fitting, plot_response_shift, plot_mass
import os
import sys
import logging
from tqdm import trange
import numpy as np

__author__ = 'Andreas P. Cuny'


class InertialMassDetermination(QObject):
    """
    Constructs a IntertialMassDetermination object
    """

    def __init__(self):
        """
        Constructs an InteritalMassDetermination object.
        """

        super(InertialMassDetermination, self).__init__()
        # Initialize settings class
        self.settings = Settings()
        self.settings_dialog = None
        self._has_valid_configuration = 0
        # Initialize data properties
        self.data_pre_start_no_cell = []
        self.data_pre_start_with_cell = []
        self.data_measured = []
        self.resonance_freq_pre_start_no_cell = []
        self.resonance_freq_pre_start_with_cell = []
        self.resonance_freq_measured = []
        self.fit_param_pre_start_no_cell = []
        self.fit_param_pre_start_with_cell = []
        self.fit_param_measured = []
        self.calculated_cell_mass = []
        self.position_correction_factor = []

        # Rename into self.settings.project_folder_path
        self.result_folder = []  # os.path.dirname(os.path.abspath(file_path3))

        self.logger = self.get_logger_object(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info('Object constructed successfully')

        # Load default settings
        self.__settings = {"figure_format": FIGURE_FORMAT,
                           "figure_width": FIGURE_WIDTH,
                           "figure_height": FIGURE_HEIGHT,
                           "figure_units": FIGURE_UNITS,
                           "figure_resolution_dpi": FIGURE_RESOLUTION_DPI,
                           "figure_name_pre_start_no_cell": FIGURE_NAME_PRE_START_NO_CELL,
                           "figure_name_pre_start_with_cell": FIGURE_NAME_PRE_START_WITH_CELL,
                           "figure_name_measured_data": FIGURE_NAME_MEASURED_DATA,
                           "figure_plot_every_nth_point": FIGURE_PLOT_EVERY_NTH_POINT,
                           "conversion_factor_hz_to_khz": CONVERSION_FACTOR_HZ_TO_KHZ,
                           "conversion_factor_deg_to_rad": CONVERSION_FACTOR_DEG_TO_RAD,
                           "spring_constant": SPRING_CONSTANT,
                           "cantilever_length": CANTILEVER_LENGTH,
                           "cell_position": CELL_POSITION,
                           "initial_parameter_guess": INITIAL_PARAMETER_GUESS,
                           "lower_parameter_bounds": LOWER_PARAMETER_BOUNDS,
                           "upper_parameter_bounds": UPPER_PARAMETER_BOUNDS,
                           "rolling_window_size": ROLLING_WINDOW_SIZE,
                           "correct_for_frequency_offset": CORRECT_FOR_FREQUENCY_OFFSET,
                           "frequency_offset_mode": FREQUENCY_OFFSET_MODE,
                           "frequency_offset_n_measurements_used" : FREQUENCY_OFFSET_N_MEASUREMENTS_USED,
                           "frequency_offset": FREQUENCY_OFFSET,
                           "read_text_data_from_line": READ_TEXT_DATA_FROM_LINE,
                           "text_data_delimiter": repr(TEXT_DATA_DELIMITER).replace("'", "")}

    def create_pyimd_project(self, pre_start_no_cell_path, pre_start_with_cell_path, measurements_path,
                             text_data_delimiter, read_text_data_from_line, calculation_mode, **kwargs):
        """
        Create a pyIMD project with the following arguments. Two modes \
        enable the analysis of different experimental setups. PLL mode and Cont.Sweep mode. For more information please
        read the documentation.

        Args:
             pre_start_no_cell_path (`str`):       File path + file name of initial frequency \
                                                   shift measurement before cell attachment (txt file).
             pre_start_with_cell_path (`str`):     File path + file name of initial frequency \
                                                   shift measurement after cell attachment (txt file).
             measurements_path (`str`):            File path + file name of the actual \
                                                   measurement (tdms file (default) or txt file).
             text_data_delimiter (`str`):          Text file data delimiter i.e '\t' for tab delimited or ',' for comma
                                                   separated data.
             read_text_data_from_line (`int`):      Line number from which data of pre start measurements should be read
                                                   Typically the first few lines contain header information and no data.
             calculation_mode (`str`):             PLL         := phase lock loops mode
                                                   Cont.Sweep  := sweep mode
                                                   Auto        := Auto detection of the mode (experimental)
        Keyword Args:
             figure_width (`float`):                  Width of result figures
             figure_height (`float`):                 Height of result figures
             figure_units (`str`):                    Figure units i.e cm, inch
             figure_format (`str`):                   Figure format i.e png or pdf
             figure_resolution_dpi (`int`):           Resolution of result figures in dpi
             figure_name_pre_start_no_cell (`str`):   Figure name of function fit for pre start with no cell loaded data
             figure_name_pre_start_with_cell (`str`): Figure name of function fit for pre start with cell loaded data
             figure_name_measured_data (`str`):       Figure name of the resulting mass of the measured data
             figure_plot_every_nth_point ('int'):     Parameter defining how many data points will be plotted. For large
                                                     data stets to increase readability and reducing file size.
             conversion_factor_hz_to_khz (`float`):   Conversion factor to convert from hertz to kilo hertz
             conversion_factor_deg_to_rad (`float`):  Conversion factor to convert from degrees to radian
             spring_constant (`float`):               Spring constant value of the cantilever
             initial_parameter_guess (`list`):        Initial parameter guess
             lower_parameter_bounds (`list`):         Lower parameter bounds
             upper_parameter_bounds (`list`):         Upper parameter bounds
             rolling_window_size ('int'):             Window size for calculating the rolling average.
             correct_for_frequency_offset ('bool'):   Correct for potential frequency offset during PLL mode.
             frequency_offset_mode ('str'):           Frequency offset correction mode (Auto or Manual)
             frequency_offset_n_measurements_used ('int'): Number of measurement data points to be used for automatic
                                                      frequency offset correction
             frequency_offset ('float'):              Frequency offset either set manually or calculated automatically
             cantilever_length (`float`):             Cantilever length in microns
             cell_position (`float`):                 Cell position offset from cantilever tip in microns
             project_folder_path (`str`):             Path to project data files. Also used to store pyIMD results such
                                                      as data and figures.
        """
        try:
            self.settings.new_pyimd_project(pre_start_no_cell_path, pre_start_with_cell_path, measurements_path,
                                            text_data_delimiter, read_text_data_from_line, calculation_mode, **kwargs)
            self._has_valid_configuration = 1
        except Exception as e:
            self.logger.info("Error during opening project: " + str(e))

    def load_pyimd_project(self, file_path):
        """
        Loads a pre defined pyIMD project form a XML file.

        Args:
            file_path (`str`):   Full path + file name to the pyIMD project file.

        Returns:
            status (`str`):      String reporting the success of failure of loading a pyIMD project.
        """
        try:
            message = self.settings.read_pyimd_project(file_path)
            self.logger.info(message)
            self._has_valid_configuration = 1
        except Exception as e:
            self.logger.info("Error during opening project: " + str(e))

    def save_pyimd_project(self, file_path):
        """
        Saves the current pyIMD project as XML file.

        Args:
            file_path (`str`):   Full path + file name to the pyIMD project file.

        Returns:
            status (`str`):      String reporting the success of failure of loading a pyIMD project.
        """
        try:
            self.settings.write_pyimd_project(file_path)
        except Exception as e:
            self.logger.info("Error during opening project: " + str(e))

    def print_pyimd_project(self):
        """
        Prints the current pyIMD settings and parameters to the console.

        Returns:
            pyIMD project summary (`str`):        pyIMD settings and parameter summary as formatted string.
        """
        self.logger.info(self.settings)

    def run_inertial_mass_determination(self):
        """Runs the inertial mass determination calculation

        Returns:
            void:            Returns result structured in a pandas data frame and saves function fit plots as pdf \
                             or png files directly to the disk.
        """

        if self._has_valid_configuration == 1:
            self.result_folder = self.settings.project_folder_path
            # Read data
            self.logger.info('Start reading all files')
            self.data_pre_start_no_cell = read_from_text(self.settings.pre_start_no_cell_path,
                                                         self.settings.text_data_delimiter,
                                                         self.settings.read_text_data_from_line)
            self.data_pre_start_with_cell = read_from_text(self.settings.pre_start_with_cell_path,
                                                           self.settings.text_data_delimiter,
                                                           self.settings.read_text_data_from_line)
            self.data_measured = read_from_file(self.settings.measurements_path, self.settings.text_data_delimiter)
            self.logger.info('Done reading all files')
            # Convert data to the correct units
            self.convert_data()
            self.logger.info('Done converting units')

            # Calc resonance frequency for pre start data without cell attached to cantilever
            self.resonance_freq_pre_start_no_cell, self.fit_param_pre_start_no_cell = calculate_resonance_frequencies(
                self.data_pre_start_no_cell.iloc[:, 0], self.data_pre_start_no_cell.iloc[:, 2],
                self.settings.initial_parameter_guess, self.settings.lower_parameter_bounds,
                self.settings.upper_parameter_bounds)

            figure_pre_start_no_cell = plot_fitting(self.data_pre_start_no_cell.iloc[:, 0],
                                                    self.data_pre_start_no_cell.iloc[:, 2],
                                                    self.resonance_freq_pre_start_no_cell,
                                                    self.fit_param_pre_start_no_cell)

            optional_fig_param = {'width': self.settings.figure_width, 'height': self.settings.figure_height,
                                  'units': self.settings.figure_units,
                                  'resolution': self.settings.figure_resolution_dpi}

            write_to_disk_as(self.settings.figure_format, figure_pre_start_no_cell,
                             '{}'.format(self.result_folder + os.sep + self.settings.figure_name_pre_start_no_cell),
                             **optional_fig_param)
            self.logger.info('Done with pre start no cell resonance frequency calculation')

            # Calc position correction for cell attached to cantilever
            self.position_correction_factor = calculate_position_correction(self.settings.cell_position,
                                                                            self.settings.cantilever_length)

            # Calc resonance frequency for pre start data with cell attached to cantilever
            self.resonance_freq_pre_start_with_cell, self.fit_param_pre_start_with_cell = \
                calculate_resonance_frequencies(self.data_pre_start_with_cell.iloc[:, 0],
                                                self.data_pre_start_with_cell.iloc[:, 2],
                                                self.settings.initial_parameter_guess,
                                                self.settings.lower_parameter_bounds,
                                                self.settings.upper_parameter_bounds)

            figure_pre_start_with_cell = plot_fitting(self.data_pre_start_with_cell.iloc[:, 0],
                                                      self.data_pre_start_with_cell.iloc[:, 2],
                                                      self.resonance_freq_pre_start_with_cell,
                                                      self.fit_param_pre_start_with_cell)

            write_to_disk_as(self.settings.figure_format, figure_pre_start_with_cell,
                             '{}'.format(self.result_folder + os.sep + self.settings.figure_name_pre_start_with_cell),
                             **optional_fig_param)
            self.logger.info('Done with pre start with cell resonance frequency calculation')

            fig = plot_response_shift(self.data_pre_start_no_cell.iloc[:, 0], self.data_pre_start_no_cell.iloc[:, 2],
                                      self.resonance_freq_pre_start_no_cell, self.fit_param_pre_start_no_cell,
                                       self.data_pre_start_with_cell.iloc[:, 0], self.data_pre_start_with_cell.iloc[:, 2],
                                      self.resonance_freq_pre_start_with_cell, self.fit_param_pre_start_with_cell)

            write_to_disk_as(self.settings.figure_format, fig,
                             '{}'.format(self.result_folder + os.sep + 'PreStartFrequencyShift'), **optional_fig_param)
            self.logger.info('Done with pre start frequency shift figure generation')
            if self.settings.calculation_mode == 'Cont.Sweep':
                # The continuous sweep mode
                self.calculated_cell_mass = []
                for iSweep in trange(0, len(self.data_measured), 3):
                    # Calc resonance frequency and function fit for the ith sweep (iSweep)
                    res_freq, param = calculate_resonance_frequencies(self.data_measured.iloc[iSweep + 2, 0:255],
                                                                      self.data_measured.iloc[iSweep + 1, 0:255],
                                                                      self.settings.initial_parameter_guess,
                                                                      self.settings.lower_parameter_bounds,
                                                                      self.settings.upper_parameter_bounds)
                    # Calculate the mass for the ith sweep (iSweep)
                    # @todo append self.resonance_freq_pre_start_with_cell to the list self.calculated_cell_mass first!
                    mass = calculate_mass(self.settings.spring_constant, res_freq, self.resonance_freq_pre_start_no_cell)
                    # Store results in a list
                    self.resonance_freq_measured.append(res_freq)
                    self.fit_param_measured.append(param)
                    self.calculated_cell_mass.append(mass * self.position_correction_factor)

                    if np.remainder(iSweep, 300) == 0:
                        figure_i_sweep = plot_fitting(self.data_measured.iloc[iSweep + 2, 0:255],
                                                      self.data_measured.iloc[iSweep + 1, 0:255], res_freq, param)
                        write_to_disk_as(self.settings.figure_format, figure_i_sweep,
                                         '{}'.format(self.result_folder + os.sep + 'ResFreqSweep_' + str(iSweep)))

                calculated_cell_mass = concat([(self.data_measured.iloc[0:int(((len(self.data_measured)) / 3)-1), 256] -
                                                self.data_measured.iloc[0, 256]) / 3600,
                                               DataFrame(self.calculated_cell_mass, columns=['Mass [ng]'])], axis=1)
                calculated_cell_mass['Mean mass [ng]'] = calculated_cell_mass['Mass [ng]'].rolling(
                    window=self.settings.rolling_window_size).mean()

                self.calculated_cell_mass = calculated_cell_mass
                figure_cell_mass = plot_mass(calculated_cell_mass, self.settings.figure_plot_every_nth_point)
                self.logger.info('Start writing figure to disk')
                write_to_disk_as(self.settings.figure_format, figure_cell_mass,
                                 '{}'.format(self.result_folder + os.sep + self.settings.figure_name_measured_data),
                                 **optional_fig_param)
                self.logger.info('Done writing figure to disk')
                self.logger.info('Start writing data to disk')
                calculated_cell_mass.to_csv(self.result_folder + os.sep +
                                            self.settings.figure_name_measured_data + '.csv', index=False, na_rep="nan")
                self.calculated_cell_mass = calculated_cell_mass
                self.logger.info('Done writing data to disk')

            else:
                # The PLL mode
                # Add resonance_freq_pre_start_with_cell to measured resonance frequency delta
                # Calculate the mass
                self.calculated_cell_mass = []
                if self.settings.correct_for_frequency_offset:
                    if self.settings.frequency_offset_mode == 'Auto':
                        # Calc auto frequency offset by averaging the first n measurement data points and save this
                        # offset value found.
                        n = int(self.settings.frequency_offset_n_measurements_used)

                        auto_freq_offset = np.mean(self.data_measured.iloc[0:n, 6])
                        self.logger.info('Offset calculation result: {}'.format(auto_freq_offset))
                        self.settings.frequency_offset = auto_freq_offset
                        self.resonance_freq_pre_start_with_cell = self.resonance_freq_pre_start_with_cell -\
                                                                  self.settings.frequency_offset
                for iPLL in trange(0, len(self.data_measured)):
                    if self.settings.correct_for_frequency_offset:
                            mass = calculate_mass(self.settings.spring_constant, (self.data_measured.iloc[iPLL, 6] -
                                                                                  self.settings.frequency_offset) +
                                                  self.resonance_freq_pre_start_with_cell,
                                                  self.resonance_freq_pre_start_no_cell)
                    else:
                        mass = calculate_mass(self.settings.spring_constant, self.data_measured.iloc[iPLL, 6] +
                                              self.resonance_freq_pre_start_with_cell,
                                              self.resonance_freq_pre_start_no_cell)

                    self.calculated_cell_mass.append(mass * self.position_correction_factor)

                calculated_cell_mass = concat([(self.data_measured.iloc[:, 0] - self.data_measured.iloc[1, 0]) / 3600,
                                               DataFrame(self.calculated_cell_mass, columns=['Mass [ng]'])], axis=1)
                calculated_cell_mass['Mean mass [ng]'] = calculated_cell_mass['Mass [ng]'].rolling(
                    window=self.settings.rolling_window_size).mean()
                self.calculated_cell_mass = calculated_cell_mass

                figure_cell_mass = plot_mass(calculated_cell_mass, self.settings.figure_plot_every_nth_point)
                self.logger.info('Start writing figure to disk')
                write_to_disk_as(self.settings.figure_format, figure_cell_mass,
                                 '{}'.format(self.result_folder + os.sep + self.settings.figure_name_measured_data),
                                 **optional_fig_param)
                self.logger.info('Done writing figure to disk')
                self.logger.info('Start writing data to disk')
                calculated_cell_mass.to_csv(self.result_folder + os.sep +
                                            self.settings.figure_name_measured_data + '.csv', index=False, na_rep="nan")
                self.logger.info('Done writing data to disk')

            self.logger.info('Done with all calculations')

        else:
            self.logger.info('No valid pyIMD configuration found. Please create or load a pyIMD project first.')

    def run_batch_inertial_mass_determination(self, *args):
        """ Runs the inertial mass determination calculation in batch mode. Specify one or multiple pyIMD project files
        which will be run sequentially. NOTE: In a future release this will be parallelized using multiple threads to
        perform the calculations in parallel to gain speed. Currently the focus is not on speed but the idea is to
        analyze many experiments conveniently over night for example.

        Args:
            args (`list`):   List of one or many file paths + file names to valid pyIMD project files.

        Returns:
            void:            Returns result structured in a pandas data frame and saves function fit plots as pdf \
                             files.
        """
        try:
            for file in args:
                self.load_pyimd_project(file)
                # load each project configuration sequentially.
                if self._has_valid_configuration == 1:
                    # start calculations if configuration was valid
                    self.run_intertial_mass_determination()
                else:
                    self.logger.info('No valid pyIMD configuration found. Please create or load a pyIMD project first.')
        except Exception as e:
            self.logger.info("Error during opening project: " + str(e))

    def convert_data(self):
        """ Converts imported data to correct units needed for further calculation.
        """

        attributes = ['data_pre_start_no_cell', 'data_pre_start_with_cell']
        for iAttribute in attributes:
            getattr(self, str(iAttribute)).iloc[:, 0] = getattr(self, str(iAttribute)).iloc[:, 0] / \
                                                        self.settings.conversion_factor_hz_to_khz
            getattr(self, str(iAttribute)).iloc[:, 2] = getattr(self, str(iAttribute)).iloc[:, 2] / \
                                                        self.settings.conversion_factor_deg_to_rad
        if self.settings.calculation_mode == 'Cont.Sweep':
            for iSweep in range(0, len(self.data_measured), 3):
                # Calc resonance frequency and function fit for the ith sweep (iSweep)
                self.data_measured.iloc[iSweep + 1, 0:255] = self.data_measured.iloc[iSweep + 1, 0:255] / \
                                                             self.settings.conversion_factor_deg_to_rad
                self.data_measured.iloc[iSweep + 2, 0:255] = self.data_measured.iloc[iSweep + 2, 0:255] / \
                                                             self.settings.conversion_factor_hz_to_khz
        else:
            self.data_measured.iloc[:, 5] = self.data_measured.iloc[:, 5] / self.settings.conversion_factor_deg_to_rad
            self.data_measured.iloc[:, 6] = self.data_measured.iloc[:, 6] / self.settings.conversion_factor_hz_to_khz

    @staticmethod
    def get_logger_object(name):
        """
        Gets a logger object to log messages of pyIMD status to the console in a standardized format.

        Returns:
            logger (`object`):      Returns a logger object with correct string formatting.
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            # Prevent logging from propagating to the root logger
            logger.propagate = 0
            console = logging.StreamHandler(sys.stderr)
            logger.addHandler(console)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            console.setFormatter(formatter)
            logger.setLevel(logging.INFO)

        return logger

    def show_settings_dialog(self):
        """
        Shows the settings dialog in a pop up window.
        """
        if self.settings_dialog is None:
            app = QApplication([])
            SettingsDialog(self.__settings)
            self.settings_dialog = SettingsDialog(self.__settings)
            self.settings_dialog.set_values()
            self.settings_dialog.settings_has_changed_signal.connect(self.on_settings_changed)
            self.establish_console_connection()
            self.settings_dialog.show()
            app.exec_()

    @pyqtSlot(dict, name="on_settings_changed")
    def on_settings_changed(self, changed_settings):
        """
        Update settings
        """

        # Update the settings
        self.__settings = changed_settings

    def establish_console_connection(self):
        """
        Establish console connection between the imd object and the settings dialog.
        """
        self.settings_dialog.send_to_console_signal.connect(self.handle_change_console_text)

    @pyqtSlot(str, name="handle_change_console_text")
    def handle_change_console_text(self, string):
        """
        Args:
            string (`str`): String received from Settings instance to print to the console.
        """
        # self.print_to_console(string)
        self.logger.info(string)
