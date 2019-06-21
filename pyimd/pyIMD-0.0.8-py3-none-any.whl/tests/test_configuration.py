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
from xmlunittest import XmlTestCase
from unittest import TestCase, main
from pyIMD.configuration.config import Settings
from pyIMD.ui.resource_path import resource_path


class TestConfiguration(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.settings = Settings()

    def tearDown(self):
        TestCase.tearDown(self)

    def testTrue(self):
        self.assertTrue(self.settings.read_pyimd_project)
        self.assertTrue(self.settings.write_pyimd_project)
        self.assertTrue(self.settings.new_pyimd_project)

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

        self.assertEqual(self.settings.__dict__, expected_result)

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
                           '_selected_files': ['20190110_ShowCase_PLL_B.txt',
                                                                           '20190110_ShowCase_PLL_A.txt',
                                                                           '20190110_ShowCase_PLL_LongTerm.txt'],
                           '_figure_resolution_dpi': 72, '_correct_for_frequency_offset': False,
                           '_frequency_offset_mode': 'Auto', '_frequency_offset_n_measurements_used': 1,
                           '_frequency_offset': 0, '_pre_start_no_cell_path': os.path.abspath("../examples/data/"
                                                                                              "show_case/"
                                                                                              "20190110_ShowCase_PLL_B.txt"),
                           '_read_text_data_from_line': 23,
                           '_figure_name_pre_start_no_cell': 'FitNoCellData', '_text_data_delimiter': '\\t',
                           '_spring_constant': 8, '_figure_format': 'pdf', '_cell_position': 9.5, '_figure_height': 20}

        print(os.path.abspath("../examples/data/show_case/20190110_ShowCase_PLL_B.txt"))
        file_path1 = os.path.abspath("../examples/data/show_case/20190110_ShowCase_PLL_B.txt")
        file_path2 = os.path.abspath("../examples/data/show_case/20190110_ShowCase_PLL_A.txt")
        file_path3 = os.path.abspath("../examples/data/show_case/20190110_ShowCase_PLL_LongTerm.txt")

        self.settings.new_pyimd_project(file_path1, file_path2, file_path3, '\t', 23, 'PLL', figure_width=16.5,
                                        figure_height=20, upper_parameter_bounds=[90.0, 7, 3.0, 3.0], spring_constant=8,
                                        cell_position=9.5, figure_format='pdf')

        self.assertEqual(self.settings.__dict__, expected_result)


