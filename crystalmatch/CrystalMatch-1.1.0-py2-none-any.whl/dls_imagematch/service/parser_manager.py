from pkg_resources import require
require("numpy>=1.11.1")
require("scipy>=0.19.1")

import argparse
import logging
import re
import cv2
from os.path import split, exists, isdir, isfile, join, abspath, getmtime, dirname, expanduser

from os import listdir, makedirs, chmod

from CrystalMatch.dls_focusstack.focus.focus_stack_lap_pyramid import FocusStack
from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_imagematch.service import readable_config_dir
from CrystalMatch.dls_imagematch.version import VersionHandler
from CrystalMatch.dls_imagematch.service.readable_config_dir import ReadableConfigDir
from CrystalMatch.dls_util.shape import Point
from CrystalMatch.dls_util.imaging import Image

class ParserManager:

    LOG_DIR_PERMISSION = 0o777
    LOG_DIR_NAME = 'logs'
    LOG_FILE_NAME = 'log'
    FOCUSED_IMAGE_NAME = 'processed.tif'
    DEFAULT_SCRIPT_PATH = '.CrystalMatch'

    def __init__(self):
        self.parser = None
        self.images_to_stack = None
        self._script_path = None

    def build_parser(self):
        """Return an argument parser for the Crystal Matching service.
        :return: Argument parser.
        """
        parser = argparse.ArgumentParser(
            description="Run Crystal Matching algorithm attempting to translate co-ordinates "
                        "on an input image to the coordinate-space of an output image while "
                        "accounting for possible movement of crystals in the sample.")
        parser.add_argument('Formulatrix_image',
                            metavar="Formulatrix_image_path",
                            type=file,
                            help='Image file from the Formulatrix - selected_point should correspond to co-ordinates on '
                                 'this image.')
        parser.add_argument('beamline_stack_path',
                            metavar="beamline_stack_path",
                            help="A path pointing at a directory which stores images to be stacked or a path to a stacked image.")
        parser.add_argument('selected_points',
                            metavar="x,y",
                            nargs='*',
                            help="Comma-separated co-ordinates of selected points to be translated from the marked image "
                                 "to the target image.")
        parser.add_argument('-o','--output',
                           metavar="focused_image_path",
                           help="Specify directory for the stacked image. "
                                "A file called 'processed.tif' will be created in the directory."
                                "'processed.tif' will be created in log directory if this is not set.")
        parser.add_argument('--config',
                            metavar="path",
                            action=ReadableConfigDir,
                            default=join(self.get_script_path(), readable_config_dir.CONFIG_DIR_NAME),
                            help="Sets the configuration directory.")
        parser.add_argument('--scale',
                            metavar="scale",
                            help="The scale between the Formulatrix and beamline image given as the resolution of each "
                                 "image separated by a colon. Note this is relative (1:2 is the same as 2:4) and a value "
                                 "must be specified for each image using the format "
                                 "'[Formulatrix_image_resolution]:[beamline_image_resolution]'.")
        parser.add_argument('-j', '--job',
                            metavar="job_id",
                            help="Specify a job_id - this will be reported in the output to help identify this run.")
        parser.add_argument('--to_json',
                            action='store_true',
                            help="Output a JSON object.")
        parser.add_argument('--version',
                            action='version',
                            version=VersionHandler.version_string())
        parser.add_argument('--log',
                            metavar="path",
                            help="Write log files to the directory specified by path.")
        self.parser = parser

    def get_args(self):
        return self.parser.parse_args()

    def get_config_dir(self):
        config_directory = self.get_args().config
        if config_directory is None:
            config_directory = abspath(join(self.get_script_path(), readable_config_dir.CONFIG_DIR_NAME))
        return abspath(config_directory)

    def get_scale_override(self):
        scale =  self.get_args().scale
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())

        if scale is not None:
            try:
                scales = scale.split(":")
                assert (len(scales) == 2)
                return float(scales[0]), float(scales[1])
            except AssertionError:
                log.error(AssertionError("Scale flag requires two values separated by a colon':'. Value given: " +
                                         str(scale)))
                raise AssertionError("Scale flag requires two values separated by a colon':'. Value given: " +
                                     str(scale))

            except ValueError:
                log.error("Scale must be given as a pair of float values separated by a colon (':'). Value given: " +
                          str(scale))
                raise ValueError(
                    "Scale must be given as a pair of float values separated by a colon (':'). Value given: " +
                    str(scale))
        return None

    def parse_selected_points_from_args(self):
        """Parse the selected points list provided by the command line for validity and returns a list of Point objects.
        :param args: Command line arguments provided by argument parser - must contain 'selected_points'
        :return: List of Selected Points.
         """
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        selected_points = []
        if self.get_args().selected_points:
            point_expected_format = re.compile("[0-9]+,[0-9]+")
            sel_points = self.get_args().selected_points
            for point_string in self.get_args().selected_points:
                point_string = point_string.strip('()')
                match_results = point_expected_format.match(point_string)
                # Check the regex matches the entire string
                # DEV NOTE: can use re.full_match in Python v3
                if match_results is not None and match_results.span()[1] == len(point_string):
                    x, y = map(int, point_string.strip('()').split(','))
                    selected_points.append(Point(x, y))
                else:
                    log.warning("Selected point with invalid format will be ignored - '" + point_string + "'")
        return selected_points

    def get_focused_image(self):
        focusing_path = abspath(self.get_args().beamline_stack_path)
        if "." not in focusing_path:
            files = self._sort_files_according_to_names(focusing_path)
            # Run focusstack
            stacker = FocusStack(files, self.get_args().config)
            focused_image = stacker.composite()

            self.images_to_stack = stacker.get_fft_images_to_stack()
        else:
            focused_image = Image(cv2.imread(focusing_path))
        return focused_image

    def get_fft_images_to_stack(self):
        return self.images_to_stack

    def get_formulatrix_image_path(self):
        path = self.get_args().Formulatrix_image.name
        self._check_is_file(path)
        return path

    def get_to_json(self):
        return self.get_args().to_json

    def get_job_id(self):
        return self.get_args().job

    # returns an error if the focused image is not saved
    # may want to change this for saving done later
    def get_focused_image_path(self):
        focusing_path = abspath(self.get_args().beamline_stack_path)
        if "." not in focusing_path:
            focusing_path =  self.get_out_file_path()
        self._check_is_file(focusing_path)
        return abspath(focusing_path)

    def save_focused_image(self, image):
        image.save(self.get_out_file_path())

    def get_out_file_path(self):
        """
         Get the path to the output file based on the contents of the config file and the location of the configuration dir.
         :return: A string representing the file path of the log file.
         """
        dir_path = self._get_output_dir()
        self._check_make_dirs(dir_path)
        return join(dir_path, self.FOCUSED_IMAGE_NAME)

    def get_log_file_path(self):
        """
        Get the path to the log file based on the contents of the config file and the location of the configuration dir.
        :return: A string representing the file path of the log file.
        """
        dir_path = self._get_log_file_dir()
        self._check_make_dirs(dir_path)
        return join(dir_path, self.LOG_FILE_NAME)

    def _get_output_dir(self):
        out = self.get_args().output
        if out is None:
            # default - log file directory
            default_output_path = self._get_log_file_dir()
            return default_output_path
        return abspath(self.get_args().output)

    def _get_log_file_dir(self):
        l = self.get_args().log
        if l is None:
            # DEV NOTE: join and abspath used over split due to uncertainty over config path ending in a slash
            default_log_path =abspath(join(self.get_script_path(), self.LOG_DIR_NAME))
            return default_log_path
        return abspath(self.get_args().log)

    def _check_make_dirs(self, directory):
        if not exists(directory) or not isdir(directory):
            log = logging.getLogger(".".join([__name__]))
            log.addFilter(logconfig.ThreadContextFilter())
            try:
                makedirs(directory)
                chmod(directory, self.LOG_DIR_PERMISSION)
                log.info("Directory created: " + directory)
            except OSError:
                log.error("Could not create find/create directory, path may be invalid: " + directory)
                exit(1)

    @staticmethod
    def _check_is_file(path):
        if not isfile(path):
            log = logging.getLogger(".".join([__name__]))
            log.addFilter(logconfig.ThreadContextFilter())
            log.error("Could not find the file, file may not been saved: " + path)
            exit(1)

    @staticmethod
    def _sort_files_according_to_names(focusing_path):
        files = []
        file_names = listdir(focusing_path)
        file_names.sort(key=lambda f: int(filter(str.isdigit, f)))
        for file_name in file_names:
            name = join(focusing_path, file_name)
            files.append(file(name))
        return files

    def set_script_path(self, path):
        new_path = self._if_egg_use_home(path)
        self._script_path = new_path

    def get_script_path(self):
        return self._script_path

    def _if_egg_use_home(self, path):
        new_path = abspath(join(path, '..'))
        if ".egg" in new_path:
            home = expanduser("~")
            new_path = abspath(join(home, self.DEFAULT_SCRIPT_PATH))
            if not exists(new_path):
                makedirs(new_path)

        return new_path