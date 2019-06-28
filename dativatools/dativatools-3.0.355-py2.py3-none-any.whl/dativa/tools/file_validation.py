from copy import deepcopy
from datetime import datetime
import glob
import logging
import os
from dativa.tools.aws.s3_lib import S3Location, S3ClientError, S3Client
from dativa.tools.pandas import date_time as dativa_date_time

try:
    import boto3
    from botocore.errorfactory import ClientError as BotocoreClientError
except ImportError:
    boto3 = None
    BotocoreClientError = None

try:
    import s3fs
except ImportError:
    s3fs = None

logger = logging.getLogger("dativa.tools.file_validation")


class FileValidationException(Exception):
    """
    A generic class for reporting errors in the FileValidation
    """
    def __init__(self, reason):
        message = 'File validation failed, reason: {}.'.format(reason)
        logger.error(message)
        Exception.__init__(self, message)
        self.reason = reason


class FileValidationTypeException(TypeError):
    """
    An generic class for reporting errors while instantiating the FileValidation class which are due to type
    """
    def __init__(self, reason):
        message = 'File validation was instantiated with incorrect type, reason: {}'.format(reason)
        logger.error(message)
        TypeError.__init__(self, message)
        self.reason = reason


class FileValidation(object):
    """
    Class to allow easy validation of files present in a given path based on various properties
    """
    default_allowed_timestamp_formats = ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H',
                                         '%Y-%m-%d', '%s')

    def __init__(self, timestamp=(), file_size=(), file_count=(), timestamp_format="", prefix="", suffix="",
                 s3_resource=None):
        """
        Class to allow easy validation of files present in a given path based on various properties

        :param timestamp: strings for min and max time (min=str or None, max=str or None). This is read in
        with dativa.tools.pd.date_time:string_to_datetime, so must use compatible formats. Comparisons are performed
        naively - without consideration of timezone. Use format to match
        :type timestamp (tuple or str or datetime or None)
        :param file_size: min and max size in bytes (min=int or None, max=int or None), treats single int as minimum
        :type file_size (tuple or int or None)
        :param file_count: min and max file count, treats single int as minimum
        :type file_count (tuple or int or None)
        :param timestamp_format: string (or list of strings) for timestamp formats to be used for max and min timestamp,
        uses dativa.tools.pd.date_time, which ports features of datetime.strptime hence must be in compatible format.
        timestamp format='%s' parses time as seconds since UNIX Epoch.
        :type timestamp_format (str)
        :param s3_resource: for S3 resource pass through
        :type prefix str
        :type suffix str
        """
        if not boto3:
            raise ImportError("boto3 must be installed to run FileValidation")

        if not s3fs:
            raise ImportError("s3fs must be installed to run FileValidation")

        self._s3resource = s3_resource if s3_resource else boto3.resource("s3")
        self._s3fs = s3fs.S3FileSystem()

        # validate timestamp format if present, else use default values
        if timestamp_format:
            if not isinstance(timestamp_format, (list, tuple)):
                timestamp_format = [timestamp_format]

            self._allowed_timestamp_formats = timestamp_format
            self._validate_timestamp_formats()
        else:
            self._allowed_timestamp_formats = deepcopy(self.default_allowed_timestamp_formats)
        logger.debug("Timestamps can be parsed with following formats: {}".format(self._allowed_timestamp_formats))

        # convert parameters to ranges
        self._timestamp = self._split_to_range(timestamp)
        self._file_size = self._split_to_range(file_size)
        self._file_count = self._split_to_range(file_count)

        logger.debug("Initialising file validation with the following limits - timestamps: {}, file size ranges: {}, "
                     "and file count range: {}.".format(*[x if x else "not checked" for x in
                                                          [self._timestamp, self._file_size, self._file_count]]))

        # validate the ranges received for _file_size and _file_count - ensure they're int or None
        if not all(isinstance(limit, int) or limit is None for limit in self._file_size):
            raise FileValidationTypeException("file_size must be a tuple of ints or Nones, e.g. (None, 100)")
        if not all(isinstance(limit, int) or limit is None for limit in self._file_count):
            raise FileValidationTypeException("file_count must be a tuple of ints or Nones, e.g. (None, 100)")

        # validate the ranges received for timestamp - ensure they're str or None
        if not all(isinstance(limit, (str, datetime)) or limit is None for limit in self._timestamp):
            raise FileValidationTypeException(
                "timestamp must be a tuple of str or Nones or datetime objects, e.g. (None, '2018-11-01'). "
                "Current current form (and their type): {} ({}). "
                "The timestamp format should be specified via timestamp_format. If no "
                "timestamp format is defined the default values are the following formats {}."
                "The formats must follow the types outlined for datetime.strftime."
                .format(self._timestamp, [type(i) for i in self._timestamp], self.default_allowed_timestamp_formats))

        # ensure all timestamps are datetime objects
        self.timestamp_object_range = []
        for time in self._timestamp:
            if time:
                self.timestamp_object_range.append(self._attempt_timestamp_convert(time))
            else:
                self.timestamp_object_range.append(None)

        # ensure that prefix and suffix are strings
        if not isinstance(prefix, str) or not isinstance(suffix, str):
            raise FileValidationTypeException("prefix/suffix must be defined as strings.")
        self.prefix, self.suffix = prefix, suffix

    def _validate_timestamp_formats(self):

        for timestamp_format in self._allowed_timestamp_formats:
            err_msg = "Timestamp format identified as invalid (and type), " \
                      "and all specified timestamps: {} ({}), and {}".format(timestamp_format, type(timestamp_format),
                                                                             self._allowed_timestamp_formats)

            if not isinstance(timestamp_format, str):
                raise FileValidationTypeException("timestamp_format must be str (or list/tuple of str) and be "
                                                  "parsable by dativa.pandas.date_time:string_to_datetime."+err_msg)

            if not dativa_date_time.format_string_is_valid(timestamp_format):
                raise FileValidationException("timestamp_format must be be parsable by "
                                              "dativa.pandas.date_time:string_to_datetime."+err_msg)

    def _attempt_timestamp_convert(self, time):
        """
        converts time to datetime object without timestamp information and returns
        :param time:  timestamp to be converted to datetime without timezone
        :type time: (str or datetime)
        :return: datetime object
        :rtype datetime
        """
        if isinstance(time, datetime):
            return time.replace(tzinfo=None)

        for timestamp_format in self._allowed_timestamp_formats:
            try:
                return dativa_date_time.string_to_datetime(time, format=timestamp_format)
            except (ValueError, TypeError):
                pass
        raise FileValidationException("Failed to convert timestamp {} ({})- must be a str in one of the following "
                                      "formats: {} or datetime.datetime object.".
                                      format(time, type(time), self._allowed_timestamp_formats))

    @staticmethod
    def _split_to_range(input_range):
        if isinstance(input_range, (str, int, datetime)):
            return input_range, None
        try:
            min_range, max_range = input_range
            return min_range, max_range
        except (TypeError, ValueError):
            if input_range:
                return input_range[0], None
            else:
                return ()

    @staticmethod
    def _remove_from_list(acceptable, files_to_remove):
        """
        return entries from the first list they are not in the second list
        :param acceptable: list of acceptable files
        :param files_to_remove: list of files which should be removed
        :return: list of files not in unacceptable_subset
        """
        return [file for file in acceptable if file not in files_to_remove]

    def run_validator(self, path, glob_pattern="*", consider_correctly_formed_files=True, raise_exceptions=False):
        """
        check all files specified by glob_pattern as to whether they match the properties specified, will return
        either those which match the pattern or those which do not.

        :param path: path to the files - can either be a path for S3Location or an absolute local file path. CANNOT HAVE '/' AS THE FINAL CHARACTER.
        :type path str
        :param glob_pattern: pattern of glob files to be examined. CANNOT HAVE '/' AS THE FIRST CHARACTER.
        :type glob_pattern str
        :param consider_correctly_formed_files: if False, consider malformed files (which do not match validation) in relation to the file_count argument
        :type consider_correctly_formed_files: bool
        :param raise_exceptions: whether to raise exception when finding files which do not match validation criteria
        :type raise_exceptions: bool
        :return: dictionary with lists of files - keys: "acceptable", "unacceptable", "all" and dictionaries of
        removed files - keys: "removed_for_time" "removed_for_size"
        """
        logger.debug("File validation with the following path and glob pattern: {} {}.".format(path, glob_pattern))
        if path.endswith("/") or glob_pattern.startswith("/"):
            raise FileValidationException("path must not end  with '/' and glob_pattern must not start with '/':"
                                          " {} {}.".format(path, glob_pattern))
        # these are the FULL paths - use os.path.basename to find filename for when it's needed
        files_tbc, bucket = self._find_file_paths_and_bucket(path, glob_pattern)
        logger.info("Files to be considered and the bucket they are in (None if local file path) : {} {}".
                    format(files_tbc, bucket))

        excl_for_filename, excluded_files = [], []
        excl_for_size, excl_for_time = {}, {}
        acceptable_files = deepcopy(files_tbc)
        logger.debug("File validation carried out with the following files: {}".format(acceptable_files))

        # perform filename validation
        if self.prefix or self.suffix:
            logger.info("Carrying out filename validation with following prefix \"{}\" and suffix \"{}\"".format(
                self.prefix, self.suffix))
            for abs_file_path in files_tbc:
                try:
                    filename = S3Location(abs_file_path).file
                except S3ClientError:
                    filename = os.path.basename(abs_file_path)
                if not filename.startswith(self.prefix):
                    excl_for_filename.append(abs_file_path)
                    continue
                if not filename.endswith(self.suffix):
                    excl_for_filename.append(abs_file_path)
            excluded_files.extend(excl_for_filename)
            logger.info("Files excluded for filename: {}".format(excl_for_filename))
        if self._file_size:
            file_size_dict = self._get_file_sizes_bytes(files_tbc, bucket)
            excl_for_size = self._file_not_matching_range(file_size_dict, "size", *self._file_size)
            acceptable_files = self._remove_from_list(acceptable_files, excl_for_size.keys())
            excluded_files.extend(excl_for_size.keys())

        if self._timestamp:
            timestamp_dict = self._get_last_time_modified(files_tbc, bucket)
            excl_for_time = self._file_not_matching_range(timestamp_dict, "timestamp", *self.timestamp_object_range)
            acceptable_files = self._remove_from_list(acceptable_files, excl_for_time.keys())
            excluded_files.extend(excl_for_time.keys())

        if consider_correctly_formed_files:
            files_considered = acceptable_files
        else:
            # use set to get unique elements then convert back to list
            files_considered = list(set(excluded_files))

        if self._file_count:
            min_prop, max_prop = self._file_count
            prop = len(files_considered)
            if (max_prop and (prop > max_prop)) or (min_prop and (prop < min_prop)):
                type_of_files = "matching" if consider_correctly_formed_files else "malformed"
                err_msg = "Number of {} files found outside of acceptable range: {}, acceptable range (inclusive): {}."\
                          .format(type_of_files, prop, self._file_count)
                raise FileValidationException(err_msg)

        if raise_exceptions:
            if excluded_files:
                raise FileValidationException("The following do not meet the validation requirements: {}".format(
                    list(set(excluded_files))))
        return {"acceptable": acceptable_files, "unacceptable": excluded_files, "all": files_tbc,
                "removed_for_time": excl_for_time, "removed_for_size": excl_for_size}

    def _find_file_paths_and_bucket(self, path, glob_pattern):
        """
        get all files in the specified directory - attempt as S3 path, if that fails then attempt as local path

        :return: files_tbc, bucket
        :rtype (list, str)
        """
        s3_exception = None
        try:
            s3loc = S3Location(path+"/"+glob_pattern, ignore_double_slash=False)
            files_with_path = self._s3fs.glob(s3loc.s3_url)

            if not files_with_path:
                # deals with bug in s3fs.glob - specifying an exact filename for glob will return empty list
                # if no files are found, check if it is the name of a specific file
                try:
                    logger.debug("Unable to resolve with s3fs.glob: {}".format(s3loc))
                    self._s3resource.Object(s3loc.bucket, s3loc.path).load()
                    single_file = s3loc.bucket+"/"+s3loc.path
                    files_with_path = [single_file]
                    logger.debug("Unable to resolve with s3fs.glob, but able to resolve as single object with following"
                                " path: {}".format(single_file))
                except BotocoreClientError:
                    # no file found - return empty list
                    files_with_path = []
            # remove bucket name from start of each path
            files_with_path = [path.split("/", 1)[1] for path in files_with_path]
            bucket = s3loc.bucket

        except (S3ClientError, FileValidationException) as exception:
            s3_exception = exception
            logger.debug("Unable to treat path ({}) as S3 path (due to {}). Attempting as local file path.".
                        format(path, repr(s3_exception)))
            files_with_path = glob.glob(os.path.join(path, glob_pattern))
            bucket = None

        if len(files_with_path) == 0:
            err_msg = str("s3fs.glob and glob found no files! Check access permissions and content of path/folder. "
                          "Path and pattern passed to S3FileSystem.glob ('{}') and glob.glob ({}).".
                          format(path+"/"+glob_pattern, os.path.join(path, glob_pattern)))
            if s3_exception:
                err_msg += " Exception from S3 attempt - {}".format(repr(s3_exception))
            raise FileValidationException(err_msg)

        return files_with_path, bucket

    def _get_last_time_modified(self, files_tbc, bucket):
        """
        :return: dictionary of file path and time last modified, as datetime objects WITHOUT timezones
        """
        time_stamps = {}
        for path in files_tbc:
            if bucket:
                datetime_obj = self._s3resource.ObjectSummary(bucket_name=bucket,
                                                              key=path).last_modified.replace(tzinfo=None)
            else:
                datetime_obj = dativa_date_time.string_to_datetime(os.path.getmtime(path), format="%s")
            time_stamps[path] = datetime_obj

        return time_stamps

    def _get_file_sizes_bytes(self, files_tbc, bucket):
        """
        :return: dictionary of file path and size in bytes
        """
        file_sizes = {}
        for path in files_tbc:
            if bucket:
                file_sizes[path] = self._s3resource.ObjectSummary(bucket_name=bucket, key=path).size
            else:
                file_sizes[path] = os.path.getsize(path)
        return file_sizes

    @staticmethod
    def _file_not_matching_range(file_and_property, name, min_prop=None, max_prop=None):
        """
        takes dictionary of file_name : prop and returns the entries where prop is not in range
        [min_prop, max_prop]. Must explicitly define min or max for the property in the same type as
        :param file_and_property: file name and property to be inspected
        :type file_and_property: dict
        :param min_prop: minimum value for inspection (inclusive)
        :param max_prop: maximum value for inspection (inclusive)
        :param name of parameter being evaluated
        :return: list of files which do not match
        """
        logger.info("Evaluating {} for specified files, with range {}.".format(name, [min_prop, max_prop]))
        files_which_do_not_match_with_prop = {}
        for file, prop in file_and_property.items():
            if (max_prop and (prop > max_prop)) or (min_prop and (prop < min_prop)):
                files_which_do_not_match_with_prop[file] = prop
        logger.info("Files which do not match criteria, with the file name and {} - {}".
                    format(name, files_which_do_not_match_with_prop))
        return files_which_do_not_match_with_prop
