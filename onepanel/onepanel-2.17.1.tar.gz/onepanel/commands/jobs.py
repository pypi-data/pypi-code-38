"""
Job commands
"""
import base64
import json
import os
import stat
import sys
import threading
import logging

import click
import configobj
import websocket

import onepanel.models.models as models
from onepanel.utilities.cloud_storage_utility import CloudStorageUtility
from onepanel.models.job import Job
from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required
from onepanel.commands.projects import ProjectViewController
from onepanel.commands.datasets import DatasetViewController
from onepanel.onepanel_types.project_repository import PROJECT_REPOSITORY
from onepanel.onepanel_types.dataset_mount_identifier import DATASET_MOUNT_IDENTIFIER
from onepanel.utilities.s3.file_sync import FileSynchronizer, ThreadedFileSynchronizer, FileDifference

import onepanel.utilities.s3.wrapper as S3
from onepanel.utilities.s3.authentication import APIProvider, MemoryCachedCredentialsProvider

import onepanel.services as services


COMMON_LOGGER = 'common_logger'


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        if cmd_name == 'ls':
            return click.Group.get_command(self, ctx, 'list')

        return None


class JobViewController(APIViewController):
    JOB_OUTPUT_FILE = os.path.join('.onepanel','output')
    s3_bucket_name = 'onepanel-datasets'

    @staticmethod
    def get_cloud_provider_root_for_job_output(account_uid='', project_uid='', job_uid=''):
        return '{account_uid}/projects/{project_uid}/jobs/{job_uid}/output'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            job_uid=job_uid
        )

    @staticmethod
    def get_cloud_provider_compressed_file_for_job_output_path(account_uid='', project_uid='', job_uid=''):
        return '{account_uid}/projects/{project_uid}/jobs/{job_uid}/job-{job_uid}-output.tar.gz'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            job_uid=job_uid
        )

    def __init__(self, conn):
        APIViewController.__init__(self, conn)
        self.job_uid = None
        self.project_account_uid = None
        self.project_uid = None

        self.initial_account_uid = conn.account_uid
        self.initial_project_uid = None

    def get_project_config(self):
        # Figure out the  account uid and project uid from file
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            return
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        if not os.path.exists(project_file):
            return

        cfg = configobj.ConfigObj(project_file)
        project_uid = cfg['uid']
        project_account_uid = cfg['account_uid']

        if len(project_uid) < 1 or len(project_account_uid) < 1:
            return

        self.project_account_uid = project_account_uid
        self.project_uid = project_uid
        self.initial_project_uid = project_uid

    def get_job_output_config(self):
        # Figure out the job uid, account uid and project uid from file
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + onepanel_dir)
            exit(-1)
        job_output_file = os.path.join(home, JobViewController.JOB_OUTPUT_FILE)
        if not os.path.isfile(job_output_file):
            print("ERROR.Job file does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + job_output_file)
            exit(-1)

        cfg = configobj.ConfigObj(job_output_file)

        job_uid = cfg['uid']
        project_uid = cfg['project_uid']
        account_uid = cfg['account_uid']

        if len(job_uid) < 1 or len(project_uid) < 1 or len(account_uid) < 1:
            print("ERROR.Project file has invalid credentials. Verify credentials or re-pull project.")
            exit(-1)
        self.job_uid = job_uid
        self.project_uid = project_uid
        self.project_account_uid = account_uid

    def update_config(self, project_uid=None, account_uid=None, caller_is_sdk=False):
        if not project_uid and not self.initial_project_uid:
            print('Error: Project UID cannot be blank.')
            if caller_is_sdk:
                print('Set it with the `project_uid` parameter.')
                return False
            else:
                print('Set it with the --project option.')
                sys.exit(1)
        if not account_uid and not self.initial_account_uid:
            print('Error: Account UID cannot be blank.\nRun \'onepanel login\' to login.')
            if caller_is_sdk:
                return False
            else:
                sys.exit(1)

        self.project_uid = self.initial_project_uid
        self.project_account_uid = self.initial_account_uid
        if project_uid:
            self.project_uid = project_uid
        if account_uid:
            self.project_account_uid = account_uid

        self.endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs'.format(
            root=self.conn.URL,
            account_uid=self.project_account_uid,
            project_uid=self.project_uid
        )

        return True

    def create(self, job):
        if job.code_repository is None:
            job.uid = self.upload_code()

        return self.post(post_object=job, json_encoder=models.APIJSONEncoder)

    def get_job(self, uid, project_uid=None, account_uid=None):
        response = self.get('/' + str(uid))
        if response['status_code'] == 404:
            print('Job not found')
            return

        dataset_mounts_response = self.get('/' + str(uid) + '/dataset_mounts')
        if dataset_mounts_response['status_code'] == 200:
            response['data']['datasetMounts'] = dataset_mounts_response['data']

        return Job.from_json(response['data'])

    def stop(self, account_uid=None, project_uid=None, job_uid=None):
        if account_uid is None and project_uid is None:
            account_uid = self.project_account_uid,
            project_uid = self.project_uid

        endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/job/'.format(
            root=self.conn.URL,
            account_uid=account_uid,
            project_uid=project_uid
        )

        return self.delete_v2(job_uid, '/active', endpoint=endpoint)

    def delete_job(self, account_uid=None, project_uid=None, job_uid=None):
        if account_uid is None and project_uid is None:
            account_uid = self.project_account_uid,
            project_uid = self.project_uid

        endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/job/'.format(
            root=self.conn.URL,
            account_uid=account_uid,
            project_uid=project_uid
        )

        return self.delete_v2(job_uid, endpoint=endpoint)

    def upload_code(self, uid=None, directory=os.getcwd()):
        endpoint = '{}/accounts/{}/projects/{}/credentials/aws'.format(self.conn.URL, self.project_account_uid, self.project_uid)
        authenticator = APIProvider(self.conn, endpoint)
        s3_wrapper = S3.Wrapper(credentials_provider=authenticator)

        print('Uploading code from current directory')

        if not uid:
            res = self.put(endpoint='{}/accounts/{}/projects/{}/job_number'.format(self.conn.URL, self.project_account_uid, self.project_uid))
            if res['status_code'] != 200:
                print('There was an error uploading your code')
                return
            uid = str(res['data'])

        s3_wrapper.upload_directory(directory, '{}/projects/{}/jobs/{}/code/'.format(self.project_account_uid, self.project_uid, uid), exclude=['.git', '.onepanel'])
        print('Code upload complete')
        
        return uid

    def download_code(self, uid, directory=os.getcwd()):
        endpoint = '{}/accounts/{}/projects/{}/credentials/aws'.format(self.conn.URL, self.project_account_uid, self.project_uid)
        authenticator = MemoryCachedCredentialsProvider(APIProvider(self.conn, endpoint))
        s3_wrapper = S3.Wrapper(credentials_provider=authenticator)

        print('Downloading code...')
        s3_wrapper.download_prefix('{}/projects/{}/jobs/{}/code/'.format(self.project_account_uid, self.project_uid, uid), directory)
        print('Code download complete')


