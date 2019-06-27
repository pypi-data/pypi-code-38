import errno
import json
import os
import random
import time

import yaml
from kubernetes import client, config
from six import raise_from
from six.moves import http_client

from orchestrate.common import safe_format
from orchestrate.core.exceptions import (
  FileAlreadyExistsError,
  MissingGpuNodesException,
  NodesNotReadyError,
  OrchestrateException,
)
from orchestrate.core.paths import ensure_dir, get_root_subdir
from orchestrate.core.services.base import Service


DEFAULT_NAMESPACE = 'default'
ORCHESTRATE_NAMESPACE = 'orchestrate'
KUBESYSTEM_NAMESPACE = 'kube-system'

class NoNodesInClusterError(NodesNotReadyError):
  def __init__(self):
    super(NoNodesInClusterError, self).__init__(
      'Looks like your cluster does not have any nodes.'
      ' Please check that your cluster configuration file has defined either `cpu` or `gpu` nodes.'
      ' For AWS clusters, check that you see nodes on the EC2 console.'
    )

class NodeStatusNotReadyError(NodesNotReadyError):
  def __init__(self):
    super(NodeStatusNotReadyError, self).__init__(
      'Looks like some of your nodes have not reached the `Ready` status.'
      ' Run `sigopt kubectl get nodes` to see the status of your nodes.'
    )

class KubernetesException(OrchestrateException):
  pass

class JobNotFoundException(KubernetesException):
  pass

class StartJobException(KubernetesException):
  pass

