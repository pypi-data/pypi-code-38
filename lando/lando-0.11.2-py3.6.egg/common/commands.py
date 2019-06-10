# Contains command classes that are used for various steps in running:
# - StageDataCommand - downloads workflow, writes job order, downloads input files
# - RunWorkflowCommand - runs workflow saving results
# - OrganizeOutputCommand - creates output project folder structure and various files
# - SaveOutputCommand - uploads output project folder to a remote store and shares project with a user
# All these classes implement a `run` method that will write out a command file and run the appropriate command
# in a separate process. Some command classes implement a `command_file_dict` method that returns a dictionary
# with contents of a command file that can be used to run the commands via k8s.
import os
import json
import subprocess
import datetime
import logging
import codecs
import tempfile
from lando.exceptions import JobStepFailed
from ddsc.config import LOCAL_CONFIG_ENV as DDSCLIENT_CONFIG_ENV, Config as DukeDSConfig

RUN_CWL_COMMAND = "cwltool"
RUN_CWL_OUTDIR_ARG = "--outdir"
JOB_STDERR_OUTPUT_MAX_LINES = 100


class StageDataTypes(object):
    URL = "url"
    WRITE = "write"
    DUKEDS = "DukeDS"


def read_file(file_path):
    """
    Read the contents of a file using utf-8 encoding, or return an empty string
    if it does not exist
    :param file_path: str: path to the file to read
    :return: str: contents of file
    """
    try:
        with codecs.open(file_path, 'r', encoding='utf-8', errors='xmlcharrefreplace') as infile:
            return infile.read()
    except OSError as e:
        logging.exception('Error opening {}'.format(file_path))
        return ''


class StepProcess(object):
    def __init__(self, command, stdout_path, stderr_path, env=None):
        self.command = command
        self.env = env
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path
        # properties filled in by run method
        self.return_code = None
        self.started = None
        self.finished = None

    def run(self):
        self.started = datetime.datetime.now()
        # Configure the subprocess to write stdout and stderr directly to files
        logging.info('Running command: {}'.format(' '.join(self.command)))
        logging.info('Redirecting stdout > {},  stderr > {}'.format(self.stdout_path, self.stderr_path))
        stdout_file = open(self.stdout_path, 'w')
        stderr_file = open(self.stderr_path, 'w')
        try:
            self.return_code = subprocess.call(self.command, env=self.env, stdout=stdout_file, stderr=stderr_file)
        except OSError as e:
            logging.error('Error running subprocess %s', e)
            error_message = "Command failed: {}".format(' '.join(self.command))
            raise JobStepFailed(error_message, e)
        finally:
            stdout_file.close()
            stderr_file.close()
            self.finished = datetime.datetime.now()

    def total_runtime_str(self):
        """
        Returns a string describing how long the command took.
        :return: str: "<number> minutes"
        """
        elapsed_seconds = (self.finished - self.started).total_seconds()
        return "{} minutes".format(elapsed_seconds / 60)


