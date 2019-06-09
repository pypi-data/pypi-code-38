import os
import sys
import glob
import patoolib
from patoolib import util
from .log import Logger

class ArchiveManager(object):
    '''
    Class to manage archiving and unarchiving of files.
    '''

    def __init__(self, path, filename):
        log_obj = Logger()
        self.logger_obj = log_obj.__get_logger__(path, filename)

    # -------------------------------------------------------------------------
    #    Args: format - string archive / unarchive format
    # Returns: flag - bool
    #    Desc: This function is used to check if the program to archive or 
    #          unarchive is present.
    # -------------------------------------------------------------------------
    def _check_program(self, format):
        '''
        Returns whether program to archive / unarchive exists
        '''
        self.logger_obj.info("Check if program exists for : {}".format(format))
        if util.find_program(format) is None:
            self.logger_obj.info("Unable to find relative programe")
            return False
        return True

    # -------------------------------------------------------------------------
    #    Args: fpath string path
    # Returns: flag - bool
    #    Desc: Check if path specified exists or not
    # -------------------------------------------------------------------------
    def check_source(self, fpath):
        self.logger_obj.info("Check if path exists {}".format(fpath))
        if not os.path.exists(fpath):
            self.logger_obj.info("path does not exists")
            return False
        return True

    # -------------------------------------------------------------------------
    #    Args: source_path string path to source file to extract
    #          destination_path string path where file needs to be extracted
    #         format - string  unarchive format
    # Returns: flag - bool
    #    Desc: Unarchive files of specified format from the source path
    # -------------------------------------------------------------------------
    def extract(self, source_path, destination_path, extension):

        if not self.check_source(source_path):
            return False

        if os.path.isfile(source_path) and (not source_path.endswith(extension)):
            self.logger_obj.info("Source file is not in the specified format")
            return False

        if not self.check_source(destination_path):
            self.logger_obj.info("Destination path does not exists")
            os.makedirs(destination_path)

        if not self._check_program(extension):
            return False

        if os.path.isdir(source_path):
            self.logger_obj.info("Source path is a directory {0} looking for files with \
                                 specified extension in directory  {1}".format(source_path, extension))
            file_list = glob.glob(os.path.join(source_path, "*{}".format(extension)))
            if len(file_list) == 0:
                self.logger_obj.info("No file exists with archive extension {}".format(extension))
                return False

            self.logger_obj.info("Extracting source files")
            for each in file_list:
                patoolib.extract_archive(archive=os.path.join(source_path, each), outdir=destination_path)
        else:
            self.logger_obj.info("Extracting source files")
            patoolib.extract_archive(archive=source_path, outdir=destination_path)

        return True

    # -------------------------------------------------------------------------
    #    Args: source_path string path to source file(s) to archive
    #          destination_path string path where file needs to be archived
    #         format - string  archive format
    # Returns: flag - bool
    #    Desc: Archive files of from the source path
    # -------------------------------------------------------------------------
    def archive(self, source_path, destination_path, archive_name, extension):

        if not self.check_source(source_path):
            return False

        if not self.check_source(destination_path):
            return False

        if not self._check_program(extension):
            return False

        if os.path.isdir(source_path):
            file_list = glob.glob(source_path)
        else:
            file_list = [source_path]

        self.logger_obj.info("Archiving source files")
        out_file = os.path.join(destination_path, archive_name)
        patoolib.create_archive(archive=out_file, filenames=file_list)

        return True