@click.group(cls=AliasedGroup, help='Job commands')
@click.pass_context
def jobs(ctx):
    ctx.obj['vc'] = JobViewController(ctx.obj['connection'])
    ctx.obj['vc'].get_project_config()


@jobs.command('create', help='Create a job')
@click.argument(
    'command',
    type=str
)
@click.option(
    '-m', '--machine-type',
    type=str,
    required=True,
    help='Machine type UID. Run "onepanel machine-types list" for a list of UIDs.'
)
@click.option(
    '-e', '--environment',
    type=str,
    required=True,
    help='Environment UID. Run "onepanel environments list" for a list of UIDs.'
)
@click.option(
    '-s', '--storage',
    type=str,
    required=True,
    help='Volume type UID. Run "onepanel volume-types list" for a list of UIDs.'
)
@click.option(
    '-c', '--code-repository',
    type=PROJECT_REPOSITORY,
    required=False,
    help='''Repository and branch to pull code from.

            Format: url=<git-repo-url>[,branch=<branch>]

            Example: url=https://github.com/tensorflow/examples.git,branch=master

            "branch" is optional and will default to "master". 

            If omitted, code from current directory is uploaded.
         '''
)
@click.option(
    '-d', '--data',
    type=DATASET_MOUNT_IDENTIFIER,
    required=False,
    multiple=True,
    help='''Datasets to mount.

            Format: source=<account>/<dataset>[,version=<version>,destination=<mount-directory>]

            Example: source=onepanel/mnist,version=3,destination=mnist

            "version" is optional. If omitted, the latest version will be used.

            "destination" is optional. If omitted, "<account-name>/<dataset-name>/<version>" will be used.
        '''
)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def create_job(ctx, command, machine_type, environment, storage, data, code_repository, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.update_config(project_uid, account_uid)

    # Get the latest versions for datasets where it is unspecified.
    dvc = DatasetViewController(ctx.obj['connection'])
    for datum in data:
        if datum.version is None:
            dvc.account_uid = vc.project_account_uid
            dvc.dataset_uid = datum.dataset_uid
            dvc.init_endpoint()
            datum.version = dvc.get_version()['data']['version']['version']

    job = Job()
    job.command = command
    job.machine_type.uid = machine_type
    job.instance_template.uid = environment
    job.volume_type.uid = storage
    job.dataset_mount_claims = data
    job.code_repository = code_repository

    response = vc.create(job)
    if response['status_code'] == 200:
        print('New job created: {}'.format(response['data']['uid']))
    else:
        print("An error occurred: {}".format(response['data']))


@jobs.command('get', help='Get job detail', hidden=True)
@click.argument(
    'job_uid',
    metavar='<job-uid>',
    type=str
)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def get_job(ctx, job_uid, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.update_config(project_uid, account_uid)

    if not job_uid:
        print("Error: Job UID cannot be blank.")
        return

    job = vc.get_job(job_uid, project_uid, account_uid)
    print('UID: ' + job.uid + '\n'
        'Name: ' + job.name + '\n'
        'Command:\n' + job.command + '\n')


@jobs.command('list', help='Show a list of jobs')
@click.option(
    '-a', '--all',
    type=bool,
    is_flag=True,
    default=False,
    help='Include completed jobs'
)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def list_jobs(ctx, all, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.update_config(project_uid, account_uid)

    items = vc.list(params='?running=true' if not all else '')
    if items == None or items['totalItems'] == 0:
        print('No jobs found. Use "--all" flag to retrieve completed jobs.')
        return

    items = [Job.from_json(item).simple_view() for item in items['data']]

    vc.print_items(items, fields=['uid', 'state', 'command'],
        field_names=['UID', 'STATE', 'COMMAND'])


@jobs.command('stop', help='Stop a job')
@click.argument(
    'job_uid',
    metavar='<job-uid>',
    type=str
)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def stop_job(ctx, job_uid, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.update_config(project_uid, account_uid)
    ctx.obj['vc'].delete(job_uid, field_path='/active', message_on_success='Job stopped',
                         message_on_failure='Job not found')


@jobs.command('logs', help='Show job log')
@click.argument(
    'job_uid',
    metavar='<job-uid>',
    type=str
)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def job_logs(ctx, job_uid, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.update_config(project_uid, account_uid)

    job_data = vc.get('/' + job_uid, field_path='/logs')
    if job_data['status_code'] != 400:
        if job_data['data'] is None:
            print('Job not found.')
            return
        log = job_data['data']
        print(log)
    else:
        # Streaming via WebSocket
        # See https://pypi.python.org/pypi/websocket-client/

        def on_message(ws, message):
            if message[0] == '0':
                message = base64.b64decode(message[1:]).decode('utf-8', 'ignore')
                sys.stdout.write(message)
                sys.stdout.flush()

        def on_error(ws, error):
            if isinstance(error, websocket.WebSocketConnectionClosedException):
                return

            if isinstance(error, KeyboardInterrupt):
                return

            if error.status_code == 502 or error.status_code == 503:
                print('Job {} is preparing'.format(job_uid))
            else:
                print(error)

        def on_close(ws):
            print('connection closed')

        def on_open(ws):
            def send_auth_token(*args):
                ws.send(json.dumps({'Authtoken': ''}))

            threading.Thread(target=send_auth_token).start()

        ws_url = '{ws_root}/{account_uid}/projects/{project_uid}/jobs/{job_uid}/logs/ws?id_token={token}'.format(
            ws_root='wss://c.onepanel.io',
            account_uid=vc.project_account_uid,
            project_uid=vc.project_uid,
            job_uid=job_uid,
            token=ctx.obj['connection'].token
        )

        ws = websocket.WebSocketApp(
            url=ws_url,
            on_message=on_message,
            on_open=on_open,
            on_error=on_error
        )

        ws.run_forever()

    return False


def jobs_download_output(ctx, path, directory, archive_flag):
    jvc = JobViewController(ctx.obj['connection'])
    #
    # Resource
    #
    dirs = path.split('/')

    # Job output: Method 2
    # <account_uid>/projects/<project_uid>/jobs/<job_uid>
    if len(dirs) == 5:
        try:
            account_uid, projects_dir, project_uid, jobs_dir, job_uid = dirs
            assert (projects_dir == 'projects') and (jobs_dir == 'jobs')
        except:
            print('Incorrect job path')
            return None
    else:
        print('Incorrect job uid')
        return None

    #
    # Directory
    #
    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # Check how the job output is stored
    jvc.update_config(project_uid, account_uid)
    job_data = jvc.get('/' + job_uid)
    if job_data['data'] is None:
        print("Job not found.")
        return False

    cloud_provider_download_to_path = home
    util = CloudStorageUtility.get_utility(jvc.project_account_uid, 'projects', entity_uid=jvc.project_uid)

    if archive_flag is True:
        print("Attempting to download the compressed output file to {home} directory.".format(home=cloud_provider_download_to_path))

        cloud_provider_path_to_download_from = jvc.get_cloud_provider_compressed_file_for_job_output_path(account_uid, project_uid, job_uid)

        stats = util.get_prefix_stats(cloud_provider_path_to_download_from)

        if stats['files'] == 0:
            print("This job did not create any output or output was not saved. \n" +
                  "If you want to save and version control your output, modify your script to "
                  "save all output to the '/onepanel/output' directory.\n")
            return

        file_name = cloud_provider_path_to_download_from.split('/')[-1]
        util.download_file(cloud_provider_download_to_path + '/' + file_name, cloud_provider_path_to_download_from)
    else:
        print("Attempting to download output to {home} directory.".format(home=cloud_provider_download_to_path))
        cloud_provider_path_to_download_from = jvc.get_cloud_provider_root_for_job_output(
            account_uid, project_uid, job_uid)

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

    print("Finished downloading.")


@jobs.command('delete', help='Delete a job')
@click.argument(
    'job_uid',
    metavar='<job-uid>',
    type=str
)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def delete_job(ctx, job_uid, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.update_config(project_uid, account_uid)
    ctx.obj['vc'].delete(job_uid, message_on_success='Job deleted', message_on_failure='Job not found')


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def upload_directory_raw(ctx, project_account_uid=None, project_uid=None, job_uid=None, source_directory=None, destination_directory=None,
                     delete=False):
    ctx.obj['vc'] = JobViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']

    if project_account_uid is None or project_uid is None or job_uid is None:
        vc.get_job_output_config()
    else:
        vc.job_uid = job_uid
        vc.project_uid = project_uid
        vc.project_account_uid = project_account_uid

    if destination_directory is None:
        destination_directory = '{}/projects/{}/jobs/{}/output'.format(
            vc.project_account_uid, vc.project_uid, vc.job_uid)

    logging.getLogger(COMMON_LOGGER).info("Arguments: {}, {}, {}".format(job_uid, project_uid, project_account_uid))

    connection = services.get_connection()
    endpoint = '{}/accounts/{}/projects/{}/credentials/aws'.format(connection.URL, vc.project_account_uid,
                                                                   vc.project_uid)
    if 'authenticator' in ctx.obj:
        authenticator = ctx.obj['authenticator']
    else:
        authenticator = MemoryCachedCredentialsProvider(APIProvider(connection, endpoint))
        ctx.obj['authenticator'] = authenticator

    ignore_file_states = []
    if not delete:
        ignore_file_states.append(FileDifference.State.DELETED)

    s3_wrapper = S3.Wrapper(credentials_provider=authenticator)
    synchronizer = FileSynchronizer(source_directory, destination_directory, s3_wrapper, ignore_file_states=ignore_file_states)
    synchronizer = ThreadedFileSynchronizer(synchronizer)

    differences = synchronizer.find_difference()

    if len(differences) == 0:
        click.echo('No file differences')
        return

    synchronizer.synchronize(differences.values())
    synchronizer.shutdown()

    logging.getLogger(COMMON_LOGGER).info("Finished output upload.")


@jobs.command('upload-directory', help='Uploads directory content for a job', hidden=True)
@click.option('-a', '--project_account_uid', type=str, help='The uid of the account that owns the project the job is in')
@click.option('-p', '--project_uid', type=str, help='The uid of the project the job is for')
@click.option('-j', '--job_uid', type=str, help='The job uid')
@click.option('-s', '--path', type=str, help='Path to sync files from')
@click.option('-d', '--destination', type=str, help='Path to sync files to')
@click.option('-v', '--verbose', type=bool, help='If command should log what it is doing')
@click.option('-x', '--delete', type=bool, help='Should remote files delete to match local?')
@click.pass_context
@login_required
def upload_directory(ctx, project_account_uid, project_uid, job_uid, source_directory=None, destination_directory=None,
                     verbose=None, delete=False):
    if verbose is None:
        verbose = False

    if verbose:
        logger = logging.getLogger(COMMON_LOGGER)
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    upload_directory_raw(ctx, project_account_uid, project_uid, job_uid, source_directory, destination_directory, delete)