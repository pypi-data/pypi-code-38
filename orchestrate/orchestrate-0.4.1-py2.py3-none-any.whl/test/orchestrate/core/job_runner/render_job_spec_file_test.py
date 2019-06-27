from tempfile import NamedTemporaryFile

import pytest
import yaml
from mock import Mock

from orchestrate.core.exceptions import OrchestrateException
from orchestrate.core.job_runner.service import JobRunnerService
from orchestrate.core.lib.types import *
from orchestrate.core.resource.service import ResourceService


EXPECTED_SPEC = """apiVersion: batch/v1
kind: Job
metadata:
  name: orchestrate-1
spec:
  template:
    spec:
      containers:
      - name: orchestrate
        image: test_i
        env:
          - name: POD_NAME
            valueFrom:
              fieldRef:
                fieldPath: metadata.name
          - name: ORCHESTRATE_EXPERIMENT_ID
            value: "1"
          - name: SIGOPT_API_TOKEN
            value: "sigopt_api_token"
        resources:
          limits:
            cpu: 55
            memory: 20Gi
            nvidia.com/gpu: 3
          requests:
            cpu: 4
            memory: 2Gi
      dnsPolicy: "None"
      dnsConfig:
        nameservers:
          - 8.8.8.8
          - 8.8.4.4
      restartPolicy: Never
      tolerations:
        - foo: bar
  backoffLimit: 4
  parallelism: 50
"""

# We can't use a simple dict compare here, because the ordering of elements in
# lists does not matter
def job_specs_equal(spec_a, spec_b):
  if type(spec_a) is not type(spec_b):
    return False

  if is_sequence(spec_a):
    if len(spec_a) != len(spec_b):
      return False

    return (
      any(job_specs_equal(item_a, item_b) for item_b in spec_b for item_a in spec_a) and
      any(job_specs_equal(item_a, item_b) for item_a in spec_a for item_b in spec_b)
    )
  elif is_mapping(spec_a):
    if sorted(spec_a.keys()) != sorted(spec_b.keys()):
      return False

    for key in spec_a:
      if not job_specs_equal(spec_a[key], spec_b[key]):
        return False

    return True
  else:
    return spec_a == spec_b
  return True


