from __future__ import print_function

import re
import time
import traceback
import types
from concurrent.futures import ThreadPoolExecutor, as_completed, thread

import six
import yaml
from botocore.exceptions import ClientError
from cement.core.exc import CaughtSignal

from orchestrate.common import safe_format
from orchestrate.core.cluster.object import AWSCluster
from orchestrate.core.exceptions import (
  AwsClusterSharePermissionError,
  AwsPermissionsError,
  ClusterDestroyError,
  OrchestrateException,
)
from orchestrate.core.paths import get_executable_path
from orchestrate.core.provider.interface import ProviderInterface


def catch_aws_permissions_errors(func):
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except ClientError as e:
      code = e.response['Error']['Code']
      http_status_code = e.response['ResponseMetadata']['HTTPStatusCode']
      if http_status_code == 403 or code in ('AccessDeniedException', 'UnauthorizedOperation'):
        six.raise_from(AwsPermissionsError(e), e)
      raise
  return wrapper

class AwsService(ProviderInterface):
  def __init__(self, services, aws_services):
    super(AwsService, self).__init__(services)
    self.aws_services = aws_services

  def __getattribute__(self, name):
    attr = super(AwsService, self).__getattribute__(name)
    if isinstance(attr, types.MethodType):
      attr = catch_aws_permissions_errors(attr)
    return attr

  def describe_kubernetes_cluster(self, cluster_name):
    try:
      return self.aws_services.eks_service.describe_cluster(cluster_name=cluster_name)['cluster']
    except self.aws_services.eks_service.client.exceptions.ResourceNotFoundException as e:
      six.raise_from(
        OrchestrateException(safe_format(
          "We cannot find an EKS cluster named '{}' using your current AWS credentials."
          " Did someone delete this cluster?",
          cluster_name
        )),
        e
      )

  def validate_cluster_options(self, cluster_name, cpu_nodes_config, gpu_nodes_config):
    assert cpu_nodes_config or gpu_nodes_config, "Looks like your cluster config file is not" \
      " asking us to spin up any CPU or GPU machines."
    name_regex = '^[a-zA-Z][-a-zA-Z0-9]*$'
    assert cluster_name and re.match(name_regex, cluster_name), \
      'Cluster names for AWS must match the regex: /' + name_regex + '/'

  def create_kubernetes_cluster(self, options):
    cluster_name = options['cluster_name']
    cpu_nodes_config = options.get('cpu')
    gpu_nodes_config = options.get('gpu')
    self.validate_cluster_options(cluster_name, cpu_nodes_config, gpu_nodes_config)

    aws_options = options.get('aws') or {}
    additional_policies = aws_options.get('additional_policies') or []

    role = self.aws_services.iam_service.ensure_eks_role(cluster_name=cluster_name)
    eks_vpc_stack = self.aws_services.cloudformation_service.ensure_eks_vpc_stack(cluster_name=cluster_name)
    eks_vpc_stack_outputs = dict((o['OutputKey'], o['OutputValue']) for o in eks_vpc_stack.outputs)
    security_groups = eks_vpc_stack_outputs.get('SecurityGroups', '').split(',')
    subnet_ids = eks_vpc_stack_outputs.get('SubnetIds', '').split(',')

    self.aws_services.eks_service.ensure_cluster(
      cluster_name=cluster_name,
      eks_role=role,
      security_groups=security_groups,
      subnet_ids=subnet_ids,
    )

    key_name = self.aws_services.ec2_service.ensure_key_pair_for_cluster(cluster_name).name

    worker_stacks = []
    if cpu_nodes_config:
      cpu_worker_stack = self.aws_services.cloudformation_service.ensure_eks_worker_stack(
        cluster_name=cluster_name,
        security_groups=eks_vpc_stack_outputs.get('SecurityGroups', '').split(','),
        vpc_id=eks_vpc_stack_outputs.get('VpcId'),
        subnet_ids=eks_vpc_stack_outputs.get('SubnetIds', '').split(','),
        max_nodes=cpu_nodes_config['max_nodes'],
        min_nodes=cpu_nodes_config['min_nodes'],
        instance_type=cpu_nodes_config['instance_type'],
        key_name=key_name,
        gpu=False,
      )
      worker_stacks.append(cpu_worker_stack)

    if gpu_nodes_config:
      gpu_instance_type = gpu_nodes_config['instance_type']
      assert gpu_instance_type.startswith('p'), safe_format(
        "The gpu instance type ({}) does not support gpus",
        gpu_instance_type
      )
      gpu_worker_stack = self.aws_services.cloudformation_service.ensure_eks_worker_stack(
        cluster_name=cluster_name,
        security_groups=eks_vpc_stack_outputs.get('SecurityGroups', '').split(','),
        vpc_id=eks_vpc_stack_outputs.get('VpcId'),
        subnet_ids=eks_vpc_stack_outputs.get('SubnetIds', '').split(','),
        max_nodes=gpu_nodes_config['max_nodes'],
        min_nodes=gpu_nodes_config['min_nodes'],
        instance_type=gpu_nodes_config['instance_type'],
        key_name=key_name,
        gpu=True,
      )
      worker_stacks.append(gpu_worker_stack)

    node_roles = []
    for worker_stack in worker_stacks:
      self.aws_services.cloudformation_service.wait_for_eks_worker_stack(worker_stack)
      instance_role = self.aws_services.iam_service.node_instance_role_from_worker_stack(worker_stack)

      for policy_arn in additional_policies:
        instance_role.attach_policy(PolicyArn=policy_arn)

      node_roles.append(dict(arn=instance_role.arn))

    self._connect_kubernetes_cluster(cluster_name=cluster_name, ignore_role=True)
    self.test_kubernetes_cluster(cluster_name=cluster_name, ignore_role=True)

    cluster_access_role = self.aws_services.iam_service.ensure_cluster_access_role(cluster_name)
    role_config_map = self.services.template_service.render_template_from_file('eks/config_map.yml.ms', dict(
      node_roles=node_roles,
      cluster_access_role=dict(
        arn=cluster_access_role.arn,
        name=cluster_access_role.name,
      ),
    ))
    self.services.kubernetes_service.ensure_config_map(yaml.load(role_config_map))

    self._disconnect_kubernetes_cluster(cluster_name=cluster_name)

    print('Testing your kubernetes configuration, you may see an error below but we should be able to resolve it...')
    self._connect_kubernetes_cluster(cluster_name=cluster_name)
    print('Successfully tested your kubernetes configuration, if you saw any errors above you may ignore them...')
    self._test_cluster_access_role(cluster_name=cluster_name, retries=3)
    # Note(Nakul): We disconnect and reconnect to solve an intermittent issue where the kubernetes python client
    # ends up with an empty api key. This is a temporary fix while we resolve the bug. This solves the issue by
    # reloading the key from the config file a second time which I found out works simply by some trial and error.
    self._disconnect_kubernetes_cluster(cluster_name=cluster_name)
    self._connect_kubernetes_cluster(cluster_name=cluster_name)

    self.test_kubernetes_cluster(cluster_name=cluster_name)

    self.services.kubernetes_service.ensure_plugins()

    print(self._node_access_instructions(cluster_name))

    return self.create_cluster_object(
      services=self.services,
      name=cluster_name,
      registry=None,
    )

  def _test_cluster_access_role(self, cluster_name, retries=0, wait_time=5):
    cluster_access_role = self.aws_services.iam_service.describe_cluster_access_role(cluster_name)
    for try_number in range(retries + 1):
      try:
        self.aws_services.sts_service.assume_role(role_arn=cluster_access_role.arn)
      except ClientError as ce:
        if try_number >= retries:
          six.raise_from(
            AwsClusterSharePermissionError(safe_format(
              "You do not have permission to use the role '{}' for accessing this cluster.\n"
              "Please read the Orchestrate documentation for sharing clusters: {}",
              cluster_access_role.name,
              "https://app.sigopt.com/docs/orchestrate/deep_dive#cluster_sharing",
            )),
            ce,
          )
          raise
        else:
          time.sleep(wait_time)

  def _connect_kubernetes_cluster(self, cluster_name, ignore_role=False):
    kubeconfig = self.create_kubeconfig(cluster_name, ignore_role)
    self.services.kubernetes_service.write_config(
      cluster_name=cluster_name,
      string=kubeconfig,
    )

  def test_kubernetes_cluster(self, cluster_name, ignore_role=False):
    if not ignore_role:
      self._test_cluster_access_role(cluster_name=cluster_name, retries=3)
    self.services.kubernetes_service.test_config()

  def _disconnect_kubernetes_cluster(self, cluster_name):
    self.services.kubernetes_service.ensure_config_deleted(cluster_name=cluster_name)

  def create_kubeconfig(self, cluster_name, ignore_role=False):
    cluster = self.describe_kubernetes_cluster(cluster_name)

    if ignore_role:
      cluster_access_role_arn = None
    else:
      cluster_access_role_arn = self.aws_services.iam_service.describe_cluster_access_role(cluster_name).arn

    # TODO(alexandra): optional role_arn is NOT the role ARN used to create the cluster
    # See Step 2 of https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html
    template_args = dict(
      endpoint_url=cluster['endpoint'],
      base64_encoded_ca_cert=cluster['certificateAuthority']['data'],
      cluster_name=cluster_name,
      role_arn=cluster_access_role_arn,
      authenticator_binary_path=get_executable_path('aws-iam-authenticator')
    )

    return self.services.template_service.render_template_from_file('eks/kube_config.ms', template_args)

  def destroy_kubernetes_cluster(self, cluster_name):
    self.services.kubernetes_service.ensure_config_deleted(cluster_name)
    self.aws_services.ec2_service.ensure_key_pair_for_cluster_deleted(cluster_name)

    for is_gpu in (False, True):
      try:
        worker_stack = self.aws_services.cloudformation_service.describe_eks_worker_stack(cluster_name, is_gpu)
        instance_role = self.aws_services.iam_service.node_instance_role_from_worker_stack(worker_stack)
        for policy in instance_role.attached_policies.all():
          instance_role.detach_policy(PolicyArn=policy.arn)
      except ClientError:
        pass

    with ThreadPoolExecutor(max_workers=6) as executor:
      futures = []
      for is_gpu in (False, True):
        futures.append(
          executor.submit(
            self.aws_services.cloudformation_service.ensure_eks_worker_stack_deleted,
            cluster_name,
            is_gpu,
          )
        )

      futures.append(
        executor.submit(self.aws_services.iam_service.ensure_cluster_access_role_deleted, cluster_name)
      )
      futures.append(
        executor.submit(self.aws_services.eks_service.ensure_cluster_deleted, cluster_name)
      )
      futures.append(
        executor.submit(self.aws_services.cloudformation_service.ensure_eks_vpc_stack_deleted, cluster_name)
      )
      futures.append(
        executor.submit(self.aws_services.iam_service.ensure_eks_role_deleted, cluster_name)
      )

      exc_stacktraces = []
      # Note(Nakul): Outer try-except is a hack for when user Ctrl-Cs to kill all the child threads and exit
      # source: https://gist.github.com/clchiou/f2608cbe54403edb0b13
      try:
        for f in as_completed(futures):
          try:
            f.result()
          except Exception as e:
            exc_stacktraces.append((e, traceback.format_exc()))
      except CaughtSignal as e:
        executor._threads.clear()  # pylint: disable=protected-access
        thread._threads_queues.clear()  # pylint: disable=protected-access
        exc_stacktraces.append((e, traceback.format_exc()))

      if exc_stacktraces:
        raise ClusterDestroyError(exc_stacktraces)

  def _node_access_instructions(self, cluster_name):
    filename = self.aws_services.ec2_service.key_pair_location(cluster_name)
    return (safe_format(
      '*Optional:'
      '\n\tTo ssh into any ec2 node in your cluster, use the username `ec2-user` with the key pair located at:'
      '\n\t\t{filename}'
      '\n\tExample:'
      '\n\t\tssh -i {filename} ec2-user@<node_dns_name>'
      '\n\tYou may be required to change security groups on your ec2 instances'
      '\n\tInstructions: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html',
      filename=filename
    ))

  def create_cluster_object(self, services, name, registry):
    return AWSCluster(
      services=services,
      name=name,
      registry=registry,
    )