class KubernetesService(Service):
  def __init__(self, services):
    super(KubernetesService, self).__init__(services)
    self._kube_config = None
    self._kube_dir = get_root_subdir('cluster')
    self._set_all_clients()

  def warmup(self):
    kube_configs = self._get_config_files()
    if kube_configs:
      self._kube_config = os.path.join(self._kube_dir, kube_configs[0])
      try:
        api_client = config.new_client_from_config(self._kube_config)
        self._set_all_clients(api_client)
      except Exception as e:
        self.services.logging_service.warning(
          'Experienced the following error while attempting to create kubernetes client from cluster configuration:'
          '\n%s'
          '\nDisconnecting and reconnecting may resolve the issue.'
          '\nPlease try running:'
          '\n\tsigopt cluster disconnect -a',
          str(e),
        )
        self._set_all_clients(None)

  @property
  def kube_config(self):
    return self._kube_config

  def get_jobs(self, job_name=None):
    if job_name:
      try:
        return self._v1_batch.read_namespaced_job(job_name, ORCHESTRATE_NAMESPACE)
      except client.rest.ApiException as e:
        if e.status == http_client.NOT_FOUND:
          raise JobNotFoundException(safe_format('Job with name {} not found', job_name))
        else:
          raise e
    else:
      return self._v1_batch.list_namespaced_job(ORCHESTRATE_NAMESPACE, watch=False)

  def delete_job(self, job_name):
    try:
      self._v1_batch.delete_namespaced_job(job_name, ORCHESTRATE_NAMESPACE, client.V1DeleteOptions())
    except client.rest.ApiException as e:
      if e.status == http_client.NOT_FOUND:
        raise JobNotFoundException(safe_format('Job with name {} not found', job_name))
      else:
        raise e

  def start_job(self, job_spec_dict):
    try:
      return self._v1_batch.create_namespaced_job(ORCHESTRATE_NAMESPACE, job_spec_dict)
    except client.rest.ApiException as e:
      if e.status == http_client.BAD_REQUEST:
        k8s_error_message = json.loads(e.body).get("message")
        error_message = safe_format(
          "\n[ERROR]\t\tKubernetes reported a bad request"
          " this is most likely from an error in the experiment configuration file."
          "\n\t\tFormated Kubernetes Error:\n{}\n", k8s_error_message)
        raise_from(StartJobException(error_message), e)
      else:
        raise e

  # TODO(alexandra): control how logs are displayed, should this be sent to stdout by subprocess or by the CLI?
  def logs(self, pod_name, follow=False):
    if follow:
      # Note(Nakul): Just a normal follow=True doesn't work in the kubernetes python client right now.
      # github issue https://github.com/kubernetes-client/python/issues/199
      return self._v1_core.read_namespaced_pod_log(
        pod_name,
        ORCHESTRATE_NAMESPACE,
        follow=True,
        _preload_content=False
        ).stream()
    return self._v1_core.read_namespaced_pod_log(pod_name, ORCHESTRATE_NAMESPACE)

  def pod_names(self, job_name):
    data = self.get_pods(job_name=job_name)
    return [item.metadata.name for item in data.items]

  def get_pods(self, job_name=None):
    if job_name:
      return self._v1_core.list_namespaced_pod(
        ORCHESTRATE_NAMESPACE,
        watch=False,
        label_selector=safe_format('job-name={}', job_name)
      )
    else:
      return self._v1_core.list_namespaced_pod(ORCHESTRATE_NAMESPACE, watch=False)

  def get_pod(self, pod_name):
    return self._v1_core.read_namespaced_pod(pod_name, ORCHESTRATE_NAMESPACE)

  def delete_pod(self, pod_name):
    return self._v1_core.delete_namespaced_pod(pod_name, ORCHESTRATE_NAMESPACE, body=client.V1DeleteOptions())

  def wait_until_nodes_are_ready(self, retries=20):
    for try_number in range(retries + 1):
      try:
        self.check_nodes_are_ready()
        return
      except NodesNotReadyError:
        if try_number >= retries:
          raise
        else:
          time.sleep(random.uniform(20, 40))

  def check_nodes_are_ready(self):
    nodes = self._get_nodes().items
    if not nodes:
      raise NoNodesInClusterError()

    for node in nodes:
      status = dict(((c.type, (c.status == 'True')) for c in node.status.conditions))
      if not status['Ready']:
        raise NodeStatusNotReadyError()

  def check_gpu_nodes(self, num_gpus):
    nodes = self._get_nodes().items
    for node in nodes:
      gpus = int(node.status.capacity.get('nvidia.com/gpu', '0'))
      if gpus >= num_gpus:
        return
    raise MissingGpuNodesException(safe_format(
      "No nodes are available with {}, you might need to add some to your cluster",
      safe_format('{} GPUs', num_gpus) if num_gpus > 1 else 'GPUs',
    ))

  def ensure_config_map(self, config_map):
    try:
      self._v1_core.create_namespaced_config_map(KUBESYSTEM_NAMESPACE, config_map)
    except client.rest.ApiException as e:
      if e.status != http_client.CONFLICT:
        raise

  def write_config(self, cluster_name, string):
    ensure_dir(self._kube_dir)
    new_file_path = self._kube_config_path(cluster_name)
    if os.path.isfile(new_file_path):
      raise FileAlreadyExistsError(new_file_path)

    with open(new_file_path, 'w') as f:
      f.write(string)

    self.warmup()

  def test_config(self, retries=0, wait_time=5):
    if self._v1_core is None:
      raise OrchestrateException(
        'We ran into an issue connecting to your cluster.'
        '\nDisconnecting and then reconnecting may resolve the issue.'
        '\nDisconnect by running:'
        '\n\tsigopt cluster disconnect -a'
      )

    for try_number in range(retries + 1):
      try:
        return self._v1_core.list_namespaced_service(DEFAULT_NAMESPACE)
      except Exception:
        if try_number >= retries:
          raise
        else:
          time.sleep(wait_time)

  def ensure_config_deleted(self, cluster_name):
    try:
      self._delete_config(cluster_name)
    except OSError as e:
      if e.errno != errno.ENOENT:
        raise

  def get_cluster_names(self):
    return [self._cluster_name_from_config(c) for c in self._get_config_files()]

  def ensure_plugins(self):
    self._ensure_plugin('nvidia-device-plugin.yml')

  def ensure_orchestrate_namespace(self):
    try:
      self._v1_core.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=ORCHESTRATE_NAMESPACE)))
    except client.rest.ApiException as e:
      if e.status != http_client.CONFLICT:
        raise

  def _ensure_plugin(self, file_name):
    with self.services.resource_service.open('plugins', file_name) as file_content:
      plugin_spec = yaml.load(file_content)
      try:
        self._v1_extensions.create_namespaced_daemon_set(KUBESYSTEM_NAMESPACE, plugin_spec)
      except client.rest.ApiException as e:
        if e.status != http_client.CONFLICT:
          raise

  def _cluster_name_from_config(self, config_name):
    basename = os.path.basename(config_name)
    if basename.startswith('config-'):
      return basename[len('config-'):]
    else:
      return None

  def _get_nodes(self):
    return self._v1_core.list_node()

  def _delete_config(self, cluster_name):
    self._kube_config = None
    self._set_all_clients()
    os.remove(self._kube_config_path(cluster_name))

  def _kube_config_path(self, cluster_name):
    filename = safe_format('config-{}', cluster_name)
    return os.path.join(self._kube_dir, filename)

  def _get_config_files(self):
    if os.path.exists(self._kube_dir):
      return [
        config
        for config
        in os.listdir(self._kube_dir)
        if config.startswith('config-')
      ]
    return []

  def _set_all_clients(self, api_client=None):
    if api_client:
      self._v1_core = client.CoreV1Api(api_client)
      self._v1_batch = client.BatchV1Api(api_client)
      self._v1_extensions = client.ExtensionsV1beta1Api(api_client)
    else:
      self._v1_core = None
      self._v1_batch = None
      self._v1_extensions = None
