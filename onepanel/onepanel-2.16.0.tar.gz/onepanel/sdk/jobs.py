import os

from onepanel.utilities.cloud_storage_utility import CloudStorageUtility
from onepanel.utilities.creds_utility import CredsUtility

from onepanel.commands.jobs import JobViewController
from onepanel.utilities.original_connection import Connection

from onepanel.models import Job

class Jobs():
    def __init__(self, conn):
        self.job_view_controller = JobViewController(conn)
        self.job_view_controller.project_account_uid = conn.account_uid

    def list(self, all=False, project_uid=None, account_uid=None):
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        jvc = self.job_view_controller

        items = jvc.list(params='?running=true' if not all else '')
        if items == None or items['totalItems'] == 0:
            msg = ['No jobs found.']
            if not all:
                msg.append(' Use "all=True" to retrieve completed jobs.')
            print(''.join(msg))
            return

        jobs = [Job.from_json(item).simple_view() for item in items['data']]
        jvc.print_items(jobs, fields=['uid', 'state', 'command'],
            field_names=['ID', 'STATE', 'COMMAND'])
        return [Job.from_json(item) for item in items['data']]

    def create(self, job):
        if not job:
            print("Error: Need a job object to create a job.")
            return
        if not job.command:
            print("Error: Job command must be provided.")
            return
        if not job.machine_type.uid:
            print("Error: Machine Type must be set.")
            return
        if not job.instance_template.uid:
            print("Error: Environment must be set.")
            return
        if not job.volume_type.uid:
            print("Error: A volume must be set.")
            return
        if not self.job_view_controller.update_config(job.project.uid, job.account.uid, caller_is_sdk=True):
            return

        response = self.job_view_controller.create(job)
        if response['status_code'] == 200:
            print('Created job: {uid}'.format(uid=response['data']['uid']))
            return response['data']['uid']
        else:
            print(response['data'])

    def stop(self, uid, project_uid=None, account_uid=None):
        if not uid:
            print("Error: Job ID cannot be blank.")
            return
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        response = self.job_view_controller.delete_v2('/' + str(uid) + '/active')
        if response['status_code'] == 200:
            print('Stopped job: {uid}'.format(uid=response['data']['uid']))
            return True
        else:
            print('Job is already stopped or does not exist.')
            return False

    def delete(self, uid, project_uid=None, account_uid=None):
        if not uid:
            print("Error: Job ID cannot be blank.")
            return
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        return self.job_view_controller.delete(uid, message_on_success='Deleted job', message_on_failure='Job not found')

    def get(self, uid, project_uid=None, account_uid=None):
        if not uid:
            print("Error: Job ID cannot be blank.")
            return
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        return self.job_view_controller.get_job(uid, project_uid, account_uid)

    def download_output(self, uid, archive_flag=False, project_uid=None, account_uid=None):
        if not uid:
            print("Error: Job ID cannot be blank.")
            return
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        home = os.getcwd()
        jvc = self.job_view_controller
        creds = CredsUtility.get_credentials(jvc.conn, jvc.project_account_uid, 'projects', jvc.project_uid)
        util = CloudStorageUtility.get_utility(creds)
        cloud_provider_download_to_path = home
        no_output_message = 'This job did not create any output or output was not saved.\n' \
                      'If you want to save and version control your output, modify your script to ' \
                      'save all output to the "/onepanel/output" directory.\n'
        if archive_flag is True:
            print('Attempting to download the compressed output file to {home} directory.'.format(
                home=cloud_provider_download_to_path))
            cloud_provider_path_to_download_from = jvc.get_cloud_provider_compressed_file_for_job_output_path(
                jvc.project_account_uid, jvc.project_uid, uid)
            full_path = util.build_full_cloud_specific_url(cloud_provider_path_to_download_from)
            investigation_results = util.check_cloud_path_for_files(full_path, False)
            if investigation_results['code'] == -1:
                print('Error encountered.')
                print(investigation_results['msg'])
                return
            if investigation_results['code'] == 0 and investigation_results['data'] == 0:
                print(no_output_message)
                return
            exit_code = util.download(cloud_provider_download_to_path, cloud_provider_path_to_download_from)
            if exit_code != 0:
                print('Error encountered.')
                return
        else:
            print('Attempting to download output to {home} directory.'.format(home=cloud_provider_download_to_path))
            cloud_provider_path_to_download_from = jvc.get_cloud_provider_root_for_job_output(
                jvc.project_account_uid, jvc.project_uid, uid)
            full_path = util.build_full_cloud_specific_url(cloud_provider_path_to_download_from)
            investigation_results = util.check_cloud_path_for_files(full_path)
            print(investigation_results)

            if investigation_results['code'] == -1:
                print('Error encountered.')
                print(investigation_results['msg'])
                return
            if investigation_results['code'] == 0 and investigation_results['data'] == 0:
                print()
                return
            # Check if there any actual files to download from the output
            exit_code = util.download_all(cloud_provider_download_to_path, cloud_provider_path_to_download_from)
            if exit_code != 0:
                print('Error encountered.')
                return
        print('Finished downloading.')
        return True
