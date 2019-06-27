import random
import re
import time

import boto3

from orchestrate.common import safe_format
from orchestrate.core.services.aws_base import AwsService


class AwsEksService(AwsService):
  def __init__(self, services, aws_services, **kwargs):
    super(AwsEksService, self).__init__(services, aws_services)
    self._client = boto3.client('eks', **kwargs)

  @property
  def client(self):
    return self._client

  @property
  def region(self):
    return boto3.session.Session().region_name

  # According to https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html cluster
  # create time is "usually less than 10 minutes"
  def wait_for_cluster_created(self, cluster_name, tries=30):
    assert tries > 0, 'Timeout'

    cluster_status = self.describe_cluster(cluster_name)['cluster']['status']
    if cluster_status == 'ACTIVE':
      return
    elif cluster_status in ['FAILED' or 'DELETING']:
      raise Exception(safe_format('Cluster status is: {}', cluster_status))

    time.sleep(random.uniform(30, 31))
    self.wait_for_cluster_created(cluster_name=cluster_name, tries=(tries - 1))

  def wait_for_cluster_deleted(self, cluster_name, tries=30):
    assert tries > 0, 'Timeout'

    try:
      cluster_status = self.describe_cluster(cluster_name)['cluster']['status']
    except self.client.exceptions.ResourceNotFoundException:
      return

    if cluster_status == 'FAILED':
      raise Exception(safe_format('Cluster status is: {}', cluster_status))

    time.sleep(random.uniform(30, 31))
    self.wait_for_cluster_deleted(cluster_name=cluster_name, tries=(tries - 1))

  def create_cluster(self, cluster_name, eks_role, security_groups, subnet_ids):
    return self.client.create_cluster(
      name=cluster_name,
      roleArn=eks_role.arn,
      resourcesVpcConfig=dict(
        subnetIds=subnet_ids,
        securityGroupIds=security_groups,
      )
    )

  def delete_cluster(self, cluster_name):
    self.client.delete_cluster(name=cluster_name)

  def describe_cluster(self, cluster_name):
    return self.client.describe_cluster(name=cluster_name)

  def ensure_cluster(
    self,
    cluster_name,
    eks_role,
    security_groups,
    subnet_ids,
  ):
    try:
      self.create_cluster(
        cluster_name=cluster_name,
        eks_role=eks_role,
        security_groups=security_groups,
        subnet_ids=subnet_ids,
      )
    except self.client.exceptions.UnsupportedAvailabilityZoneException as e:
      if self.region != 'us-east-1':
        raise
      match = re.match('.*(us-east-1[a-z]), (us-east-1[a-z]), (us-east-1[a-z])', str(e))
      if not match:
        raise
      valid_zones = match.groups()
      subnets = self.aws_services.ec2_service.get_subnets(subnet_ids)
      filtered_subnet_ids = [
        subnet.id for subnet in subnets
        if subnet.availability_zone in valid_zones
      ]
      if not filtered_subnet_ids:
        raise
      self.create_cluster(
        cluster_name=cluster_name,
        eks_role=eks_role,
        security_groups=security_groups,
        subnet_ids=filtered_subnet_ids,
      )
    except self.client.exceptions.ResourceInUseException:
      pass

    self.wait_for_cluster_created(cluster_name)
    return self.describe_cluster(cluster_name)

  def ensure_cluster_deleted(self, cluster_name):
    try:
      self.delete_cluster(cluster_name)
      self.wait_for_cluster_deleted(cluster_name=cluster_name)
    except self.client.exceptions.ResourceNotFoundException:
      pass
