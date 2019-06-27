from __future__ import print_function

import os
import random
import sys
import time

import six
import yaml
from botocore.exceptions import NoRegionError
from cement.core.foundation import CementApp
from cement.ext.ext_argparse import ArgparseController

from orchestrate.common import safe_format
from orchestrate.core.cement_utils import ArgparseArgumentHandler, expose
from orchestrate.core.exceptions import CheckExecutableError, OrchestrateException
from orchestrate.core.kubernetes.service import JobNotFoundException
from orchestrate.core.paths import (
  check_iam_authenticator_executable,
  check_kubectl_executable,
  download_iam_authenticator_executable,
  download_kubectl_executable,
  ensure_dir,
  get_bin_dir,
)
from orchestrate.core.services.orchestrate_bag import OrchestrateServiceBag
from orchestrate.version import VERSION


class OrchestrateController(ArgparseController):
  class Meta(object):
    label = 'base'
    description = 'A machine learning training and tuning management tool built for parameter optimization'

  def default(self):
    print('usage: sigopt [options] <command> [<subcommand> ...]')
    print('\nLearn more at: https://app.sigopt.com/docs/orchestrate')
    print('\nTo see help messages, you can run:')
    print('  sigopt --help')
    print('  sigopt <command> --help')
    print('  sigopt <command> <subcommand> --help')

  @expose(help="Current version")
  def version(self):
    print(VERSION)

  def get_remote_repository_name(self, repository_name):
    cluster = self.app.services.cluster_service.test()
    creds = cluster.get_registry_login_credentials(repository_name)
    if creds is not None:
      self.app.services.docker_service.login(creds)
    return cluster.generate_image_tag(repository=repository_name)

  def runner(self, local=False, quiet=False):
    directory = self.app.pargs.directory

    options = self.app.user_options
    self.app.services.options_validator_service.validate_orchestrate_options(**options)

    name = options.get('name')
    optimization_options = options.get('optimization')
    language = options.get('language')
    framework, resource_options = (
      self.app.services.gpu_options_validator_service.get_framework_and_resource_options(
        options,
        local_run=local,
      )
    )

    image_name = options.get('image')
    repository_name, tag = self.app.services.docker_service.get_repository_and_tag(image_name)

    build_image = options.get('build_image', True)

    if build_image:
      if not quiet:
        print('Containerizing your model and starting your experiment, this may take a few minutes...')
      image = self.app.services.model_packer_service.build_image(
        repository=repository_name,
        tag=tag,
        directory=directory,
        install_commands=options.get('install'),
        run_command=options.get('run'),
        optimization_options=optimization_options,
        language=language,
        framework=framework,
        pythonpath=options.get('pythonpath'),
        quiet=quiet,
      )
    else:
      if not quiet:
        print('Starting your experiment')

    if local:
      if not build_image:
        repository_name = self.get_remote_repository_name(repository_name)
        print(safe_format(
          "Pulling the model environment from image registry: {}. This may be limited by your connection speed...",
          self.app.services.docker_service.format_image_name(repository_name, tag),
        ))
        self.app.services.docker_service.pull(repository_name, tag=tag)
      return self.app.services.job_runner_service.run_local_job(
        name=name,
        repository=repository_name,
        tag=tag,
        optimization_options=optimization_options,
      )
    else:
      repository_name = self.get_remote_repository_name(repository_name)
      if build_image:
        image.tag(repository=repository_name, tag=tag)
        if not quiet:
          print(safe_format(
            "Uploading the model environment to image registry: {}. This may be limited by your connection speed...",
            self.app.services.docker_service.format_image_name(repository_name, tag),
          ))
        self.app.services.docker_service.push(repository_name, tag=tag, quiet=quiet)
      return self.app.services.job_runner_service.run_job(
        name=name,
        repository=repository_name,
        tag=tag,
        optimization_options=optimization_options,
        resource_options=resource_options,
        job_spec_patch_path=options.get('job_spec_patch'),
      )

  @expose(
    help="Initialize a directory for orchestrate. Use with sigopt init >> orchestrate.yml",
  )
  def init(self):
    print(
        """name: My Orchestrate Experiment
install:
#  -   Fill in install command/commands, such as pip install -r requirements.txt
run:
#  -   Fill in run command/commands, such as python model.py
image: #[IMAGE]
optimization:
  metrics:
   - name: #[METRIC_NAME]
  parameters:
   - name: #[PARAMETER_NAME]
     type: #[PARMETER_TYPE]
     bounds:
       min: #[MIN_BOUND]
       max: #[MAX_BOUND]
  parallel_bandwidth: 1
  observation_budget: 10
""")

  @expose(
    arguments=[
      (['--directory'], dict(help='orchestrate project directory, default: current directory', default='.')),
      (['-f', '--filename'], dict(help='orchestrate yaml file, default: orchestrate.yml', default='orchestrate.yml')),
      (['-q', '--quiet'], dict(help='only print the experiment id', action='store_true')),
    ],
    help="Run orchestrate experiment",
  )
  def run(self):
    self.app.services.cluster_service.assert_is_connected()

    quiet = self.app.pargs.quiet

    experiment_id = self.runner(local=False, quiet=quiet)
    if self.app.pargs.quiet:
      print(experiment_id)
    else:
      print(safe_format('Started experiment "{}"', experiment_id))

  @expose(
    arguments=[
      (['--directory'], dict(help='orchestrate project directory, default: current directory', default='.')),
      (['-f', '--filename'], dict(help='orchestrate yaml file, default: orchestrate.yml', default='orchestrate.yml')),
    ],
    help="Run a orchestrate experiment in a local docker container",
  )
  def run_local(self):
    self.runner(local=True, quiet=False)

  @expose(
    arguments=[
      (['experiment'], dict(help='An experiment id')),
    ],
    help='Deletes an experiment on the cluster (experiment will still exist on sigopt.com)',
  )
  def delete(self):
    self.app.services.cluster_service.assert_is_connected()
    experiment_id = self.app.pargs.experiment

    job_name = self.app.services.job_runner_service.job_name(experiment_id)
    assert job_name, safe_format('Internal error: job name empty: {}', job_name)

    pods = self.app.services.kubernetes_service.get_pods(job_name=job_name).items
    for pod in pods:
      self.app.services.kubernetes_service.delete_pod(pod.metadata.name)

    try:
      self.app.services.kubernetes_service.delete_job(job_name)
    except JobNotFoundException:
      raise Exception(safe_format('We could not find an experiment {} running on your cluster', experiment_id))

  @expose(
    arguments=[
      (['experiment'], dict(help='An experiment id')),
    ],
    help='Retrieve experiment status',
  )
  def status(self):
    self.app.services.cluster_service.assert_is_connected()
    experiment_id = self.app.pargs.experiment

    job = self.app.services.job_status_service.get_job_by_experiment_id(experiment_id)
    parsed_job = self.app.services.job_status_service.parse_job(job)
    job_name = parsed_job['name']

    observations_by_pod = self.app.services.job_status_service.get_observations_by_pod(experiment_id)
    total_failures = sum(v['failed'] for v in observations_by_pod.values())
    parsed_pods = [
      self.app.services.job_status_service.parse_pod(pod, observations_by_pod)
      for pod
      in self.app.services.kubernetes_service.get_pods(job_name=job_name).items
    ]
    unschedulable_pods = [pod for pod in parsed_pods if pod['status'] == 'Unschedulable']

    print(safe_format('Job Name: {name}', **parsed_job))
    print(safe_format('Job Status: {status}', **parsed_job))
    print()
    print(safe_format('Experiment Name: {experiment_name}', **parsed_job))
    print(safe_format(
      '{observation_budget_consumed} / {observation_budget} Observations',
      **parsed_job
    ))
    print(safe_format('{} Observation(s) failed', total_failures))

    print('\nPod status:')
    print(safe_format(
      '\n{:20}\t{:25}\t{:20}\t{:20}',
      "Pod Name",
      "Status",
      "Success",
      "Failed",
    ))
    for parsed_pod in parsed_pods:
      print(safe_format(
        '{name:20}\t{status:25}\t{success:<20}\t{failed:<20}',
        **parsed_pod
      ))

    print(safe_format(
      '\nView more at: https://app.sigopt.com/experiment/{}',
      experiment_id
    ))
    if unschedulable_pods:
      print(file=sys.stderr)
      print("The following pods are unable to be scheduled:", file=sys.stderr)
      for pod in unschedulable_pods:
        print(pod['name'], file=sys.stderr)
      print(
        "Check that your cluster has sufficient resources to schedule them."
        " Maybe you're missing some nodes?",
        file=sys.stderr,
      )

  @expose(
    help='Retrieve all experiments\' statuses',
  )
  def status_all(self):
    self.app.services.cluster_service.assert_is_connected()
    parsed_jobs = [
      self.app.services.job_status_service.parse_job(job)
      for job in
      self.app.services.kubernetes_service.get_jobs().items
    ]

    print(safe_format('Total Jobs: {}', len(parsed_jobs)))
    experiment_base_path = 'https://app.sigopt.com/experiment'
    print(safe_format(
      '{:20}\t{:40}\t{:20}\t{:20}',
      "Experiment ID",
      "Experiment URL",
      "Job Status",
      "Observations",
    ))
    for parsed_job in parsed_jobs:
      observation_progress = safe_format(
        '{observation_budget_consumed} / {observation_budget}',
        **parsed_job
      )
      print(safe_format(
        '{experiment_id:20}\t{experiment_url:40}'
        '\t{status:20}'
        '\t{observation_progress:<20}',
        experiment_url=safe_format('{}/{}', experiment_base_path, parsed_job['experiment_id']),
        observation_progress=observation_progress,
        **parsed_job
      ))

  @expose(
    arguments=[
      (['experiment'], dict(help='An experiment id')),
      (['--follow', '-f'], dict(help='Option to follow all logs', action='store_true')),
      (['--color-off', '-c'], dict(help='Remove color from followed logs', action='store_true')),
    ],
    help='Retrieve experiment logs',
  )
  def logs(self):
    self.app.services.cluster_service.assert_is_connected()
    if self.app.pargs.follow:
      self.app.services.job_logs_service.follow_logs(self.app.pargs.experiment, self.app.pargs.color_off)
    else:
      self.app.services.job_logs_service.get_logs(self.app.pargs.experiment)

  @expose(
    arguments=[
      (['experiment'], dict(help='An experiment id')),
      (['-q', '--quiet'], dict(help='Do not print output', action='store_true')),
    ],
    help='Wait until an experiment is Completed',
  )
  def wait(self):
    self.app.services.cluster_service.assert_is_connected()
    experiment_id = self.app.pargs.experiment
    quiet = self.app.pargs.quiet

    if not quiet:
      print(safe_format('Waiting for experiment {} to finish...', experiment_id))

    wait_time = 1
    job = self.app.services.job_status_service.get_job_by_experiment_id(experiment_id)
    parsed_job = self.app.services.job_status_service.parse_job(job)
    while parsed_job['status'] not in ['Complete', 'Failed']:
      if not quiet:
        print(safe_format(
          'Experiment {}, status: {}, sleeping for {}s...',
          experiment_id,
          parsed_job['status'],
          wait_time
        ))
      time.sleep(wait_time)

      job = self.app.services.job_status_service.get_job_by_experiment_id(experiment_id)
      parsed_job = self.app.services.job_status_service.parse_job(job)

      if wait_time < 5 * 60:
        wait_time = 2 * wait_time + random.uniform(0, 1)

    if parsed_job['status'] == 'Failed':
      raise OrchestrateException(
        safe_format('Experiment {} finished, status: {}', experiment_id, parsed_job['status'])
      )

    if not quiet:
      print(safe_format('Experiment {} finished! Status: {}', experiment_id, parsed_job['status']))

  @expose(
    arguments=[
      (['--all', '-a'], dict(help='also remove current Orchestrate frameworks', action='store_true')),
    ],
    help='Cleanup Orchestrate build artifacts',
  )
  def clean(self):
    self.app.services.docker_service.clean(remove_current_frameworks=self.app.pargs.all)

  @expose(
    add_help=False,
    ignore_unknown_arguments=True,
  )
  def kubectl(self):
    self.app.services.cluster_service.assert_is_connected()
    cmd = self.app.services.kubectl_service.kubectl_command
    args = [cmd] + self.app.args.unknown_args
    os.execvpe(
      cmd,
      args,
      self.app.services.kubectl_service.kubectl_env(),
    )

  @expose(
    help='Check that Orchestrate is installed properly',
  )
  def test(self):
    print('Testing your installation of SigOpt Orchestrate, this may take a minute...')
    failed = False
    for name, check, extra in [
      (
        'kubectl',
        lambda: check_kubectl_executable(full_check=True),
        None,
      ),
      (
        'aws-iam-authenticator',
        lambda: check_iam_authenticator_executable(full_check=True),
        None,
      ),
      (
        'docker',
        self.app.services.docker_service.check_connection,
        None,
      ),
      (
        'SigOpt connection',
        self.app.services.sigopt_service.check_connection,
        "You can get your API token from https://app.sigopt.com/tokens/info."
        " See https://app.sigopt.com/docs/overview/authentication for more information.",
      ),
    ]:
      try:
        check()
      except Exception as e:
        print(safe_format("{} error: {}", name, str(e)))
        if extra:
          print(extra)
        failed = True

    if failed:
      print(
        "One or more checks failed."
        " Correct the issues and run `sigopt test` again."
      )
      self.app.exit_code = 1
    else:
      print("All checks passed, you can start using SigOpt Orchestrate!")


