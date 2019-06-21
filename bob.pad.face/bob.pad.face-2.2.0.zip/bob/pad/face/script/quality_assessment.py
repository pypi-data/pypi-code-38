#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is designed to assess the quality of the data(images, videos, etc.)
in the user-defined folder and split/copy the data into two folders
according to their quality.

Good quality data will be copied to ``<save_path>/good_quality_data/`` folder,
respectively "low"  quality to ``<save_path>/low_quality_data/`` folder.

The data loading and quality assessment functionality are defined in the
configuration file. The config file MUST contain at least the following
functions:

``load_datafile(file_name)`` - returns the ``data`` given ``file_name``, and

``assess_quality(data, **assess_quality_kwargs)`` - returns ``True`` for good
quality ``data``, and ``False`` for low quality data, and

``assess_quality_kwargs`` - a dictionary with kwargs for ``assess_quality()``
function.

@author: Olegs Nikisins
"""
# =============================================================================
# Import here:

import argparse
import importlib
import os
from shutil import copyfile


# =============================================================================
def parse_arguments(cmd_params=None):
    """
    Parse command line arguments.

    **Parameters:**

    ``cmd_params``: []
        An optional list of command line arguments. Default: None.

    **Returns:**

    ``data_folder``: py:class:`string`
        A directory containing the data to be used in quality assessment.

    ``save_folder``: py:class:`string`
        A directory to save the results to. Two sub-folders will be created
        here: ``good_quality_data``, and ``low_quality_data``.

    ``file_extension``: py:class:`string`
        An extension of the data files.
        Default: ``.hdf5``.

    ``relative_mod_name``: py:class:`string`
        Relative name of the module to import configurations from.
        Default: ``celeb_a/quality_assessment_config.py``.

    ``config_group``: py:class:`string`
        Group/package name containing the configuration file.
        Default: ``bob.pad.face.config.quality_assessment``.

    ``verbosity``: py:class:`int`
        Verbosity level.
    """

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("data_folder", type=str,
                        help="A directory containing the data to be used in quality assessment.")

    parser.add_argument("save_folder", type=str,
                        help="A directory to save the results to. "
                        "Two sub-folders will be created here: good_quality_data, and low_quality_data.")

    parser.add_argument("-e", "--file-extension", type=str, help="An extension of the data files.",
                        default = ".hdf5")

    parser.add_argument("-c", "--config-file", type=str, help="Relative name of the config file containing "
                        "quality assessment function, and data loading function.",
                        default = "celeb_a/quality_assessment_config.py")

    parser.add_argument("-cg", "--config-group", type=str, help="Name of the group, where config file is stored.",
                        default = "bob.pad.face.config.quality_assessment")

    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="Only -v level is currently supported.")

    if cmd_params is not None:
        args = parser.parse_args(cmd_params)
    else:
        args = parser.parse_args()

    data_folder = args.data_folder
    save_folder = args.save_folder

    file_extension = args.file_extension
    config_file = args.config_file
    config_group = args.config_group

    verbosity = args.verbosity

    relative_mod_name = '.' + os.path.splitext(config_file)[0].replace(os.path.sep, '.')

    return data_folder, save_folder, file_extension, relative_mod_name, config_group, verbosity


# =============================================================================
def get_all_filenames_for_path_and_extension(path, extension):
    """
    Get all filenames with specific extension in all subdirectories of the
    given path

    **Parameters:**

    ``path`` : str
        String containing the path to directory with files.

    ``extension`` : str
        Extension of the files.

    **Returns:**

    ``all_filenames`` : [str]
        A list of selected absolute filenames.
    """

    all_filenames = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                 all_filenames.append(os.path.join(root, file))

    return all_filenames


# =============================================================================
def copy_file(file_name, data_folder, save_folder):
    """
    Copy the file from from source to destanation.

    **Parameters:**

    ``file_name`` : str
        Absolute name of the file to be copied.

    ``data_folder`` : str
        Folder containing all data files.

    ``save_folder`` : str
        Folder to copy the results to.
    """

    # absolute name of the destanation file:
    save_filename = os.path.join(save_folder ,file_name.replace( data_folder, "" ))

    # make the folders to save the file to:
    dst_folder = os.path.split(save_filename)[0]
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    copyfile(file_name, save_filename)


# =============================================================================
def main(cmd_params=None):
    """
    The following steps are performed in this function:

    1. The command line arguments are first parsed.

    2. Folder to save the results to is created.

    3. Configuration file specifying the quality function, and data loading
       functionality, is loaded.

    4. All files in data folder with specified extension are obtained.

    5. Data is loaded and quality is computed for each data sample.

    6. Good quality samples are coppied to <save_folder>/good_quality_data
       folder, low quality to <save_folder>/low_quality_data.

    NOTE:
    The config file used in this function MUST contain at least the following
    functions:

    ``load_datafile(file_name)`` - returns the ``data`` given ``file_name``,
    and

    ``assess_quality(data, **assess_quality_kwargs)`` - returns ``True``
    for good quality ``data``, and ``False`` for low quality data, and

    ``assess_quality_kwargs`` - a dictionary with kwargs for
    ``assess_quality()`` function.
    """

    # Parse the command line arguments:
    data_folder, save_folder, file_extension, relative_mod_name, config_group, verbosity = \
                                parse_arguments(cmd_params = cmd_params)

    # Create the directories:
    good_quality_folder = os.path.join(save_folder, "good_quality_data")
    low_quality_folder = os.path.join(save_folder, "low_quality_data")

    if not os.path.exists(good_quality_folder):
        os.makedirs(good_quality_folder)

    if not os.path.exists(low_quality_folder):
        os.makedirs(low_quality_folder)

    # Load the configuretion file:
    config_module = importlib.import_module(relative_mod_name, config_group)

    # Obtain a list of data files:
    all_filenames = get_all_filenames_for_path_and_extension(data_folder,
                                                             file_extension)

    if verbosity > 0:
        print( "The number of files to process: {}".format( len( all_filenames ) ) )

    for idx, file_name in enumerate(all_filenames):

        data = config_module.load_datafile(file_name)

        quality_flag = config_module.assess_quality(data, **config_module.assess_quality_kwargs)

        if quality_flag:

            copy_file(file_name, data_folder, good_quality_folder)

            if verbosity > 0:
                print("Good quality sample copied. {} out of {} samples processed.".format(idx, len(all_filenames)))

        else:

            copy_file(file_name, data_folder, low_quality_folder)

            if verbosity > 0:
                print("Bad quality sample copied. {} out of {} samples processed.".format(idx, len(all_filenames)))

    if verbosity > 0:
        print("Done!")
