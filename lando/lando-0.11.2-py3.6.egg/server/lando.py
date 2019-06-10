"""
Server that starts/terminates VMs based on messages received from a queue.
"""

from datetime import datetime
import traceback
import json
import logging
from lando.server.jobapi import JobApi, JobStates, JobSteps
from lando.server.cloudconfigscript import CloudConfigScript
from lando.server.cloudservice import CloudService, FakeCloudService
from lando.worker.worker import CONFIG_FILE_NAME as WORKER_CONFIG_FILE_NAME
from lando_messaging.clients import LandoWorkerClient, StartJobPayload
from lando_messaging.messaging import MessageRouter
from lando_messaging.workqueue import WorkProgressQueue

CONFIG_FILE_NAME = '/etc/lando_config.yml'
LANDO_QUEUE_NAME = 'lando'
WORK_PROGRESS_EXCHANGE_NAME = 'job_status'


class JobSettings(object):
    """
    Creates objects for external communication to be used in JobActions.
    """
    def __init__(self, job_id, config):
        """
        Specifies which job and configuration settings to use
        :param job_id: int: unique id for the job
        :param config: ServerConfig
        """
        self.job_id = job_id
        self.config = config

    def get_cloud_service(self, vm_settings):
        """
        Creates cloud service for creating and deleting VMs.
        If configuration has fake_cloud_service set to True this will create a fake cloud service for debugging purposes.
        :param project_name: name of the project(tenant) which will contain our VMs
        :return: CloudService
        """
        if self.config.fake_cloud_service:
            return FakeCloudService(self.config, vm_settings)
        else:
            return CloudService(self.config, vm_settings)

    def get_job_api(self):
        """
        Creates object for communicating with Bespin Job API.
        :return: JobApi
        """
        return JobApi(config=self.config, job_id=self.job_id)

    def get_worker_client(self, queue_name):
        """
        Creates object for sending messages to a worker process.
        :param queue_name: str: name of the queue the worker is listening on
        :return: LandoWorkerClient
        """
        return LandoWorkerClient(self.config, queue_name=queue_name)

    def get_work_progress_queue(self):
        """
        Creates object for sending progress notifications to queue containing job progress info.
        """
        return WorkProgressQueue(self.config, WORK_PROGRESS_EXCHANGE_NAME)


class BaseJobActions(object):
    def __init__(self, settings):
        self.settings = settings
        self.job_id = settings.job_id
        self.config = settings.config
        self.job_api = settings.get_job_api()
        self.work_progress_queue = settings.get_work_progress_queue()

    def cannot_restart_step_error(self, step_name):
        """
        Set job to error due to trying to restart a job in a step that cannot be restarted.
        :param step_name: str:
        """
        msg = "Cannot restart {} step.".format(step_name)
        self._set_job_state(JobStates.ERRORED)
        self._show_status(msg)
        self._log_error(message=msg)

    def _log_error(self, message):
        job = self.job_api.get_job()
        self.job_api.save_error_details(job.step, message)

    def _set_job_state(self, state):
        self.job_api.set_job_state(state)
        self._send_job_progress_notification()

    def _set_job_step(self, step):
        self.job_api.set_job_step(step)
        if step:
            self._send_job_progress_notification()

    def _send_job_progress_notification(self):
        job = self.job_api.get_job()
        payload = json.dumps({
            "job": job.id,
            "state": job.state,
            "step": job.step,
        })
        self.work_progress_queue.send(payload)

    def _get_cloud_service(self, job):
        return self.settings.get_cloud_service(job.vm_settings)

    def _show_status(self, message):
        format_str = "{}: {} for job: {}."
        logging.info(format_str.format(datetime.now(), message, self.job_id))

    def generic_job_error(self, action_name, details):
        """
        Sets current job state to error and creates a job error with the details.
        :param action_name: str: name of the action that failed
        :param details: str: details about what went wrong typically a stack trace
        """
        self._set_job_state(JobStates.ERRORED)
        message = "Running {} failed with {}".format(action_name, details)
        self._show_status(message)
        self._log_error(message=message)