class OrchestrateClusterController(ArgparseController):
  class Meta(object):
    label = 'cluster'
    stacked_on = 'base'
    stacked_type = 'nested'
    description = 'Handle the cluster interface'

  def default(self):
    print('run sigopt cluster -h to see a list of commands')

  @expose(
    help='create a cluster',
    arguments=[
      (['-f', '--filename'], dict(help='cluster config yaml file, default: cluster.yml', default='cluster.yml')),
    ],
  )
  def create(self):
    print('Creating your cluster, this process may take 10-15 minutes or longer...')

    cluster_name = self.app.services.cluster_service.create(options=self.app.user_options)

    print(safe_format('Successfully created kubernetes cluster: {}', cluster_name))

  @expose(
    help='destroy a cluster',
    arguments=[
      (['--cluster-name', '-n'], dict(help='cluster name', required=True)),
      (['--provider'], dict(help='The provider used to create this cluster', required=True)),
    ],
  )
  def destroy(self):
    cluster_name = self.app.pargs.cluster_name
    provider_string = self.app.pargs.provider

    print(safe_format('Destroying cluster {}, this process may take 10-15 minutes or longer...', cluster_name))
    self.app.services.cluster_service.destroy(
      cluster_name=cluster_name,
      provider_string=provider_string,
    )
    print(safe_format('Successfully destroyed kubernetes cluster: {}', cluster_name))

  @expose(
    help='connect to a cluster',
    arguments=[
      (['--cluster-name', '-n'], dict(help='cluster name', required=True)),
      (['--provider'], dict(help='The provider used to create this cluster', required=True)),
      (['--kubeconfig'], dict(help='(Optional) A kubeconfig used to connect to this cluster')),
      (['--registry'], dict(help='(Optional) A custom image registry (host or host:port)')),
    ],
  )
  def connect(self):
    cluster_name = self.app.pargs.cluster_name
    provider_string = self.app.pargs.provider
    registry = self.app.pargs.registry

    kubeconfig_filename = self.app.pargs.kubeconfig
    if kubeconfig_filename:
      with open(kubeconfig_filename) as f:
        kubeconfig = f.read()
    else:
      kubeconfig = None

    print(safe_format('Connecting to cluster...', cluster_name))
    self.app.services.cluster_service.connect(
      cluster_name=cluster_name,
      provider_string=provider_string,
      kubeconfig=kubeconfig,
      registry=registry,
    )
    print(safe_format('Successfully connected to kubernetes cluster: {}', cluster_name))

  @expose(
    help='disconnect from a cluster',
    arguments=[
      (['--cluster-name', '-n'], dict(help='cluster name')),
      (['--all', '-a'], dict(help='disconnect from all connected clusters', action='store_true')),
    ],
  )
  def disconnect(self):
    cluster_name = self.app.pargs.cluster_name
    disconnect_all = self.app.pargs.all

    if cluster_name:
      print(safe_format('Disconnecting from cluster {}...', cluster_name))
    if disconnect_all:
      print('Disconnecting from all clusters...')

    self.app.services.cluster_service.disconnect(cluster_name, disconnect_all)
    if cluster_name:
      print(safe_format('Successfully disconnected from kubernetes cluster: {}', cluster_name))
    else:
      # TODO(alexandra): if we keep the --all option around we'll want to print out the cluster names again
      print(safe_format('Successfully disconnected from all kubernetes clusters'))

  @expose(help='test your current cluster connection')
  def test(self):
    print('Testing if you are connected to a cluster, this may take a moment...')
    cluster = self.app.services.cluster_service.test()
    print(safe_format(
      '\nYou are connected to a cluster! Here is the info:'
      '\n\tcluster name: {cluster_name}'
      '\n\tprovider: {provider}'
      '\n\tregistry: {registry}',
      cluster_name=cluster.name,
      provider=cluster.provider_string,
      registry=cluster.registry if cluster.registry is not None else 'default',
    ))

