import logging
import unittest
from os import path
import boto3
import pandas as pd
from dativa.tools.aws import RetryException, AthenaClient, AthenaClientError, S3Client, S3ClientError, S3Csv2Parquet
logger = logging.getLogger("dativa.tools.athena.tests")


# noinspection SqlNoDataSourceInspection
class AthenaTest(unittest.TestCase):
    source_file = "s3://gd.dativa.test/s3_upload_athena/demographic/"
    tablename = "demographic"
    aws_role = "dativatools_athena_poc"
    region = "eu-west-1"
    database = "test_athena_database"
    bucket = "gd.dativa.test"
    output_location = "s3://gd.dativa.test/"
    invalid_file_location = "/this/location/does/not/exist.csv"
    glue = None

    @classmethod
    def setUpClass(cls):
        logger.info("Running setupclass for Athena test")
        cls.base_path = "{0}/test_data/".format(
            path.dirname(path.abspath(__file__)))
        logger.info("Uploading test data to s3")
        cls.s3 = S3Client()
        cls.s3.delete_files(cls.bucket, "s3_upload_athena")

        cls.s3.put_folder(source=path.join(cls.base_path, "s3_upload_athena"),
                          bucket=cls.bucket,
                          destination="s3_upload_athena",
                          file_format="*")
        cls.scp = S3Csv2Parquet(region=cls.region,
                                template_location="{0}temp/template/".format(cls.output_location),
                                glue_role=cls.aws_role)
        cls.athena_client = AthenaClient(cls.region, cls.database, s3_parquet=cls.scp)
        cls.glue = boto3.client(service_name='glue',
                                region_name=cls.region)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.glue.get_database(Name=cls.database)
            logger.info("Deleting database: {}".format(cls.database))
            cls.glue.delete_database(Name=cls.database)
        except cls.glue.exceptions.EntityNotFoundException:
            logger.info("Skipping deletion of database {} Since it was deleted in a previous step".format(cls.database))

    def setUp(self):
        if not self._check_table_exists(self.tablename):
            self._create_table()

    def _check_table_exists(self, tablename):
        try:
            self.glue.get_table(DatabaseName=self.database, Name=tablename)
            return True
        except self.glue.exceptions.EntityNotFoundException:
            return False

    def _check_database_exists(self, database):
        try:
            self.glue.get_database(Name=database)
            return True
        except self.glue.exceptions.EntityNotFoundException:
            return False

    def _create_table(self):
        logger.info("Creating Table: {}".format(self.tablename))
        self.athena_client.create_table(crawler_target={'S3Targets': [{'Path': self.source_file}]},
                                        table_name=self.tablename,
                                        aws_role=self.aws_role)

    def test_create_table(self):

        logger.info("running test_create_table")
        self.assertTrue(self._check_table_exists(self.tablename))

    def test_queries(self):
        logger.info("Querying athena")
        self.s3.delete_files(self.bucket, "pq")
        self.athena_client.add_query("select * from {}".format(self.tablename),
                                     "athena_test",
                                     "{0}pq/".format(self.output_location),
                                     parquet=True)
        count = self.athena_client.add_query("select count(*) from {}".format(self.tablename),
                                             "athena_test",
                                             self.output_location)
        self.athena_client.wait_for_completion()

        self.assertEqual(0, self.scp.number_active)
        self.assertEqual(0, self.athena_client.number_active)

        df_count = self.athena_client.get_query_result(count)
        self.assertEqual(df_count.iloc[0, 0], 42)

        # now try to create a table from the parquet files
        self.athena_client.create_table({'S3Targets': [{'Path': "{0}pq/".format(self.output_location)}]},
                                        table_name="pq",
                                        aws_role=self.aws_role)
        query = self.athena_client.add_query("select * from {}".format("pq"),
                                             "pq_test",
                                             self.output_location)
        self.athena_client.wait_for_completion()
        df_pq = self.athena_client.get_query_result(query)
        local_df = pd.read_csv(path.join(self.base_path, "demographic_data_op.csv"))
        df_pq.drop("partition_0", axis=1, inplace=True)
        self.assertTrue(df_pq.equals(local_df))

    def test_missing_scp_class(self):
        ac = AthenaClient(self.region, self.database)
        with self.assertRaises(AthenaClientError):
            ac.add_query("select * from {}".format(self.tablename),
                         "athena_test",
                         self.output_location,
                         parquet=True)

    def test_raise_athena_exception(self):
        logger.info("Checking if AthenaClient throws exception when a request\
                     for results of an incomplete query is made")

        query = self.athena_client.add_query("select * from {}".format(self.tablename),
                                             "athena_test",
                                             self.output_location)
        with self.assertRaises(AthenaClientError):
            self.athena_client.get_query_result(query)

    def test_raise_s3_exception(self):
        logger.info("Checking if S3Client throws exception when a invalid\
                     path is provided")
        with self.assertRaises(S3ClientError):
            self.s3.put_folder(self.invalid_file_location, self.bucket)

    def test_reset_query(self):
        """Test to check if is_complete  attribute for a failed query is
        set after checking query status"""
        with self.assertRaises(RetryException):
            query = self.athena_client.add_query("select {0} from {1}".format("table_doesnt_exist", self.tablename),
                                                 "athena_test",
                                                 self.output_location)
            self.athena_client.wait_for_completion()

    def test_maximum_retries_imposed(self):
        """Test to check query doesn't exceed maximum retries"""
        with self.assertRaises(RetryException):
            query = self.athena_client.add_query("select {0} from {1}".format("table_doesnt_exist", self.tablename),
                                                 "athena_test",
                                                 self.output_location)
            self.athena_client.wait_for_completion()

        self.athena_client._update_task_status(query)
        self.assertEqual(query.retries, 3)
        self.assertTrue(query.is_complete)
        self.assertEqual(query.error, "SYNTAX_ERROR: line 1:8: Column 'table_doesnt_exist' cannot be resolved")

    def test_update_columns_serde(self):
        """Test to check if serde and columns updates"""
        columns = [{'Name': 'jurisdiction name', 'Type': 'string'},
                   {'Name': 'count participants', 'Type': 'bigint'},
                   {'Name': 'count female', 'Type': 'bigint'},
                   {'Name': 'percent female', 'Type': 'double'},
                   {'Name': 'count male', 'Type': 'bigint'},
                   {'Name': 'percent male', 'Type': 'double'}]

        serde = 'org.apache.hadoop.hive.serde2.OpenCSVSerde'

        self.athena_client.create_table(crawler_target={'S3Targets': [{'Path': self.source_file}]},
                                        table_name=self.tablename,
                                        aws_role=self.aws_role,
                                        columns=columns,
                                        serde=serde)
        table = self.glue.get_table(DatabaseName=self.database, Name=self.tablename)["Table"]
        self.assertEqual(columns, table["StorageDescriptor"]["Columns"])
        self.assertEqual(serde, table["StorageDescriptor"]["SerdeInfo"]["SerializationLibrary"])
        self.glue.delete_database(Name=self.database)

    def test_ensuring_tasks_are_deleted_after_failure(self):
        """
        if a query fails, the athena client encompassing it should clean up queueing and running tasks during deletion
        """
        queries = []
        # this athena client should fail and delete itself
        doomed_ac = AthenaClient(region=self.region, db=self.database, s3_parquet=self.scp,
                                 max_retries=1, max_queries=2)
        doomed_ac.create_table(crawler_target={'S3Targets': [{'Path': "s3://gd.dativa.test/s3_upload_athena/",
                                                              "Exclusions": ["/demographic**"]}]},
                               table_name="long_file_of_ints_csv",
                               aws_role=self.aws_role)

        # may finish but will take a bit of time
        query_success = doomed_ac.add_query(sql="select distinct * from {}".format("long_file_of_ints_csv"),
                                            name="athena_test_success",
                                            output_location="{0}".format(self.output_location))
        queries.append(query_success)
        # this query will fail
        query_fail = doomed_ac.add_query("select * from {}".format("table_doesnt_exist"),
                                         "athena_test_failing",
                                         self.output_location)
        queries.append(query_fail)
        # intended to start running but not finish
        query_success2 = doomed_ac.add_query(sql="select distinct * from {}".format("long_file_of_ints_csv"),
                                            name="athena_test_success_2",
                                            output_location="{0}".format(self.output_location))
        queries.append(query_success2)
        # intended to be cancelled while still pending
        query_pending = doomed_ac.add_query(sql="select distinct * from {}".format("long_file_of_ints_csv"),
                                            name="athena_test_pending",
                                            output_location="{0}".format(self.output_location))
        queries.append(query_pending)
        self.assertGreater(doomed_ac.pending_tasks.qsize(), 0)
        self.assertGreater(len(doomed_ac.active_queue), 0)
        with self.assertRaises(RetryException):
            doomed_ac.wait_for_completion()
        self.assertEqual(doomed_ac.pending_tasks.qsize(), 0)
        self.assertEqual(len(doomed_ac.active_queue), 0)