class BaseCommand(object):
    @staticmethod
    def write_json_file(filename, data):
        with open(filename, 'w') as outfile:
            outfile.write(json.dumps(data))

    def run_command(self, command, env=None, stdout_path=None, stderr_path=None):
        # Create temp files for saving stdout and stderr if the caller didn't specify them.
        # When the process fails an exception will be raised with content from these two files
        # so these temporary files must persist beyond when they are closed.
        stdout_path, cleanup_stdout_path = self._create_temp_filename_if_none(stdout_path)
        stderr_path, cleanup_stderr_path = self._create_temp_filename_if_none(stderr_path)
        try:
            process = StepProcess(command, stdout_path=stdout_path, stderr_path=stderr_path, env=env)
            process.run()
            if process.return_code != 0:
                self._raise_exception_for_failed_process(process.return_code, stdout_path, stderr_path)
            return process
        finally:
            if cleanup_stderr_path:
                os.remove(stdout_path)
            if cleanup_stderr_path:
                os.remove(stderr_path)

    def _raise_exception_for_failed_process(self, return_code, stdout_path, stderr_path):
        stderr_output = read_file(stderr_path)
        tail_error_output = self._tail_stderr_output(stderr_output)
        error_message = "Process failed with exit code: {}\n{}".format(return_code, tail_error_output)
        stdout_output = read_file(stdout_path)
        raise JobStepFailed(error_message, stdout_output)

    @staticmethod
    def _create_temp_filename_if_none(filename):
        """
        Create a temporary filename that is not cleaned up after the file is closed if the passed filename is None.
        :return (str, boolean): returns tuple of a filename and boolean saying we created a temp file that
        will need to be manually deleted up.
        """
        created_temp_file = False
        if not filename:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                filename = tmp_file.name
            created_temp_file = True
        return filename, created_temp_file

    @staticmethod
    def _tail_stderr_output(stderr_data):
        """
        Trim stderr data to the last JOB_STDERR_OUTPUT_MAX_LINES lines
        :param stderr_data: str: stderr data to be trimmed
        :return: str
        """
        lines = stderr_data.splitlines()
        last_lines = lines[-JOB_STDERR_OUTPUT_MAX_LINES:]
        return '\n'.join(last_lines)

    def run_command_with_dds_env(self, command, dds_config_filename):
        env = os.environ.copy()
        env[DDSCLIENT_CONFIG_ENV] = dds_config_filename
        return self.run_command(command, env=env)

    @staticmethod
    def dds_config_dict(credentials):
        return {
            DukeDSConfig.URL: credentials.endpoint_api_root,
            DukeDSConfig.AGENT_KEY: credentials.endpoint_agent_key,
            DukeDSConfig.USER_KEY: credentials.token,
        }

    def write_dds_config_file(self, dds_config_filename, dds_credentials):
        self.write_json_file(dds_config_filename, self.dds_config_dict(dds_credentials))


class StageDataCommand(BaseCommand):
    def __init__(self, workflow, names, paths):
        self.workflow = workflow
        self.names = names
        self.paths = paths

    def command_file_dict(self, input_files):
        items = [
            # Stages workflow that will be run. Downloads the file at the specified URL and
            # optionally unzips downloaded file if unzip_workflow_url_to_path is not None
            self.create_stage_data_config_item(StageDataTypes.URL,
                                               self.workflow.workflow_url,
                                               self.names.workflow_download_dest,
                                               self.names.unzip_workflow_url_to_path),
            # Create a job order file specifying inputs used when running the workflow.
            # Writes job order data to the specified job_order_path
            self.create_stage_data_config_item(StageDataTypes.WRITE,
                                               self.workflow.job_order,
                                               self.names.job_order_path)
        ]
        for dds_file in input_files.dds_files:
            dest = '{}/{}'.format(self.paths.JOB_DATA, dds_file.destination_path)
            items.append(self.create_stage_data_config_item(StageDataTypes.DUKEDS, dds_file.file_id, dest))
        return {"items": items}

    @staticmethod
    def create_stage_data_config_item(workflow_type, source, dest, unzip_to=None):
        item = {"type": workflow_type, "source": source, "dest": dest}
        if unzip_to:
            item["unzip_to"] = unzip_to
        return item

    def run(self, base_command, dds_credentials, input_files):
        command_filename = self.names.stage_data_command_filename
        self.write_json_file(command_filename, self.command_file_dict(input_files))

        dds_config_filename = self.names.dds_config_filename
        self.write_dds_config_file(dds_config_filename, dds_credentials)

        command = base_command.copy()
        command.append(command_filename)
        command.append(self.names.workflow_input_files_metadata_path)
        self.run_command_with_dds_env(command, dds_config_filename)


