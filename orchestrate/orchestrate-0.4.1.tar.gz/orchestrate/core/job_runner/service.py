from __future__ import print_function

import copy

import yaml

from orchestrate.common import safe_format
from orchestrate.core.exceptions import OrchestrateException
from orchestrate.core.lib.lists import list_get, partition
from orchestrate.core.services.base import Service


class JobRunnerService(Service):
  def env_vars(self, experiment_id):
    return {
      'ORCHESTRATE_EXPERIMENT_ID': str(experiment_id),
      'SIGOPT_API_TOKEN': self.services.sigopt_service.api_token,
    }

  def formatted_env_vars(self, experiment_id):
    return [
      dict(name=key, value=value)
      for key, value in self.env_vars(experiment_id).items()
    ]

  def format_resources(self, resource_options):
    resources = dict(
      limits=resource_options.get('limits') or dict(),
      requests=resource_options.get('requests') or dict(),
    )

    if resource_options.get('gpus'):
      if 'nvidia.com/gpu' in resources['limits']:
        raise OrchestrateException(
          'The value in resources_per_model.gpus will override the value in resources_per_model.limits.nvidia.com/gpu,'
          'please remove one of these fields.'
        )
      resources['limits']['nvidia.com/gpu'] = resource_options.get('gpus')

    return resources

  def merge_container_resource_specs(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    for k, v in user_spec.items():
      if k in ('requests', 'limits'):
        if new_spec[k]:
          raise OrchestrateException(safe_format(
            'resources_per_model.{key} will be overridden by {key} provided in the custom container spec.'
            ' Please remove one of the conflicting instances.',
            key=k,
          ))

      new_spec[k] = v

    return new_spec

  def merge_orchestrate_environment_variables(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    new_env_dict = dict((v['name'], v) for v in new_spec)
    user_env_dict = dict((v['name'], v) for v in user_spec)
    new_env_dict.update(user_env_dict)
    new_spec = list(new_env_dict.values())

    return new_spec

  def merge_orchestrate_container_specs(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    for k, v in user_spec.items():
      if k == 'env':
        new_spec[k] = self.merge_orchestrate_environment_variables(new_spec[k], v)
      elif k == 'resources':
        new_spec[k] = self.merge_container_resource_specs(new_spec[k], v)
      else:
        new_spec[k] = v
    return new_spec

  def merge_containers_specs(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    (orch_containers, not_orch_containers) = partition(user_spec, lambda c: c.get('name') == 'orchestrate')

    if orch_containers:
      assert len(orch_containers) == 1, 'You have two custom container specs with the name `orchestrate`'

    assert len(new_spec) == 1
    new_orch_container = self.merge_orchestrate_container_specs(new_spec[0], list_get(orch_containers, 0))
    return [new_orch_container] + not_orch_containers

  def merge_pod_specs(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    for k, v in user_spec.items():
      if k == 'containers':
        new_spec[k] = self.merge_containers_specs(new_spec[k], v)
      else:
        new_spec[k] = v

    return new_spec

  def merge_job_metadata(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    for k, v in user_spec.items():
      if k == 'name':
        raise OrchestrateException("We currently do not support changing the kubernetes job name")
      else:
        new_spec[k] = v

    return new_spec

  def merge_job_spec_specs(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    for k, v in user_spec.items():
      if k == 'template':
        old_pod_spec = new_spec[k]['spec']
        new_spec[k] = v
        if 'spec' in v:
          new_spec[k]['spec'] = self.merge_pod_specs(old_pod_spec, v['spec'])
      else:
        new_spec[k] = v

    return new_spec

  def merge_job_specs(self, old_spec, user_spec):
    if not user_spec:
      return old_spec

    new_spec = copy.deepcopy(old_spec)
    for k, v in user_spec.items():
      if k == 'spec':
        new_spec[k] = self.merge_job_spec_specs(new_spec[k], v)
      elif k == 'metadata':
        new_spec[k] = self.merge_job_metadata(new_spec[k], v)
      else:
        new_spec[k] = v

    return new_spec

  def create_orchestrate_container_spec(
    self,
    experiment_id,
    image_name,
    resource_options,
    template_container_spec,
  ):
    new_spec = copy.deepcopy(template_container_spec)
    new_spec.update(
      image=image_name,
      resources=self.format_resources(resource_options)
    )
    new_spec['env'].extend(self.formatted_env_vars(experiment_id))
    return new_spec

  def create_pod_spec(
    self,
    experiment_id,
    image_name,
    resource_options,
    template_pod_spec,
  ):
    new_spec = copy.deepcopy(template_pod_spec)
    assert len(new_spec['containers']) == 1
    new_spec['containers'] = [self.create_orchestrate_container_spec(
      experiment_id=experiment_id,
      image_name=image_name,
      resource_options=resource_options,
      template_container_spec=new_spec['containers'][0],
    )]
    return new_spec

  def create_job_spec(
    self,
    experiment_id,
    optimization_options,
    image_name,
    resource_options,
    template_job_spec,
  ):
    new_spec = copy.deepcopy(template_job_spec)
    new_spec['metadata']['name'] = self.job_name(experiment_id)
    new_spec['spec']['parallelism'] = optimization_options.get('parallel_bandwidth', 1)
    new_spec['spec']['template']['spec'] = self.create_pod_spec(
      experiment_id=experiment_id,
      image_name=image_name,
      resource_options=resource_options,
      template_pod_spec=new_spec['spec']['template']['spec'],
    )
    return new_spec

  def render_job_spec_file(
    self,
    experiment_id,
    optimization_options,
    image_name,
    resource_options,
    job_spec_patch_path,
  ):
    template_job_spec = yaml.safe_load(self.services.resource_service.read('kubernetes_spec', 'job_spec.yml'))
    job_spec_patch = None
    if job_spec_patch_path:
      with open(job_spec_patch_path, 'r') as f:
        job_spec_patch = yaml.safe_load(f) or dict()

    job_spec = self.create_job_spec(
      experiment_id=experiment_id,
      optimization_options=optimization_options,
      image_name=image_name,
      resource_options=resource_options,
      template_job_spec=template_job_spec,
    )
    new_job_spec = self.merge_job_specs(job_spec, job_spec_patch)
    return yaml.safe_dump(new_job_spec, default_flow_style=False)

  def job_name(self, experiment_id):
    return safe_format('orchestrate-{}', experiment_id)

  def experiment_id(self, job_name):
    if job_name.startswith('orchestrate-'):
      return job_name[len('orchestrate-'):]
    return None

  def create_sigopt_experiment(self, name, optimization_options):
    data = optimization_options.copy()
    data.pop('sigopt', dict())

    try:
      metadata = data.pop('metadata')
    except KeyError:
      metadata = dict()

    # Note: We could concatenate this string with a uuid to further reduce the possibility of collision
    if 'orchestrate_experiment' not in metadata:
      metadata['orchestrate_experiment'] = "True"

    experiment = self.services.sigopt_service.create_experiment(name=name, metadata=metadata, **data)
    return experiment.id

  def run_job(self, repository, tag, name, optimization_options, resource_options, job_spec_patch_path):
    self.services.kubernetes_service.check_nodes_are_ready()

    experiment_id = self.create_sigopt_experiment(name, optimization_options)
    rendered_job_spec = self.render_job_spec_file(
      experiment_id=experiment_id,
      optimization_options=optimization_options,
      image_name=self.services.docker_service.format_image_name(repository, tag),
      resource_options=resource_options,
      job_spec_patch_path=job_spec_patch_path,
    )

    self.services.kubernetes_service.start_job(yaml.load(rendered_job_spec))
    return experiment_id

  def run_local_job(self, repository, tag, name, optimization_options):
    experiment_id = self.create_sigopt_experiment(name, optimization_options)

    self.services.docker_service.run(
      self.services.docker_service.format_image_name(repository, tag),
      env=self.env_vars(experiment_id),
    )

    return experiment_id
