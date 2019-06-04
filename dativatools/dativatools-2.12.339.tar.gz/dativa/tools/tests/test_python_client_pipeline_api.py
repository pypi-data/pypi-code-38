import time
import logging
import unittest
import os
import boto3
import pandas as pd
import json
from copy import deepcopy
from pandas.testing import assert_frame_equal
from dativa.tools.aws import PipelineClient, PipelineClientException, BucketPolicyAlreadyExists
from dativa.tools.aws import S3Location, S3Client
from botocore.exceptions import ClientError
from types import SimpleNamespace


logger = logging.getLogger("dativa.python_client.tests")


class TimeExceededException(Exception):
    pass


class PipelineClientTest(unittest.TestCase):
    # todo must use S3Location rather than current implementation!

    @classmethod
    def setUpClass(cls):
        """
        upload all files to the s3 bucket from local storage
        - could make it set bucket policy appropriately (currently it's doing this multiple times)
        - if files not present or unable to upload it will not run the rest of the tests
        """
        # read in API key and buckets to be used on AWS S3
        cls.api_key = os.environ["DATIVA_PIPELINE_API_KEY"]

        try:
            cls.bucket_only = os.environ["DATIVA_PIPELINE_API_BUCKET"]
        except KeyError:
            cls.bucket_only = "sanjeev-test-pipeline-demo"

        try:
            cls.bucket_only_dest = os.environ["DATIVA_PIPELINE_API_DESTINATION_BUCKET"]
        except KeyError:
            cls.bucket_only_dest = "sanjeev-test-pipeline-dest"

        try:
            cls.bucketregion = os.environ["DATIVA_PIPELINE_API_S3"]
            cls.bucketpath = cls.bucketregion + cls.bucket_only + "/"
        except KeyError:
            cls.bucketregion = "https://s3-us-west-2.amazonaws.com/"
            cls.bucketpath = cls.bucketregion + cls.bucket_only + "/"

        try:
            cls.bucketregion_dest = os.environ["DATIVA_PIPELINE_API_S3_DEST"]
            cls.bucketpath_dest = cls.bucketregion_dest + cls.bucket_only_dest + "/"
        except KeyError:
            cls.bucketregion_dest = "https://s3-us-west-2.amazonaws.com/"
            cls.bucketpath_dest = cls.bucketregion_dest + cls.bucket_only_dest + "/"
        cls.nonexistent_bucket = "the-bucket-that-should-not-be"
        cls.policy = {"Version": "2012-10-17",
                      "Statement": [
                          {
                              "Sid": "pipeline_permission",
                              "Effect": "Allow",
                              "Principal": {
                                  "AWS": "arn:aws:iam::538486622005:root"
                              },
                              "Action": "s3:*",
                              "Resource": "arn:aws:s3:::{}/*".format(cls.bucket_only)
                          }]
                      }

        cls.rules = [{'field': 'to',
                      'params': {'fallback_mode': 'remove_record',
                                 'maximum_length': 1024,
                                 'minimum_length': 5,
                                 'regex': '[^@]+@[^.]..*[^.]',
                                 'token_date_field': 'date',
                                 'token_date_format': '%Y-%m-%d %H:%M:%S',
                                 'token_store': 'https://s3-us-west-2.amazonaws.com/pipeline-api-demo/source/anonymization/email_list_%Y_%m_%d.csv',
                                 'tokenize': True},
                      'rule_type': 'String'},
                     {'field': 'from',
                      'params': {'fallback_mode': 'remove_record',
                                 'maximum_length': 1024,
                                 'minimum_length': 5,
                                 'regex': '[^@]+@[^.]..*[^.]',
                                 'token_date_field': 'date',
                                 'token_date_format': '%Y-%m-%d %H:%M:%S',
                                 'token_store': 'https://s3-us-west-2.amazonaws.com/pipeline-api-demo/source/anonymization/email_list_%Y_%m_%d.csv',
                                 'tokenize': True},
                      'rule_type': 'String'},
                     {'field': 'date',
                      'params': {'date_format': '%Y-%m-%d %H:%M:%S',
                                 'fallback_mode': 'remove_record',
                                 'range_maximum': '2100-01-01 00:00:00',
                                 'range_minimum': '1970-01-01 00:00:00'},
                      'rule_type': 'Date'},
                     {'field': 'subject',
                      'params': {'fallback_mode': 'remove_record',
                                 'maximum_length': 1024,
                                 'minimum_length': 0},
                      'rule_type': 'String'}]

        # identify local files to be used
        cls.filepath = os.path.dirname(os.path.abspath(__file__))
        cls.filepath_testdata = os.path.join(cls.filepath, "test_data", "pipeline_api")
        # todo write for destination bucket too
        cls.policyfile = os.path.join(cls.filepath_testdata, "policy.json")
        cls.rulesfile = os.path.join(cls.filepath_testdata, "rules.json")
        with open(cls.policyfile, "w") as file:
            file.write(json.dumps(cls.policy))
        with open(cls.rulesfile, "w") as file:
            file.write(json.dumps(cls.rules))

        # copy files to chosen S3 bucket
        s3c = S3Client()
        # s3c.delete_files(cls.bucket_only, "test_data/pipeline_api")
        s3c.put_folder(source=os.path.join(cls.filepath, "test_data", "pipeline_api"),
                       bucket=cls.bucket_only,
                       destination="test_data/pipeline_api/")

        # URLs for RESTful Pipeline API
        cls.base_url = "https://pipeline-api.dativa.com"
        cls.clean_endpoint = "/clean"
        cls.status_endpoint = "/status"
        cls.invalid_rest_request = "/not-a-valid-request"

    @staticmethod
    def cb_func(response, orig_base_path):
        s3 = boto3.client('s3')
        bucket = response.json()['destination']['s3_url'].split("/")[3]
        key = response.json()['destination']['s3_url'].split("/")[-1]
        local_path = os.path.join(orig_base_path, key)
        s3.download_file(bucket, key, local_path)

    @classmethod
    def tearDownClass(cls):
        local_path = os.path.join(cls.filepath_testdata, "emails.csv.cleaned")
        os.remove(local_path)

    def setUp(self):
        """
        Clear the bucket policy for the start of each test
        :return:
        """
        s3 = boto3.client("s3")
        s3.delete_bucket_policy(Bucket=self.bucket_only)
        s3.delete_bucket_policy(Bucket=self.bucket_only_dest)

    def test_run_job_required_params_only(self):
        s3 = boto3.client("s3")
        s3.delete_bucket_policy(Bucket=self.bucket_only)
        obj = PipelineClient(api_key=self.api_key,
                             rules="{}/rules.json".format(self.filepath_testdata),
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath)
                             )
        obj.set_s3_bucket_policy(self.policy)
        response = obj.run_job()
        while obj.check_status(response).json()['status'] not in ('ERROR', 'COMPLETED'):
            time.sleep(1)
        response = obj.check_status(response)
        s3_url = response.json()['destination']['s3_url']
        s3_url = "s3://{}".format("/".join(s3_url.split("/")[3:]))
        df_cl = pd.read_csv(s3_url)
        val_csv = "{0}/test_data/pipeline_api/emails.csv.clean".format(os.path.dirname(os.path.abspath(__file__)))
        df_val = pd.read_csv(val_csv)
        assert_frame_equal(df_cl, df_val)

    def test_BucketPolicyAlreadyExists(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath)
                             )
        obj.set_s3_bucket_policy(self.policy)

        with self.assertRaises(BucketPolicyAlreadyExists):
            obj.run_job_synchronously(True, True)

    def test_BucketPolicyExceptionOther(self):
        bucket = self.nonexistent_bucket
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}{}/test_data/pipeline_api/emails.csv".format(self.bucketregion, bucket)
                             )

        with self.assertRaises(PipelineClientException):
            obj.run_job_synchronously(update_policy=True,
                                      delete_policy_after_job_run=True)

    def test_run_job(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{0}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             destination_s3_url="{0}emails.csv".format(self.bucketpath),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8"
                             )
        obj.set_s3_bucket_policy(self.policy)
        response = obj.run_job()
        while obj.check_status(response).json()['status'] not in ('ERROR', 'COMPLETED'):
            time.sleep(1)
        response = obj.check_status(response)
        s3_url = response.json()['destination']['s3_url']
        s3_url = "s3://{}".format("/".join(s3_url.split("/")[3:]))
        df_cl = pd.read_csv(s3_url)
        val_csv = "{0}/emails.csv.clean".format(self.filepath_testdata)
        df_val = pd.read_csv(val_csv)
        assert_frame_equal(df_cl, df_val)

    def test_run_job_synchronously(self):

        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{0}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             destination_s3_url="{0}emails.csv".format(self.bucketpath),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8"
                             )

        response = obj.run_job_synchronously(update_policy=True,
                                             delete_policy_after_job_run=True
                                             )

        s3_url = response.json()['destination']['s3_url']
        s3_url = "s3://{}".format("/".join(s3_url.split("/")[3:]))
        df_cl = pd.read_csv(s3_url)
        val_csv = "{0}/emails.csv.clean".format(self.filepath_testdata)
        df_val = pd.read_csv(val_csv)
        assert_frame_equal(df_cl, df_val)

    def test_set_s3_bucket_policy(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             destination_s3_url="{}emails.csv".format(self.bucketpath),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8"
                             )
        for resp in obj.set_s3_bucket_policy(self.policy):
            self.assertEqual(resp["ResponseMetadata"]["HTTPStatusCode"], 204)

    def test_set_s3_bucket_policy_file(self):
        policy = self.policy
        policy_dest = os.path.join(self.filepath_testdata, "policy_dest.json")
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             destination_s3_url="{}emails.csv".format(self.bucketpath_dest),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8",
                             source_quotechar='\"',
                             source_skiprows=0,
                             source_strip_whitespace=True,
                             source_header=0
                             )
        for resp in obj.set_s3_bucket_policy(policy, policy_dest):
            self.assertEqual(resp["ResponseMetadata"]["HTTPStatusCode"], 204)

    def test_set_s3_bucket_policy_invalid(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             destination_s3_url="{}emails.csv".format(self.bucketpath_dest),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8"
                             )
        with self.assertRaises(PipelineClientException):
            obj.set_s3_bucket_policy([], [])

    def test_run_job_with_callback(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             destination_s3_url="{}emails.csv".format(self.bucketpath_dest),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8"
                             )

        local_path = os.path.join(self.filepath_testdata, "emails.csv.cleaned")
        response = obj.run_job_with_callback(callback=lambda x: self.cb_func(x, self.filepath_testdata),
                                             update_policy=True,
                                             delete_policy_after_job_run=True,
                                             response=None,
                                             call_no=0
                                             )

        # wait for completion and check for file return
        while not (obj.check_status(response).json()['status'] in ('ERROR', 'COMPLETED')):
            time.sleep(1)
        else:
            counter = 0
            while not os.path.exists(local_path):
                logger.info("%s", local_path)
                if counter >= 10:
                    raise TimeExceededException("Callback taking too long to be called")
                time.sleep(5)
                counter += 1

    def test_run_job_with_callback_call_limit(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             destination_s3_url="{}emails.csv".format(self.bucketpath_dest),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8"
                             )

        with self.assertRaises(ValueError):
            obj.run_job_with_callback(callback=self.cb_func,
                                      update_policy=True,
                                      delete_policy_after_job_run=True,
                                      response=None,
                                      call_no=11)

    def test_job_passing_fp_error_incorrect_config(self):
        """
        Provides invalid rule set - this rule set is not valid with rule_type Number hence will give error
        """
        broken_rules = deepcopy(self.rules[0])
        broken_rules["rule_type"] = "Number"
        obj = PipelineClient(api_key=self.api_key,
                             rules=[broken_rules],
                             source_s3_url="{0}test_data/anonymization/emails.csv".format(self.bucketpath),
                             destination_s3_url="{0}emails.csv".format(self.bucketpath),
                             source_delimiter=",",
                             destination_delimiter=",",
                             source_encoding="UTF-8",
                             destination_encoding="UTF-8"
                             )
        with self.assertRaises(PipelineClientException):
            obj.run_job_synchronously(update_policy=True,
                                      delete_policy_after_job_run=True)

    def test_job_with_invalid_report(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath)
                             )

        with self.assertRaises(PipelineClientException):
            obj._response_validator([])

    def test_with_invalid_job_id(self):
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath)
                             )

        # a function which returns a faux job-id which is not valid
        def json():
            return {"job_id": 0}

        dummy_report = SimpleNamespace()
        dummy_report.json = json
        with self.assertRaises(PipelineClientException):
            obj._response_validator(dummy_report)

    def test_deleting_bucket_policy_on_nonexistent_bucket(self):
        s3 = boto3.client("s3")
        with self.assertRaises(ClientError):
            s3.delete_bucket_policy(Bucket=self.nonexistent_bucket)

    def test_custom_url(self):
        """
        check client call to api with custom url to access restful functions
        """
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             base_url=self.base_url,
                             clean_endpoint=self.clean_endpoint,
                             status_endpoint=self.status_endpoint
                             )
        obj.run_job_synchronously(update_policy=True,
                                  delete_policy_after_job_run=True)

    def test_invalid_url(self):
        """
        make sure it's not ignoring the input by giving it an invalid url - this should give an error
        """
        obj = PipelineClient(api_key=self.api_key,
                             rules=self.rules,
                             source_s3_url="{}test_data/pipeline_api/emails.csv".format(self.bucketpath),
                             base_url="s3://pipeline-api.dativa.com"
                             )

        with self.assertRaises(ValueError):
            obj.run_job_synchronously(update_policy=True,
                                      delete_policy_after_job_run=True)
