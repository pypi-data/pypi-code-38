from six import raise_from

from orchestrate.common import safe_format
from orchestrate.core.exceptions import OrchestrateException
from orchestrate.core.kubernetes.service import JobNotFoundException
from orchestrate.core.services.base import Service


class JobStatusService(Service):
  def parse_job(self, job):
    job_name = job.metadata.name

    conditions = []
    if job.status.conditions:
      for c in job.status.conditions:
        if c.status == 'True':
          conditions.append(c.type)
        elif c.status == 'False':
          conditions.append(safe_format("Not {}", c.type))
        else:
          conditions.append(safe_format("Maybe {}", c.type))

    job_status = ', '.join(conditions) if conditions else 'Not Complete'

    experiment_id = self.services.job_runner_service.experiment_id(job_name)
    experiment = self.services.sigopt_service.safe_fetch_experiment(experiment_id)

    return dict(
      name=job_name,
      status=job_status,
      experiment_id=experiment_id or '??',
      experiment_name=(experiment.name if experiment else 'unknown'),
      observation_budget=(
        str(float(experiment.observation_budget))
        if experiment and experiment.observation_budget is not None
        else 'n/a'
      ),
      observation_budget_consumed=str(experiment.progress.observation_budget_consumed) if experiment else 'n/a',
    )

  def get_observations_by_pod(self, experiment_id):
    observations_by_pod = dict()
    for o in self.services.sigopt_service.iterate_observations(experiment_id):
      pod_name = o.metadata.get('pod_name') if o.metadata else 'UNKNOWN'

      if pod_name not in observations_by_pod:
        observations_by_pod[pod_name] = dict(success=0, failed=0)

      if o.failed:
        observations_by_pod[pod_name]['failed'] += 1
      else:
        observations_by_pod[pod_name]['success'] += 1

    return observations_by_pod

  def parse_pod(self, pod, observations_by_pod):
    pod_name = pod.metadata.name
    observations = observations_by_pod.get(pod_name, dict(success=0, failed=0))

    phase = pod.status.phase
    status = phase
    if phase in ['Pending', 'Failed', 'Unknown']:
      reasons = [condition.reason for condition in pod.status.conditions if condition.reason]
      if reasons:
        status = safe_format(
          '{} - {}',
          status,
          ', '.join(reasons),
        )

    return dict(
      name=pod_name,
      success=observations['success'],
      failed=observations['failed'],
      status=status,
    )

  def get_job_by_experiment_id(self, experiment_id):
    job_name = self.services.job_runner_service.job_name(experiment_id)
    try:
      return self.services.kubernetes_service.get_jobs(job_name)
    except JobNotFoundException as e:
      raise_from(
        OrchestrateException(
          safe_format('We could not find an experiment with id "{}" running on your cluster.', experiment_id)
        ),
        e,
      )
