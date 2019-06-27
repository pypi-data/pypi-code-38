from orchestrate.common import safe_format
from orchestrate.core.lib.types import *
from orchestrate.core.services.base import Service


class OptionsValidatorService(Service):
  def validate_orchestrate_options(
    self,
    name=None,
    install=None,
    run=None,
    optimization=None,
    aws=None,
    resources_per_model=None,
    framework=None,
    language=None,
    sigopt=None,
    pythonpath=None,
    image=None,
    build_image=None,
    job_spec_patch=None,
  ):
    assert is_string(name) and len(name) > 0, 'Please provide a string name in your .yml configuration file'

    if install:
      assert is_string(install) or is_string_sequence(install), safe_format(
        'install is not a string or a list of strings: {}',
        install
      )

    if run:
      assert is_string(run), safe_format(
        'run is not a string: {}',
        run
      )

    if optimization is not None:
      assert is_mapping(optimization), safe_format(
        'optimization is not a mapping: {}',
        optimization
      )
      self.validate_optimization(**optimization)

    if resources_per_model is not None:
      assert is_mapping(resources_per_model), safe_format(
        'resources_per_model is not a mapping: {}',
        resources_per_model
      )
      self.validate_resources_per_model(**resources_per_model)

    assert framework is None or is_string(framework), safe_format(
      "framework is not a string: {}",
      framework
    )
    assert language is None or is_string(language), safe_format(
      "language is not a string: {}",
      language
    )

    if aws:
      assert is_mapping(aws), safe_format('aws is not a mapping: {}', aws)
      self.validate_aws_for_orchestrate(**aws)

    if sigopt is not None:
      assert is_mapping(sigopt), safe_format(
        'sigopt is not a mapping: {}',
        sigopt
      )
      self.validate_sigopt(**sigopt)

    assert pythonpath is None or is_string(pythonpath), safe_format(
      "pythonpath is not a string: {}",
      pythonpath,
    )

    assert image and is_string(image), safe_format(
      'image is not non-empty a string: {}',
      image
    )

    if job_spec_patch:
      assert is_string(job_spec_patch), safe_format('job_spec_patch is not a string: {}', job_spec_patch)

    assert build_image is None or is_boolean(build_image), safe_format(
      'build_image is not a boolean: {}',
      build_image,
    )

  def validate_optimization(self, metrics=None, **kwargs):
    assert is_sequence(metrics), safe_format(
      'optimization.metrics is not a sequence: {}',
      metrics
    )
    for metric in metrics:
      assert is_mapping(metric), safe_format(
        'One member of optimization.metrics is not a mapping: {}',
        metric
      )
      name = metric.get('name')
      assert is_string(name) and len(name) > 0, safe_format(
        'One member of optimization.metrics is missing a name: {}',
        metric
      )

  def validate_resources_per_model(self, gpus=None, requests=None, limits=None):
    if gpus is not None:
      assert is_integer(gpus) and gpus >= 0, safe_format(
        'resources_per_model.gpus is not a non-negative integer: {}',
        gpus
      )
    if requests is not None:
      assert is_mapping(requests), safe_format('resources_per_model.requests is not a mapping: {}', requests)
    if limits is not None:
      assert is_mapping(limits), safe_format('resources_per_model.limits is not a mapping: {}', limits)

  def validate_aws_for_orchestrate(
    self,
    aws_access_key_id=None,
    aws_secret_access_key=None,
  ):
    self.validate_aws_keys(
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key
    )

  def validate_aws_for_cluster(
    self,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    additional_policies=None,
  ):
    self.validate_aws_keys(
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key
    )

    if additional_policies:
      assert is_sequence(additional_policies), safe_format(
        'aws.additional_policies is not a list: {}',
        additional_policies
      )

  def validate_aws_keys(
    self,
    aws_access_key_id=None,
    aws_secret_access_key=None,
  ):
    if aws_secret_access_key is not None:
      assert is_string(aws_secret_access_key) and len(aws_secret_access_key) > 0, safe_format(
        'Please provide a string aws.aws_secret_access_key: {}',
        aws_secret_access_key
      )
    if aws_access_key_id is not None:
      assert is_string(aws_access_key_id) and len(aws_access_key_id) > 0, safe_format(
        'Please provide a string aws.aws_access_key_id: {}',
        aws_access_key_id
      )

  def validate_sigopt(self, api_token=None):
    if api_token is not None:
      assert is_string(api_token) and len(api_token) > 0, safe_format(
        'Please provide a string sigopt.api_token: {}',
        api_token
      )

  def validate_cluster_options(
    self,
    provider=None,
    cluster_name=None,
    cpu=None,
    gpu=None,
    aws=None,
  ):
    assert provider and is_string(provider), \
      safe_format('We need a string `provider` to create your cluster: {}', provider)

    if aws is not None:
      self.validate_aws_for_cluster(**aws)

    assert is_string(cluster_name) and len(cluster_name) > 0, 'We need a string `cluster_name` to create your cluster'
    assert cpu is not None or gpu is not None, 'Please specify some cpu or gpu (or both) nodes for your cluster'
    if cpu:
      assert is_mapping(cpu), safe_format(
        'cpu is not a mapping: {}',
        cpu
      )
      self.validate_worker_stack(name='cpu', **cpu)
    if gpu:
      assert is_mapping(gpu), safe_format(
        'gpu is not a mapping: {}',
        gpu
      )
      self.validate_worker_stack(name='gpu', **gpu)

  def validate_worker_stack(
    self,
    name,
    instance_type=None,
    max_nodes=None,
    min_nodes=None,
  ):
    assert instance_type is not None, safe_format(
      'Missing: {}.instance_type',
      name
    )
    assert max_nodes is not None, safe_format(
      'Missing: {name}.max_nodes (can be the same as {name}.min_nodes)',
      name=name
    )
    assert min_nodes is not None, safe_format(
      'Missing: {name}.min_nodes (can be the same as {name}.max_nodes)',
      name=name
    )

    assert is_string(instance_type), safe_format(
      '{}.instance_type is not a string: {}',
      name,
      instance_type
    )
    assert is_integer(max_nodes) and max_nodes > 0, safe_format(
      '{}.max_nodes is not a positive integer: {}',
      name,
      max_nodes
    )
    assert is_integer(min_nodes) and min_nodes > 0, safe_format(
      '{}.min_nodes is not a positive integer: {}',
      name,
      min_nodes
    )
