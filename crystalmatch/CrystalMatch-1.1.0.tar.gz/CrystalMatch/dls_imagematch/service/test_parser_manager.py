from pkg_resources import require
require("mock>=1.0.1")
import unittest
from os import remove, rmdir

import numpy as np
from os.path import join, isfile, split, abspath, exists, dirname
import shutil

from mock import Mock

from CrystalMatch.dls_imagematch.service.parser_manager import ParserManager
from CrystalMatch.dls_util.imaging import Image


class TestParserManager(unittest.TestCase):

    def setUp(self):
        self.pm = ParserManager()
        path = join(dirname(abspath(__file__)), '..')
        self.pm.set_script_path(path)

    def tearDown(self):
        # make sure the default destination does not contain processed file
        self.pm.get_args = Mock(return_value=Mock(output=None, log=None, config="test_config"))
        default_path = self.pm.get_out_file_path()
        try:
            remove(default_path)
        except:
            pass

    @classmethod
    def tearDownClass(self):
        pm = ParserManager()
        pm.set_script_path('test')
        pm.get_args = Mock(return_value=Mock(output=None, log=None, config="test_config"))
        default_log_path = pm._get_log_file_dir()
        config = pm.get_config_dir()
        default_script_path = pm.DEFAULT_SCRIPT_PATH
        try:
            shutil.rmtree(default_log_path)
            shutil.rmtree(config)
            shutil.rmtree(default_script_path)
        except:
            pass

    def test_build_parer_creates_parser_object(self):
        self.assertIsNone(self.pm.parser)
        self.pm.build_parser()
        self.assertIsNotNone(self.pm.parser)

    def test_get_config_returns_default_config_directory_when_config_directory_is_not_specified(self):
        self.pm.get_args = Mock(return_value=Mock(config=None)) #!! return value has to be a mock with particular parameters
        config_dir = self.pm.get_config_dir()
        default_config_dir = abspath(join(self.pm.get_script_path(), 'config'))
        self.assertEquals(config_dir, default_config_dir)

    def test_get_config_returns_whatever_is_specified_as_config(self):
        test_string = 'ble'
        self.pm.get_args = Mock(return_value=Mock(config=test_string))
        self.assertIn(test_string, self.pm.get_config_dir())

    def test_get_scale_override_returns_None_if_not_set(self):
        self.pm.get_args = Mock(return_value=Mock(scale=None))
        self.assertIsNone(self.pm.get_scale_override())

    def test_get_scale_override_returns_scale_when_set_correctly(self):
        correct_scale = "2.0:3.0"
        self.pm.get_args = Mock(return_value=Mock(scale=correct_scale))
        self.assertEquals(self.pm.get_scale_override(), (float(2),float(3)))

    def test_get_scale_override_raises_assertion_error_when_scale_element_divided_by_coma(self):
        bad_scale = "20,3"
        self.pm.get_args = Mock(return_value=Mock(scale=bad_scale))

        with (self.assertRaises(AssertionError)):
            self.pm.get_scale_override()

    def test_get_scale_override_raises_assertion_error_when_only_one_element(self):
        bad_scale = ":3"
        self.pm.get_args = Mock(return_value=Mock(scale=bad_scale))

        with (self.assertRaises(ValueError)):
            self.pm.get_scale_override()

    def test_parse_selected_point_returns_empty_array_when_no_points_specified(self):
        self.pm.get_args = Mock(return_value=Mock(selected_points=None))
        self.assertEquals(self.pm.parse_selected_points_from_args(), [])

    def test_parse_selected_point_ignores_point_with_invalid_format(self):
        points_invalid_format = "2:4 4:5"
        self.pm.get_args = Mock(return_value=Mock(selected_points=points_invalid_format))
        self.assertEquals(self.pm.parse_selected_points_from_args(),[])

    def test_parse_selected_points_creates_list_of_points_when_the_format_is_valid(self):
        valid_format = ['1800,1690']
        self.pm.get_args = Mock(return_value=Mock(selected_points=valid_format))
        points = self.pm.parse_selected_points_from_args()
        self.assertEquals(len(points), 1)

    #ten
    def test_get_focused_image_returns_an_instance_of_image_when_single_image_path_is_passed(self):
        path = 'system-tests/resources/stacking/ideal.tif'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path))
        im = self.pm.get_focused_image()
        self.assertIsInstance(im, Image)
        self.assertGreater(im.size(), 0)

    #ten
    def test_get_focused_image_returns_an_instance_of_image_when_directory_path_is_passed(self):
        path = 'system-tests/resources/stacking/levels'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path, config="test_config"))
        im = self.pm.get_focused_image()
        self.assertIsInstance(im, Image)
        self.assertGreater(im.size(), 0)

    #ten
    def test_sort_files_according_to_names(self):
        path = 'system-tests/resources/stacking/levels'
        files = ParserManager._sort_files_according_to_names(path)
        self.assertIn('FL0', files[0].name)
        self.assertIn('FL10', files[-1].name)

    #ten
    def test_get_focused_image_path_when_beamline_image_path_points_to_file(self):
        path = 'system-tests/resources/stacking/ideal.tif'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path))
        result_path = self.pm.get_focused_image_path()
        self.assertIn('ideal.tif', result_path)

    def test_get_focused_image_path_when_beamline_image_path_points_to_dictionary_and_file_saved(self):
        path = 'levels'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path, output=None, log=None, config="test_config"))
        self.pm._check_is_file = Mock() # mute check_is_file
        result_path = self.pm.get_focused_image_path()
        self.assertIn('processed.tif', result_path)#def when output and log are none

    def test_get_focused_image_path_throws_exp_when_beamline_image_path_points_to_dictionary_and_file_not_saved(self):
        path = 'levels'
        self.pm.get_args = Mock(
            return_value=Mock(beamline_stack_path=path, output=None, log=None, config="test_config"))
        with (self.assertRaises(SystemExit)):
            self.pm.get_focused_image_path()


    def test_get_focused_image_path_beamline_image_path_points_to_nonexisting_file(self):
        path = 'ideal_gost.tif'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path))
        with (self.assertRaises(SystemExit)):
           self.pm.get_focused_image_path()

    def test_save_function_saves_image_in_a_default_destination(self):
        self.pm.get_args = Mock(return_value=Mock(output=None, log=None, config="test_config"))
        default_path = self.pm.get_out_file_path()
        self.assertFalse(isfile(default_path))
        self.pm.save_focused_image(Image(np.zeros((3, 3),dtype=np.uint8)))
        self.assertTrue(isfile(default_path))

    def test_get_out_file_path_returns_path_to_output_file_called_processed(self):
        self.pm.get_args = Mock(return_value=Mock(output=None, log=None, config="test_config"))
        path = self.pm.get_out_file_path()
        head, tail = split(path)
        self.assertEquals(tail, self.pm.FOCUSED_IMAGE_NAME)

    def test_log_file_path_returns_path_to_log_file_called_log(self):
        self.pm.get_args = Mock(return_value=Mock(output=None, log=None, config="test_config"))
        path = self.pm.get_log_file_path()
        head, tail = split(path)
        self.assertEquals(tail, self.pm.LOG_FILE_NAME)

    def test_get_log_file_dir_returnes_defualt_when_log_parameter_not_set(self):
        self.pm.get_args = Mock(return_value=Mock(log=None, config="test_config"))
        log_dir = self.pm._get_log_file_dir()
        default_log_dir = abspath(join(self.pm.get_script_path(), 'logs'))

        self.assertEquals(log_dir, default_log_dir)


    def test_get_log_file_dir_uses_location_specified_by_parameter_log(self):
        self.pm.get_args = Mock(return_value=Mock(log='test_dir', config="test_config"))
        log_dir = self.pm._get_log_file_dir()
        head, tail = split(log_dir)
        self.assertEquals(tail, 'test_dir')
        self.assertEquals(abspath('.'), head )

    def test_get_output_dir_uses_location_specified_by_parameter_output(self):
        self.pm.get_args = Mock(return_value=Mock(output='out_dir'))
        out_dir = self.pm._get_output_dir()
        head, tail = split(out_dir)
        self.assertEquals(tail, 'out_dir')
        self.assertEquals(abspath('.'), head)

    def test_get_output_dir_is_log_file_dir_if_parameter_out_not_specified(self):
        self.pm.get_args = Mock(return_value=Mock(output=None, log='hoho'))
        out_dir = self.pm._get_output_dir()
        log_file_dir = self.pm._get_log_file_dir()
        head, tail = split(out_dir)
        self.assertEquals(tail, 'hoho')
        self.assertEquals(out_dir, log_file_dir)

    def test_check_is_file_raises_system_exit_when_no_file(self):
        with (self.assertRaises(SystemExit)):
            self.pm._check_is_file('nofile.tif')

    def test_check_make_dirs_creates_new_directory_if_does_not_exist(self):
        self.pm.get_args = Mock()
        try:
            rmdir('new')
        except: pass
        self.pm._check_make_dirs('new')
        self.assertTrue(exists('new'))
        rmdir('new')
        self.assertFalse(exists('new'))

    def test_if_egg_use_home_creates_new_directory(self):
        path = abspath("site-packages/CrystalMatch-v1.0.0-py2.7.egg/CrystalMatch/")
        new_path = self.pm._if_egg_use_home(path)
        self.assertTrue(exists(new_path))
        self.assertTrue(".CrystalMatch" in new_path)

    def test_get_log_file_dir_returns_CrystalMatch_when_log_parameter_not_set_and_running_form_egg(self):
        pm = ParserManager()
        path = "site-packages/CrystalMatch-v1.0.0-py2.7.egg/CrystalMatch/"
        pm.set_script_path(path)
        pm.get_args = Mock(return_value=Mock(log=None, config="test_config"))
        log_dir = pm._get_log_file_dir()
        self.assertTrue(".CrystalMatch" in log_dir)
        default_log_dir = abspath(join(pm.get_script_path(), 'logs'))
        self.assertEquals(log_dir, default_log_dir)

    def test_get_config_returns_CrystalMatch_when_config_directory_is_not_specified_and_running_from_egg(self):
        pm = ParserManager()
        path = "site-packages/CrystalMatch-v1.0.0-py2.7.egg/CrystalMatch/"
        pm.set_script_path(path)
        pm.get_args = Mock(return_value=Mock(config=None))
        config_dir = pm.get_config_dir()
        self.assertTrue(".CrystalMatch" in config_dir)
        default_config_dir = abspath(join(pm.get_script_path(), 'config'))
        self.assertEquals(config_dir, default_config_dir)
