import json
from onepanel.commands.base import APIViewController

class DatasetAPI(APIViewController):
    def __init__(self, connection):
        APIViewController.__init__(self, connection)
        self.connection = self.conn

    def claim_instance_mount(self, account_uid, project_uid, instance_uid, downloader_id, downloader_pid):
        endpoint = '/accounts/{account_uid}/projects/{project_uid}/instances/{instance_uid}/claim_dataset_mount'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            instance_uid=instance_uid
        )

        post = {
            'downloaderID': downloader_id,
            'downloaderPID': downloader_pid
        }

        return self.put(params=endpoint, post_object=post)

    def claim_job_mount(self, account_uid, project_uid, job_uid, downloader_id, downloader_pid):
        endpoint = '/accounts/{account_uid}/projects/{project_uid}/jobs/{job_uid}/claim_dataset_mount'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            job_uid=job_uid
        )

        post = {
            'downloaderID': downloader_id,
            'downloaderPID': downloader_pid
        }

        return self.put(params=endpoint, post_object=post)

    def get_dataset_version(self, account_uid, dataset_uid, version=None):
        if version is None:
            version = 'current'

        endpoint = '/accounts/{account_uid}/datasets/{dataset_uid}/version/{version}'.format(
            account_uid=account_uid,
            dataset_uid=dataset_uid,
            version=version
        )
        return self.get(params=endpoint)

    def update_dataset_mount_downloader(self, account_uid, project_uid, dataset_mount_uuid, files_downloaded, bytes_downloaded):
        endpoint = '/accounts/{account_uid}/projects/{project_uid}/dataset_mounts/{dataset_mount_uuid}/update'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            dataset_mount_uuid=dataset_mount_uuid
        )

        post = {
            'filesDownloaded': files_downloaded,
            'bytesDownloaded': bytes_downloaded
        }

        return self.put(params=endpoint, post_object=post)

    def finish_dataset_mount_downloader(self, account_uid, project_uid, dataset_mount_uuid):
        endpoint = '/accounts/{account_uid}/projects/{project_uid}/dataset_mounts/{dataset_mount_uuid}/finish'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            dataset_mount_uuid=dataset_mount_uuid
        )

        return self.put(params=endpoint)

    def get_dataset_mount(self, account_uid, project_uid, dataset_mount_uuid):
        endpoint = '/accounts/{account_uid}/projects/{project_uid}/dataset_mounts/{dataset_mount_uuid}'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            dataset_mount_uuid=dataset_mount_uuid
        )

        return self.get(params=endpoint)

    def delete_dataset_mount(self, account_uid, project_uid, dataset_mount_uuid):
        endpoint = '/accounts/{account_uid}/projects/{project_uid}/dataset_mounts/{dataset_mount_uuid}'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            dataset_mount_uuid=dataset_mount_uuid
        )

        return self.delete(uid=endpoint)