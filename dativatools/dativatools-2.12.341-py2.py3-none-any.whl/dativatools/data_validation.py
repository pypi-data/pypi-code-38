import glob
import os
import re
import sys
from datetime import datetime, timedelta
from .log import Logger


class DataValidation(object):
    '''
    DataValidation class, contains the methods to validate the
    files sizes, count, names, extension at specified location.
    Expected source_name dictionary:
        source_name = {
                        'folder_name': {
                            'date_range': [], # Range of dates for expected files
                            'expected_extension': '', # Extension of files
                            'expected_filenames': '', # File prefix
                            'file_count_threshold': [], # Range in which file count should be
                            'max_sizes': [], # Max limit of file
                            'min_sizes': [], # Min limit of file
                            'other_expected_files': [], # Files to ignore if present
                            'path': '', # folder path
                            'processing_date': '' # Date of folder for checking
                        }
                    }
    '''

    def __init__(self, source_name, log_path='', log_filename='', logger_obj=None):
        self.source_name = source_name
        self.file_list = self.get_req_files_in_dir()
        if log_path and log_filename:
            log_obj = Logger()
            self.logger_obj = log_obj.__get_logger__(log_path, log_filename)
        elif logger_obj:
            self.logger_obj = logger_obj

    # -------------------------------------------------------------------------
    #    Name: get_all_in_dir()
    #    Returns: list of files
    #    Desc: method called within the class to get all the files
    #          in the specified directory.
    # -------------------------------------------------------------------------
    def get_all_in_dir(self):
        path = self.source_name['path']
        return glob.glob(os.path.join(path, '*'))

    # -------------------------------------------------------------------------
    #    Name: get_req_files_in_dir()
    #    Returns: list of sorted files
    #    Desc: method called within the class to get the files
    #          with the expected filenames from the specified directory.
    # -------------------------------------------------------------------------
    def get_req_files_in_dir(self):
        path = self.source_name['path']
        expected_filenames = self.source_name['expected_filenames']
        file_list = glob.glob(os.path.join(path, expected_filenames))
        file_list.sort()
        return file_list

    # -------------------------------------------------------------------------
    #    Name: check_name()
    #    Returns: flag
    #    Desc: Check if the files with the expected filenames are present in the
    #          specified directory.
    # -------------------------------------------------------------------------
    def check_name(self):
        file_list = self.file_list
        if file_list:
            self.logger_obj.info(file_list, "Expected filenames found in directory", status = "completed")
            return True
        else:
            self.logger_obj.exception("No files of expected filenames found in directory")
            return False

    # -------------------------------------------------------------------------
    #    Name: check_extra_files()
    #    Returns: flag and list of extra files
    #    Desc: Given a directory location, get files with the expected filenames,
    #          also get all the files present in the directory. chck if there is a
    #          difference between the two list of files, if there is check if other
    #          files are expected at location, if no the return False else check if
    #          the extra files are with specified names.
    # -------------------------------------------------------------------------
    def check_extra_files(self):
        all_files = self.get_all_in_dir()
        file_list = self.file_list
        if not file_list:
            self.logger_obj.exception("No files names with specified names found in the directory.")
            return False, file_list
        add_file = set(all_files) - set(file_list)
        add_file = list(add_file)
        expected_other_files = self.source_name['other_expected_files']
        extra_files = []
        if add_file and not expected_other_files:
            self.logger_obj.exception("The following extra items were found in the directory {0}".format(str(add_file)))
            return False, add_file
        elif add_file:
            # check additional files with the other expected filenames
            for extras in add_file:
                extra_name = os.path.basename(extras)

                '''
                matches will be a list containing the integer 1 if the filename
                matches with the other specified expected filenames or else it will
                a blank list
                '''
                matches = [1 for foo in expected_other_files if extra_name.startswith(foo)]
                if not matches:
                    extra_files.append(extras)
        if extra_files:
            self.logger_obj.exception("The following extra items were found in the directory {0}".format(str(extra_files)))
            return False, extra_files
        else:
            self.logger_obj.info(file_list, "No extra files were found in directory", status="completed")
            return True, extra_files

    # -------------------------------------------------------------------------
    #    Name: check_date()
    #    Returns: flag and list of files whose date is out of range
    #    Desc: Given a directory location, get the files with expected filenames from the
    #          directory, look for a date in their filenames and
    #          check if that date is within the expected daterange.
    # -------------------------------------------------------------------------
    def check_date(self):
        file_list = self.file_list
        if not file_list:
            self.logger_obj.exception("No files names with specified names found in the directory.")
            return False, file_list
        date_range = self.source_name['date_range']
        processing_date = datetime.strptime(self.source_name['processing_date'], self.source_name['date_format'])
        start_day = processing_date + timedelta(date_range[0])
        end_day = processing_date + timedelta(date_range[1])
        out_of_daterange_files = []
        for each in file_list:
            file_name = os.path.basename(each)
            file_date = re.search("([0-9]{8})", file_name).group(0)
            file_date = datetime.strptime(file_date, self.source_name['date_format'])
            if start_day <= file_date <= end_day:
                pass
            else:
                out_of_daterange_files.append(file_name)
        if out_of_daterange_files:
            self.logger_obj.exception("The following files are out of the expected date range {0}".format(str(out_of_daterange_files)))
            return False, out_of_daterange_files
        else:
            self.logger_obj.info(file_list, "All files are within the expected date range", status="completed")
            return True, out_of_daterange_files

    # -------------------------------------------------------------------------
    #    Name: check_size()
    #    Returns: flag and list of files whose sizes out of threshold
    #    Desc: Given a directory location, get the files with the expected filenames from the
    #    location and check if their sizes fall within the prescribed thresholds, this works
    #    if only one min and max size is specified and also if multiple min and max sizes are prescribed.
    #    If multiple file sizes are prescribed the number of sizes specified should be equal to the
    #    count of files expected at location.
    # -------------------------------------------------------------------------
    def check_size(self):
        file_list = self.file_list
        if not file_list:
            self.logger_obj.exception("No files names with specified names found in the directory.")
            return False, file_list
        min_sizes = self.source_name['min_sizes']
        max_sizes = self.source_name['max_sizes']
        if not (len(min_sizes) == len(max_sizes)):
            self.logger_obj.exception('Mismatch in the length of arrays for minimum and maximum size thresholds')
            return False, file_list
        size_out_of_threshold_files = []
        if len(min_sizes) == 1:
            for each in file_list:
                size_out_of_threshold_files.extend(DataValidation.check_size_helper(each, min_sizes[0], max_sizes[0]))
        else:
            for key, value in enumerate(file_list):
                size_out_of_threshold_files.extend(DataValidation.check_size_helper(value, min_sizes[key], max_sizes[key]))
        if size_out_of_threshold_files:
            self.logger_obj.exception("The following files had sizes outside the threshold {0}".format(str(size_out_of_threshold_files)))
            return False, size_out_of_threshold_files
        else:
            self.logger_obj.info(file_list, "All files at location were of expected size", status="completed")
            return True, size_out_of_threshold_files

    # -------------------------------------------------------------------------
    #    Name: check_size_helper()
    #    Args: file_name : name of single file
    #          min_threshold : minimum expected size
    #          max_threshold : maximum expected size
    #    Returns: list : Empty if within threshold else list of file names
    #    Desc: Helper method for check size method to check if the size of file is
    #          within the expected minimum and maximum sizes.
    # -------------------------------------------------------------------------
    @staticmethod
    def check_size_helper(file_name, min_threshold, max_threshold):
        file_size = os.path.getsize(file_name)
        if min_threshold <= file_size <= max_threshold:
            return []
        else:
            return [file_name]

    # -------------------------------------------------------------------------
    #    Name: check_file_count()
    #    Returns: flag and count of files
    #    Desc: Given a folder location, fetch the files with expected files names
    #          and check if the count of files are within the expected threshold.
    # -------------------------------------------------------------------------
    def check_file_count(self):
        file_list = self.file_list
        count_of_files = len(file_list)
        file_count_threshold = self.source_name['file_count_threshold']
        if file_count_threshold[0] <= count_of_files <= file_count_threshold[1]:
            self.logger_obj.info(file_list, 'count of files are within the expected threshold.', status="completed")
            return True, count_of_files
        else:
            self.logger_obj.exception("Count of files, {0}, is not within the prescribed threshold, "
                               "{1} and {2}.".format(count_of_files, file_count_threshold[0],
                                                     file_count_threshold[1]))
            return False, count_of_files

    # -------------------------------------------------------------------------
    #    Name: check_file_extension()
    #    Returns: flag and list of files with unexpected extension
    #    Desc: Given a folder location, fetch the files with expected filenames are within the
    #          folder, and check if the extension mathches the expected extension.
    # -------------------------------------------------------------------------
    def check_file_extension(self):
        file_list = self.file_list
        if not file_list:
            self.logger_obj.exception("No files names with specified names found in the directory.")
            return False, file_list
        expected_extension = self.source_name['expected_extension']
        files_unexpected_ext = []
        for each in file_list:
            if not each.endswith(expected_extension):
                files_unexpected_ext.append(each)

        if files_unexpected_ext:
            self.logger_obj.exception("The following files at specified location"
                               "were with with unexpected extension {0}".format(str(files_unexpected_ext)))
            return False, files_unexpected_ext
        else:
            self.logger_obj.info(file_list, "All files at specified path are with expected extension.", status="completed")
            return True, files_unexpected_ext
