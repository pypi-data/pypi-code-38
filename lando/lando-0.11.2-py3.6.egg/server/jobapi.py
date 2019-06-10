"""
Allows reading and updating job information when talking to Bespin REST api.
"""

import requests
import json


class BespinApi(object):
    """
    Low level api that interfaces with the bespin REST api.
    """
    def __init__(self, config):
        """
        :param config: ServerConfig: contains settings for connecting to REST api
        """
        self.settings = config.bespin_api_settings

    def headers(self):
        """
        Create HTTP header containing auth info.
        :return: dict: request headers
        """
        return {
            'Authorization': 'Token {}'.format(self.settings.token),
            'Content-type': 'application/json'
        }

    def get_job(self, job_id):
        """
        Get dictionary of info about a job.
        :param job_id: int: unique job id
        :return: dict: job details
        """
        path = 'jobs/{}/'.format(job_id)
        url = self._make_url(path)
        resp = requests.get(url, headers=self.headers())
        resp.raise_for_status()
        return resp.json()

    def get_jobs_for_vm_instance_name(self, vm_instance_name):
        """
        Get list of jobs that are setup to run on vm_instance_name.
        :param vm_instance_name: str: unique name of the vm (also name of the vm's queue)
        :return: list: list of dict: list of job info
        """
        path = 'jobs/?vm_instance_name={}'.format(vm_instance_name)
        url = self._make_url(path)
        return self._get_results(url)

    def put_job(self, job_id, data):
        """
        Update a job with some fields.
        :param job_id: int: unique job id
        :param data: dict: params we want to update on the job
        :return: dict: put response
        """
        path = 'jobs/{}/'.format(job_id)
        url = self._make_url(path)
        resp = requests.put(url, headers=self.headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    def get_file_stage_group(self, stage_group):
        """
        Get the list of input files(files that need to be staged) for a job.
        :param stage_group: int: unique stage group id
        :return: dict: details about files that need to be staged
        """
        path = 'job-file-stage-groups/{}'.format(stage_group)
        url = self._make_url(path)
        return self._get_results(url)

    def _make_url(self, suffix):
        return '{}/admin/{}'.format(self.settings.url, suffix)

    def get_dds_user_credentials(self):
        """
        Get all duke data service user credentials.
        :return: dict: credentials details
        """
        path = 'dds-user-credentials/'
        url = self._make_url(path)
        return self._get_results(url)

    def post_error(self, job_id, job_step, content):
        """
        Record message associated with an error that occurred while running a job.
        :param job_id: int: unique job id
        :param job_step: str: value from JobSteps representing where in running the job we where when this error occured
        :param content: str: text we want to store describing the error
        :return: dict: post response
        """
        path = 'job-errors/'
        url = self._make_url(path)
        resp = requests.post(url, headers=self.headers(), json={
            "job": job_id,
            "job_step": job_step,
            "content": content,
        })
        resp.raise_for_status()
        return resp.json()

    def _get_results(self, url):
        """
        Given a url that returns a JSON array send a GET request and return the results
        :param url: str: url which returns a list of items
        :return: [dict]: items returned from request
        """
        results = []
        resp = requests.get(url, headers=self.headers())
        resp.raise_for_status()
        json_data = resp.json()
        return json_data

    def put_job_output_project(self, job_dds_output_project_id, data):
        """
        Update a job with some fields.
        :param job_dds_output_project_id: int: unique job_dds_output_project id
        :param data: dict: params we want to update on the job_output_project
        :return: dict: put response
        """
        path = 'job-dds-output-projects/{}/'.format(job_dds_output_project_id)
        url = self._make_url(path)
        resp = requests.put(url, headers=self.headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    def get_share_dds_ids(self, share_group):
        """
        Get the list of users who are part of a share_group (should have job results shared with them).
        :param share_group: int: unique share group id
        :return: dict: details about users that need to have results shared with them
        """
        path = 'share-groups/{}'.format(share_group)
        url = self._make_url(path)
        return self._get_results(url)

    def get_workflow_methods_document(self, methods_document_id):
        """
        Get details about a workflow version's methods document
        :param methods_document_id: int: unique methods document id
        :return: dict: details of a methods document
        """
        path = 'workflow-methods-documents/{}'.format(methods_document_id)
        url = self._make_url(path)
        return self._get_results(url)


class JobApi(object):
    """
    Allows communicating with bespin job api for a particular job.
    """
    def __init__(self, config, job_id):
        """
        :param config: ServerConfig: contains settings for connecting to REST api
        :param job_id: int: unique job id we want to work with
        """
        self.api = BespinApi(config)
        self.job_id = job_id

    def get_job(self):
        """
        Get information about our job.
        :return: Job: contains properties about this job
        """
        return Job(self.api.get_job(self.job_id))

    def set_job_state(self, state):
        """
        Change the state of the job to the passed value.
        :param state: str: value from JobStates
        """
        self._set_job({'state': state})

    def set_job_step(self, step):
        """
        Change the step of the job is working on.
        :param state: str: value from JobSteps
        """
        self._set_job({'step': step})

    def set_vm_instance_name(self, vm_instance_name):
        """
        Set the vm instance name that this job is being run on.
        :param vm_instance_name: str: openstack instance name
        """
        self._set_job({'vm_instance_name': vm_instance_name})

    def set_vm_volume_name(self, vm_volume_name):
        """
        Set the vm volume name that this job is being run on.
        :param vm_volume_name: str: openstack volume name
        """
        self._set_job({'vm_volume_name': vm_volume_name})

    def _set_job(self, params):
        self.api.put_job(self.job_id, params)

    def get_input_files(self):
        """
        Get the list of input files(files that need to be staged) for a job.
        :return: InputFiles: list of files to be downloaded.
        """
        job = self.get_job()
        stage_group = self.api.get_file_stage_group(job.stage_group)
        return InputFiles(stage_group)

    def get_credentials(self):
        """
        Get all bespin service account credentials.
        :return: Credentials: bespin DukeDS credentials
        """
        job = self.get_job()
        credentials = Credentials()

        for user_credential_data in self.api.get_dds_user_credentials():
            credentials.add_user_credential(DDSUserCredential(user_credential_data))

        return credentials

    def save_error_details(self, job_step, content):
        """
        Send details about an error back to bespin-api.
        :param job_step: str: value from JobSteps representing where in running the job we where when this error occured
        :param content: str: text we want to store describing the error
        """
        self.api.post_error(self.job_id, job_step, content)

    def save_project_details(self, project_id, readme_file_id):
        """
        Update the output project with the specified project_id/readme_file_id
        :param project_id: str: uuid of the project
        :param readme_file_id: str: uuid of the readme file
        """
        job = self.get_job()
        data = {
            'id': job.output_project.id,
            'job': self.job_id,
            'project_id': project_id,
            'readme_file_id': readme_file_id
        }
        self.api.put_job_output_project(job.output_project.id, data)

    @staticmethod
    def get_jobs_for_vm_instance_name(config, vm_instance_name):
        """
        Get list of jobs that are setup to run on vm_instance_name.
        :param vm_instance_name: str: unique name of the vm (also name of the vm's queue)
        :return: list: [Job]: list of jobs for this instance(should only be one)
        """
        result = []
        api = BespinApi(config)
        for job_dict in api.get_jobs_for_vm_instance_name(vm_instance_name):
            result.append(Job(job_dict))
        return result

    def get_run_job_data(self):
        """
        Get Job data for use with running the job
        :return: RunJobData
        """
        job_data = self.api.get_job(self.job_id)
        methods_document = self.get_workflow_methods_document(job_data['workflow_version']['methods_document'])
        return RunJobData(job_data, methods_document)

    def get_store_output_job_data(self):
        """
        Get Job data for use with storing output
        :return: StoreOutputJobData
        """
        job_data = self.api.get_job(self.job_id)
        share_group_data = self.api.get_share_dds_ids(job_data['share_group'])
        share_dds_ids = [share_user['dds_id'] for share_user in share_group_data['users']]
        return StoreOutputJobData(job_data, share_dds_ids)

    def get_workflow_methods_document(self, methods_document_id):
        """
        Returns the methods document for an id. If methods_document_id is empty returns None
        :param methods_document_id: int: id of the methods document
        :return: WorkflowMethodsDocument
        """
        if methods_document_id:
            methods_document_data = self.api.get_workflow_methods_document(methods_document_id)
            return WorkflowMethodsDocument(methods_document_data)
        return None


class Job(object):
    """
    Top level job information.
    """
    def __init__(self, data):
        """
        :param data: dict: job values returned from bespin.
        """
        self.id = data['id']
        self.user_id = data['user']['id']
        self.username = data['user']['username']
        self.created = data['created']
        self.name = data['name']
        self.state = data['state']
        self.step = data['step']
        self.job_flavor_name = data['job_flavor']['name']
        self.job_flavor_cpus = data['job_flavor']['cpus']
        self.job_flavor_memory = data['job_flavor']['memory']
        self.vm_instance_name = data['vm_instance_name']
        self.vm_volume_name = data['vm_volume_name']
        self.stage_group = data['stage_group']
        self.workflow = Workflow(data)
        self.output_project = OutputProject(data)
        self.volume_size = data['volume_size']
        # Volume mounts is JSON encoded in a text field
        self.volume_mounts = json.loads(data['vm_volume_mounts'])
        self.cleanup_vm = data.get('cleanup_vm', True)

        job_settings = data['job_settings']
        self.vm_settings = None
        if job_settings['job_runtime_openstack']:
            self.vm_settings = VMSettings(job_settings['job_runtime_openstack'])

        self.k8s_settings = None
        if job_settings['job_runtime_k8s']:
            self.k8s_settings = K8sSettings(job_settings['job_runtime_k8s'])


class RunJobData(Job):
    """
    Job data plus a workflow methods document
    """
    def __init__(self, job_data, methods_document):
        super(RunJobData, self).__init__(job_data)
        self.workflow_methods_document = methods_document


class StoreOutputJobData(Job):
    """
    Job data plus a list of dds user ids to share results with
    """
    def __init__(self, job_data, share_dds_ids):
        super(StoreOutputJobData, self).__init__(job_data)
        self.share_dds_ids = share_dds_ids


class Workflow(object):
    """
    The workflow we should run as part of a job. Returned from bespin.
    """
    def __init__(self, data):
        """
        :param data: dict: workflow values returned from bespin.
        """
        self.job_order = data['job_order']
        workflow_version = data['workflow_version']
        self.workflow_url = workflow_version['url']
        self.workflow_type = workflow_version['type']
        self.name = workflow_version['name']
        self.version = workflow_version['version']
        self.workflow_path = workflow_version['workflow_path']
        self.methods_document = workflow_version['methods_document']


class WorkflowMethodsDocument(object):
    def __init__(self, data):
        self.content = data['content']


class OutputProject(object):
    def __init__(self, data):
        output_project = data['output_project']
        self.id = output_project['id']
        self.dds_user_credentials = output_project['dds_user_credentials']


class InputFiles(object):
    """
    Represents dds/url array of files that need to be staged.
    """
    def __init__(self, data):
        """
        :param data: dict: input file values returned from bespin.
        """
        self.dds_files = [DukeDSFile(field) for field in data['dds_files']]
        self.url_files = [URLFile(field) for field in data['url_files']]

    def __str__(self):
        return 'Input file "{}" ({})'.format(self.workflow_name, self.file_type)


class DukeDSFile(object):
    """
    Information about a duke ds file that we will download during job staging.
    """
    def __init__(self, data):
        """
        :param data: dict: duke data service file values returned from bespin.
        """
        self.file_id = data['file_id']
        self.destination_path = data['destination_path']
        self.user_id = data['dds_user_credentials']
        self.size = data['size']


class URLFile(object):
    """
    Information about a url we will download during job staging.
    """
    def __init__(self, data):
        """
        :param data: dict: url values returned from bespin.
        """
        self.url = data['url']
        self.destination_path = data['destination_path']
        self.size = data['size']


class Credentials(object):
    """
    Keys for downloading from remote storage.
    """
    def __init__(self):
        self.dds_user_credentials = {}

    def add_user_credential(self, user_credential):
        """
        Add app credential to user dictionary for user_credential.id
        :param user_credential: DDSUserCredential
        """
        self.dds_user_credentials[user_credential.id] = user_credential


class DDSUserCredential(object):
    """
    Contains user key for talking to DukeDS.
    """
    def __init__(self, data):
        """
        :param data: dict: user credential values returned from bespin.
        """
        self.id = data['id']
        self.user = data['user']
        self.token = data['token']
        endpoint = data['endpoint']
        self.endpoint_api_root = endpoint['api_root']
        self.endpoint_agent_key = endpoint['agent_key']

    def __str__(self):
        return self.token


class JobStates(object):
    """
    Values for state that must match up those supported by Bespin.
    """
    NEW = 'N'
    AUTHORIZED = 'A'
    RUNNING = 'R'
    FINISHED = 'F'
    ERRORED = 'E'
    CANCELED = 'C'


class JobSteps(object):
    """
    Values for state that must match up those supported by Bespin.
    """
    CREATE_VM = 'V'
    STAGING = 'S'
    RUNNING = 'R'
    ORGANIZE_OUTPUT_PROJECT = 'o'
    STORING_JOB_OUTPUT = 'O'
    RECORD_OUTPUT_PROJECT = 'P'
    TERMINATE_VM = 'T'
    NONE = ''


class CWLCommand(object):
    """
    Stores CWL commands to pass to the worker
    """

    def __init__(self, data):
        """
        Loads JSON-encoded CWL commands from dictionary
        :param data:
        """
        self.base_command = data['cwl_base_command']
        self.pre_process_command = data.get('cwl_pre_process_command', [])
        self.post_process_command = data.get('cwl_post_process_command', [])

    def __str__(self):
        return self.base_command


class VMSettings(object):
    """
    Contains OpenStack details for launching VMs
    """
    def __init__(self, data):
        # These come from the nested cloud_settings
        cloud_settings = data['cloud_settings']
        self.vm_project_name = cloud_settings['vm_project']['name']
        self.ssh_key_name = cloud_settings['ssh_key_name']
        self.network_name = cloud_settings['network_name']
        self.allocate_floating_ips = cloud_settings['allocate_floating_ips']
        self.floating_ip_pool_name = cloud_settings['floating_ip_pool_name']
        # These are in the data dictionary directly
        self.image_name = data['image_name']
        self.cwl_commands = CWLCommand(data)


class K8sSettings(object):
    """
    Contains k8s details for launching jobs
    """
    def __init__(self, data):
        steps = {}
        for step in data['steps']:
            name = step['step_type']
            steps[name] = K8sStepCommand(step)
        self.stage_data = steps['stage_data']
        self.run_workflow = steps['run_workflow']
        self.organize_output = steps['organize_output']
        self.save_output = steps['save_output']
        self.record_output_project = steps['record_output_project']


class K8sStepCommand(object):
    def __init__(self, data):
        self.image_name = data['image_name']
        self.base_command = data['base_command']
        self.cpus = data['flavor']['cpus']
        self.memory = data['flavor']['memory']
