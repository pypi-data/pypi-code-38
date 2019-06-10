"""
Testing that lando can have top level methods called which will propogate to LandoActions and
perform the expected actions.
"""

from unittest import TestCase
import json
from lando.server.lando import Lando, JobActions, JobSettings, WORK_PROGRESS_EXCHANGE_NAME
from lando.server.jobapi import JobStates, JobSteps, Job
from lando_messaging.messaging import RestartJobPayload
from unittest.mock import MagicMock, patch, Mock, call
from shade import OpenStackCloudException


LANDO_CONFIG = """
work_queue:
  host: 127.0.0.1
  username: lando
  password: odnal
  worker_username: lobot
  worker_password: tobol
  listen_queue: lando

cloud_settings:
  auth_url: http://10.109.252.9:5000/v3
  username: jpb67
  user_domain_name: Default
  project_name: jpb67
  project_domain_name: Default
  password: secret

job_api:
  url: http://localhost:8000/api
  username: jpb67
  password: secret

fake_cloud_service: True
"""

LANDO_WORKER_CONFIG = """
host: 10.109.253.74
username: worker
password: workerpass
queue_name: task-queue
"""

CLOUD_CONFIG = """#cloud-config

disk_setup:
  /dev/vdb:
    layout: true
    table_type: gpt
fs_setup:
- device: /dev/vdb1
  filesystem: ext3
manage_etc_hosts: localhost
mounts:
- - /dev/vdb1
  - /work
write_files:
- content: '

    host: 10.109.253.74

    username: worker

    password: workerpass

    queue_name: task-queue

    '
  path: /etc/lando_worker_config.yml
"""


class Report(object):
    """
    Builds a text document of steps executed by Lando.
    This makes it easier to assert what operations happened.
    """
    def __init__(self):
        self.text = ''
        self.job_state = 'N'
        self.job_step = JobSteps.NONE
        self.vm_instance_name = 'worker_x'
        self.vm_volume_name = 'volume_x'
        self.launch_instance_error = None
        self.create_volume_error = None

    def add(self, line):
        self.text += line + '\n'

    def make_vm_name(self, job_id):
        self.add("Created vm name for job {}.".format(job_id))
        return "worker_x"

    def make_volume_name(self, job_id):
        self.add("Created volume name for job {}.".format(job_id))
        return "volume_x"

    def launch_instance(self, server_name, flavor_name, script_contents, volumes):
        if self.launch_instance_error:
            raise self.launch_instance_error
        self.add("Launched vm {}.".format(server_name))
        return MagicMock(), MagicMock()

    def terminate_instance(self, server_name, volume_names):
        if not server_name:
            raise ValueError("Can't delete empty server_name.")
        self.add("Terminated vm {}.".format(server_name))
        for volume_name in volume_names:
            self.add("Deleted volume {}.".format(volume_name))

    def create_volume(self, size, name):
        if self.create_volume_error:
            raise self.create_volume_error
        self.add("Created volume {}.".format(name))
        return MagicMock(), MagicMock()

    def get_job(self):
        job = MagicMock()
        job.id = '1'
        job.user_id = '1'
        job.state = self.job_state
        job.step = self.job_step
        job.job_flavor_name = ''
        job.vm_instance_name = self.vm_instance_name
        job.vm_volume_name = self.vm_volume_name
        job.vm_project_name = 'bespin_user1'
        job.workflow = MagicMock()
        job.output_project = MagicMock()
        return job

    def set_job_state(self, state):
        self.add("Set job state to {}.".format(state))
        self.job_state = state

    def set_job_step(self, step):
        self.add("Set job step to {}.".format(step or 'EMPTY'))
        self.job_step = step

    def set_vm_instance_name(self, instance_name):
        self.add("Set vm instance name to {}.".format(instance_name))

    def set_vm_volume_name(self, volume_name):
        self.add("Set vm volume name to {}.".format(volume_name))

    def stage_job(self, credentials, job_id, files, vm_instance_name):
        self.add("Put stage message in queue for {}.".format(vm_instance_name))

    def run_job(self, job_id, workflow, vm_instance_name):
        self.add("Put run_job message in queue for {}.".format(vm_instance_name))

    def store_job_output(self, credentials, job_id, vm_instance_name):
        self.add("Put store_job_output message in queue for {}.".format(vm_instance_name))

    def organize_output_project(self, job_id, vm_instance_name):
        self.add("Put organize_output_project message in queue for {}.".format(vm_instance_name))

    def delete_queue(self):
        self.add("Delete my worker's queue.")

    def get_jobs_for_vm_instance_name(self):
        self.add("Get jobs for vm instance.")
        return [
            MagicMock(stuff='ok')
        ]

    def work_progress_queue_send(self, payload):
        data = json.loads(payload)
        self.add("Send progress notification. Job:{} State:{} Step:{}".format(
            data['job'], data['state'], data['step'] or 'EMPTY'))


