import os
import re
import dateutil.parser


class WorkflowTypes(object):
    ZIPPED = 'zipped'
    PACKED = 'packed'


class ZippedWorkflowNames(object):
    def __init__(self, job_workflow, workflow_base_dir, workflow_download_dest):
        self.workflow_download_dest = workflow_download_dest
        self.workflow_to_run = '{}/{}'.format(workflow_base_dir, job_workflow.workflow_path)
        self.workflow_to_read = self.workflow_to_run
        self.unzip_workflow_url_to_path = workflow_base_dir


class PackedWorkflowNames(object):
    def __init__(self, job_workflow, workflow_download_dest):
        self.workflow_download_dest = workflow_download_dest
        self.workflow_to_run = '{}{}'.format(self.workflow_download_dest, job_workflow.workflow_path)
        self.workflow_to_read = self.workflow_download_dest
        self.unzip_workflow_url_to_path = None


class WorkflowNames(object):
    def __init__(self, job, paths):
        job_workflow = job.workflow
        workflow_type = job_workflow.workflow_type
        workflow_download_dest = '{}/{}'.format(paths.WORKFLOW, os.path.basename(job_workflow.workflow_url))
        if workflow_type == WorkflowTypes.ZIPPED:
            self._names_target = ZippedWorkflowNames(job_workflow, paths.WORKFLOW, workflow_download_dest)
        elif workflow_type == WorkflowTypes.PACKED:
            self._names_target = PackedWorkflowNames(job_workflow, workflow_download_dest)
        else:
            raise ValueError("Unknown workflow type {}".format(workflow_type))

    def __getattr__(self, name):
        # Pass all properties to internal target *WorkflowNames object
        return getattr(self._names_target, name)


class BaseNames(WorkflowNames):
    def __init__(self, job, paths):
        super(BaseNames, self).__init__(job, paths)
        stripped_username = re.sub(r'@.*', '', job.username)
        self.suffix = '{}-{}'.format(job.id, stripped_username)
        self.job_order_path = '{}/job-order.json'.format(paths.JOB_DATA)
        self.run_workflow_stdout_path = '{}/bespin-workflow-output.json'.format(paths.OUTPUT_DATA)
        self.run_workflow_stderr_path = '{}/bespin-workflow-output.log'.format(paths.OUTPUT_DATA)
        job_created = dateutil.parser.parse(job.created).strftime("%Y-%m-%d")
        self.output_project_name = "Bespin {} v{} {} {}".format(
            job.workflow.name, job.workflow.version, job.name, job_created)
        self.workflow_input_files_metadata_path = '{}/workflow-input-files-metadata.json'.format(paths.JOB_DATA)
        self.usage_report_path = '{}/job-{}-resource-usage.json'.format(paths.OUTPUT_DATA, self.suffix)
        self.activity_name = "{} - Bespin Job {}".format(job.name, job.id)
        self.activity_description = "Bespin Job {} - Workflow {} v{}".format(
            job.id, job.workflow.name, job.workflow.version)


class Paths(object):
    def __init__(self, base_directory):
        self.JOB_DATA = '{}bespin/job-data'.format(base_directory)
        self.WORKFLOW = '{}bespin/job-data/workflow'.format(base_directory)
        self.CONFIG_DIR = '{}bespin/config'.format(base_directory)
        self.STAGE_DATA_CONFIG_FILE = '{}bespin/config/stagedata.json'.format(base_directory)
        self.OUTPUT_DATA = '{}bespin/output-data'.format(base_directory)
        self.OUTPUT_RESULTS_DIR = '{}bespin/output-data/results'.format(base_directory)
        self.TMPOUT_DATA = '{}bespin/output-data/tmpout'.format(base_directory)
        self.REMOTE_README_FILE_PATH = 'results/docs/README.md'