class TestConfigurationIO(XmlTestCase):

    def testNewPyimdProject(self):
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
                           '_figure_plot_every_nth_point': 1, '_project_folder_path': os.path.abspath("../examples/"
                                                                                                      "data/show_case/"),
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

        settings = Settings()
        settings.new_pyimd_project(file_path1, file_path2, file_path3, '\t', 23, 'PLL', figure_width=16.5,
                                   figure_height=20, upper_parameter_bounds=[90.0, 7, 3.0, 3.0], spring_constant=8,
                                   cell_position=9.5, figure_format='pdf')
        self.assertEqual(settings.__dict__, expected_result)

    def testWritePyimdProject(self):
        # Create the inertial mass determination object
        settings = Settings()
        # Save the project
        settings.write_pyimd_project(resource_path('TestConfig.xml'))

        with open('TestConfig.xml', 'rb', ) as myfile:
            data = myfile.read()

        # Everything starts with `assertXmlDocument`
        root = self.assertXmlDocument(data)

        # Check
        self.assertXmlNode(root, tag='PyIMDSettings')
        self.assertXpathValues(root, './GeneralSettings/figure_format/text()', 'png')
        self.assertXpathValues(root, './GeneralSettings/figure_width/text()', '56.44')
        self.assertXpathValues(root, './GeneralSettings/figure_height/text()', '45.16')
        self.assertXpathValues(root, './GeneralSettings/figure_units/text()', 'cm')
        self.assertXpathValues(root, './GeneralSettings/figure_resolution_dpi/text()', '72')
        self.assertXpathValues(root, './GeneralSettings/figure_name_pre_start_no_cell/text()', 'FitNoCellData')
        self.assertXpathValues(root, './GeneralSettings/figure_name_pre_start_with_cell/text()', 'FitWithCellData')
        self.assertXpathValues(root, './GeneralSettings/figure_name_measured_data/text()', 'CalculatedCellMass')
        self.assertXpathValues(root, './GeneralSettings/figure_plot_every_nth_point/text()', '1')
        self.assertXpathValues(root, './GeneralSettings/conversion_factor_hz_to_khz/text()', '1000.0')
        self.assertXpathValues(root, './GeneralSettings/conversion_factor_deg_to_rad/text()', '-57.3')
        self.assertXpathValues(root, './GeneralSettings/spring_constant/text()', '4.0')
        self.assertXpathValues(root, './GeneralSettings/cantilever_length/text()', '100')
        self.assertXpathValues(root, './GeneralSettings/cell_position/text()', '9.5')
        self.assertXpathValues(root, './GeneralSettings/initial_parameter_guess/text()', '[70.0, 2.0, 0.0, 0.0]')
        self.assertXpathValues(root, './GeneralSettings/lower_parameter_bounds/text()', '[10.0, 1.0, -3, -3]')
        self.assertXpathValues(root, './GeneralSettings/upper_parameter_bounds/text()', '[100.0, 5.0, 3, 3]')
        self.assertXpathValues(root, './GeneralSettings/rolling_window_size/text()', '1000')
        self.assertXpathValues(root, './GeneralSettings/frequency_offset/text()', '0')
        self.assertXpathValues(root, './GeneralSettings/read_text_data_from_line/text()', '23')
        self.assertXpathValues(root, './GeneralSettings/text_data_delimiter/text()', '\t')
        self.assertXpathValues(root, './ProjectSettings/selected_files/File/text()',
                               ('20190110_ShowCase_PLL_A.txt', '20190110_ShowCase_PLL_B.txt',
                                '20190110_ShowCase_PLL_LongTerm.txt'))
        self.assertXpathValues(root, './ProjectSettings/project_folder_path/text()', '')
        self.assertXpathValues(root, './ProjectSettings/pre_start_no_cell_path/text()', '')
        self.assertXpathValues(root, './ProjectSettings/pre_start_with_cell_path/text()', '')
        self.assertXpathValues(root, './ProjectSettings/measurements_path/text()', '')
        self.assertXpathValues(root, './ProjectSettings/calculation_mode/text()', 'PLL')

        self.assertXpathsUniqueValue(root, ('./leaf/@id',))
        self.assertXpathValues(root, './leaf/@active', ('on', 'off'))

    def testReadPyimdProject(self):

        settings = Settings()
        # Change a settings field
        settings.figure_format = 'pdf'
        # Save changes
        settings.write_pyimd_project(resource_path('TestConfig.xml'))
        # Change back to default
        settings.figure_format = 'png'
        # Observe change back to what was saved to file
        settings.read_pyimd_project(resource_path('TestConfig.xml'))

        expected_result = {'_figure_units': 'cm', '_figure_name_pre_start_with_cell': 'FitWithCellData',
                           '_calculation_mode': 'PLL', '_figure_name_measured_data': 'CalculatedCellMass',
                           '_pre_start_with_cell_path': '', '_measurements_path': '',
                           '_upper_parameter_bounds': [100.0, 5.0, 3, 3], '_conversion_factor_deg_to_rad': -57.3,
                           '_initial_parameter_guess': [70.0, 2.0, 0.0, 0.0], '_lower_parameter_bounds':
                               [10.0, 1.0, -3, -3], '_cantilever_length': 100, '_rolling_window_size': 1000,
                           '_figure_width': 56.44, '_conversion_factor_hz_to_khz': 1000.0,
                           '_figure_plot_every_nth_point': 1, '_project_folder_path': '', '_selected_files': [],
                           '_figure_resolution_dpi': 72, '_correct_for_frequency_offset': False,
                           '_frequency_offset_mode': 'Auto', '_frequency_offset_n_measurements_used': 1,
                           '_frequency_offset': 0, '_pre_start_no_cell_path': '', '_read_text_data_from_line': 23,
                           '_figure_name_pre_start_no_cell': 'FitNoCellData', '_text_data_delimiter': '\t',
                           '_spring_constant': 4.0, '_figure_format': 'pdf', '_cell_position': 5, '_figure_height':
                               45.16}

        self.assertEqual(settings.__dict__, expected_result)


if __name__ == "__main__":
    main()