def make_mock_settings_and_report(job_id):
    report = Report()
    settings = MagicMock()
    cloud_service = MagicMock()
    cloud_service.make_vm_name = report.make_vm_name
    cloud_service.launch_instance = report.launch_instance
    cloud_service.create_volume = report.create_volume
    cloud_service.make_volume_name = report.make_volume_name
    cloud_service.terminate_instance = report.terminate_instance

    job_api = MagicMock()
    job_api.set_job_state = report.set_job_state
    job_api.set_job_step = report.set_job_step
    job_api.set_vm_instance_name = report.set_vm_instance_name
    job_api.get_job = report.get_job
    job_api.get_jobs_for_vm_instance_name = report.get_jobs_for_vm_instance_name

    worker_client = MagicMock()
    worker_client.stage_job = report.stage_job
    worker_client.run_job = report.run_job
    worker_client.delete_queue = report.delete_queue
    worker_client.store_job_output = report.store_job_output

    work_progress_queue = MagicMock()
    work_progress_queue.send = report.work_progress_queue_send

    settings.get_cloud_service.return_value = cloud_service
    settings.get_job_api.return_value = job_api
    settings.get_worker_client.return_value = worker_client
    settings.get_work_progress_queue.return_value = work_progress_queue
    settings.job_id = job_id
    settings.config.make_worker_config_yml = MagicMock(return_value='config_file_content')
    return settings, report