def check_binaries(app):
  ensure_dir(get_bin_dir())

  for check, download, name in [
    (check_kubectl_executable, download_kubectl_executable, 'kubernetes'),
    (check_iam_authenticator_executable, download_iam_authenticator_executable, 'aws iam-authentication'),
  ]:
    try:
      check()
    except CheckExecutableError:
      print(safe_format("Downloading {} executable, this could take some time...", name))
      download()
      check(full_check=True)

def load_options(app):
  try:
    with open(app.pargs.filename) as f:
      options = yaml.safe_load(f) or {}
    app.extend('user_options', options)
  except AttributeError:
    app.extend('user_options', None)


# TODO(alexandra): accept credentials as command line arguments for SigOpt and AWS
def extend_app_services(app):
  try:
    services = OrchestrateServiceBag(app.user_options)
  except NoRegionError as e:
    six.raise_from(
      Exception("No default region is selected, please run `aws configure`"),
      e,
    )
  app.extend('services', services)

class OrchestrateApp(CementApp):
  class Meta(object):
    label = 'sigopt'
    base_controller = 'base'
    argument_handler = ArgparseArgumentHandler
    handlers = [
      OrchestrateController,
      OrchestrateClusterController,
    ]
    hooks = [
      ('post_argument_parsing', check_binaries),
      ('post_argument_parsing', load_options),
      ('post_argument_parsing', extend_app_services),
    ]
    exit_on_close = True

def main():
  with OrchestrateApp() as app:
    app.run()