class JobActions(BaseJobActions):
    """
    Used by LandoRouter to handle messages at a job specific context.
    """

    def make_worker_client(self, vm_instance_name):
        """
        Makes a worker client to talk to the queue associated with a particular worker(vm_instance_name).
        :param vm_instance_name: str: name of the instance and also it's queue name.
        :return: LandoWorkerClient
        """
        return self.settings.get_worker_client(queue_name=vm_instance_name)

    def start_job(self, payload):
        """
        Request from user to start running a job. This is a multi step process.
        First step is to launch the vm and send stage data request.
        Then we wait for stage data complete message.
        :param payload:StartJobPayload contains job_id we should start
        """
        self._set_job_state(JobStates.RUNNING)
        job = self.job_api.get_job()
        cloud_service = self._get_cloud_service(job)
        vm_instance_name = cloud_service.make_vm_name(self.job_id)
        vm_volume_name = cloud_service.make_volume_name(self.job_id)
        self.launch_vm(vm_instance_name, vm_volume_name)
        # Once the VM launches it will send us the worker_started message
        # this will cause send_stage_job_message to be run.

    def restart_job(self, payload):
        """
        Request from user to resume running a job. It will resume based on the value of job.step
        returned from the job api. Canceled jobs will always restart from the beginning(vm was terminated).
        :param payload:RestartJobPayload contains job_id we should restart
        """
        job = self.job_api.get_job()
        vm_instance_name = job.vm_instance_name
        if vm_instance_name and job.state != JobStates.CANCELED:
            payload.vm_instance_name = vm_instance_name
            if job.step in [JobSteps.STAGING, JobSteps.RUNNING, JobSteps.STORING_JOB_OUTPUT, JobSteps.TERMINATE_VM]:
                self._set_job_state(JobStates.RUNNING)
            if job.step == JobSteps.STAGING:
                self.send_stage_job_message(job.vm_instance_name)
            elif job.step == JobSteps.RUNNING:
                self.stage_job_complete(payload)
            elif job.step == JobSteps.STORING_JOB_OUTPUT:
                self.run_job_complete(payload)
            elif job.step == JobSteps.RECORD_OUTPUT_PROJECT:
                self.cannot_restart_step_error(step_name="record output project")
            elif job.step == JobSteps.TERMINATE_VM:
                self.terminate_vm()
            else:
                self.start_job(StartJobPayload(payload.job_id))
        else:
            self.start_job(StartJobPayload(payload.job_id))

    def launch_vm(self, vm_instance_name, vm_volume_name):
        """
        Sets job state to creating vm, then creates a new VM with vm_instance_name and gives it a floating IP address.
        :param vm_instance_name: str: name we should assign to the new vm
        :param vm_volume_name: str: name we should assign to the attached volume
        """
        self._set_job_step(JobSteps.CREATE_VM)
        self._show_status("Creating VM")
        job = self.job_api.get_job()
        worker_config_yml = self.config.make_worker_config_yml(vm_instance_name, job.vm_settings.cwl_commands)
        cloud_config_script = CloudConfigScript()
        cloud_config_script.add_write_file(content=worker_config_yml, path=WORKER_CONFIG_FILE_NAME)
        for partition, mount_point in job.volume_mounts.items():
            cloud_config_script.add_volume(partition, mount_point)
        cloud_config_script.add_manage_etc_hosts()
        cloud_service = self._get_cloud_service(job)
        volume, volume_id = cloud_service.create_volume(job.volume_size, vm_volume_name)
        instance, ip_address = cloud_service.launch_instance(vm_instance_name, job.job_flavor_name, cloud_config_script.content,
                                                             [volume_id])
        self._show_status("Launched vm with ip {}".format(ip_address))
        self.job_api.set_vm_instance_name(vm_instance_name)
        self.job_api.set_vm_volume_name(vm_volume_name)

    def send_stage_job_message(self, vm_instance_name):
        """
        Sets the job's state to staging and puts the stage job message into the queue for the worker with vm_instance_name.
        :param vm_instance_name: str: name of the instance we will send this message to
        """
        self._set_job_step(JobSteps.STAGING)
        self._show_status("Staging data")
        credentials = self.job_api.get_credentials()
        job = self.job_api.get_job()
        worker_client = self.make_worker_client(vm_instance_name)
        input_files = self.job_api.get_input_files()
        worker_client.stage_job(credentials, job, input_files, vm_instance_name)

    def stage_job_complete(self, payload):
        """
        Message from worker that a the staging job step is complete and successful.
        Sets the job state to RUNNING and puts the run job message into the queue for the worker.
        :param payload: JobStepCompletePayload: contains job id and vm_instance_name
        """
        self._set_job_step(JobSteps.RUNNING)
        self._show_status("Running job")
        run_job_data = self.job_api.get_run_job_data()
        worker_client = self.make_worker_client(payload.vm_instance_name)
        worker_client.run_job(run_job_data, run_job_data.workflow, payload.vm_instance_name)

    def run_job_complete(self, payload):
        """
        Message from worker that a the run job step is complete and successful.
        Sets the job state to ORGANIZE_OUTPUT_PROJECT and puts the organize output project message into the queue for
        the worker.
        :param payload: JobStepCompletePayload: contains job id and vm_instance_name
        """
        self._set_job_step(JobSteps.ORGANIZE_OUTPUT_PROJECT)
        self._show_status("Organizing output project")
        job_data = self.job_api.get_store_output_job_data()
        worker_client = self.make_worker_client(payload.vm_instance_name)
        worker_client.organize_output_project(job_data, payload.vm_instance_name)

    def organize_output_complete(self, payload):
        """
        Message from worker that a the organize output project job step is complete and successful.
        Sets the job state to STORING_OUTPUT and puts the store output message into the queue for the worker.
        :param payload: JobStepCompletePayload: contains job id and vm_instance_name
        """
        self._set_job_step(JobSteps.STORING_JOB_OUTPUT)
        self._show_status("Storing job output")
        credentials = self.job_api.get_credentials()
        job_data = self.job_api.get_store_output_job_data()
        worker_client = self.make_worker_client(payload.vm_instance_name)
        worker_client.store_job_output(credentials, job_data, payload.vm_instance_name)

    def store_job_output_complete(self, payload):
        """
        Message from worker that a the store output job step is complete and successful.
        Records information about the resulting output project and frees cloud resources.
        :param payload: JobStepCompletePayload: contains job id and vm_instance_name
        """
        self.record_output_project_info(payload.output_project_info)
        self.terminate_vm()

    def record_output_project_info(self, output_project_info):
        """
        Records the output project id and readme file id that were created by the worker with the results of the job.
        :param output_project_info: staging.ProjectDetails: info about the project created containing job results
        """
        self._set_job_step(JobSteps.RECORD_OUTPUT_PROJECT)
        project_id = output_project_info.project_id
        readme_file_id = output_project_info.readme_file_id
        self._show_status("Saving project id {} and readme id {}.".format(project_id, readme_file_id))
        self.job_api.save_project_details(project_id, readme_file_id)
        self._show_status("Terminating VM and queue")

    def terminate_vm(self):
        """
        Terminate vm and delete worker message queue.
        """
        self._set_job_step(JobSteps.TERMINATE_VM)
        job = self.job_api.get_job()
        cloud_service = self._get_cloud_service(job)
        if job.cleanup_vm:
            cloud_service.terminate_instance(job.vm_instance_name, [job.vm_volume_name])
        worker_client = self.make_worker_client(job.vm_instance_name)
        worker_client.delete_queue()
        self._set_job_step(JobSteps.NONE)
        self._set_job_state(JobStates.FINISHED)

    def cancel_job(self, payload):
        """
        Request from user to cancel a running a job.
        Sets status to canceled and terminates the associated VM and deletes the queue.
        :param payload: CancelJobPayload: contains job id we should cancel
        """
        self._set_job_step(JobSteps.NONE)
        self._set_job_state(JobStates.CANCELED)
        self._show_status("Canceling job")
        job = self.job_api.get_job()
        if job.vm_instance_name:
            cloud_service = self._get_cloud_service(job)
            if job.cleanup_vm:
                cloud_service.terminate_instance(job.vm_instance_name, [job.vm_volume_name])
            worker_client = self.make_worker_client(job.vm_instance_name)
            worker_client.delete_queue()

    def stage_job_error(self, payload):
        """
        Message from worker that it had an error staging data.
        :param payload:JobStepErrorPayload: info about error
        """
        self._set_job_state(JobStates.ERRORED)
        self._show_status("Staging job failed")
        self._log_error(message=payload.message)

    def run_job_error(self, payload):
        """
        Message from worker that it had an error running a job.
        :param payload:JobStepErrorPayload: info about error
        """
        self._set_job_state(JobStates.ERRORED)
        self._show_status("Running job failed")
        self._log_error(message=payload.message)

    def store_job_output_error(self, payload):
        """
        Message from worker that it had an error storing output.
        :param payload:JobStepErrorPayload: info about error
        """
        self._set_job_state(JobStates.ERRORED)
        self._show_status("Storing job output failed")
        self._log_error(message=payload.message)


