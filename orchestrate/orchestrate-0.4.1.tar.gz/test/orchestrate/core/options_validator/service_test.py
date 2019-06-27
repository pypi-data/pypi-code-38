import pytest
from mock import Mock

from orchestrate.core.options_validator.service import OptionsValidatorService


class TestOptionsValidatorService(object):
  @pytest.fixture()
  def options_validator_service(self):
    services = Mock()
    return OptionsValidatorService(services)

  @pytest.fixture()
  def orchestrate_options(self):
    return dict(
      name='test',
      install='pip install -r requirements.txt',
      run='python model.py',
      optimization=dict(
        metrics=[
          dict(name='accuracy'),
        ],
      ),
      image='orchestrate/test',
      resources_per_model=dict(
        gpus=1,
      ),
      framework='keras',
      language='python3.6',
      sigopt=dict(api_token='q2o3u9kdf'),
      pythonpath='.',
      build_image=True,
    )

  @pytest.mark.parametrize('field', ['install', 'run'])
  @pytest.mark.parametrize('val', [
    1,
    True,
    [1],
    ["string", True],
  ])
  def test_validate_orchestrate_options_wrong_run_install(
    self,
    options_validator_service,
    orchestrate_options,
    field,
    val,
  ):
    orchestrate_options[field] = val
    with pytest.raises(AssertionError):
      options_validator_service.validate_orchestrate_options(**orchestrate_options)

  @pytest.mark.parametrize('resource', [
    {'requests': {'cpu': 1, 'memory': '200Gi'}, 'gpus': 1},
    {'limits': {'cpu': '200m', 'memory': 200}},
    {'requests': None, 'gpus': 1},
    {'requests': {'cpu': 1, 'memory': '200Gi'}, 'gpus': None},
  ])
  def test_validate_orchestrate_resources_per_model(self, options_validator_service, orchestrate_options, resource):
    orchestrate_options['resources_per_model'] = resource
    options_validator_service.validate_orchestrate_options(**orchestrate_options)
    options_validator_service.validate_resources_per_model(**resource)

  @pytest.mark.parametrize('resource', [
    {'requests': {'cpu': 1, 'memory': '200Gi'}, 'gpus': -1},
    {'limits': {'cpu': '200m', 'memory': 200}, 'requests': 55},
  ])
  def test_validate_orchestrate_resources_per_model_bad(self, options_validator_service, orchestrate_options, resource):
    orchestrate_options["resources_per_model"] = resource
    with pytest.raises(AssertionError):
      options_validator_service.validate_orchestrate_options(**orchestrate_options)
    with pytest.raises(AssertionError):
      options_validator_service.validate_resources_per_model(**resource)

  def test_validate_orchestrate_options_list_run(self, options_validator_service, orchestrate_options):
    orchestrate_options['run'] = ['python model.py']
    with pytest.raises(AssertionError):
      options_validator_service.validate_orchestrate_options(**orchestrate_options)

  def test_validate_orchestrate_options(self, options_validator_service):
    options_validator_service.validate_orchestrate_options(
      name='test',
      install='pip install -r requirements.txt',
      run='python model.py',
      optimization=dict(
        metrics=[
          dict(name='accuracy'),
        ],
      ),
      image='orchestrate/test',
      resources_per_model=dict(
        gpus=1,
      ),
      framework='keras',
      language='python3.6',
      sigopt=dict(api_token='q2o3u9kdf'),
      pythonpath='.',
      build_image=True,
    )

  def test_validate_orchestrate_options_ok_missing_values(self, options_validator_service):
    options_validator_service.validate_orchestrate_options(
      name='test',
      image='orchestrate/test',
    )

  @pytest.mark.parametrize('name', ['', None, dict()])
  def test_validate_orchestrate_options_name(self, options_validator_service, name):
    with pytest.raises(AssertionError):
      options_validator_service.validate_orchestrate_options(
        name=name,
        run='python model.py',
        image='orchestrate/test',
      )

  def test_validate_optimization(self, options_validator_service):
    options_validator_service.validate_optimization(
      name='',
      metrics=[dict(name='foobar')],
      parameters=[],
    )

  def test_validate_optimization_wrong_type(self, options_validator_service):
    with pytest.raises(AssertionError):
      options_validator_service.validate_optimization(
        name='',
        metrics='foobar',
        parameters=[],
      )

  def test_validate_optimization_wrong_metric(self, options_validator_service):
    with pytest.raises(AssertionError):
      options_validator_service.validate_optimization(
        name='',
        metrics=[dict(foobar='name')],
        parameters=[],
      )

    with pytest.raises(AssertionError):
      options_validator_service.validate_optimization(
        name='',
        metrics=['name'],
        parameters=[],
      )

  def test_validate_resources_per_model(self, options_validator_service):
    options_validator_service.validate_resources_per_model(gpus=2)

  @pytest.mark.parametrize('gpus', [-1, [], dict()])
  def test_validate_resources_per_model_wrong_type(self, options_validator_service, gpus):
    with pytest.raises(AssertionError):
      options_validator_service.validate_resources_per_model(gpus=gpus)

  def test_validate_aws(self, options_validator_service):
    options_validator_service.validate_aws_for_orchestrate(
      aws_access_key_id='foobar',
      aws_secret_access_key='barfoo',
    )

    options_validator_service.validate_aws_for_cluster(
      aws_access_key_id='foobar',
      aws_secret_access_key='barfoo',
      additional_policies=['bar']
    )

  def test_validate_aws_simple(self, options_validator_service):
    options_validator_service.validate_aws_for_orchestrate()
    options_validator_service.validate_aws_for_cluster()

  def test_validate_aws_rejects_ecr(self, options_validator_service):
    with pytest.raises(TypeError):
      options_validator_service.validate_aws_for_cluster(
        ecr=dict(
          image='orchestrate/test',
        ),
      )

    with pytest.raises(TypeError):
      options_validator_service.validate_aws_for_orchestrate(
        ecr=dict(
          image='orchestrate/test',
        ),
      )

    with pytest.raises(TypeError):
      options_validator_service.validate_aws_for_orchestrate(
        ecr=dict(),
      )

  def test_validate_aws_additional_policies(self, options_validator_service):
    options_validator_service.validate_aws_for_cluster(additional_policies=[])
    options_validator_service.validate_aws_for_cluster(additional_policies=None)

    with pytest.raises(AssertionError):
      options_validator_service.validate_aws_for_cluster(additional_policies='policy')

  def test_validate_sigopt(self, options_validator_service):
    options_validator_service.validate_sigopt(
      api_token='foobar',
    )

  def test_validate_sigopt_simple(self, options_validator_service):
    options_validator_service.validate_sigopt()

  @pytest.mark.parametrize('api_token', ['', 0])
  def test_validate_sigopt_wrong_value(self, options_validator_service, api_token):
    with pytest.raises(AssertionError):
      options_validator_service.validate_sigopt(
        api_token=api_token,
      )

  def test_validate_cluster_options(self, options_validator_service):
    options_validator_service.validate_cluster_options(
      provider='aws',
      cluster_name='test-cluster',
      cpu=dict(
        instance_type='t2.small',
        min_nodes=1,
        max_nodes=1,
      ),
      gpu=dict(
        instance_type='p3.2xlarge',
        min_nodes=2,
        max_nodes=2,
      ),
    )

  def test_validate_cluster_options_ok_missing_values(self, options_validator_service):
    options_validator_service.validate_cluster_options(
      cluster_name='test-cluster',
      provider='custom',
      cpu=dict(
        instance_type='t2.small',
        min_nodes=1,
        max_nodes=1,
      ),
      gpu=dict(
        instance_type='p3.2xlarge',
        min_nodes=2,
        max_nodes=2,
      ),
    )

    options_validator_service.validate_cluster_options(
      provider='aws',
      cluster_name='test-cluster',
      gpu=dict(
        instance_type='p3.2xlarge',
        min_nodes=2,
        max_nodes=2,
      ),
    )

    options_validator_service.validate_cluster_options(
      provider='aws',
      cluster_name='test-cluster',
      cpu=dict(
        instance_type='t2.small',
        min_nodes=1,
        max_nodes=1,
      ),
    )

  @pytest.mark.parametrize('cluster_name', ['', None, dict()])
  def test_validate_cluster_options_cluster_name(self, options_validator_service, cluster_name):
    with pytest.raises(AssertionError):
      options_validator_service.validate_cluster_options(
        provider='aws',
        cluster_name=cluster_name,
        cpu=dict(
          instance_type='t2.small',
          min_nodes=1,
          max_nodes=1,
        ),
      )

  def test_validate_cluster_options_extra_options(self, options_validator_service):
    with pytest.raises(TypeError):
      options_validator_service.validate_cluster_options(
        provider='aws',
        cluster_name='test-cluster',
        tpu=dict(
          instance_type='p3.2xlarge',
          min_nodes=2,
          max_nodes=2,
        ),
      )

  def test_validate_cluster_options_wrong_type(self, options_validator_service):
    with pytest.raises(AssertionError):
      options_validator_service.validate_cluster_options(
        provider='aws',
        cluster_name='test-cluster',
        gpu=[dict(
          instance_type='p3.2xlarge',
          min_nodes=2,
          max_nodes=2,
        )],
      )

    with pytest.raises(AssertionError):
      options_validator_service.validate_cluster_options(
        provider='aws',
        cluster_name='test-cluster',
        cpu=[dict(
          instance_type='t2.small',
          min_nodes=1,
          max_nodes=1,
        )],
      )

  def test_validate_cluster_options_ignore_values(self, options_validator_service):
    options_validator_service.validate_cluster_options(
      provider='aws',
      cluster_name='test-cluster',
      cpu=dict(
        instance_type='t2.small',
        min_nodes=1,
        max_nodes=1,
      )
    )

  def test_validate_worker_stack(self, options_validator_service):
    options_validator_service.validate_worker_stack(
      name='cpu',
      instance_type='t2.small',
      min_nodes=1,
      max_nodes=1,
    )

  def test_validate_worker_stack_ignores_values(self, options_validator_service):
    options_validator_service.validate_worker_stack(
      name='foobar',
      instance_type='bazzle',
      min_nodes=2,
      max_nodes=19,
    )

  def test_validate_worker_stack_missing_options(self, options_validator_service):
    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        min_nodes=1,
        max_nodes=1,
      )

    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        instance_type='t2.small',
        max_nodes=1,
      )

    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        instance_type='t2.small',
        min_nodes=1,
      )

  def test_validate_worker_stack_wrong_type(self, options_validator_service):
    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        instance_type=2,
        min_nodes=1,
        max_nodes=1,
      )

    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        instance_type='t2.small',
        min_nodes='1',
        max_nodes=1,
      )

    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        instance_type='t2.small',
        min_nodes=1,
        max_nodes='1',
      )

  def test_validate_worker_stack_negative(self, options_validator_service):
    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        instance_type='t2.small',
        min_nodes=-1,
        max_nodes=1,
      )

    with pytest.raises(AssertionError):
      options_validator_service.validate_worker_stack(
        name='cpu',
        instance_type='t2.small',
        min_nodes=1,
        max_nodes=-1,
      )
