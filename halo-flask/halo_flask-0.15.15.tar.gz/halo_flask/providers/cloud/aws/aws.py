from __future__ import print_function
import json
import logging
import boto3
from botocore.exceptions import ClientError
from halo_flask.exceptions import ProviderError
from halo_flask.logs import log_json
from halo_flask.providers.providers import Provider

from halo_flask.settingsx import settingsx

settings = settingsx()
logger = logging.getLogger(__name__)

class AwsProvider(Provider) :

    @classmethod
    def send_event(self,ctx,messageDict,service_name):
        try:
            client = boto3.client('lambda', region_name=settings.AWS_REGION)
            ret = client.invoke(
                FunctionName=service_name,
                InvocationType='Event',
                LogType='None',
                Payload=bytes(json.dumps(messageDict), "utf8")
            )
            return ret
        except ClientError as e:
            logger.error("Unexpected boto client Error", extra=log_json(ctx, messageDict, e))
            raise ProviderError(e)