class TestLando(TestCase):
    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_start_job(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.start_job(MagicMock(job_id=job_id))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:EMPTY
Created vm name for job 1.
Created volume name for job 1.
Set job step to V.
Send progress notification. Job:1 State:R Step:V
Created volume volume_x.
Launched vm worker_x.
Set vm instance name to worker_x.
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobApi')
    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_worker_started(self, mock_requests, MockLandoWorkerClient, MockJobSettings, MockJobApi):
        MockJobApi.get_jobs_for_vm_instance_name.return_value = [MagicMock(state="R", step="V")]
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.worker_started(MagicMock(worker_queue_name='stuff'))
        expected_report = """
Set job step to S.
Send progress notification. Job:1 State:N Step:S
Put stage message in queue for stuff.
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_cancel_job(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 2
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.cancel_job(MagicMock(job_id=job_id))
        expected_report = """
Set job step to EMPTY.
Set job state to C.
Send progress notification. Job:1 State:C Step:EMPTY
Terminated vm worker_x.
Deleted volume volume_x.
Delete my worker's queue.
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_stage_job_complete(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 3
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.stage_job_complete(MagicMock(job_id=1, vm_instance_name='worker_x'))
        expected_report = """
Set job step to R.
Send progress notification. Job:1 State:N Step:R
Put run_job message in queue for worker_x.
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_run_job_complete(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 4
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.run_job_complete(MagicMock(job_id=1, vm_instance_name='worker_x'))
        expected_report = """
Set job step to O.
Send progress notification. Job:1 State:N Step:O
Put store_job_output message in queue for worker_x.
        """
        expected_report = """
Set job step to o.
Send progress notification. Job:1 State:N Step:o
"""
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_stage_job_error(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 4
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.stage_job_error(MagicMock(job_id=1, vm_instance_name='worker_5', message='Oops1'))
        expected_report = """
Set job state to E.
Send progress notification. Job:1 State:E Step:EMPTY
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_run_job_error(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 4
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.run_job_error(MagicMock(job_id=1, vm_instance_name='worker_5', message='Oops2'))
        expected_report = """
Set job state to E.
Send progress notification. Job:1 State:E Step:EMPTY
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_store_job_output_error(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 4
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.store_job_output_error(MagicMock(job_id=1, vm_instance_name='worker_5', message='Oops3'))
        expected_report = """
Set job state to E.
Send progress notification. Job:1 State:E Step:EMPTY
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_restart_new_job(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        report.vm_instance_name = None
        lando = Lando(MagicMock())
        lando.restart_job(RestartJobPayload(job_id=1))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:EMPTY
Created vm name for job 1.
Created volume name for job 1.
Set job step to V.
Send progress notification. Job:1 State:R Step:V
Created volume volume_x.
Launched vm worker_x.
Set vm instance name to worker_x.
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_restart_staging_job(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        report.vm_instance_name = 'some_vm'
        report.job_state = JobStates.ERRORED
        report.job_step = JobSteps.STAGING
        lando = Lando(MagicMock())
        lando.restart_job(RestartJobPayload(job_id=1))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:S
Set job step to S.
Send progress notification. Job:1 State:R Step:S
Put stage message in queue for some_vm.
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_restart_workflow_running_job(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        report.vm_instance_name = 'some_vm'
        report.job_state = JobStates.ERRORED
        report.job_step = JobSteps.RUNNING
        lando = Lando(MagicMock())
        lando.restart_job(RestartJobPayload(job_id=1))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:R
Set job step to R.
Send progress notification. Job:1 State:R Step:R
Put run_job message in queue for some_vm.
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_restart_store_output_job(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        report.vm_instance_name = 'some_vm'
        report.job_state = JobStates.ERRORED
        report.job_step = JobSteps.STORING_JOB_OUTPUT
        lando = Lando(MagicMock())
        lando.restart_job(RestartJobPayload(job_id=1))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:O
Set job step to o.
Send progress notification. Job:1 State:R Step:o
"""
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.jobapi.requests')
    def test_restart_record_output_project(self, mock_requests, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        report.vm_instance_name = 'some_vm'
        report.vm_volume_name = 'volume_x'
        report.job_state = JobStates.ERRORED
        report.job_step = JobSteps.RECORD_OUTPUT_PROJECT
        lando = Lando(MagicMock())
        lando.restart_job(RestartJobPayload(job_id=1))
        expected_report = """
Set job state to E.
Send progress notification. Job:1 State:E Step:P
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_restart_terminate_vm_job(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        MockJobSettings.return_value = mock_settings
        report.vm_instance_name = 'some_vm'
        report.vm_volume_name = 'volume_x'
        report.job_state = JobStates.ERRORED
        report.job_step = JobSteps.TERMINATE_VM
        lando = Lando(MagicMock())
        lando.restart_job(RestartJobPayload(job_id=1))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:T
Set job step to T.
Send progress notification. Job:1 State:R Step:T
Terminated vm some_vm.
Deleted volume volume_x.
Delete my worker's queue.
Set job step to EMPTY.
Set job state to F.
Send progress notification. Job:1 State:F Step:EMPTY"""
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_create_failing_vm(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        report.launch_instance_error = OpenStackCloudException('some vm image')
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.start_job(MagicMock(job_id=job_id))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:EMPTY
Created vm name for job 1.
Created volume name for job 1.
Set job step to V.
Send progress notification. Job:1 State:R Step:V
Created volume volume_x.
Set job state to E.
Send progress notification. Job:1 State:E Step:V
        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_cancel_job_with_no_vm_name(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        """
        When canceling a job that doesn't have a VM yet just set the state to canceled.
        There is no need to try to delete a VM or queue that doesn't exist.
        """
        job_id = 2
        mock_settings, report = make_mock_settings_and_report(job_id)
        report.vm_instance_name = ''
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.cancel_job(MagicMock(job_id=job_id))
        expected_report = """
Set job step to EMPTY.
Set job state to C.
Send progress notification. Job:1 State:C Step:EMPTY

        """
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    def test_create_failing_volume(self, mock_requests, MockLandoWorkerClient, MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        report.create_volume_error = OpenStackCloudException('unable to create volume')
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.start_job(MagicMock(job_id=job_id))
        expected_report = """
Set job state to R.
Send progress notification. Job:1 State:R Step:EMPTY
Created vm name for job 1.
Created volume name for job 1.
Set job step to V.
Send progress notification. Job:1 State:R Step:V
Set job state to E.
Send progress notification. Job:1 State:E Step:V
"""
        self.assertMultiLineEqual(expected_report.strip(), report.text.strip())

    @patch('lando.server.lando.JobSettings')
    @patch('lando.server.lando.LandoWorkerClient')
    @patch('lando.server.jobapi.requests')
    @patch('lando.server.lando.logging')
    @patch('lando.server.lando.traceback')
    def test_error_sending_error(self, mock_traceback, mock_logging, mock_requests, MockLandoWorkerClient,
                                 MockJobSettings):
        job_id = 1
        mock_settings, report = make_mock_settings_and_report(job_id)
        mock_traceback.format_exc.side_effect = [
            'StackTrace1',
            'StackTrace2'
        ]
        failing_job_api = MagicMock()
        failing_job_api.get_job.side_effect = [ValueError("Error1"), ValueError("Error2")]
        mock_settings.get_job_api.return_value = failing_job_api
        MockJobSettings.return_value = mock_settings
        lando = Lando(MagicMock())
        lando.start_job(MagicMock(job_id=job_id))
        mock_logging.error.assert_has_calls([
            call('Handling error that occurred during start_job for job 1.'),
            call('Error contents: StackTrace1'),
            call('Additional error occurred while handling an error: StackTrace2')
        ])


class TestJobActions(TestCase):
    def test_store_job_output_complete_cleanup_vm_true(self):
        mock_job = Mock(id='1', state='', step='', cleanup_vm=True, vm_instance_name='vm1', vm_volume_name='vol1')
        mock_job_api = MagicMock()
        mock_job_api.get_job.return_value = mock_job
        mock_cloud_service = MagicMock()
        mock_settings = MagicMock()
        mock_settings.get_job_api.return_value = mock_job_api
        mock_settings.get_cloud_service.return_value = mock_cloud_service
        job_actions = JobActions(mock_settings)
        mock_output_project_info = Mock(project_id='123', readme_file_id='456')
        job_actions.store_job_output_complete(MagicMock(output_project_info=mock_output_project_info))
        mock_cloud_service.terminate_instance.assert_called_with('vm1', ['vol1'])
        mock_job_api.save_project_details.assert_called_with('123', '456')

    def test_store_job_output_complete_cleanup_vm_false(self):
        mock_job = Mock(id='1', state='', step='', cleanup_vm=False, vm_instance_name='vm1', vm_volume_name='vol1')
        mock_job_api = MagicMock()
        mock_job_api.get_job.return_value = mock_job
        mock_cloud_service = MagicMock()
        mock_settings = MagicMock()
        mock_settings.get_job_api.return_value = mock_job_api
        mock_settings.get_cloud_service.return_value = mock_cloud_service
        job_actions = JobActions(mock_settings)
        job_actions.store_job_output_complete(MagicMock())
        mock_cloud_service.terminate_instance.assert_not_called()

    def test_cancel_job_cleanup_true(self):
        mock_job = Mock(id='1', state='', step='', cleanup_vm=True, vm_instance_name='vm1', vm_volume_name='vol1')
        mock_job_api = MagicMock()
        mock_job_api.get_job.return_value = mock_job
        mock_cloud_service = MagicMock()
        mock_settings = MagicMock()
        mock_settings.get_job_api.return_value = mock_job_api
        mock_settings.get_cloud_service.return_value = mock_cloud_service
        job_actions = JobActions(mock_settings)
        job_actions.cancel_job(MagicMock())
        mock_cloud_service.terminate_instance.assert_called_with('vm1', ['vol1'])

    def test_cancel_job_cleanup_vm_false(self):
        mock_job = Mock(id='1', state='', step='', cleanup_vm=False, vm_instance_name='vm1', vm_volume_name='vol1')
        mock_job_api = MagicMock()
        mock_job_api.get_job.return_value = mock_job
        mock_cloud_service = MagicMock()
        mock_settings = MagicMock()
        mock_settings.get_job_api.return_value = mock_job_api
        mock_settings.get_cloud_service.return_value = mock_cloud_service
        job_actions = JobActions(mock_settings)
        job_actions.cancel_job(MagicMock())
        mock_cloud_service.terminate_instance.assert_not_called()

    def test_launch_vm(self):
        mock_vm_settings = Mock(cwl_commands=None)
        mock_job = Mock(id='1', state='', step='', cleanup_vm=False, job_flavor_name='flavor1',
                        volume_mounts={'/dev/vdb1':'/work'}, vm_settings=mock_vm_settings)
        mock_job_api = MagicMock()
        mock_job_api.get_job.return_value = mock_job

        mock_cloud_service = MagicMock()
        mock_cloud_service.create_volume = MagicMock(return_value=(MagicMock(), 'vol-id-123',))
        mock_cloud_service.launch_instance = MagicMock(return_value=(MagicMock(), '1.2.3.4',))
        mock_settings = MagicMock()
        mock_settings.get_job_api.return_value = mock_job_api
        mock_settings.get_cloud_service.return_value = mock_cloud_service
        mock_make_worker_config_yml = MagicMock()
        mock_make_worker_config_yml.return_value = LANDO_WORKER_CONFIG
        mock_settings.config.make_worker_config_yml = mock_make_worker_config_yml
        job_actions = JobActions(mock_settings)
        job_actions.launch_vm('vm1', 'vol1')

        name, args, kwargs = mock_cloud_service.launch_instance.mock_calls[0]
        # Easier to debug this assertion
        self.assertMultiLineEqual(args[2], CLOUD_CONFIG)

        mock_cloud_service.launch_instance.assert_called_with(
            'vm1', # Should call launch_instance with Instance name from launch_vm
            'flavor1', # Should call launch_instance with flavor from job.job_flavor_name
            CLOUD_CONFIG, # Should generate a cloud config with manage_etc_hosts, fs_setup, and write_files
            ['vol-id-123'] # Should call launch_instance with list of vol ids from create_volume
        )

        mock_job_api.set_vm_instance_name.assert_called_with('vm1')
        mock_job_api.set_vm_volume_name.assert_called_with('vol1')


class TestJobSettings(TestCase):

    def setUp(self):
        self.job_id = '1'
        self.config = Mock()

    @patch('lando.server.lando.CloudService')
    @patch('lando.server.lando.FakeCloudService')
    def test_get_real_cloud_service(self, mock_fake_cloud_service, mock_cloud_service):
        self.config.fake_cloud_service = False
        job_settings = JobSettings(self.job_id, self.config)
        vm_settings = Mock()
        cloud_service = job_settings.get_cloud_service(vm_settings)
        self.assertEqual(cloud_service, mock_cloud_service.return_value)
        self.assertTrue(mock_cloud_service.called)
        self.assertFalse(mock_fake_cloud_service.called)
        args, kwargs = mock_cloud_service.call_args
        self.assertEqual(args, (self.config, vm_settings,))

    @patch('lando.server.lando.CloudService')
    @patch('lando.server.lando.FakeCloudService')
    def test_get_fake_cloud_service(self, mock_fake_cloud_service, mock_cloud_service):
        self.config.fake_cloud_service = True
        job_settings = JobSettings(self.job_id, self.config)
        vm_settings = Mock()
        cloud_service = job_settings.get_cloud_service(vm_settings)
        self.assertEqual(cloud_service, mock_fake_cloud_service.return_value)
        self.assertFalse(mock_cloud_service.called)
        self.assertTrue(mock_fake_cloud_service.called)
        args, kwargs = mock_fake_cloud_service.call_args
        self.assertEqual(args, (self.config, vm_settings))

    @patch('lando.server.lando.JobApi')
    def test_get_job_api(self, mock_job_api):
        job_settings = JobSettings(self.job_id, self.config)
        job_api = job_settings.get_job_api()
        args, kwargs = mock_job_api.call_args
        self.assertEqual(job_api, mock_job_api.return_value)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {'config': self.config, 'job_id': self.job_id})

    @patch('lando.server.lando.LandoWorkerClient')
    def test_get_worker_client(self, mock_lando_worker_client):
        job_settings = JobSettings(self.job_id, self.config)
        worker_client = job_settings.get_worker_client('test-queue')
        args, kwargs = mock_lando_worker_client.call_args
        self.assertEqual(worker_client, mock_lando_worker_client.return_value)
        self.assertEqual(args, (self.config,))
        self.assertEqual(kwargs, {'queue_name': 'test-queue'})

    @patch('lando.server.lando.WorkProgressQueue')
    def test_get_work_progress_queue(self, mock_work_progress_queue):
        job_settings = JobSettings(self.job_id, self.config)
        work_progress_queue = job_settings.get_work_progress_queue()
        args, kwargs = mock_work_progress_queue.call_args
        self.assertEqual(work_progress_queue, mock_work_progress_queue.return_value)
        self.assertEqual(args, (self.config, WORK_PROGRESS_EXCHANGE_NAME))
        self.assertEqual(kwargs, {})
