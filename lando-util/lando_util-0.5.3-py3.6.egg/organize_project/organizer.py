"""
Organizes an output project before uploading to a remote data store.

Directory structure:
results/           # this directory is uploaded in the store output stage (destination_dir in config)
   ...output files from workflow
   docs/
      README.md
      README.html
      scripts/
          <workflow name>.cwl
          job-<jobid>-input.json
      logs/
          bespin-workflow-output.json   #stdout from cwl-runner - json job results
          bespin-workflow-output.log    #stderr from cwl-runner
          job-data.json                 # non-cwl job data used to create Bespin-Report.txt
"""
import os
import json
import shutil
import zipfile
import click
import dateutil.parser
from lando_util.organize_project.reports import ReadmeReport, create_workflow_info


def write_data_to_file(data, filepath):
    with open(filepath, 'w') as outfile:
        outfile.write(data)


class Settings(object):
    README_MD_FILENAME = "README.md"
    README_HTML_FILENAME = "README.html"
    DOCS_DIRNAME = "docs"
    LOGS_DIRNAME = "logs"
    SCRIPTS_DIRNAME = "scripts"
    BESPIN_WORKFLOW_STDOUT_FILENAME = "bespin-workflow-output.json"
    BESPIN_WORKFLOW_STDERR_FILENAME = "bespin-workflow-output.log"
    JOB_DATA_FILENAME = "job-data.json"

    def __init__(self, cmdfile):
        data = json.load(cmdfile)
        self.bespin_job_id = data['bespin_job_id']  # bespin job id of the job this output project is for
        self.destination_dir = data['destination_dir']  # directory where we will add files/folders
        self.downloaded_workflow_path = data['downloaded_workflow_path']  # path to downloaded workflow (zip/packed cwl)
        self.workflow_to_read = data['workflow_to_read']  # path to where the workflow main file can be read
        self.workflow_type = data['workflow_type']  # format of workflow file ('zipped' or 'packed')
        self.job_order_path = data['job_order_path']  # path to job order used when running the workflow
        self.bespin_workflow_stdout_path = data['bespin_workflow_stdout_path']  # path to stdout created by CWL runner
        self.bespin_workflow_stderr_path = data['bespin_workflow_stderr_path']  # path to stderr created by CWL runner
        self.bespin_workflow_started = data.get('bespin_workflow_started', '')  # workflow started running iso date
        self.bespin_workflow_finished = data.get('bespin_workflow_finished', '')  # workflow completed running iso date
        self.additional_log_files = data.get('additional_log_files', [])  # additional files to be copied to /logs

    @property
    def docs_dir(self):
        return os.path.join(self.destination_dir, self.DOCS_DIRNAME)

    @property
    def readme_md_dest_path(self):
        return os.path.join(self.docs_dir, self.README_MD_FILENAME)

    @property
    def readme_html_dest_path(self):
        return os.path.join(self.docs_dir, self.README_HTML_FILENAME)

    @property
    def logs_dir(self):
        return os.path.join(self.docs_dir, self.LOGS_DIRNAME)

    @property
    def bespin_workflow_stdout_dest_path(self):
        return os.path.join(self.logs_dir, self.BESPIN_WORKFLOW_STDOUT_FILENAME)

    @property
    def bespin_workflow_stderr_dest_path(self):
        return os.path.join(self.logs_dir, self.BESPIN_WORKFLOW_STDERR_FILENAME)

    @property
    def job_data_dest_path(self):
        return os.path.join(self.logs_dir, self.JOB_DATA_FILENAME)

    @property
    def scripts_dir(self):
        return os.path.join(self.docs_dir, self.SCRIPTS_DIRNAME)

    @property
    def workflow_dest_path(self):
        return os.path.join(self.scripts_dir, os.path.basename(self.downloaded_workflow_path))

    @property
    def job_order_dest_path(self):
        return os.path.join(self.scripts_dir, os.path.basename(self.job_order_path))

    @property
    def bespin_workflow_elapsed_minutes(self):
        if self.bespin_workflow_started and self.bespin_workflow_finished:
            started = dateutil.parser.parse(self.bespin_workflow_started)
            finished = dateutil.parser.parse(self.bespin_workflow_finished)
            return (finished - started).total_seconds() / 60
        else:
            return 0


class ProjectData(object):
    def __init__(self, settings):
        self.workflow_info = create_workflow_info(settings.workflow_to_read)
        self.workflow_info.update_with_job_order(job_order_path=settings.job_order_path)
        self.workflow_info.update_with_job_output(job_output_path=settings.bespin_workflow_stdout_path)
        run_time = "{} minutes".format(settings.bespin_workflow_elapsed_minutes)
        self.job_data = {
            'id': settings.bespin_job_id,
            'started': settings.bespin_workflow_started,
            'finished': settings.bespin_workflow_finished,
            'run_time': run_time,
            'num_output_files': self.workflow_info.count_output_files(),
            'total_file_size_str': self.workflow_info.total_file_size_str(),
        }
        self.readme_report = ReadmeReport(self.workflow_info, self.job_data)


class Organizer(object):
    def __init__(self, settings):
        self.settings = settings
        self.project_data = ProjectData(settings)

    def run(self):
        # create all new directories
        os.makedirs(name=self.settings.docs_dir, exist_ok=True)
        os.makedirs(name=self.settings.scripts_dir, exist_ok=True)
        os.makedirs(name=self.settings.logs_dir, exist_ok=True)

        # create docs README files markdown and HTML
        write_data_to_file(
            filepath=self.settings.readme_md_dest_path,
            data=self.project_data.readme_report.render_markdown()
        )
        write_data_to_file(
            filepath=self.settings.readme_html_dest_path,
            data=self.project_data.readme_report.render_html()
        )

        # create docs/logs job data files
        write_data_to_file(
            filepath=self.settings.job_data_dest_path,
            data=json.dumps(self.project_data.job_data)
        )

        # copy docs/scripts cwl workflow file
        if self.settings.workflow_type == 'packed':
            shutil.copy(self.settings.downloaded_workflow_path, self.settings.workflow_dest_path)
        elif self.settings.workflow_type == 'zipped':
            with zipfile.ZipFile(self.settings.downloaded_workflow_path) as z:
                z.extractall(self.settings.workflow_dest_path)
        else:
            raise ValueError("Unknown workflow type {}".format(self.settings.workflow_type))
        # copy docs/scripts job order file
        shutil.copy(self.settings.job_order_path, self.settings.job_order_dest_path)
        # copy docs/logs bespin workflow stdout
        shutil.copy(self.settings.bespin_workflow_stdout_path, self.settings.bespin_workflow_stdout_dest_path)
        # copy docs/logs bespin workflow stderr
        shutil.copy(self.settings.bespin_workflow_stderr_path, self.settings.bespin_workflow_stderr_dest_path)

        for log_file_source in self.settings.additional_log_files:
            log_filename = os.path.basename(log_file_source)
            log_file_dest = os.path.join(self.settings.logs_dir, log_filename)
            shutil.copy(log_file_source, log_file_dest)


@click.command()
@click.argument('cmdfile', type=click.File())
def organize_project(cmdfile):
    settings = Settings(cmdfile)
    organizer = Organizer(settings)
    organizer.run()


if __name__ == '__main__':
    organize_project()
