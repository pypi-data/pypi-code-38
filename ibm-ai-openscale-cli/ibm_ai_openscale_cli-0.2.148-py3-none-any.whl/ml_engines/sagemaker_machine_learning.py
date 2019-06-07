# coding=utf-8
import boto3
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import json
import time
from ibm_ai_openscale.supporting_classes import PayloadRecord

logger = FastpathLogger(__name__)

class SageMakerMachineLearningEngine:

    def __init__(self, credentials):
        access_id = credentials['access_key_id']
        access_key = credentials['secret_access_key']
        region = credentials['region']
        self._runtime = boto3.client('sagemaker-runtime', region_name=region, aws_access_key_id=access_id, aws_secret_access_key=access_key)

    def setup_scoring_metadata(self, subscription):
        subscription_details = subscription.get_details()
        self._endpoint_name = subscription_details['entity']['deployments'][0]['name']

    def score(self, fields, data):
        start_time = time.time()
        req_text = ','.join(str(s) for s in data)
        response = self._runtime.invoke_endpoint(EndpointName=self._endpoint_name, ContentType='text/csv', Body=req_text)
        response_time = time.time() - start_time
        result = json.loads(response['Body'].read().decode())
        response_data = {
            'fields': list(result['predictions'][0]),
            'values': [list(x.values()) for x in result['predictions']]
        }
        # values = []
        # for v in data.split('\n'):
        #     values.append([float(s) for s in v.split(',')])
        request_data = {
            'fields': fields,
            'values': data
        }
        record = PayloadRecord(request=request_data, response=response_data, response_time=int(response_time))
        return record
