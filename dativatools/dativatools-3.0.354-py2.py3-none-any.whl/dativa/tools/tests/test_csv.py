import unittest
import warnings
import os
import tempfile
import shutil
import logging
from pandas.util.testing import assert_frame_equal
from dativa.tools.aws import S3Client
from dativa.tools.pandas import CSVHandler, FpCSVEncodingError
import boto3
from glob import glob
from Crypto.Cipher import AES
from Crypto import Random
from time import sleep

logger = logging.getLogger("dativa.tools.csv.tests")
s3_bucket = "gd.dativa.test"


class CSVFileTests(unittest.TestCase):

    saved_suffix = ".saved"
    root_prefix = "csvhandler"
    s3 = None
    local_base_path = None

    @classmethod
    def setUpClass(cls):

        # Original test data location
        cls.orig_base_path = "{0}/test_data/".format(
            os.path.dirname(os.path.abspath(__file__)))

        # Upload test data to s3
        cls.s3 = S3Client()
        cls.s3.delete_files(s3_bucket, cls.root_prefix)
        cls.s3.put_folder(cls.orig_base_path + cls.root_prefix,
                          s3_bucket, destination=cls.root_prefix)
        cls.s3_base_path = "s3://{}/".format(s3_bucket)

        # Save test data to local folder
        cls.local_base_path = tempfile.mkdtemp() + '/'
        os.mkdir(cls.local_base_path + cls.root_prefix)

    @classmethod
    def tearDownClass(cls):
        # Delete uploaded/created files
        cls.s3.delete_files(s3_bucket, cls.root_prefix)
        shutil.rmtree(cls.local_base_path)

    def _run_file_tests(self, location):

        warnings.simplefilter("ignore", ResourceWarning)

        # Test file location
        test_path = self.root_prefix + '/' + location
        os.mkdir(self.local_base_path + test_path)

        # Get list of the files
        files = self.s3.list_files(
            s3_bucket, prefix=test_path, suffix='.csv')

        # Create the handlers
        csv_orig = CSVHandler(base_path=self.orig_base_path,
                              detect_parameters=True)
        csv_s3 = CSVHandler(base_path=self.s3_base_path,
                            detect_parameters=True)
        csv_local = CSVHandler(base_path=self.local_base_path,
                               detect_parameters=True)
        csv_empty = CSVHandler(detect_parameters=True)

        # Alternate how the path is split
        use_empty_base = True

        for file in files:

            logger.info("testing file {0}".format(file))

            # Read file from S3
            if use_empty_base:
                df1 = csv_empty.load_df(self.s3_base_path + file)
            else:
                df1 = csv_s3.load_df(file)

            # Write file to S3
            if use_empty_base:
                csv_empty.save_df(df1, self.s3_base_path +
                                  file + self.saved_suffix)
            else:
                csv_s3.save_df(df1, file + self.saved_suffix)

            # Check DataFrames match
            if use_empty_base:
                df2 = csv_empty.load_df(
                    self.s3_base_path + file + self.saved_suffix)
            else:
                df2 = csv_s3.load_df(file + self.saved_suffix)
            assert_frame_equal(df1, df2)

            # Check strings match
            str1 = csv_s3.df_to_string(df1)
            str2 = csv_s3.df_to_string(df2)
            self.assertMultiLineEqual(str1, str2)

            # Read file locally
            if use_empty_base:
                df3 = csv_empty.load_df(self.orig_base_path + file)
            else:
                df3 = csv_orig.load_df(file)

            # Write file locally
            if use_empty_base:
                csv_empty.save_df(df3, self.local_base_path +
                                  file + self.saved_suffix)
            else:
                csv_local.save_df(df3, file + self.saved_suffix)

            # Check DataFrames match
            if use_empty_base:
                df4 = csv_empty.load_df(
                    self.local_base_path + file + self.saved_suffix)
            else:
                df4 = csv_local.load_df(file + self.saved_suffix)
            assert_frame_equal(df3, df4)

            # Check strings match
            str3 = csv_orig.df_to_string(df3)
            str4 = csv_local.df_to_string(df4)
            self.assertMultiLineEqual(str3, str4)

            use_empty_base = not use_empty_base

    def test_anonymization_files(self):

        self._run_file_tests('anonymization')

    def test_date_files(self):

        self._run_file_tests('date')

    def test_generic_files(self):

        self._run_file_tests('generic')

    def test_lookup_files(self):

        self._run_file_tests('lookup')

    def test_number_files(self):

        self._run_file_tests('number')

    def test_session_files(self):

        self._run_file_tests('session')

    def test_string_files(self):

        self._run_file_tests('string')

    def test_unique_files(self):

        self._run_file_tests('unique')


