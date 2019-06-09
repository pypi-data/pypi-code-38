import logging
import unittest
from os import path
import boto3
import pandas as pd
from dativa.tools.aws import RetryException, S3Csv2Parquet, S3Client, S3Csv2ParquetConversionError


logger = logging.getLogger("dativa.tools.s3csv2parquet.tests")


class S3Csv2ParquetTest(unittest.TestCase):
    s3_bucket = "gd.dativa.test"
    aws_role = "dativatools_athena_poc"
    region = "eu-west-1"
    temporary_directory = "scripts/test"
    job_name = "csv_parquet_convert_test"
    csv_file = path.join("s3://{}".format(s3_bucket), temporary_directory, "100_Sales_Records.csv")
    s3_client = None

    @classmethod
    def setUpClass(cls):
        logger.info("Running setupclass")
        cls.glue = boto3.client(service_name="glue", region_name=cls.region)
        cls.base_path = "{0}/test_data/s3csv2parquet".format(
            path.dirname(path.abspath(__file__)))
        cls.s3_client = S3Client()
        cls.s3_client.put_folder(
            cls.base_path, cls.s3_bucket, cls.temporary_directory)
        cls.s3_boto_client = boto3.client(service_name='s3')
        cls.csv2parquet_obj = S3Csv2Parquet(region=cls.region,
                                            template_location="s3://{}/{}".format(cls.s3_bucket,
                                                                                  cls.temporary_directory),
                                            glue_role=cls.aws_role)

    def test_file_conversion(self):
        """
        This test checks if result of files conversion are as expected.
        """
        logger.info("Running Test: test_valid_separator")
        self.csv2parquet_obj.convert([self.csv_file],
                                     delete_csv=False, name=self.job_name, with_header=1)
        self.csv2parquet_obj.wait_for_completion()

        local_file = path.join(self.base_path, "sample1.snappy.parquet")
        local_df = pd.read_parquet(local_file)
        converted_files = self.s3_client.list_files(self.s3_bucket, prefix=path.join(self.temporary_directory, "part-"),
                                                    suffix="parquet")
        if len(converted_files) > 1:
            logger.error("Please clean up files at location {}".format(
                path.join(self.s3_bucket, self.temporary_directory)))
        else:
            key = converted_files[0]
            converted_df = pd.read_parquet(path.join("s3://", self.s3_bucket, key))
            self.assertTrue(converted_df.equals(local_df))

    def test_file_conversion_with_schema(self):
        """
        This test checks if result of files conversion are as expected.
        """
        logger.info("Running Test: test_file_conversion_with_schema")
        self.csv2parquet_obj.convert([self.csv_file], schema=[("Country", "string"), ("Region", "string")],
                                     delete_csv=False, name=self.job_name, with_header=1)
        self.csv2parquet_obj.wait_for_completion()

    def test_csv_file_validation(self):
        """
        Test to check if error is raised if csv files is not formed correctly.
        """
        logger.info("Running test: test_csv_file_validation")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert("s3:/bucket/foldet")

    def test_output_folder_validation(self):
        """
        Test to check if error is raised if output folder
        is not formed correctly.
        """
        logger.info("Running test: test_output_folder_validation")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, output_folder="s3//gd.dativa.test")

    def test_output_allocated_capacity_belowthreshold(self):
        """
        Test to check if error is raise if allocated_capacity is outside threshold
        """
        logger.info("Running Test: test_output_allocated_capacity_belowthreshold")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, allocated_capacity=1)

    def test_output_header_parameter_negative_test(self):
        """
        Test to check if exception is raised if withHeader is invalid
        """
        logger.info("Running Test: test_output_header_parameter_negative_test")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, with_header='yes')

    def test_delete_csv_parameter_negative_test(self):
        """
        Test to check if error is thrown if delete csv parameter
        field is invalod
        """
        logging.info("Running test: test_delete_csv_parameter_negative_test")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, delete_csv=0)

    def test_failed_job(self):
        """
        This test checks if failed Jobs are handled properly
        """
        logger.info("Running test: test_failed_job")
        self.csv2parquet_obj.convert([self.csv_file],
                                     "s3://this_bucket_does_exist/file1.csv",
                                     with_header=0, name=self.job_name)

        with self.assertRaises(RetryException):
            self.csv2parquet_obj.wait_for_completion()

    def test_multiple_jobs(self):
        """
        This test checks if class can handle multiple jobs
        """
        logger.info("Running Test:test_failed_job")
        for i in range(6):
            self.csv2parquet_obj.convert([self.csv_file],
                                         "s3://{}/{}".format(self.s3_bucket,
                                                             self.temporary_directory),
                                         delete_csv=False, name=self.job_name, with_header=1)
        self.csv2parquet_obj.wait_for_completion()

    def test_invalid_output_folder_type(self):
        """
        This test ensures that only string is accepted as valida
        parameter for output folder
        """
        logger.info("Running Test: test_invalid_output_folder_type")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, output_folder=["s3://bucketname/"])

    def test_invalid_output_s3_location(self):
        """
        This test ensures that output folder
        has valid s3 location format
        """
        logger.info("Running Test: test_invalid_output_s3_location")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, output_folder="bucketname/folder")

    def test_supported_schema_datatype(self):
        """
        This test checks if schema supplied is of supported
        format before running glue job
        """
        logger.info("Running Test: test_supported_schema_datatype")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, schema=[("col_1", "list")])

    def test_invalid_schema_data_type(self):
        """
        This test checks if schema supplied is of list
        datatype before running glue job
        """
        logger.info("Running Test: test_invalid_schema_data_type")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, schema=("col_1", "string"))

    def test_invalid_compression(self):
        """
        This tests checks if an error is thrown if
        an unsupported compression format is provided
        """
        logger.info("Running Test: test_invalid_compression")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, compression="tar.gz")

    def test_invalid_list_partition_by(self):
        """
        This tests checks if the  partition column is of correct type
        """
        logger.info("Running Test: test_invalid_list_partition_by")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, partition_by="col_1")

    def test_valid_mode(self):
        """
        This tests checks if an error is thrown if
        an unsupported mode is provided
        """
        logger.info("Running Test: This tests checks if an error is thrown if an unsupported mode is provided")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, mode="appends")

    def test_valid_separator(self):
        """
        This tests checks if an error is thrown if
        an unsupported seperator format is provided
        """
        logger.info("Running Test: test_valid_separator")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert(self.csv_file, separator=123)

    def test_mode_append(self):
        """
        This test checks if appends mode runs correctly
        The expectation is that in this mode files are not overwritten
        """
        logger.info("Running Test: test_mode_append")
        convert_count = 2
        for i in range(convert_count):
            self.csv2parquet_obj.convert([self.csv_file], delete_csv=False,
                                         name=self.job_name, with_header=1,
                                         mode="append")
        self.csv2parquet_obj.wait_for_completion()
        converted_files = self.s3_client.list_files(self.s3_bucket, prefix=path.join(self.temporary_directory, "part-"),
                                                    suffix="parquet")

        self.assertEqual(len(converted_files), convert_count)

    def test_mode_ignore(self):
        """
        This test checks if overwrite mode runs correctly
        The expectation is that in this mode is that files are overwritten
        """
        logger.info("Running Test: test_mode_overwrite")
        output_folder = "scripts/test/output/"
        full_output_path = path.join("s3://", self.s3_bucket, output_folder)
        self.s3_client.put_folder(self.base_path, self.s3_bucket,
                                  output_folder)
        self.csv2parquet_obj.convert([self.csv_file], delete_csv=False,
                                     name=self.job_name, output_folder=full_output_path,
                                     with_header=1, mode="ignore")
        self.csv2parquet_obj.wait_for_completion()
        converted_files = self.s3_client.list_files(self.s3_bucket, prefix=output_folder)
        self.assertEqual(len(converted_files), 2)

    def test_mode_overwrite(self):
        """
        This test checks if overwrite mode runs correctly
        The expectation is that in this mode is that files are overwritten
        """
        logger.info("Running Test: test_mode_overwrite")
        output_folder = "scripts/test/output/"
        full_output_path = path.join("s3://", self.s3_bucket, output_folder)
        self.s3_client.put_folder(self.base_path, self.s3_bucket,
                                  output_folder)
        self.csv2parquet_obj.convert([self.csv_file], delete_csv=False,
                                     name=self.job_name, output_folder=full_output_path,
                                     with_header=1, mode="overwrite")
        self.csv2parquet_obj.wait_for_completion()
        converted_files = self.s3_client.list_files(self.s3_bucket, prefix=output_folder, suffix="parquet")
        self.assertEqual(len(converted_files), 1)

    def test_overwrite_mode_validation_one(self):
        """
        This tests expects a exception to be raised if
        output folder is not
        specified when mode is overwrite
        """
        logger.info("Running Test: test_overwrite_mode_validation_one")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert([self.csv_file], name=self.job_name,
                                         mode="overwrite")

    def test_overwrite_mode_validation_two(self):
        """
        This tests expects a exception to be raised if
        csv file is a subdirectory of output folder.
        """
        logger.info("Running Test: test_overwrite_mode_validation_two")
        with self.assertRaises(S3Csv2ParquetConversionError):
            self.csv2parquet_obj.convert([self.csv_file], name=self.job_name, mode="overwrite",
                                         output_folder=path.join("s3://{}".format(self.s3_bucket),
                                                                 self.temporary_directory))

    def tearDown(self):
        self.s3_client.delete_files(
            bucket=self.s3_bucket, prefix=self.temporary_directory, suffix="parquet")
        self.glue.delete_job(JobName=self.job_name)

    @classmethod
    def tearDownClass(cls):
        cls.s3_client.delete_files(
            bucket=cls.s3_bucket, prefix=cls.temporary_directory)
