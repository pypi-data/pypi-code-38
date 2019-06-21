#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Aug 13:43:21 2015
#



import os
from bob.bio.base import utils


@utils.Singleton
class FileSelector(object):
    """This class provides shortcuts for selecting different files for different stages of the snti-spoofing process.

    It communicates with the database and provides lists of file names for all steps of the tool chain.

    **Parameters:**

    database : :py:class:`bob.pad.base.database.PadDatabase` or derived.
      The database object that provides the list of files.

    preprocessed_directory : str
      The directory, where preprocessed data should be written to.

    extractor_file : str
      The filename, where the extractor should be written to (if any).

    extracted_directory : str
      The directory, where extracted features should be written to.

    projector_file : str
      The filename, where the projector should be written to (if any).

    projected_directory : str
      The directory, where projected features should be written to (if required).

    score_directories : (str, str)
      The directories, where score files for no-norm should be written to.


    default_extension : str
      The default extension of all intermediate files.

    compressed_extension : str
      The extension for writing compressed score files.
      By default, no compression is performed.

    """

    def __init__(
            self,
            database,
            preprocessed_directory,
            extractor_file,
            extracted_directory,
            projector_file,
            projected_directory,
            score_directories,
            default_extension='.hdf5',
            compressed_extension=''
    ):

        """Initialize the file selector object with the current configuration."""
        self.database = database
        self.extractor_file = extractor_file
        self.projector_file = projector_file

        self.score_directories = score_directories
        self.default_extension = default_extension
        self.compressed_extension = compressed_extension

        self.directories = {
            'original': database.original_directory,
            'preprocessed': preprocessed_directory,
            'extracted': extracted_directory,
            'projected': projected_directory
        }

    def get_paths(self, files, directory_type=None, combined=True):
        """Returns the lists of file names [real, attacks] for the given File objects."""
        try:
            directory = self.directories[directory_type]
        except KeyError:
            raise ValueError("The given directory type '%s' is not supported." % directory_type)

        # only one set of files
        if len(files) != 2:
            return self.database.file_names(files, directory, self.default_extension)
        realfiles = files[0]
        attackfiles = files[1]
        realpaths = self.database.file_names(realfiles, directory, self.default_extension)
        attackpaths = self.database.file_names(attackfiles, directory, self.default_extension)
        if combined:
            return realpaths + attackpaths
        else:
            return [realpaths, attackpaths]

    # List of files that will be used for all files
    def original_data_list(self, groups = None):
        """Returns the list of original ``PadFile`` objects that can be used for preprocessing."""
        files = self.database.all_files(groups=groups)
        if len(files) != 2:
            fileset = files
        else:
            fileset = files[0]+files[1]
        return fileset

    def original_directory_and_extension(self):
        """Returns the directory and extension of the original files."""
        return self.database.original_directory, self.database.original_extension

    def original_data_list_files(self, groups=None):
        """Returns the joint list of original (real and attack) data files that can be used for preprocessing."""
        fileset = self.original_data_list(groups=groups)
        return fileset, self.database.original_directory, self.database.original_extension

    def preprocessed_data_list(self, groups=None):
        """Returns the tuple of lists (real, attacks) of preprocessed data files."""
        return self.get_paths(self.database.all_files(groups=groups), "preprocessed")

    def feature_list(self, groups=None):
        """Returns the tuple of lists (real, attacks) of extracted feature files."""
        return self.get_paths(self.database.all_files(groups=groups), "extracted")

    def projected_list(self, groups=None):
        """Returns the tuple of lists (real, attacks) of projected feature files."""
        return self.get_paths(self.database.all_files(groups=groups), "projected")

    # Training lists
    def training_list(self, directory_type, step, combined=False):
        """
        Returns a list of lists (real, attacks) or just list of all real and
        attack features depending on combined that should be used for projector
        training. The directory_type might be any of 'preprocessed',
        'extracted', or 'projected'. The step might by any of
        'train_extractor', 'train_projector', or 'train_enroller'.
        """
        return self.get_paths(self.database.training_files(step), directory_type, combined)

    def toscore_objects(self, group):
        """Returns the File objects used to compute the raw scores."""
        # get the test files for all models
        return self.database.all_files(groups=(group,))

    def score_file_combined(self, group):
        """Returns the resulting score text file for the given group."""
        no_norm_dir = self.score_directories[0]
        return os.path.join(no_norm_dir, "scores-" + group) + self.compressed_extension

    def score_file_for_type(self, group, obj_type):
        """Returns the resulting score text file for the given group."""
        no_norm_dir = self.score_directories[0]
        return os.path.join(no_norm_dir, "scores-" + group + "-" + obj_type) + self.compressed_extension

    def annotation_list(self, groups=None):
        """Returns the list of annotations objects."""
        files = self.database.all_files(groups=groups)
        if len(files) != 2:
            return files
        else:
            return files[0] + files[1]

    def get_annotations(self, annotation_file):
        """Returns the annotations of the given file."""
        return self.database.annotations(annotation_file)
