import json
import platform
import subprocess
import os
import sys
from google.oauth2 import service_account
from google.cloud import storage


class GCPUtility:
    env = {}  # Use for shell command environment variables
    suppress_output = False
    run_cmd_background = False
    # Windows Specific
    # https://docs.microsoft.com/en-us/windows/desktop/ProcThread/process-creation-flags
    # This is used to run processes in the background on Windows
    CREATE_NO_WINDOW = 0x08000000

    def __init__(self):
        json_str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON_STR', '')
        if not json_str:
            print("Google credentials cannot be empty! Check the environment variable: {env_var}.".format(env_var='GOOGLE_APPLICATION_CREDENTIALS_JSON_STR'))
            exit(-1)
        service_account_info = json.loads(json_str)
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        self.storageClient = storage.Client("onepanelio", credentials)
        if platform.system() is 'Windows':
            self.env[str('SYSTEMROOT')] = os.environ['SYSTEMROOT']
            self.env[str('PATH')] = os.environ['PATH']
            self.env[str('PYTHONPATH')] = os.pathsep.join(sys.path)

    def build_full_gcs_url(self, cs_path):
        cs_path = 'gs://{bucket}/{path}'.format(bucket=self.get_dataset_bucket_name(), path=cs_path)
        return cs_path

    def build_full_cloud_specific_url(self, path):
        return self.build_full_gcs_url(path)

    def get_dataset_bucket_name(self):
        return os.getenv('DATASET_BUCKET', 'onepanel-datasets')

    def upload_dir(self, dataset_directory, gcs_directory, exclude=''):
        bucket = self.storageClient.get_bucket(self.get_dataset_bucket_name())
        dataset_directory_for_upload = dataset_directory.rstrip("/")
        dataset_dir_for_hidden_check = dataset_directory.rstrip("/")
        for root, subdirs, files in os.walk(dataset_directory):
            inside_onepanel_dir = False
            # If we have a path like "/onepanel/.onepanel/job/6/" to upload from,
            # we don't want the code to prevent the upload because it has ".onepanel" in the path.
            if root != dataset_dir_for_hidden_check:
                # As we delve into sub-directories, we need to remove any occurrence
                # of .onepanel, from the original path. This is to prevent those .onepanel
                # occurrences from affecting the rest of the upload.
                # Example: "/onepanel/.onepanel/job/6/" will work.
                # We need to ensure "/onepanel/.onepanel/job/6/subdir" will also work.
                updated_root = root.replace(dataset_dir_for_hidden_check,"",1)
                file_path_list = updated_root.split(os.path.sep)
                for path_chunk in file_path_list:
                    if '.onepanel' == path_chunk:
                        inside_onepanel_dir = True
                        break
            if inside_onepanel_dir:
                continue
            for filename in files:
                root_path_for_gcp = root
                if platform.system() is 'Windows':
                    root_path_for_gcp = root_path_for_gcp.replace("\\","/")
                    dataset_directory_for_upload = dataset_directory_for_upload.replace("\\","/")
                # We want to set the specified directory as the "current directory" or context of upload.
                # This is to avoid uploading the entire absolute path.
                root_path_for_gcp = root_path_for_gcp.replace(dataset_directory_for_upload,"",1)

                file_path = os.path.join(root, filename)

                # This will be empty for top-level walking, but not sub-directories
                if not root_path_for_gcp:
                    upload_path = "/".join([gcs_directory, filename])
                else:
                    upload_path = "".join([gcs_directory, root_path_for_gcp])
                    upload_path = "/".join([upload_path, filename])
                print("Uploading {file}...".format(file=file_path))
                blob = bucket.blob(upload_path)
                blob.upload_from_filename(file_path)
                print("Uploaded {file}".format(file=file_path))
        return 0

    def download_all(self, local_directory_path_to_download_to, storage_provider_download_from_path):
        """
        This can be run in the background via 'datasets-background-download' CLI command.
        :param local_directory_path_to_download_to: string
        :param storage_provider_download_from_path: string
        :return: int
        """
        bucket = self.storageClient.get_bucket(self.get_dataset_bucket_name())
        blobs = bucket.list_blobs(prefix=storage_provider_download_from_path)
        for blob in blobs:
            blob = bucket.blob(blob.name)
            download_context = blob.name.replace(storage_provider_download_from_path, "", 1).lstrip("/")
            if platform.system() is 'Windows':
                download_context = download_context.replace("/", "\\")
            download_path = os.path.sep.join([local_directory_path_to_download_to, download_context])
            # Ensure the parent directories exist before downloading
            if platform.system() is 'Windows':
                separator_before_file = download_path.rfind("\\")
            else:
                separator_before_file = download_path.rfind("/")
            dir_path = download_path[:separator_before_file]
            if not os.path.exists(dir_path):
                os.makedirs(dir_path,exist_ok=True)
            blob.download_to_filename(download_path)
            if self.suppress_output is False:
                print('File {} downloaded to {}.'.format(
                    download_context,
                    download_path))
        return 0

    def download_all_background(self, download_to_dataset_directory, cloud_provider_download_from_directory,
                                account_uid = None, dataset_uid = None, entity_type = None):
        """
        To allow this to execute in the background, I use a subprocess.
        Well, to pass enough information to the subprocess command, I need extra information to pass in.
        Hence all these extra parameters.
        This is for GCP background download only, and not AWS.
        :param download_to_dataset_directory: string
        :param cloud_provider_download_from_directory: string
        :param account_uid: string
        :param dataset_uid: string
        :param entity_type: string
        :return:
        """
        close_fds = False
        cmd_list = ['onepanel', 'background-download']
        if cloud_provider_download_from_directory:
            cmd_list.append(cloud_provider_download_from_directory)
        if download_to_dataset_directory:
            cmd_list.append(download_to_dataset_directory)
        if self.suppress_output:
            cmd_list.append('-q')
        cmd_list.append('-b')
        cmd_list.append('--account_uid ' + account_uid)
        cmd_list.append('--entity_type ' + entity_type)
        cmd_list.append('--entity_uid ' + dataset_uid)
        if sys.platform != 'win32':
            cmd_list.insert(0, 'nice')
            cmd_list.insert(0, 'nohup')
            close_fds = True
        else:
            # /i so that windows doesn't create "%SYSTEM_DRIVE%" folder
            cmd_list.insert(0, 'start /b /i')
        cmd = ' '.join(cmd_list)
        if sys.platform != 'win32':
            stdout = open(os.path.devnull, 'a')
            stderr = open(os.path.devnull, 'a')
            p = subprocess.Popen(args=cmd, stdin=subprocess.PIPE, stdout=stdout,
                    stderr=stderr, shell=True, close_fds=close_fds, preexec_fn=os.setpgrp)
        else:
            # Windows specific instructions
            # https://docs.microsoft.com/en-us/windows/desktop/ProcThread/process-creation-flags
            CREATE_NO_WINDOW = 0x08000000
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            p = subprocess.Popen(args=cmd, shell=True, close_fds=close_fds,
                    creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP)

        return 0, p

    # todo support running in the background
    def download(self, to_dir, cloud_provider_full_path_to_file):
        bucket = self.storageClient.get_bucket(self.get_dataset_bucket_name())
        blob = bucket.blob(cloud_provider_full_path_to_file)
        if not blob.exists():
            print("File does not exist.")
            return -1
        file_to_download_idx = blob.name.rfind("/")
        download_context = blob.name[file_to_download_idx:].lstrip("/")
        if platform.system() is 'Windows':
            download_context = download_context.replace("/", "\\")
        download_path = os.path.sep.join([to_dir, download_context])
        blob.download_to_filename(download_path)
        if self.suppress_output is False:
            print('File {} downloaded to {}.'.format(
                download_context,
                download_path))
        return 0

    def check_cloud_path_for_files(self, full_cloud_path='', recursive=True):
        # We have a collision between AWS CLI code and the SDK code of GCP.
        # For AWS, this same function passes in the entire path, such as "s3://<bucket>/<project>/<etc>"
        # The reason for this path is because the AWS CLI needs this notation, so that it can download the files.
        # The GCP SDK does NOT need this, since the bucket object is retrieved from the client, and that
        # already has the "gs://<bucket>" portion of the path.
        # If "gsutil" was compatible with Python 3.x, we could use the same path as for AWS.
        # But it's not, so we have to remove the "gs://<dataset>" prefix, since it'll be passed in.
        path_without_prefix = full_cloud_path.replace(self.build_full_gcs_url(""),"",1)
        if path_without_prefix == '':
            ret_val = {'data': None, 'code': -1, 'msg': 'Need the full cloud path passed in.'}
            return ret_val
        bucket = self.storageClient.get_bucket(self.get_dataset_bucket_name())
        # Another collision between AWS CLI code and the SDK code of GCP.
        # AWSCLI would get summary information, regardless if the path to a file was passed in
        # or a directory.
        # GCP SDK has to do this differently, hence we rely that "recursive" means a directory
        if recursive:
            blobs = bucket.list_blobs(prefix=path_without_prefix)
            # Can't get initialization until you try to iterate through the blobs.
            num_files = 0
            for blob in blobs:
                num_files = num_files + 1
            ret_val = {'data': num_files, 'code': 0, 'msg': 'Total files found.'}
        else:
            blob = bucket.blob(path_without_prefix)
            if blob.exists():
                data = 1
            else:
                data = 0
            ret_val = {'data': data, 'code': 0, 'msg': 'Total files found.'}
        return ret_val

    def get_cs_path_details(self, full_cs_path='', total_files=True, total_bytes=True):
        data = {}
        if full_cs_path == '':
            ret_val = {'data': None, 'code': -1, 'msg': 'Need the full google cloud storage path passed in.'}
            return ret_val

        bucket = self.storageClient.get_bucket(self.get_dataset_bucket_name())
        total_files = 0
        total_bytes = 0

        objects_list = bucket.list_blobs(prefix=full_cs_path)
        if objects_list.num_results < 1:
            data['total_bytes'] = total_bytes
            data['total_files'] = total_files
            ret_val = {'data': data, 'code': 0, 'msg': 'Data found.'}
            return ret_val
        else:
            for obj in objects_list:
                total_files += 1
                total_bytes += obj.size

        if total_bytes:
            data['total_bytes'] = total_bytes
        if total_files:
            data['total_files'] = total_files
        ret_val = {'data': data, 'code': 0, 'msg': 'Data found.'}
        return ret_val