class TestRenderJobSpecFile(object):
  @pytest.fixture
  def services(self):
    services = Mock(
      sigopt_service=Mock(api_token="sigopt_api_token")
    )
    services.resource_service = ResourceService(services)
    return services

  @pytest.fixture
  def job_runner_service(self, services):
    return JobRunnerService(services)

  def test_render_job_spec_file(self, job_runner_service):
    job_spec_patch_path = None
    with NamedTemporaryFile(mode='w', delete=False) as job_spec_patch:
      yaml.safe_dump(
        dict(spec=dict(template=dict(spec=dict(tolerations=[dict(foo='bar')])))),
        job_spec_patch,
      )
      job_spec_patch_path = job_spec_patch.name

    job_spec = job_runner_service.render_job_spec_file(
      experiment_id=1,
      optimization_options=dict(parallel_bandwidth=50),
      image_name="test_i",
      resource_options=dict(
        gpus=3,
        requests=dict(cpu=4, memory='2Gi'),
        limits=dict(cpu=55, memory='20Gi'),
      ),
      job_spec_patch_path=job_spec_patch_path,
    )

    assert job_specs_equal(yaml.load(EXPECTED_SPEC), yaml.load(job_spec))

  def test_no_patch_path(self, job_runner_service):
    assert job_runner_service.render_job_spec_file(
      experiment_id=1,
      optimization_options=dict(parallel_bandwidth=50),
      image_name="test_i",
      resource_options=dict(),
      job_spec_patch_path=None,
    )

  def test_merge_container_resource_specs(self, job_runner_service):
    assert job_runner_service.merge_container_resource_specs(
      old_spec=dict(requests=dict(), limits=dict()),
      user_spec=None,
    ) == dict(requests=dict(), limits=dict())

    assert job_runner_service.merge_container_resource_specs(
      old_spec=dict(requests=dict(), limits=dict()),
      user_spec=dict(requests=dict(cpu=4, memory='2Gi'), limits=dict(cpu=55, memory='20Gi')),
    ) == dict(requests=dict(cpu=4, memory='2Gi'), limits=dict(cpu=55, memory='20Gi'))

    assert job_runner_service.merge_container_resource_specs(
      old_spec=dict(requests=dict(cpu=4, memory='2Gi'), limits=dict()),
      user_spec=dict(limits=dict(cpu=55, memory='20Gi')),
    ) == dict(requests=dict(cpu=4, memory='2Gi'), limits=dict(cpu=55, memory='20Gi'))

    with pytest.raises(OrchestrateException):
      job_runner_service.merge_container_resource_specs(
        old_spec=dict(requests=dict(), limits=dict(cpu=4, memory='2Gi')),
        user_spec=dict(requests=dict(), limits=dict(cpu=55, memory='20Gi')),
      )

    with pytest.raises(OrchestrateException):
      job_runner_service.merge_container_resource_specs(
        old_spec=dict(requests=dict(cpu=4, memory='2Gi'), limits=dict()),
        user_spec=dict(requests=dict(cpu=55, memory='20Gi'), limits=dict()),
      )

  def test_merge_orchestrate_environment_variables(self, job_runner_service):
    assert job_runner_service.merge_orchestrate_environment_variables(
      old_spec=[],
      user_spec=[],
    ) == []

    assert sorted(job_runner_service.merge_orchestrate_environment_variables(
      old_spec=[dict(name='a')],
      user_spec=[dict(name='b')],
    ), key=lambda v: v['name']) == [dict(name='a'), dict(name='b')]

    assert sorted(job_runner_service.merge_orchestrate_environment_variables(
      old_spec=[dict(name='a', value='foobar'), dict(name='c')],
      user_spec=[dict(name='b'), dict(name='a', valueFrom='foobar')],
    ), key=lambda v: v['name']) == [dict(name='a', valueFrom='foobar'), dict(name='b'), dict(name='c')]

  def test_merge_orchestrate_container_specs(self, job_runner_service):
    assert job_runner_service.merge_orchestrate_container_specs(dict(foo='bar'), None) == dict(foo='bar')
    assert job_runner_service.merge_orchestrate_container_specs(
      old_spec=dict(
        name='orchestrate',
        image_name='foo/bar',
        env=[dict(name='a')],
        resources=dict(requests=dict(), limits=dict(cpu=5)),
      ),
      user_spec=dict(
        name='orchestrate',
        image_name='bar/foo',
        env=[dict(name='b')],
        resources=dict(requests=dict(cpu=4)),
      ),
    ) == dict(
      name='orchestrate',
      image_name='bar/foo',
      env=[dict(name='a'), dict(name='b')],
      resources=dict(requests=dict(cpu=4), limits=dict(cpu=5)),
    )

    assert job_runner_service.merge_orchestrate_container_specs(
      old_spec=dict(name='orchestrate', image_name='bar/foo', env=[dict(name='a')]),
      user_spec=dict(name='orchestrate', image_name='foo/bar')
    ) == dict(name='orchestrate', image_name='foo/bar', env=[dict(name='a')])

  def test_merge_containers_specs(self, job_runner_service):
    assert job_runner_service.merge_containers_specs([dict(name='orchestrate')], None) == [dict(name='orchestrate')]
    assert job_runner_service.merge_containers_specs(
      old_spec=[
        dict(
          name='orchestrate',
          image_name='foo/bar',
          env=[dict(name='a')],
          resources=dict(requests=dict(), limits=dict(cpu=5)),
        ),
      ],
      user_spec=[
        dict(
          name='orchestrate',
          image_name='bar/foo',
          env=[dict(name='b')],
          resources=dict(requests=dict(cpu=4)),
        ),
        dict(
          name='foobar',
          image_name='bar/foo',
        ),
      ],
    ) == [
      dict(
        name='orchestrate',
        image_name='bar/foo',
        env=[dict(name='a'), dict(name='b')],
        resources=dict(requests=dict(cpu=4), limits=dict(cpu=5)),
      ),
      dict(
        name='foobar',
        image_name='bar/foo',
      ),
    ]

    assert job_runner_service.merge_containers_specs(
      old_spec=[dict(name='orchestrate', image_name='bar/foo', env=[dict(name='a')])],
      user_spec=[dict(name='orchestrate', image_name='foo/bar'), dict(name='foobar')]
    ) == [dict(name='orchestrate', image_name='foo/bar', env=[dict(name='a')]), dict(name='foobar')]

    with pytest.raises(AssertionError):
      job_runner_service.merge_containers_specs(old_spec=[], user_spec=[dict(name='foobar')])

    with pytest.raises(AssertionError):
      job_runner_service.merge_containers_specs(
        old_spec=[dict()],
        user_spec=[dict(name='orchestrate'), dict(name='orchestrate')]
      )

  def test_merge_pod_specs(self, job_runner_service):
    assert job_runner_service.merge_pod_specs(dict(foo='bar'), None) == dict(foo='bar')
    assert job_runner_service.merge_pod_specs(
      old_spec=dict(
        containers=[dict(name='orchestrate', image_name='bar/foo', env=[dict(name='a')])],
      ),
      user_spec=dict(
        containers=[dict(name='orchestrate', image_name='foo/bar'), dict(name='foobar')],
        tolerations=[dict(bar='foo')],
        affinity=dict(foo='bar')
      ),
    ) == dict(
        containers=[dict(name='orchestrate', image_name='foo/bar', env=[dict(name='a')]), dict(name='foobar')],
        tolerations=[dict(bar='foo')],
        affinity=dict(foo='bar')
    )

  def test_merge_job_metadata(self, job_runner_service):
    assert job_runner_service.merge_job_metadata(
      old_spec=dict(name='experiment-foobar'),
      user_spec=dict(not_name='foobar'),
    ) == dict(
      name='experiment-foobar',
      not_name='foobar',
    )

    with pytest.raises(OrchestrateException):
      job_runner_service.merge_job_metadata(
        old_spec=dict(name='experiment-foobar'),
        user_spec=dict(name='foobar'),
      )

  def test_merge_job_spec(self, job_runner_service):
    assert job_runner_service.merge_job_specs(
      old_spec=dict(
        metadata=dict(name='experiment-foobar'),
        spec=dict(
          template=dict(spec=dict(
            containers=[
              dict(name='orchestrate', image_name='bar/foo', env=[dict(name='a')]),
            ],
          )),
          parallelism=1,
        ),
      ),
      user_spec=dict(
        metadata=dict(not_name='foobar'),
        spec=dict(
          template=dict(spec=dict(
            containers=[
              dict(name='orchestrate', image_name='foo/bar', env=[dict(name='a', value='b')]),
              dict(name='foobar'),
            ],
            tolerations=[dict(bar='foo')],
            affinity=dict(foo='bar')
          )),
          parallelism=2,
        ),
      ),
    ) == dict(
      metadata=dict(name='experiment-foobar', not_name='foobar'),
      spec=dict(
        template=dict(spec=dict(
          containers=[
            dict(name='orchestrate', image_name='foo/bar', env=[dict(name='a', value='b')]),
            dict(name='foobar')
          ],
          tolerations=[dict(bar='foo')],
          affinity=dict(foo='bar'),
        )),
        parallelism=2,
      ),
    )
