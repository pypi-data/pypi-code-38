# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)
"""This script enables users to query the pipeline
api on the aws marketplace. Pipeline api helps to
clean csvs as per rules specified"""
import time
import json
import threading
import logging
from copy import deepcopy

try:
    import requests
except ImportError:
    requests = None

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None


pipeline_logger = logging.getLogger("dativa.tools.aws")


class PipelineClientException(Exception):
    """
    General Exception class to be raised
    for PipelineClient errors
    """
    pass


class BucketPolicyAlreadyExists(Exception):
    """
    General Exception class to be raised
    for PipelineClient errors
    """
    pass


class PipelineClient:
    """
    PipelineClient class, provide api key, source s3 location,
    destination s3 location, rules, and get source file cleaned and
    posted to destination.
    :param api_key                  : The individual key provided by the pipeline api
    :type api_key                   : str
    :param source_s3_url            : The s3 source where the
                                      csv files are present
    :type source_s3_url             : str
    :param destination_s3_url       : The destination where the files
                                      are to be posted after cleansing
    :type destination_s3_url        : str
    :param rules                    : Rules by which to clean the file
    :type rules                     : list, str specifying location of the rules file
    :param base_url                 : The url of the pipeline api, appends clean and status endpoints to get functions,
                                      defaults to
                                      https://pipeline-api.dativa.com
    :type base_url                  : str
    :param clean_endpoint           : The url of clean request for the pipeline api, defaults to
                                      /clean
    :type clean_endpoint            : str
    :param status_endpoint          : the url to query for to check status of the api call, defaults to
                                      /status
    :type status_endpoint           : str
    :param source_delimiter         : the delimiter of the source file, defaults to ,
    :type source_delimiter          : str
    :param destination_delimiter    : the delimiter of the destination file, defaults to ,
    :type destination_delimiter     : str
    :param source_encoding          : the encoding of the source file, defaults to utf-8
    :type source_encoding           : str
    :param destination_encoding     : the encoding of the destination file, defaults to utf-8
    :type destination_encoding      : str
    :param source_quotechar         : the quotechar in the source file
    :type source_quotechar          : str
    :param source_skiprows          : The rows to skip in the source file
    :type source_skiprows           : int
    :param source_strip_whitespace  : Strips white space in source if set to True
    :type source_strip_whitespace   : bool
    :param source_header            : the row in source to consider as header
    :param source_header            : int
    """

    base_url = "https://pipeline-api.dativa.com"
    clean_endpoint = "/clean"
    status_endpoint = "/status"

    headers = {
        'Content-type': 'application/json',
        'x-api-key': ''
        }

    data = {
        'source': {
            'delimiter': ',',
            'encoding': 'UTF-8',
            's3_url': '',
            'quotechar': '\"',
            'skiprows': 0,
            'strip_whitespace': True,
            'header': 0
            },
        'rules': [],
        }

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "pipeline_permission",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::538486622005:root"
                    },
                "Action": "s3:*",
                "Resource": "arn:aws:s3:::{0}/*"
                }
            ]
        }

    def __init__(self,
                 api_key,
                 rules,
                 source_s3_url,
                 destination_s3_url=None,
                 base_url=None,
                 status_endpoint=None,
                 clean_endpoint=None,
                 source_delimiter=None,
                 destination_delimiter=None,
                 source_encoding=None,
                 destination_encoding=None,
                 source_quotechar=None,
                 source_skiprows=None,
                 source_strip_whitespace=None,
                 source_header=None):

        if not boto3:
            raise ImportError("boto3 must be installed to run PipelineClient")

        if not requests:
            raise ImportError("requests must be installed to run PipelineClient")

        self.headers['x-api-key'] = api_key
        self.data['source']['s3_url'] = source_s3_url
        self.source_bucket = self.data['source']['s3_url'].split("/")[3]

        if destination_s3_url:
            self.data['destination'] = dict(s3_url=destination_s3_url)
            self.dest_bucket = destination_s3_url.split("/")[3]
            if destination_encoding:
                self.data['destination']['encoding'] = destination_encoding
            if destination_delimiter:
                self.data['destination']['delimiter'] = destination_delimiter

        if base_url:
            self.base_url = base_url
        if status_endpoint:
            self.status_endpoint = status_endpoint
        if clean_endpoint:
            self.clean_endpoint = clean_endpoint
        if source_delimiter:
            self.data['source']['delimiter'] = source_delimiter
        if source_encoding:
            self.data['source']['encoding'] = source_encoding
        if source_quotechar:
            self.data['source']['quotechar'] = source_quotechar
        if source_skiprows != None:
            self.data['source']['skiprows'] = source_skiprows
        if source_strip_whitespace:
            self.data['source']['strip_whitespace'] = source_strip_whitespace
        if source_header != None:
            self.data['source']['header'] = source_header

        if isinstance(rules, str):
            with open(rules, 'r') as rules_file:
                self.data['rules'] = json.load(rules_file)
        elif isinstance(rules, list):
            self.data['rules'] = rules

    def _force_s3_policy(self):
        buckets = [self.source_bucket]
        if hasattr(self, "dest_bucket") and self.source_bucket != self.dest_bucket:
            buckets.append(self.dest_bucket)
        s3_client = boto3.client("s3")
        for bucket in buckets:
            policy = deepcopy(self.policy)
            policy["Statement"][0]["Resource"] = policy["Statement"][0]["Resource"].format(bucket)
            try:
                s3_client.get_bucket_policy(Bucket=bucket)
                raise BucketPolicyAlreadyExists("Bucket policy already exists for {0}".format(bucket))
            except ClientError as e:
                if "NoSuchBucketPolicy" in e.__str__():
                    s3_client.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
                    pipeline_logger.info("Applying default bucket policy to %s",
                                         bucket)
                else:
                    raise PipelineClientException("The following error occured"\
                                                  " while updating bucket policy {0}".format(e.__str__()))

    def _delete_bucket_policy(self):
        self.delete_bucket_policy(self.source_bucket)
        if hasattr(self, "dest_bucket") and self.source_bucket != self.dest_bucket:
            self.delete_bucket_policy(self.dest_bucket)

    @staticmethod
    def delete_bucket_policy(bucket, iteration=0, max_iteration=5):
        s3_client = boto3.client("s3")
        try:
            s3_client.get_bucket_policy(Bucket=bucket)
            if iteration < max_iteration:
                PipelineClient.delete_bucket_policy(bucket, iteration+1)
                time.sleep(0.1)
        except ClientError as e:
            if "NoSuchBucketPolicy" in e.__str__():
                return
            else:
                raise PipelineClientException("The following error occurred while deleting bucket policy "
                                              "{0} after {1} iterations".format(e.__str__(), iteration))

    @staticmethod
    def _response_validator(response):
        """
        ensures that the response from a REST request is not mangled
        :param response: the response from the requests module
        :type response: requests.Response
        """
        try:
            response_json = response.json()
            if not isinstance(response_json['job_id'], str):
                pipeline_logger.debug("Invalid job ID picked up by report validator")
                raise PipelineClientException("Process returned json file which contained no job_id.")

        except (KeyError, AttributeError) as e:
            raise PipelineClientException('Response object did not contain expected key/attribute: {}'.
                                          format(repr(e)))

    @staticmethod
    def _report_validator(report):
        """
        Checks whether the current status of a job is in error, if so it raises exceptions as appropriate
        :param report: the body of the response from check_status
        :type report: requests.Response.json()
        """
        if report['status'] == "ERROR":
            raise PipelineClientException("Execution error - {}. "
                                          "Check report associated with job_id {} for more details."
                                          .format(report["reason"], report["job_id"]))

    def run_job(self):
        """
        Query the api using the specified parameters.
        :return : response from querying the api
        :rtype  : requests.models.Response
        """
        clean_url = self.base_url + self.clean_endpoint

        pipeline_logger.info("Cleaning file %s",
                             self.data['source']['s3_url'])
        response = requests.post(
            url=clean_url,
            headers=self.headers,
            data=json.dumps(self.data)
        )
        self._response_validator(response)
        pipeline_logger.info("Queried api, job id %s",
                             response.json()['job_id'])
        return response

    def check_status(self, response):
        """
        Check the status of the job,
        using the job id from the response
        object.
        :param response : response from querying the api
        :type response  : requests.models.Response
        :return         : response with status from querying the api
        :rtype          : requests.models.Response
        """
        response_json = response.json()
        job_id = response_json['job_id']
        pipeline_logger.debug("Checking status of job %s", job_id)
        status_url = self.base_url + self.status_endpoint + '/{}'.format(job_id)
        pipeline_logger.debug("Checking status of job %s", job_id)
        status_response = requests.get(
            status_url,
            headers=self.headers
        )
        pipeline_logger.debug("The status of job, %s, is %s",
                              job_id, status_response.json()['status'])
        return status_response

    def run_job_synchronously(self, update_policy=False, delete_policy_after_job_run=True, response_check_delay=5):
        """
        Run job specified in client synchronously
        :param update_policy: whether to update bucket policy prior to running job - will fail if policy is already set
        :type update_policy: bool
        :param delete_policy_after_job_run: whether to delete bucket policy after successfully finishing job
        :type delete_policy_after_job_run: bool
        :param response_check_delay: time (in seconds) between each poll of the job status - if running many tasks this
        can be set higher to avoid running out of API Gateway requests associated with each API Key
        :type response_check_delay: float or int, time in seconds
        :return:  response with status from querying the api
        :rtype requests.models.Response
        """
        if update_policy:
            self._force_s3_policy()
        response = self.run_job()
        pipeline_logger.info("Cleaning file %s",
                             self.data['source']['s3_url'])
        current_report = self.check_status(response).json()
        while current_report['status'] != 'COMPLETED':
            self._response_validator(response=response)
            current_report = self.check_status(response).json()
            self._report_validator(report=current_report)
            pipeline_logger.info("...waiting for completion - job_id{} status {}".format(
                current_report["job_id"], current_report["status"]))
            time.sleep(response_check_delay)

        self._report_validator(report=current_report)
        pipeline_logger.info("Job run completed %s", response.json()['job_id'])
        if delete_policy_after_job_run:
            self._delete_bucket_policy()
        return self.check_status(response)

    def run_job_with_callback(self, callback, update_policy=False, delete_policy_after_job_run=True, response=None, call_no=0, *args):
        """
        Run job asynchronously with callback
        :param callback : Function to call after job is completed
        :type callback  : function
        :param response : response from running job
        :type response  : requests.models.Response or None
        :param call_no  : the number of time the function was called
        :type call_no   : int
        """
        if call_no > 10:
            raise ValueError("Max Retries limit reached")
        call_no += 1
        if not response:
            pipeline_logger.info("Cleaning file %s",
                                 self.data['source']['s3_url'])
            if update_policy:
                self._force_s3_policy()
            response = self.run_job()
        if self.check_status(response).json()['status'] in ('ERROR', 'COMPLETED'):
            pipeline_logger.info("Job %s completed, calling callback",
                                 response.json()['job_id'])
            callback(self.check_status(response), *args)
            if delete_policy_after_job_run:
                self._delete_bucket_policy()
        else:
            pipeline_logger.info("Waiting for error or completion of job, %s",
                                 response.json()['job_id'])
            threading.Timer(3, self.run_job_with_callback,
                            [callback, update_policy, delete_policy_after_job_run, response, call_no] + list(args)).start()
        return response

    @staticmethod
    def _get_s3_policy(policy):
        if isinstance(policy, dict):
            result = json.dumps(policy)
        elif isinstance(policy, str):
            with open(policy, 'r') as policy_doc:
                result = json.dumps(json.load(policy_doc))
        else:
            raise PipelineClientException("Policy has to be dict or string"
                                          " specifying the location of the policy document")
        return result

    def set_s3_bucket_policy(self, policy, policy_dest=None):
        """
        Sets the bucket policy for both source
        and destination bucket to allow pipeline
        api access to the bucket.
        :param policy : location of the policy document,
                        dictionary of the policy
        :type policy  : dict, str
        """
        policy = PipelineClient._get_s3_policy(policy)
        if policy_dest:
            policy_dest = PipelineClient._get_s3_policy(policy_dest)
        s3_client = boto3.client('s3')
        response = []
        pipeline_logger.info("Applying policy allowing access for api on source")
        response.append(s3_client.put_bucket_policy(Bucket=self.source_bucket, Policy=policy))
        if hasattr(self, "dest_bucket") and (self.source_bucket != self.dest_bucket):
            pipeline_logger.info("Applying policy allowing access for api on destination")
            response.append(
                s3_client.put_bucket_policy(
                    Bucket=self.dest_bucket, Policy=policy_dest
                    )
                )
        return response
