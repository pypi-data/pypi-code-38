import platform
import subprocess
import os
import sys
from distutils.sysconfig import get_python_lib

from onepanel.utilities.s3.aws_cli_wrapper import AWSCLIWrapper


class AWSUtility:
    env = {}  # Use for shell command environment variables
    suppress_output = False
    run_cmd_background = False
    # Windows Specific
    # https://docs.microsoft.com/en-us/windows/desktop/ProcThread/process-creation-flags
    # This is used to run processes in the background on Windows
    CREATE_NO_WINDOW = 0x08000000

    def __init__(self, aws_access_key_id='',
                 aws_secret_access_key='',
                 aws_session_token=''):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.env = {'AWS_ACCESS_KEY_ID': self.aws_access_key_id, 'AWS_SECRET_ACCESS_KEY': self.aws_secret_access_key,
                    'AWS_SESSION_TOKEN': self.aws_session_token,
                    }
        if platform.system() is 'Windows':
            self.env[str('SYSTEMROOT')] = os.environ['SYSTEMROOT']
            self.env[str('PATH')] = os.environ['PATH']
            self.env[str('PYTHONPATH')] = os.pathsep.join(sys.path)

    def build_full_s3_url(self, s3_path):
        s3_path = 's3://{bucket}/{path}'.format(bucket=self.get_dataset_bucket_name(), path=s3_path)
        return s3_path

    def build_full_cloud_specific_url(self, path):
        return self.build_full_s3_url(path)

    def get_dataset_bucket_name(self):
        return os.getenv('DATASET_BUCKET', 'onepanel-datasets')

    def upload_dir(self, dataset_directory, s3_directory, exclude='', delete_removed=False, authenticator=None):
        s3_path = 's3://{bucket}/{path}'.format(bucket=self.get_dataset_bucket_name(), path=s3_directory)
        aws_full_path = self.get_full_path_to_aws_cli()
        if "aws" not in aws_full_path:
            return -1

        cmd_list = []
        close_fds = False
        exclude_arg = '--exclude "{ex_str}"'.format(ex_str=exclude)
        cmd_list = cmd_list + [aws_full_path, 's3', 'sync', "\"" + dataset_directory + "\"" , s3_path, exclude_arg]

        if delete_removed:
            cmd_list.append('--delete')

        # Need to pass the command as one long string. Passing in a list does not work when executed.
        cmd = ' '.join(cmd_list)
        print("Uploading...")

        wrapper = AWSCLIWrapper(authenticator)
        results = wrapper.run(args=cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, shell=True, close_fds=close_fds)

        if self.suppress_output is False:
            suppress_s3_info = s3_path.rsplit('/', 1)[0]

            cleaned_output = results[1].replace(suppress_s3_info, '')
            sys.stdout.write(cleaned_output)

            cleaned_err = results[2].replace(suppress_s3_info, '')
            sys.stdout.write(cleaned_err)

        return 0

    def download_all(self, dataset_directory, s3_directory, delete=False):
        s3_path = 's3://{bucket}/{path}'.format(bucket=self.get_dataset_bucket_name(), path=s3_directory)
        aws_full_path = self.get_full_path_to_aws_cli()
        if "aws" in aws_full_path:
            cmd_list = []
            close_fds = False
            if self.run_cmd_background:
                if sys.platform != 'win32':
                    cmd_list.insert(0, 'nice')
                    cmd_list.insert(0, 'nohup')
                    close_fds = True
                else:
                    # /i so that windows doesn't create "%SYSTEM_DRIVE%" folder
                    cmd_list.insert(0, 'start /b /i')

            # Adding "" to handle file paths with spaces on Windows.
            # https://docs.python.org/3/library/subprocess.html#converting-argument-sequence
            cmd_list = cmd_list + ["\"" + aws_full_path + "\"", 's3', 'sync', "\"" + s3_path + "\"",
                                   "\"" + dataset_directory + "\""]
            if delete:
                cmd_list.append('--delete')
                cmd_list.append('--exclude ".onepanel/*"')
            # Need to pass the command as one long string. Passing in a list does not work when executed.
            cmd = ' '.join(cmd_list)
            if self.run_cmd_background:
                print("Download starting in background.")
            else:
                print("Downloading...")

            # shell=True because we want to intercept the output from the command.
            # And also, it fixes issues with executing the string of commands.
            if self.run_cmd_background:
                if sys.platform != 'win32':
                    subprocess.Popen(args=cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, shell=True, close_fds=close_fds)
                else:
                    subprocess.Popen(args=cmd, env=self.env, shell=True, close_fds=close_fds,
                                     creationflags=self.CREATE_NO_WINDOW)
            else:
                p = subprocess.Popen(args=cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, shell=True, close_fds=close_fds)
                suppress_s3_info = s3_path.rsplit('/', 1)[0]
                for line in iter(p.stdout.readline, '' or b''):  # replace '' with b'' for Python 3
                    if self.suppress_output is False:
                        line_str = line.decode()
                        cleaned_line = line_str.replace(suppress_s3_info, '')
                        sys.stdout.write(cleaned_line)
            return 0
        return -1

    # TODO temporary method - need to redefine interface for above method
    def download_all_background(self, dataset_directory, s3_directory):
        s3_path = 's3://{bucket}/{path}'.format(bucket=self.get_dataset_bucket_name(), path=s3_directory)
        aws_full_path = self.get_full_path_to_aws_cli()

        if 'aws' not in aws_full_path:
            return -1

        cmd_list = []
        close_fds = False
        if sys.platform != 'win32':
            cmd_list.insert(0, 'nice')
            cmd_list.insert(0, 'nohup')
            close_fds = True
        else:
            # /i so that windows doesn't create "%SYSTEM_DRIVE%" folder
            cmd_list.insert(0, 'start /b /i')
        cmd_list = cmd_list + ["\"" + aws_full_path + "\"", 's3', 'sync', "\"" + s3_path + "\"",
                               "\"" + dataset_directory + "\""]

        # Need to pass the command as one long string. Passing in a list does not work when executed.
        cmd = ' '.join(cmd_list)

        # shell=True because we want to intercept the output from the command.
        # And also, it fixes issues with executing the string of commands.
        if sys.platform != 'win32':
            p = subprocess.Popen(args=cmd, env=self.env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, shell=True, close_fds=close_fds)

            return 0, p
        else:
            p = subprocess.Popen(args=cmd, env=self.env, shell=True, close_fds=close_fds,
                                 creationflags=self.CREATE_NO_WINDOW)

            return 0, p

    def download(self, to_dir, s3_full_path_to_file):
        s3_path = 's3://{bucket}/{path}'.format(bucket=self.get_dataset_bucket_name(), path=s3_full_path_to_file)
        aws_full_path = self.get_full_path_to_aws_cli()
        if "aws" in aws_full_path:
            cmd_list = []
            close_fds = False
            if self.run_cmd_background:
                if sys.platform != 'win32':
                    cmd_list.insert(0, 'nice')
                    cmd_list.insert(0, 'nohup')
                    close_fds = True
                else:
                    # /i so that windows doesn't create "%SYSTEM_DRIVE%" folder
                    cmd_list.insert(0, 'start /b /i')
            cmd_list = cmd_list + [aws_full_path, 's3', 'cp', s3_path, "\"" + to_dir + "\""]
            # Need to pass the command as one long string. Passing in a list does not work when executed.
            cmd = ' '.join(cmd_list)
            if self.run_cmd_background:
                print("Download starting in background.")
                if sys.platform != 'win32':
                    subprocess.Popen(args=cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, shell=True, close_fds=close_fds)
                else:
                    subprocess.Popen(args=cmd, env=self.env, shell=True, close_fds=close_fds,
                                     creationflags=self.CREATE_NO_WINDOW)
            else:
                print("Downloading...")
                # Also need to execute through the shell
                p = subprocess.Popen(args=cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, shell=True, close_fds=close_fds)
                suppress_s3_info = s3_path.rsplit('/', 1)[0]
                for line in iter(p.stdout.readline, '' or b''):  # replace '' with b'' for Python 3
                    if self.suppress_output is False:
                        line_str = line.decode()
                        cleaned_line = line_str.replace(suppress_s3_info, '')
                        sys.stdout.write(cleaned_line)
            return 0
        return -1

    def check_cloud_path_for_files(self,full_path,recursive=True):
        return self.check_s3_path_for_files(full_path,recursive)

    def check_s3_path_for_files(self, full_s3_path='', recursive=True):
        ret_val = {'data': None, 'code': -1, 'msg': ''}
        if full_s3_path == '':
            ret_val = {'data': None, 'code': -1, 'msg': 'Need the full s3 path passed in.'}
            return ret_val
        aws_full_path = self.get_full_path_to_aws_cli()
        if "aws" in aws_full_path:
            recursive_arg = ''
            if recursive:
                recursive_arg = '--recursive'
            # Need to pass the command as one long string. Passing in a list does not work when executed.
            cmd = ' '.join([aws_full_path, 's3', 'ls', recursive_arg, '--summarize', full_s3_path])
            # Also need to execute through the shell
            p = subprocess.Popen(args=cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
            stdout, stderr = p.communicate()
            try:
                stderr = stderr.decode()
            except AttributeError:
                pass
            if stderr != '':
                print("Error encountered.")
                print(stderr)
                return ret_val

            try:
                stdout = stdout.decode()
            except AttributeError:
                pass

            line_sep = "\n"
            if platform.system() is 'Windows':
                line_sep = "\r\n"
            raw_output = stdout.split(line_sep)
            for line in raw_output:
                if 'Total Objects' in line:
                    objects_str = line
                    str_split = objects_str.split(':')
                    # Grab the string of the number
                    string_num = str_split[-1].strip()
                    ret_val = {'data': int(string_num), 'code': 0, 'msg': 'Total files found.'}
                    break
            return ret_val
        return ret_val

    def get_cs_path_details(self, full_cs_path='', total_files=True, total_bytes=True):
        return self.get_s3_path_details(full_cs_path, total_files, total_bytes)

    def get_s3_path_details(self, full_s3_path='', total_files=True, total_bytes=True):
        ret_val = {'data': None, 'code': -1, 'msg': ''}
        data = {}
        if full_s3_path == '':
            ret_val = {'data': None, 'code': -1, 'msg': 'Need the full s3 path passed in.'}
            return ret_val
        aws_full_path = self.get_full_path_to_aws_cli()
        if "aws" in aws_full_path:
            # Need to pass the command as one long string. Passing in a list does not work when executed.
            cmd = ' '.join([aws_full_path, 's3api', 'list-objects', '--bucket', self.get_dataset_bucket_name(),
                            '--prefix', full_s3_path, '--output', 'json', '--query',
                            '"[sum(Contents[].Size), length(Contents[])]"'])
            # Also need to execute through the shell
            p = subprocess.Popen(args=cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
            p.wait()
            raw_output = p.stdout.readlines()
            # This can happen if the updater thread calls this before the upload starts
            # There will not be any output at that point, we don't want it to try
            if len(raw_output) < 1:
                data['total_bytes'] = "0"
                data['total_files'] = "0"
                ret_val = {'data': data, 'code': 0, 'msg': 'Data found.'}
                return ret_val
            if total_bytes:
                total_bytes_str = raw_output[1].decode("utf-8").strip().strip(',')
                data['total_bytes'] = total_bytes_str
            if total_files:
                total_files_str = raw_output[2].decode("utf-8").strip().strip(',')
                data['total_files'] = total_files_str

            ret_val = {'data': data, 'code': 0, 'msg': 'Data found.'}
        return ret_val

    def get_full_path_to_aws_cli(self):
        # Figure out the full path to awscli
        if platform.system() is 'Windows':
            path_to_aws_cmd = ['where', 'aws']
        else:
            path_to_aws_cmd = ['which', 'aws']
        p = subprocess.Popen(args=path_to_aws_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=False)
        p.wait()
        line = p.stdout.readline()
        return line.decode().rstrip()
