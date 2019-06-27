import uuid

import boto3

from orchestrate.common import safe_format
from orchestrate.core.services.aws_base import AwsService


class AwsStsService(AwsService):
  def __init__(self, services, aws_services, **kwargs):
    super(AwsStsService, self).__init__(services, aws_services)
    self._client = boto3.client('sts', **kwargs)

  @property
  def client(self):
    return self._client

  def assume_role(self, role_arn, duration_seconds=900):
    return self.client.assume_role(
      RoleArn=role_arn,
      RoleSessionName=safe_format('orchestrate-{}', uuid.uuid4()),
      DurationSeconds=duration_seconds,
    )
