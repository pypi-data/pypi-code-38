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

import os
from unittest import TestCase, main
from pyIMD.imd import InertialMassDetermination


class TestConfiguration(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.imd = InertialMassDetermination()

    def tearDown(self):
        TestCase.tearDown(self)

    def testTrue(self):
        self.assertTrue(self.imd.create_pyimd_project)
        self.assertTrue(self.imd.load_pyimd_project)
        self.assertTrue(self.imd.save_pyimd_project)
        self.assertTrue(self.imd.run_batch_inertial_mass_determination)
        self.assertTrue(self.imd.run_inertial_mass_determination)

    def testSettingsInitDefaults(self):

        expected_result = {'_project_folder_path': '', '_rolling_window_size': 1000, '_selected_files': [],
                           '_measurements_path': '', '_read_text_data_from_line': 23, '_pre_start_with_cell_path': '',
                           '_conversion_factor_hz_to_khz': 1000.0, '_figure_units': 'cm', '_figure_width': 56.44,
                           '_cell_position': 5, '_spring_constant': 4.0, '_figure_resolution_dpi': 72,
                           '_cantilever_length': 100, '_figure_name_pre_start_with_cell': 'FitWithCellData',
                           '_correct_for_frequency_offset': False,  '_frequency_offset_mode': 'Auto',
                           '_frequency_offset_n_measurements_used': 1, '_frequency_offset': 0,
                           '_pre_start_no_cell_path': '', '_figure_height': 45.16, '_figure_name_measured_data':
                               'CalculatedCellMass', '_conversion_factor_deg_to_rad': -57.3, '_calculation_mode': 'PLL',
                           '_figure_plot_every_nth_point': 1, '_initial_parameter_guess': [70.0, 2.0, 0.0, 0.0],
                           '_upper_parameter_bounds': [100.0, 5.0, 3, 3], '_figure_format': 'png',
                           '_lower_parameter_bounds': [10.0, 1.0, -3, -3], '_text_data_delimiter': '\t',
                           '_figure_name_pre_start_no_cell': 'FitNoCellData'}

        self.assertEqual(self.imd.settings.__dict__, expected_result)

    def testSettingsNewProject(self):

        expected_result = {'_figure_units': 'cm', '_figure_name_pre_start_with_cell': 'FitWithCellData',
                           '_calculation_mode': 'PLL', '_figure_name_measured_data': 'CalculatedCellMass',
                           '_pre_start_with_cell_path': os.path.abspath("../examples/data/show_case/"
                                                                        "20190110_ShowCase_PLL_A.txt"),
                           '_measurements_path': os.path.abspath("../examples/data/show_case/"
                                                                 "20190110_ShowCase_PLL_LongTerm.txt"),
                           '_upper_parameter_bounds': [90.0, 7, 3.0, 3.0], '_conversion_factor_deg_to_rad': -57.3,
                           '_initial_parameter_guess': [70.0, 2.0, 0.0, 0.0], '_lower_parameter_bounds':
                               [10.0, 1.0, -3, -3], '_cantilever_length': 100, '_rolling_window_size': 1000,
                           '_figure_width': 16.5, '_conversion_factor_hz_to_khz': 1000.0,
                           '_figure_plot_every_nth_point': 1, '_project_folder_path': os.path.abspath("../examples/data/"
                                                                                                      "show_case/"),
                           '_selected_files': ['20190110_ShowCase_PLL_B.txt', '20190110_ShowCase_PLL_A.txt',
                                               '20190110_ShowCase_PLL_LongTerm.txt'],
                           '_figure_resolution_dpi': 72, '_correct_for_frequency_offset': False,
                           '_frequency_offset_mode': 'Auto', '_frequency_offset_n_measurements_used': 1,
                           '_frequency_offset': 0, '_pre_start_no_cell_path': os.path.abspath("../examples/data/"
                                                                                              "show_case/"
                                                                                              "20190110_ShowCase_PLL_B.txt"),
                           '_read_text_data_from_line': 23,
                           '_figure_name_pre_start_no_cell': 'FitNoCellData', '_text_data_delimiter': '\\t',
                           '_spring_constant': 8, '_figure_format': 'pdf', '_cell_position': 9.5, '_figure_height': 20}

        file_path1 = os.path.abspath("../examples/data/show_case/20190110_ShowCase_PLL_B.txt")
        file_path2 = os.path.abspath("../examples/data/show_case/20190110_ShowCase_PLL_A.txt")
        file_path3 = os.path.abspath("../examples/data/show_case/20190110_ShowCase_PLL_LongTerm.txt")

        self.imd.create_pyimd_project(file_path1, file_path2, file_path3, '\t', 23, 'PLL', figure_width=16.5,
                                        figure_height=20, upper_parameter_bounds=[90.0, 7, 3.0, 3.0], spring_constant=8,
                                        cell_position=9.5, figure_format='pdf')

        self.assertEqual(self.imd.settings.__dict__, expected_result)


if __name__ == "__main__":
    main()