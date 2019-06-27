import json

import boto3
from botocore.exceptions import ClientError

from orchestrate.common import safe_format
from orchestrate.core.services.aws_base import AwsService


# From https://docs.aws.amazon.com/eks/latest/userguide/service_IAM_role.html
EKS_ASSUME_ROLE_POLICY_DOCUMENT = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

# From https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html
# https://docs.aws.amazon.com/cli/latest/userguide/cli-roles.html
CLUSTER_ACCESS_ASSUME_ROLE_POLICY_DOCUMENT = {
  "Version": "2012-10-17",
  "Statement": {
    "Effect": "Allow",
    "Principal": {
      "AWS": None
    },
    "Action": "sts:AssumeRole",
  }
}


class AwsIamService(AwsService):
  def __init__(self, services, aws_services, **kwargs):
    super(AwsIamService, self).__init__(services, aws_services)
    self._client = boto3.client('iam', **kwargs)
    self._iam = boto3.resource('iam', **kwargs)

  @property
  def client(self):
    return self._client

  @property
  def iam(self):
    return self._iam

  def get_user_arn(self):
    response = self.client.get_user()
    user = response['User']
    return user['Arn']

  def cluster_access_role_name(self, cluster_name):
    return safe_format('{}-k8s-access-role', cluster_name)

  def describe_cluster_access_role(self, cluster_name):
    return self.iam.Role(self.cluster_access_role_name(cluster_name))

  def delete_cluster_access_role(self, cluster_name):
    role = self.describe_cluster_access_role(cluster_name)

    for policy in role.attached_policies.all():
      role.detach_policy(PolicyArn=policy.arn)

    for role_policy in role.policies.all():
      role_policy.delete()

    role.delete()

  def create_cluster_access_role(self, cluster_name):
    assume_role_policy_document = CLUSTER_ACCESS_ASSUME_ROLE_POLICY_DOCUMENT.copy()
    assume_role_policy_document['Statement']['Principal']['AWS'] = self.get_user_arn()
    return self.iam.create_role(
      RoleName=self.cluster_access_role_name(cluster_name),
      AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
      Description=safe_format('Access the kubernentes cluster: {}, created by orchestrate', cluster_name),
    )

  def ensure_cluster_access_role(self, cluster_name):
    try:
      self.create_cluster_access_role(cluster_name)
    except self.client.exceptions.EntityAlreadyExistsException:
      pass

    return self.describe_cluster_access_role(cluster_name)

  def ensure_cluster_access_role_deleted(self, cluster_name):
    try:
      self.delete_cluster_access_role(cluster_name)
    except self.client.exceptions.NoSuchEntityException:
      pass

  def create_eks_role(self, cluster_name):
    eks_role = self.iam.create_role(
      RoleName=self.eks_role_name(cluster_name),
      AssumeRolePolicyDocument=json.dumps(EKS_ASSUME_ROLE_POLICY_DOCUMENT),
      Description='Allows EKS to manage clusters on your behalf.'
    )

    eks_role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AmazonEKSClusterPolicy')
    eks_role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AmazonEKSServicePolicy')

    return eks_role

  def delete_eks_role(self, cluster_name):
    role = self.describe_eks_role(cluster_name)

    for policy in role.attached_policies.all():
      role.detach_policy(PolicyArn=policy.arn)

    role.delete()

  def describe_eks_role(self, cluster_name):
    return self.iam.Role(self.eks_role_name(cluster_name))

  def eks_role_name(self, cluster_name):
    return safe_format('{}-eks-role', cluster_name)

  def ensure_eks_role(self, cluster_name):
    try:
      self.create_eks_role(cluster_name)
    except self.client.exceptions.EntityAlreadyExistsException:
      pass
    except ClientError as e:
      if not e.response['Error']['Code'] == 'AccessDenied':
        raise

    return self.describe_eks_role(cluster_name)

  def ensure_eks_role_deleted(self, cluster_name):
    try:
      self.delete_eks_role(cluster_name)
    except self.client.exceptions.NoSuchEntityException:
      pass

  def node_instance_role_from_worker_stack(self, worker_stack):
    role_arn = next(o['OutputValue'] for o in worker_stack.outputs if o['OutputKey'] == 'NodeInstanceRole')
    role_name = role_arn.split(':role/')[1]
    role = self.iam.Role(role_name)
    assert role.arn == role_arn
    return role
