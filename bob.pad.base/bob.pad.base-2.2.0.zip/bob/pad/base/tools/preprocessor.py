#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Aug 13:43:21 2015
#


import bob.io.base
import os

import logging

from .FileSelector import FileSelector
from bob.bio.base import utils
from bob.bio.base.tools import read_preprocessed_data

logger = logging.getLogger("bob.pad.base")


def preprocess(preprocessor, groups=None, indices=None, allow_missing_files=False, force=False):
    """Preprocesses the original data of the database with the given preprocessor.

    The given ``preprocessor`` is used to preprocess all data required for the current experiment.
    It writes the preprocessed data into the directory specified by the :py:class:`bob.pad.base.tools.FileSelector`.
    By default, if target files already exist, they are not re-created.

    **Parameters:**

    preprocessor : py:class:`bob.bio.base.preprocessor.Preprocessor` or derived
      The preprocessor, which should be applied to all data.

    groups : some of ``('train', 'dev', 'eval')`` or ``None``
      The list of groups, for which the data should be preprocessed.

    indices : (int, int) or None
      If specified, only the data for the given index range ``range(begin, end)`` should be preprocessed.
      This is usually given, when parallel threads are executed.

    allow_missing_files : bool
      If set to ``True``, files for which the preprocessor returns ``None`` are silently ignored.

    force : bool
      If given, files are regenerated, even if they already exist.
    """
    if not preprocessor.writes_data:
        # The preprocessor does not write anything, so no need to call it
        logger.info(
            "Skipping preprocessing as preprocessor does not write any data")
        return

    # the file selector object
    fs = FileSelector.instance()

    # get the file lists
    data_files = fs.original_data_list(groups=groups)
    original_directory, original_extension = fs.original_directory_and_extension()
    preprocessed_data_files = fs.preprocessed_data_list(groups=groups)

    # select a subset of keys to iterate
    if indices is not None:
        index_range = range(indices[0], indices[1])
        logger.info(
            "- Preprocessing: splitting of index range %s", str(indices))
    else:
        index_range = range(len(data_files))

    logger.info("- Preprocessing: processing %d data files from directory '%s' to directory '%s'",
                len(index_range), fs.directories['original'], fs.directories['preprocessed'])

    # read annotation files
    annotation_list = fs.annotation_list(groups=groups)

    # iterate over the selected files
    for i in index_range:
        preprocessed_data_file = preprocessed_data_files[i]
        file_object = data_files[i]
        file_name = file_object.make_path(
            original_directory, original_extension)

        # check for existence
        if not utils.check_file(preprocessed_data_file, force,
                                preprocessor.min_preprocessed_file_size):
            logger.debug("... Processing original data file '%s'", file_name)
            data = preprocessor.read_original_data(
                file_object, original_directory, original_extension)
            # create output directory before reading the data file (is
            # sometimes required, when relative directories are specified,
            # especially, including a .. somewhere)
            bob.io.base.create_directories_safe(
                os.path.dirname(preprocessed_data_file))

            # get the annotations; might be None
            annotations = fs.get_annotations(annotation_list[i])

            # call the preprocessor
            preprocessed_data = preprocessor(data, annotations)
            if preprocessed_data is None:
                if allow_missing_files:
                    logger.debug(
                        "... Processing original data file '%s' was not successful", file_name)
                    continue
                else:
                     raise RuntimeError(
                        "Preprocessing of file '%s' was not successful", file_name)

            # write the data
            preprocessor.write_data(preprocessed_data, preprocessed_data_file)

        else:
            logger.debug("... Skipping original data file '%s' since preprocessed data '%s' exists",
                         file_name, preprocessed_data_file)
