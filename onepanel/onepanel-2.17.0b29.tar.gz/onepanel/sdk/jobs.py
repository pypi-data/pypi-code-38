import os

from onepanel.utilities.cloud_storage_utility import CloudStorageUtility
from onepanel.utilities.s3.file_sync import FileSynchronizer, FileDifference
from onepanel.commands.jobs import JobViewController

from onepanel.models import Job


class Jobs:
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
            field_names=['UID', 'STATE', 'COMMAND'])
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
            print("Error: Job UID cannot be blank.")
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
            print("Error: Job UID cannot be blank.")
            return
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        return self.job_view_controller.delete(uid, message_on_success='Deleted job', message_on_failure='Job not found')

    def get(self, uid, project_uid=None, account_uid=None):
        if not uid:
            print("Error: Job UID cannot be blank.")
            return
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        return self.job_view_controller.get_job(uid, project_uid, account_uid)

    def download_output(self, uid, archive_flag=False, project_uid=None, account_uid=None):
        if not uid:
            print("Error: Job UID cannot be blank.")
            return
        if not self.job_view_controller.update_config(project_uid, account_uid, caller_is_sdk=True):
            return

        home = os.getcwd()
        jvc = self.job_view_controller
        cloud_provider_download_to_path = home

        util = CloudStorageUtility.get_utility(jvc.project_account_uid, 'projects', entity_uid=jvc.project_uid)
        if archive_flag is True:
            print('Attempting to download the compressed output file to {home} directory.'.format(
                home=cloud_provider_download_to_path))
            cloud_provider_path_to_download_from = jvc.get_cloud_provider_compressed_file_for_job_output_path(
                jvc.project_account_uid, jvc.project_uid, uid)

            stats = util.get_prefix_stats(cloud_provider_path_to_download_from)

            if stats['files'] == 0:
                print("This job did not create any output or output was not saved. \n" +
                      "If you want to save and version control your output, modify your script to "
                      "save all output to the '/onepanel/output' directory.\n")
                return

            file_name = cloud_provider_path_to_download_from.split('/')[-1]

            util.download_file(cloud_provider_download_to_path + '/' + file_name, cloud_provider_path_to_download_from)
        else:
            print('Attempting to download output to {home} directory.'.format(home=cloud_provider_download_to_path))
            cloud_provider_path_to_download_from = jvc.get_cloud_provider_root_for_job_output(
                jvc.project_account_uid, jvc.project_uid, uid)

            prefix = cloud_provider_path_to_download_from
            cloud_provider_path_to_download_from += '/'

            # Check if there any actual files to download from the output
            stats = util.get_prefix_stats(cloud_provider_path_to_download_from)
            if stats['files'] == 0:
                print("This job did not create any output or output was not saved. \n" +
                      "If you want to save and version control your output, modify your script to "
                      "save all output to the '/onepanel/output' directory.\n")
                return

            ignore_file_states = [FileDifference.State.DELETED]
            CloudStorageUtility.sync_files(jvc.project_account_uid, 'projects', jvc.project_uid,
                                           cloud_provider_download_to_path, cloud_provider_path_to_download_from,
                                           master=FileSynchronizer.REMOTE, s3_full_path=prefix,
                                           ignore_file_states=ignore_file_states)

        print('Finished downloading.')
        return True
