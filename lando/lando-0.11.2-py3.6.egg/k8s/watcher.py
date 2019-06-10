from lando.k8s.cluster import ClusterApi, JobConditionType, EventTypes, ItemNotFoundException
from lando.k8s.config import create_server_config
from lando.k8s.jobmanager import JobLabels, JobStepTypes
from lando_messaging.clients import LandoClient
from lando_messaging.messaging import JobCommands
from kubernetes.client.rest import ApiException
import logging
import sys

JOB_STEP_TO_COMMANDS = {
    JobStepTypes.STAGE_DATA: (JobCommands.STAGE_JOB_COMPLETE, JobCommands.STAGE_JOB_ERROR),
    JobStepTypes.RUN_WORKFLOW: (JobCommands.RUN_JOB_COMPLETE, JobCommands.RUN_JOB_ERROR),
    JobStepTypes.ORGANIZE_OUTPUT: (JobCommands.ORGANIZE_OUTPUT_COMPLETE, JobCommands.ORGANIZE_OUTPUT_ERROR),
    JobStepTypes.SAVE_OUTPUT: (JobCommands.STORE_JOB_OUTPUT_COMPLETE, JobCommands.STORE_JOB_OUTPUT_ERROR),
    JobStepTypes.RECORD_OUTPUT_PROJECT:
        (JobCommands.RECORD_OUTPUT_PROJECT_COMPLETE, JobCommands.RECORD_OUTPUT_PROJECT_ERROR),
}


def check_condition_status(job, condition_type):
    """
    Determines if a generic job has a condition type: Complete(Success) or Failure
    """
    conditions = job.status.conditions
    if conditions:
        for condition in conditions:
            if condition.type == condition_type and condition.status == "True":
                return True
    return False


class JobStepPayload(object):
    def __init__(self, job_id, job_step):
        self.job_id = job_id
        self.vm_instance_name = None
        commands = JOB_STEP_TO_COMMANDS[job_step]
        self.success_command = commands[0]
        self.error_command = commands[1]


class JobWatcher(object):
    def __init__(self, config):
        self.config = config
        self.cluster_api = self.get_cluster_api(config)
        self.lando_client = LandoClient(config, config.work_queue_config.listen_queue)

    @staticmethod
    def get_cluster_api(config):
        settings = config.cluster_api_settings
        return ClusterApi(settings.host, settings.token, settings.namespace, verify_ssl=settings.verify_ssl)

    def run(self):
        # run on_job_change for jobs that have the bespin job label
        bespin_job_label_selector = "{}={}".format(JobLabels.BESPIN_JOB, "true")
        self.cluster_api.wait_for_job_events(self.on_job_change,
                                             label_selector=bespin_job_label_selector)

    def on_job_change(self, event):
        # We only want ADDED or MODIFIED events. We need ADDED to pick up jobs that have 'Failed' or 'Completed'
        # before we started watching. We need MODIFIED for jobs that 'Failed' or 'Completed' while we are watching.
        if event['type'] in [EventTypes.ADDED, EventTypes.MODIFIED]:
            self.on_job_added_or_modified(event['object'])
        else:
            logging.debug('Ignoring event {}'.format(event['type']))

    def on_job_added_or_modified(self, job):
        bespin_job_id = job.metadata.labels.get(JobLabels.JOB_ID)
        bespin_job_step = job.metadata.labels.get(JobLabels.STEP_TYPE)
        if bespin_job_id and bespin_job_step:
            if bespin_job_step in JOB_STEP_TO_COMMANDS:
                if check_condition_status(job, JobConditionType.COMPLETE):
                    self.on_job_succeeded(bespin_job_id, bespin_job_step)
                elif check_condition_status(job, JobConditionType.FAILED):
                    self.on_job_failed(job.metadata.name, bespin_job_id, bespin_job_step)
            else:
                logging.error("Unable to find job commands:", bespin_job_step, bespin_job_id)

    def on_job_succeeded(self, bespin_job_id, bespin_job_step):
        payload = JobStepPayload(bespin_job_id, bespin_job_step)
        if payload.success_command == JobCommands.STORE_JOB_OUTPUT_COMPLETE:
            self.lando_client.job_step_store_output_complete(payload, None)
        else:
            self.lando_client.job_step_complete(payload)

    def on_job_failed(self, job_name, bespin_job_id, bespin_job_step):
        try:
            logs = self.cluster_api.read_job_logs(job_name)
        except (ApiException, ItemNotFoundException) as ex:
            logging.error("Unable to read logs {}".format(str(ex)))
            logs = "Unable to read logs."
        self.send_step_error_message(bespin_job_step, bespin_job_id, message=logs)

    def send_step_error_message(self, bespin_job_step, bespin_job_id, message):
        payload = JobStepPayload(bespin_job_id, bespin_job_step)
        self.lando_client.job_step_error(payload, message)


def main():
    config = create_server_config(sys.argv[1])
    logging.basicConfig(stream=sys.stdout, level=config.log_level)
    watcher = JobWatcher(config)
    watcher.run()


if __name__ == '__main__':
    main()
