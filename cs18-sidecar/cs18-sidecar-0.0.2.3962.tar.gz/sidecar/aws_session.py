from typing import Optional

import boto3
from botocore.config import Config
from logging import Logger

from sidecar.model.objects import AwsSidecarConfiguration
from sidecar.utils import Utils


class AwsSession:
    def __init__(self, region_name: str, aws_config: AwsSidecarConfiguration, logger: Logger):

        self.logger = logger
        self.aws_config = aws_config
        self._sandbox_stack_name = None

        config_dict = {'connect_timeout': 20, 'read_timeout': 20, 'max_pool_connections': 100,
                       'retries': {'max_attempts': 2}}
        self._config = Config(**config_dict)
        self._region_name = region_name

        self._init_session()

        self.cf_client = self._get_client('cloudformation', self._config)

        if aws_config:
            try:
                Utils.wait_for(func=lambda: self._test_credentials() is not None,
                               interval_sec=1,
                               max_retries=5,
                               error='Credentials service is not responding')
            except Exception:
                self.logger.exception(msg="Failed to access credentials service after 5 times")
                return

        self.ec2_client = self._get_client('ec2', self._config)

        self.ec2_resource = self._get_resource('ec2', self._config)
        self._autoscalling_client = self._get_client('autoscaling', self._config)
        self._elb_client = self._get_client('elb', self._config)
        self._elb_v2_client = self._get_client('elbv2', self._config)
        self.cloudwatch_client = self._get_client('logs', self._config)

    def _init_session(self):
        self.session = boto3.Session()

    def get_ec2_client(self):
        return self.ec2_client

    def get_cf_client(self):
        return self.cf_client

    def get_ec2_resource(self):
        return self.ec2_resource

    def get_cloudwatch_client(self):
        return self.cloudwatch_client

    def get_autoscaling_client(self):
        return self._autoscalling_client

    def get_elb_client(self):
        return self._elb_client

    def get_elb_v2_client(self):
        return self._elb_v2_client

    def _get_client(self, client: str, config: Config):
        return self.session.client(client, region_name=self._region_name, config=config)

    def _get_resource(self, resource: str, config: Config):
        return self.session.resource(resource, region_name=self._region_name, config=config)

    def get_dynamo_resource(self, default_region: str = None):
        region = self._region_name

        if default_region:
            region = default_region

        return self.session.resource('dynamodb', region_name=region, config=self._config)

    def _test_credentials(self):
        try:
            response = self.cf_client.describe_stacks(StackName=self.sandbox_stack_name, NextToken='0')
            self.logger.info("test credentials Success")
            return response
        except Exception:
            self.logger.info("test credentials FAIL", exc_info=True)
            return None

    @property
    def sandbox_stack_name(self) -> str:
        if not self._sandbox_stack_name:
            if self.aws_config.production_id:
                self._sandbox_stack_name = f'production-{self.aws_config.production_id}-sandbox-{self.aws_config.sandbox_id}'
            else:
                self._sandbox_stack_name = f'sandbox-{self.aws_config.sandbox_id}'

        return self._sandbox_stack_name

    @property
    def production_infra_stack_name(self) -> Optional[str]:
        if self.aws_config.production_id:
            return f'production-{self.aws_config.production_id}'
        else:
            return None