def create_job_actions(lando, job_id):
    return JobActions(JobSettings(job_id, lando.config))


class Lando(object):
    """
    Contains base methods for handling messages related to managing/running a workflow.
    Main function is to unpack incoming messages creating a JobActions object for the job id
    and running the appropriate method.
    """
    def __init__(self, config, job_actions_constructor=create_job_actions):
        """
        Setup configuration.
        :param config: ServerConfig: settings used by JobActions methods
        :param job_actions_constructor: func(lando, job_id) that returns JobActions
        """
        self.config = config
        self.job_actions_constructor = job_actions_constructor

    def _make_actions(self, job_id):
        """
        Create JobActions a job specific object for handling messages received on the queue.
        :param job_id: int: unique id for the job
        :return: JobActions: object with methods for processing messages received in listen_for_messages
        """
        return self.job_actions_constructor(self, job_id)

    @staticmethod
    def _make_job_settings(job_id, config):
        return JobSettings(job_id, config)

    def __getattr__(self, name):
        """
        Forwards all unhandled methods to a new JobActions object based on payload param
        :param name: str: name of the method we are trying to call
        :return: func(payload): function that will call the appropriate JobActions method
        """
        def action_method(payload):
            actions = self._make_actions(payload.job_id)
            try:
                getattr(actions, name)(payload)
            except:  # Trap all exceptions
                tb = traceback.format_exc()
                self._handle_action_error(actions, name, payload, tb)
        return action_method

    def _handle_action_error(self, actions, name, payload, error_stacktrace_str):
        try:
            logging.error("Handling error that occurred during {} for job {}.".format(name, payload.job_id))
            logging.error("Error contents: {}".format(error_stacktrace_str))
            actions.generic_job_error(name, error_stacktrace_str)
        except:
            tb = traceback.format_exc()
            logging.error("Additional error occurred while handling an error: {}".format(tb))

    def worker_started(self, worker_started_payload):
        """
        Called when a worker VM has finished launching and is ready to run a job.
        Sends message to this worker to stage their job(s).
        :param worker_started_payload: WorkerStartedPayload: contains worker_queue_name for the worker
        """
        vm_instance_name = worker_started_payload.worker_queue_name
        for job in JobApi.get_jobs_for_vm_instance_name(self.config, vm_instance_name):
            if job.state == JobStates.RUNNING and job.step == JobSteps.CREATE_VM:
                actions = self._make_actions(job.id)
                actions.send_stage_job_message(vm_instance_name)

    def listen_for_messages(self):
        """
        Blocks and waits for messages on the queue specified in config.
        """
        router = self._make_router()
        logging.info("Lando listening for messages on queue '{}'.".format(router.queue_name))
        router.run()

    def _make_router(self):
        work_queue_config = self.config.work_queue_config
        return MessageRouter.make_lando_router(self.config, self, work_queue_config.listen_queue)