class RunWorkflowCommand(BaseCommand):
    def __init__(self, job, names, paths):
        self.job = job
        self.names = names
        self.paths = paths
        self.max_stderr_output_lines = JOB_STDERR_OUTPUT_MAX_LINES

    def run(self, cwl_base_command, cwl_post_process_command):
        command = self.make_command(cwl_base_command)
        step_process = self.run_command(command,
                                        stdout_path=self.names.run_workflow_stdout_path,
                                        stderr_path=self.names.run_workflow_stderr_path)
        self.write_usage_report(step_process.started, step_process.finished)
        if cwl_post_process_command:
            self.run_post_process_command(cwl_post_process_command)

    def make_command(self, cwl_base_command):
        base_command = cwl_base_command
        if not base_command:
            base_command = [RUN_CWL_COMMAND]
        command = base_command.copy()
        # cwltoil requires an absolute path for output directory
        absolute_output_directory = os.path.abspath(self.paths.OUTPUT_RESULTS_DIR)
        command.extend([RUN_CWL_OUTDIR_ARG, absolute_output_directory,
                        self.names.workflow_to_run,
                        self.names.job_order_path])
        return command

    def write_usage_report(self, started, finished):
        data = {
            "start_time": started.isoformat(),
            "finish_time": finished.isoformat(),
        }
        self.write_json_file(self.names.usage_report_path, data)

    def run_post_process_command(self, cwl_post_process_command):
        original_directory = os.getcwd()
        os.chdir(self.paths.OUTPUT_RESULTS_DIR)
        subprocess.call(cwl_post_process_command)
        os.chdir(original_directory)


class OrganizeOutputCommand(BaseCommand):
    def __init__(self, job, names, paths):
        self.job = job
        self.names = names
        self.paths = paths

    def command_file_dict(self, methods_document_content):
        additional_log_files = []
        if self.names.usage_report_path:
            additional_log_files.append(self.names.usage_report_path)
        return {
            "bespin_job_id": self.job.id,
            "destination_dir": self.paths.OUTPUT_RESULTS_DIR,
            "downloaded_workflow_path": self.names.workflow_download_dest,
            "workflow_to_read": self.names.workflow_to_read,
            "workflow_type": self.job.workflow.workflow_type,
            "job_order_path": self.names.job_order_path,
            "bespin_workflow_stdout_path": self.names.run_workflow_stdout_path,
            "bespin_workflow_stderr_path": self.names.run_workflow_stderr_path,
            "methods_template": methods_document_content,
            "additional_log_files": additional_log_files
        }

    def run(self, base_command, methods_document_content):
        command_filename = self.names.organize_output_command_filename
        self.write_json_file(command_filename, self.command_file_dict(methods_document_content))
        command = base_command.copy()
        command.append(self.names.organize_output_command_filename)
        self.run_command(command)


class SaveOutputCommand(BaseCommand):
    def __init__(self, names, paths, activity_name, activity_description):
        self.names = names
        self.paths = paths
        self.activity_name = activity_name
        self.activity_description = activity_description

    def command_file_dict(self, share_dds_ids, started_on, ended_on):
        return {
            "destination": self.names.output_project_name,
            "readme_file_path": self.paths.REMOTE_README_FILE_PATH,
            "paths": [self.paths.OUTPUT_RESULTS_DIR],
            "share": {
                "dds_user_ids": share_dds_ids
            },
            "activity": {
                "name": self.activity_name,
                "description": self.activity_description,
                "started_on": started_on,
                "ended_on": ended_on,
                "input_file_versions_json_path": self.names.workflow_input_files_metadata_path,
                "workflow_output_json_path": self.names.run_workflow_stdout_path
            }
        }

    def run(self, base_command, dds_credentials, share_dds_ids, started_on, ended_on):
        command_filename = self.names.save_output_command_filename
        self.write_json_file(command_filename, self.command_file_dict(share_dds_ids, started_on, ended_on))

        dds_config_filename = self.names.dds_config_filename
        self.write_dds_config_file(dds_config_filename, dds_credentials)

        command = base_command.copy()
        command.append(command_filename)
        command.append(self.names.output_project_details_filename)
        command.append("--outfile-format")
        command.append("json")
        self.run_command_with_dds_env(command, dds_config_filename)

    def get_project_details(self):
        with open(self.names.output_project_details_filename) as infile:
            return json.load(infile)