class CSVOtherTests(unittest.TestCase):

    local_base_path = None

    @classmethod
    def setUpClass(cls):
        # Original test data location
        cls.orig_base_path = "{0}/test_data/csvhandler/".format(
            os.path.dirname(os.path.abspath(__file__)))

        cls.local_base_path = tempfile.mkdtemp() + '/'
        cls.s3_base_path = "s3://{}/".format(s3_bucket)

        # AES
        cls.key, cls.iv = ("a"*32).encode(), Random.new().read(AES.block_size)
        cls.key2, cls.iv2, = ("b"*32).encode(), Random.new().read(AES.block_size)

        # unencrypted
        cls.csv = CSVHandler(base_path=cls.orig_base_path)
        cls.csv_windows = CSVHandler(base_path=cls.orig_base_path, csv_encoding="Windows-1252")
        # encrypt with specific IV
        cls.csv_encrypt = CSVHandler(base_path=cls.orig_base_path, aes_key=cls.key, aes_iv=cls.iv)
        cls.csv_decrypt = CSVHandler(base_path=cls.orig_base_path, aes_key=cls.key, aes_iv=cls.iv)
        cls.csv_decrypt_fail = CSVHandler(base_path=cls.orig_base_path, aes_key=cls.key2, aes_iv=cls.iv2)
        # encrypt with random IV from AESCipher object
        cls.csv_encrypt_no_iv = CSVHandler(base_path=cls.orig_base_path, aes_key=cls.key)
        cls.csv_decrypt_no_iv = CSVHandler(base_path=cls.orig_base_path, aes_key=cls.key)
        cls.csv_decrypt_fail_no_iv = CSVHandler(base_path=cls.orig_base_path, aes_key=cls.key2)

    @classmethod
    def tearDownClass(cls):
        # Delete uploaded/created files
        shutil.rmtree(cls.local_base_path)

    def test_encoding_error(self):

        with self.assertRaises(FpCSVEncodingError):
            csv = CSVHandler(base_path=self.orig_base_path)
            csv.load_df("lookup/test_cities_reference1252.csv")

    def test_csv_parameter(self):
        csv = CSVHandler(base_path=self.orig_base_path)
        csv.load_df("lookup/test_cities_reference1252.csv",
                    csv_encoding="Windows-1252")

    def test_invalid_compression(self):
        with self.assertRaises(ValueError):
            CSVHandler(base_path=self.orig_base_path, compression="garbage")

    def test_quoting_error(self):
        with self.assertRaises(ValueError):
            CSVHandler(base_path=self.orig_base_path, quoting=-1)

    def test_no_header(self):
        csv = CSVHandler(base_path=self.orig_base_path)
        df = csv.load_df("lookup/test_cities_reference1252.csv",
                         csv_encoding="Windows-1252",
                         header=-1,
                         nan_values=["NaN"],
                         force_dtype=str)

        csv2 = CSVHandler(base_path=self.local_base_path,
                          header=-1)
        csv2.save_df(df, "banana.csv")
        df2 = csv2.load_df("banana.csv",
                           force_dtype=str)

        assert_frame_equal(df, df2, check_index_type=False)

    def test_sniffer(self):
        csv = CSVHandler(base_path=self.orig_base_path)
        csv._sniff_parameters("generic/email_test.csv")

    def test_sniffer_unable_to_decode(self):
        """
        cannot find encoding for encrypted file - need to decrypt first
        """
        with self.assertRaises(FpCSVEncodingError):
            self.csv._sniff_parameters("encryption/unable_to_decode.csv")

    def test_sniffer_no_limiter_etc(self):
        """
        passes empty file - sniffer cannot pick up a separator/delimiter because there are no characters
        """
        with self.assertRaises(FpCSVEncodingError):
            self.csv_decrypt._sniff_parameters("encryption/empty_file.csv")

    def encrypt_decrypt_compare_for_all_files_in_folder(self, folder):
        # get list of csv files in folder from glob
        path = os.path.join(self.orig_base_path, folder, "*csv")
        logger.info(f"Testing encryption on {folder} files")
        files = glob(path)

        # loop over csv files
        for file in files:
            rel_file = os.path.relpath(file, self.orig_base_path)
            logger.info("file for testing {}".format(rel_file))
            try:
                df_init = self.csv.load_df(rel_file)
            except FpCSVEncodingError:
                df_init = self.csv_windows.load_df(rel_file)
            # save with encryption
            self.csv_encrypt.save_df(df_init, "encryption/temporary.encrypted")
            self.csv_encrypt_no_iv.save_df(df_init, "encryption/temporary2.encrypted")
            # compare to make sure they're identical
            assert_frame_equal(df_init, self.csv_decrypt.load_df("encryption/temporary.encrypted"))
            assert_frame_equal(df_init, self.csv_decrypt_no_iv.load_df("encryption/temporary2.encrypted"))
            # try to decrypt with incorrect key - should be unable to decode, ValueError or UnicodeDecodeError
            with self.assertRaises((UnicodeDecodeError, FpCSVEncodingError)):
                self.csv_decrypt_fail.load_df("encryption/temporary.encrypted")
            with self.assertRaises((UnicodeDecodeError, FpCSVEncodingError)):
                self.csv_decrypt_fail_no_iv.load_df("encryption/temporary2.encrypted")
            os.remove(os.path.join(self.orig_base_path, "encryption/temporary.encrypted"))
            os.remove(os.path.join(self.orig_base_path, "encryption/temporary2.encrypted"))

    def test_encryption_saving_and_loading(self):
        basepath = self.orig_base_path
        folder_to_consider = ["anonymization",
                              "date",
                              "generic",
                              "lookup",
                              "number",
                              "session",
                              "string",
                              "unique"]
        for folder in folder_to_consider:
            self.encrypt_decrypt_compare_for_all_files_in_folder(folder)

    def test_encryption_saving_and_loading_s3(self):
        """
        maybe worth making this work for all the files? the decryption sh
        """
        csv_s3 = CSVHandler(base_path=self.s3_base_path,
                            aes_key=b"a"*32)
        df_init = self.csv.load_df("generic/email_test.csv")
        csv_s3.save_df(df_init, "email_test_encrypted.csv")
        sleep(10)   # wait so that S3 updates to include the new file
        df_from_encryption = csv_s3.load_df("email_test_encrypted.csv")
        assert_frame_equal(df_init, df_from_encryption)

    def test_encryption_ensure_failure_with_no_key(self):
        """
        this should return a less horrible error!
        """

        df_init = self.csv.load_df("generic/email_test.csv")
        self.csv_encrypt.save_df(df_init, "encryption/email_test_encrypted.csv")
        with self.assertRaises(FpCSVEncodingError):
            self.csv.load_df("encryption/email_test_encrypted.csv")

    def test_garbage_encryption_keys(self):
        """
        fails to initialise when keys which aren't AES compatible as bytes are given
        """
        with self.assertRaises(ValueError):
            CSVHandler(base_path=self.orig_base_path,
                       aes_key=b"garbage")

        with self.assertRaises((TypeError, ValueError)):
            CSVHandler(base_path=self.orig_base_path,
                       aes_key="garbage")
        with self.assertRaises(TypeError):
            CSVHandler(base_path=self.orig_base_path,
                       aes_key="a"*32)

    def test_nan_values(self):
        """
        the test data should actually include nans to make this test better!
        """
        csv_nan = CSVHandler(base_path=self.orig_base_path, nan_values=["1", "2"])
        temp_df = csv_nan.load_df("generic/email_test.csv")
        csv_nan.save_df(temp_df, "encryption/temporary.csv")
        os.remove(os.path.join(self.orig_base_path, "encryption", "temporary.csv"))

    def test_file_line_terminator(self):

        csv_dl = CSVHandler(base_path=self.orig_base_path,
                            line_terminator="\r")
        print(csv_dl.line_terminator)
        df_init = self.csv.load_df("generic/email_test.csv")
        csv_dl.save_df(df_init, "encryption/email_test_new_terminator.csv")
        df_lt = csv_dl.load_df("encryption/email_test_new_terminator.csv")
        assert_frame_equal(df_init, df_lt)

    def test_is_s3_file_false(self):
        """
        surely passing in some garbage like an integer for the file should cause an error rather than treating it as
        something other than a S3File?
        :return:
        """
        path = self.csv._get_file("arbitrary_file")
        self.assertFalse(self.csv._is_s3_file(path))
        self.assertTrue(self.csv._is_s3_file("s3://some-bucket/some-path/arbitrary-file"))

    def test_encryption_iv_without_key(self):
        """
        cannot specify an iv without a key - you can randomly generate an iv but not a key
        """
        with self.assertRaises(ValueError):
            CSVHandler(base_path=self.orig_base_path,
                       aes_iv=self.iv)

    def test_failure_of_encryption_and_detect_parameters(self):
        """
        specifying detect parameters and encryption simultaneously is not possible
        (FOR NOW, the code should be updated to support this eventually)
        """
        with self.assertRaises(NotImplementedError):
            CSVHandler(aes_key=self.key, detect_parameters=True)

    def test_pd_kwargs_for_reading(self):
        """
        allows pass through of features not directly supported by CSVHandler
        (test by making sure that blank entries are read in as blanks)
        """
        CSVHandler(base_path=self.orig_base_path,
                   pd_kwargs=dict(keep_na_values=False,))

    def test_s3_client_passthrough(self):
        """
        requires me to replace the s3fs object first!
        """
        s3c = boto3.client("s3")
        csvh = CSVHandler(base_path=self.orig_base_path, s3c=s3c)
        df_lt = csvh.load_df("generic/email_test.csv")
        df_init = self.csv.load_df("generic/email_test.csv")
        assert_frame_equal(df_init, df_lt)

    def test_s3_client_init_kwargs(self):
        s3c = boto3.client("s3")
        pd_kwargs = dict(keep_default_na=False)
        csvh = CSVHandler(base_path=self.orig_base_path, s3c=s3c, pd_kwargs=pd_kwargs)
        df_lt = csvh.load_df("generic/email_test.csv")
        df_init = self.csv.load_df("generic/email_test.csv")
        df_init.loc[df_init["e-mail"].isna(), "e-mail"] = ""
        assert_frame_equal(df_init, df_lt)
