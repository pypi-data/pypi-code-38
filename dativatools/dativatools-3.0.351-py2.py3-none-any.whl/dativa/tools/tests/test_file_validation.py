import time
import unittest
import os
from datetime import datetime
from dativa.tools import FileValidation, FileValidationException, FileValidationTypeException
from dativa.tools.aws import S3Location, S3Client


class FileValidationTest(unittest.TestCase):
    """
    Test that the file validation can correctly include, exclude and highlight files
    """
    @classmethod
    def setUpClass(cls):
        try:
            bucket_only = os.environ["DATIVA_PIPELINE_API_BUCKET"]
        except KeyError:
            bucket_only = "abr-dev-bucket"

        cls.s3c = S3Client()
        cls.bytes_in_megabyte = 2 ** 20
        cls.bytes_in_kilobyte = 2 ** 10
        cls.timestamp_format = '%Y-%m-%d %H:%M:%S.%f'

        cls.smaller_than_10b = ["empty_file.asdf", "empty_file.bsdf"]
        cls.between_1kb_10b = ["100b_file.asdf", "100b_file.bsdf"]
        cls.larger_than_1kb = ["100kb_file.asdf", "100kb_file.bsdf"]

        cls.rel_path_test_data_s3 = "test_data/file_validation"
        cls.s3loc = S3Location("s3://{}/{}".format(bucket_only, cls.rel_path_test_data_s3))
        cls.s3_smaller_than_10b = [cls.rel_path_test_data_s3 + "/" + file for file in cls.smaller_than_10b]
        cls.s3_between_1kb_10b = [cls.rel_path_test_data_s3 + "/" + file for file in cls.between_1kb_10b]
        cls.s3_larger_than_1kb = [cls.rel_path_test_data_s3 + "/" + file for file in cls.larger_than_1kb]

        cls.rel_path_test_data = os.path.join("test_data", "file_validation")
        cls.abs_path_test_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), cls.rel_path_test_data)
        cls.local_smaller_than_10b = [os.path.join(cls.abs_path_test_data, file) for file in cls.smaller_than_10b]
        cls.local_between_1kb_10b = [os.path.join(cls.abs_path_test_data, file) for file in cls.between_1kb_10b]
        cls.local_larger_than_1kb = [os.path.join(cls.abs_path_test_data, file) for file in cls.larger_than_1kb]

        # generate files and upload them to S3 a short time apart
        cls.time_first = datetime.utcnow()
        cls.smaller_than_10b_files = cls._create_and_upload_files(cls.smaller_than_10b, cls.s3loc, desired_size=0)
        time.sleep(2)
        cls.time_second = datetime.utcnow()
        cls.between_1kb_10b_files = cls._create_and_upload_files(cls.between_1kb_10b, cls.s3loc, desired_size=20)
        time.sleep(2)
        cls.time_third = datetime.utcnow()
        cls.larger_than_1kb_files = cls._create_and_upload_files(cls.larger_than_1kb, cls.s3loc,
                                                                 desired_size=cls.bytes_in_kilobyte+1)

    @staticmethod
    def _create_and_upload_files(list_of_files, s3loc, desired_size=0):
        """
        create file and upload to S3
        :type list_of_files list
        :param desired_size:
        :return: list of TemporaryFile objects
        """
        s3c = S3Client()
        return_list = []
        for file in list_of_files:
            return_list.append(FileValidationTest.TemporaryFile(file, desired_size))
        for file in return_list:
            s3c.s3_client.upload_file(
                Filename=file.file_path,
                Bucket=s3loc.bucket, Key=s3loc.path + "/" + file.file_name)
        return return_list

    def _run_and_consider_output(self, incorrect, correct):
        """
        ensure that the output from run_validator matches the expected matching (/correct) and
        non-matching (/incorrect) elements exactly.
        :param incorrect: list
        :param correct: list
        """
        # assertCountEqual is a method which ensures that two lists are the same independent of their order
        # - it counts the number of times each element appears in a list then checks that the two counts are the same
        return_obj = self.object.run_validator(self.abs_path_test_data,
                                               glob_pattern="*",
                                               consider_correctly_formed_files=False,
                                               raise_exceptions=False)
        self.assertCountEqual(return_obj["unacceptable"], incorrect)
        self.assertCountEqual(return_obj["acceptable"], correct)

    def _run_and_consider_output_s3(self, incorrect, correct):

        return_obj = self.object.run_validator(self.s3loc.s3_url,
                                               glob_pattern="*",
                                               consider_correctly_formed_files=False,
                                               raise_exceptions=False)
        self.assertCountEqual(return_obj["unacceptable"], incorrect)
        self.assertCountEqual(return_obj["acceptable"], correct)

    def test_min_and_max_file_size_s3(self):
        self.object = FileValidation(file_size=(10, 2**10))
        self._run_and_consider_output_s3(incorrect=self.s3_larger_than_1kb + self.s3_smaller_than_10b,
                                         correct=self.s3_between_1kb_10b)

    def test_non_existent_bucket(self):
        obj = FileValidation()
        with self.assertRaises(FileValidationException):
            obj.run_validator(path="s3://bucket-that-should-not-be/path-that-also-should-not-exist", glob_pattern="*")

    def test_single_file_on_s3(self):
        obj = FileValidation()
        return_dict = obj.run_validator(self.s3loc.s3_url,
                                        glob_pattern="empty_file.asdf")
        self.assertEqual(return_dict["all"], [self.s3loc.path+"/empty_file.asdf"])
        self.assertEqual(return_dict["acceptable"], [self.s3loc.path+"/empty_file.asdf"])

    def test_single_file_which_does_not_exist_on_s3(self):
        obj = FileValidation()
        with self.assertRaises(FileValidationException):
            obj.run_validator(self.s3loc.s3_url,
                              glob_pattern="the-file-that-should-not-be.asdfasdfasdfasdf")

    def test_link_with_double_slash_in_path(self):
        """
        should fail in s3loc rather than with s3fs
        :return:
        """
        obj = FileValidation()
        with self.assertRaises(FileValidationException):
            obj.run_validator("s3://{}/test_data//file_validation".format(self.s3loc.bucket))
    # def test_single_path_which_points_to_folder(self):
    #     """
    #     this test fails rather ungracefully - can't call object summary on a folder so it crashes. Need to decide best
    #     course to take in this case
    #     """
    #     obj = FileValidation(file_size=(1,))
    #     obj.run_validator(self.s3loc.bucket, glob_pattern="test_data")

    def test_min_and_max_file_size_local(self):
        self.object = FileValidation(file_size=(10, 2**10))
        self._run_and_consider_output(correct=self.local_between_1kb_10b,
                                      incorrect=self.local_smaller_than_10b + self.local_larger_than_1kb)

    def test_fails_with_appended_slash_on_url_or_pre_pending_glob_pattern(self):
        object = FileValidation()
        with self.assertRaises(FileValidationException):
            object.run_validator(self.s3loc.s3_url+"/")
        with self.assertRaises(FileValidationException):
            object.run_validator(self.s3loc.s3_url, "/*")
        with self.assertRaises(FileValidationException):
            object.run_validator(self.s3loc.s3_url+"/", "/*")

    def test_min_and_max_file_size_exact_local(self):
        self.object = FileValidation(file_size=(20, 2**10))
        self._run_and_consider_output(correct=self.local_between_1kb_10b,
                                      incorrect=self.local_smaller_than_10b + self.local_larger_than_1kb)

    def test_tuple_min_only_file_size_local(self):
        """
        1 element tuple (as minimum)
        """
        self.object = FileValidation(file_size=(10, ))
        self._run_and_consider_output(correct=self.local_between_1kb_10b + self.local_larger_than_1kb,
                                      incorrect=self.local_smaller_than_10b)

    def test_tuple_max_only_file_size_local(self):
        """
        2 element tuple (no minimum)
        """
        self.object = FileValidation(file_size=(None, 10))
        self._run_and_consider_output(incorrect=self.local_between_1kb_10b + self.local_larger_than_1kb,
                                      correct=self.local_smaller_than_10b)

    def test_min_only_file_size_local(self):
        """
        just 1 int - should be treated as the minimum value
        """
        self.object = FileValidation(file_size=10)
        self._run_and_consider_output(correct=self.local_between_1kb_10b + self.local_larger_than_1kb,
                                      incorrect=self.local_smaller_than_10b)

    def test_tuple_not_ints_file_size_local(self):
        """
        check that passing noninteger as part of the tuple will cause it to
        """
        with self.assertRaises(FileValidationTypeException):
            self.object = FileValidation(file_size=("10", None))

        with self.assertRaises(FileValidationTypeException):
            self.object = FileValidation(file_size=(None, "10"))

    def test_tuple_not_ints_file_count_local(self):
        """
        must pass in ints for file_size and file_count or it will fail
        """
        with self.assertRaises(FileValidationTypeException):
            self.object = FileValidation(file_count=("10", None))

    def test_exact_file_count_local(self):
        """
        ensure that having the correct number as both a minimum and maximum will give an exact match
        """
        self.object = FileValidation(file_count=(3, 3))
        self.object.run_validator(self.abs_path_test_data,
                                  glob_pattern="*asdf",
                                  consider_correctly_formed_files=True,
                                  raise_exceptions=True)

    def test_too_few_acceptable_file_count_local(self):
        """
        ensure it raises when there are too few files matching the pattern specified
        """
        self.object = FileValidation(file_count=(0, 2))
        with self.assertRaises(FileValidationException):
            self.object.run_validator(self.abs_path_test_data,
                                      glob_pattern="*asdf",
                                      raise_exceptions=True)

    def test_unacceptable_file_count_local(self):
        """
        check a minimum of files is found
        """
        self.object = FileValidation(file_count=1)

        self.object.run_validator(self.abs_path_test_data,
                                  glob_pattern="*asdf",
                                  raise_exceptions=True)
        return_obj = self.object.run_validator(self.abs_path_test_data,
                                               glob_pattern="*asdf",
                                               consider_correctly_formed_files=True)
        self.assertGreater(len(return_obj), 1)

    def test_unacceptable_number_of_files_found(self):
        """
        ensure that it raises if it finds a number of files which do not match the spec
        """
        self.object = FileValidation(file_size=(0, 2))
        with self.assertRaises(FileValidationException):
            self.object.run_validator(self.abs_path_test_data,
                                      glob_pattern="*",
                                      raise_exceptions=True)

    def test_none_type_for_input(self):
        self.object = FileValidation(file_size=None)

    def test_no_file_validation(self):
        """
        make sure all files expected are returned if no file validation is present
        """
        self.object = FileValidation()
        self._run_and_consider_output(
            correct=self.local_between_1kb_10b + self.local_larger_than_1kb + self.local_smaller_than_10b,
            incorrect=[])

    def test_time_min_and_max_s3(self):
        self.object = FileValidation(timestamp=(self.time_first.strftime(self.timestamp_format),
                                                self.time_third.strftime(self.timestamp_format)),
                                     timestamp_format=self.timestamp_format)
        self._run_and_consider_output_s3(correct=self.s3_smaller_than_10b + self.s3_between_1kb_10b,
                                         incorrect=self.s3_larger_than_1kb)

    def test_time_min_and_max_ints_s3(self):
        self.object = FileValidation(timestamp=(str(self.time_first.timestamp()),
                                                str(self.time_third.timestamp())),
                                     timestamp_format="%s")
        self._run_and_consider_output_s3(correct=self.s3_smaller_than_10b + self.s3_between_1kb_10b,
                                         incorrect=self.s3_larger_than_1kb)

    def test_time_max_and_min(self):
        self.object = FileValidation(timestamp=(self.time_first.strftime(self.timestamp_format),
                                                self.time_third.strftime(self.timestamp_format)),
                                     timestamp_format=self.timestamp_format
                                     )
        self._run_and_consider_output(correct=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      incorrect=self.local_larger_than_1kb)

    def test_time_min_and_max_datetime_obj(self):
        self.object = FileValidation(timestamp=(self.time_first,
                                                self.time_third),
                                     timestamp_format=self.timestamp_format
                                     )
        self._run_and_consider_output(correct=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      incorrect=self.local_larger_than_1kb)

    def test_time_min_only(self):
        self.object = FileValidation(timestamp=(self.time_third.strftime(self.timestamp_format), ))
        self._run_and_consider_output(incorrect=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      correct=self.local_larger_than_1kb)

        self.object = FileValidation(timestamp=self.time_third.strftime(self.timestamp_format)
                                     )
        self._run_and_consider_output(incorrect=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      correct=self.local_larger_than_1kb)

        self.object = FileValidation(timestamp=self.time_third)
        self._run_and_consider_output(incorrect=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      correct=self.local_larger_than_1kb)

    def test_time_max_only(self):
        self.object = FileValidation(timestamp=(None, self.time_third.strftime(self.timestamp_format)))
        self._run_and_consider_output(correct=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      incorrect=self.local_larger_than_1kb)

        self.object = FileValidation(timestamp=(None, str(self.time_third.timestamp())),
                                     timestamp_format="%s")
        self._run_and_consider_output(correct=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      incorrect=self.local_larger_than_1kb)

        self.object = FileValidation(timestamp=(None, self.time_third))
        self._run_and_consider_output(correct=self.local_smaller_than_10b + self.local_between_1kb_10b,
                                      incorrect=self.local_larger_than_1kb)

    def test_time_str_not_correct_format(self):
        """
        If you pass it a tuple of strings with the wrong format it will fail
        """
        garbage_timestamp = "garbage-time-stamp"
        with self.assertRaises(FileValidationException):
            FileValidation(timestamp=(garbage_timestamp, garbage_timestamp))
        with self.assertRaises(FileValidationException):
            FileValidation(timestamp=(garbage_timestamp,))
        with self.assertRaises(FileValidationException):
            FileValidation(timestamp=(None, garbage_timestamp))

    def test_time_not_strings(self):
        """
        If you pass it a tuple of anything other than string, datetime or None it will fail
        """

        with self.assertRaises(FileValidationTypeException):
            FileValidation(timestamp=(123456, ))

        with self.assertRaises(FileValidationTypeException):
            FileValidation(timestamp=(None, 123456))

        with self.assertRaises(FileValidationTypeException):
            FileValidation(timestamp=(123456, None))

    def test_incorrect_timestamp_format(self):
        with self.assertRaises(FileValidationException):
            FileValidation(timestamp_format="garbage-timestamp-format")

        with self.assertRaises(FileValidationTypeException):
            FileValidation(timestamp_format=123456)

    def test_prefix_type_failures(self):
        """
        ensure that str is parsed properly
        """
        with self.assertRaises(FileValidationTypeException):
            fv = FileValidation(prefix=1)
        fv = FileValidation(prefix="arbitrary_string")

    def test_matching_prefix(self):
        fv = FileValidation(prefix="empty_file")
        returned = fv.run_validator(self.abs_path_test_data,
                                    glob_pattern="empty_file*",
                                    raise_exceptions=True)
        self.assertCountEqual(returned["acceptable"], self.local_smaller_than_10b)

    def test_matching_prefix_s3(self):
        fv = FileValidation(prefix="empty_file")
        returned = fv.run_validator(self.s3loc.s3_url,
                                    glob_pattern="empty_file*",
                                    raise_exceptions=True)
        self.assertCountEqual(returned["acceptable"], self.s3_smaller_than_10b)

    def test_not_matching_prefix(self):
        with self.assertRaises(FileValidationException):
            fv = FileValidation(prefix="garbage")
            fv.run_validator(self.s3loc.s3_url,
                             glob_pattern="empty_file*",
                             raise_exceptions=True)
        fv = FileValidation(prefix="garbage")
        returned_dictionary = fv.run_validator(self.s3loc.s3_url,
                                               glob_pattern="empty_file*",
                                               raise_exceptions=False)
        self.assertCountEqual(returned_dictionary["unacceptable"], self.s3_smaller_than_10b)

    def test_not_matching_suffix(self):
        with self.assertRaises(FileValidationException):
            fv = FileValidation(suffix="garbage")
            fv.run_validator(self.abs_path_test_data,
                             glob_pattern="*.asdf",
                             raise_exceptions=True)

    class TemporaryFile:
        """
        temporary file that is deleted when it leaves scope
        """

        def __init__(self, file_name, desired_size=0):
            self.file_name = file_name
            self.file_path = os.path.join(os.path.dirname(__file__), "test_data", "file_validation", file_name)
            self.size = desired_size
            self.time_creation = datetime.utcnow()
            # writes random characters to file so it matches a given length
            with open(self.file_path, "wb") as file:
                file.write(os.urandom(desired_size))

        def __del__(self):
            try:
                os.remove(self.file_path)
            except OSError:
                pass
