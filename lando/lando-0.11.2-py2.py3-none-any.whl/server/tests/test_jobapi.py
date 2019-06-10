
from unittest import TestCase
import copy
from lando.server.jobapi import JobApi, BespinApi, Job, CWLCommand, VMSettings
from unittest.mock import MagicMock, patch, call


@patch('lando.server.jobapi.VMSettings')
@patch('lando.server.jobapi.K8sSettings')
@patch('lando.server.jobapi.requests')
class TestJobApi(TestCase):

    def setUp(self):
        self.job_response_payload = {
            'id': 1,
            'user': {
                'id': 23,
                'username': 'joe@joe.com'
            },
            'state': 'N',
            'step': '',
            'name': 'myjob',
            'created': '2017-03-21T13:29:09.123603Z',
            'job_flavor': {
                'name': 'm1.tiny',
                'cpus': 1,
                'memory': '200MB',
            },
            'vm_instance_name': '',
            'vm_volume_name': '',
            'vm_volume_mounts': '{}',
            'job_order': '{ "value": 1 }',
            'workflow_version': {
                'name': 'SomeWorkflow',
                'version': 1,
                'url': 'file:///mnt/fastqc.cwl',
                'workflow_path': '#main',
                'type': 'packed',
                "methods_document": 7,
            },
            'job_settings': {
                'job_runtime_openstack': 'mock_job_settings',
                'job_runtime_k8s': None,
            },
            'output_project': {
                'id': 5,
                'dds_user_credentials': 123
            },
            'stage_group': None,
            'share_group': 42,
            'volume_size': 100,
            'cleanup_vm': True,
        }

    def setup_job_api(self, job_id):
        def empty_headers():
            return {}
        mock_config = MagicMock()
        mock_config.bespin_api_settings.url = 'APIURL'
        job_api = JobApi(mock_config, job_id)
        job_api.api.headers = empty_headers
        return job_api

    def test_get_job_api(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        """
        Test requesting job status, etc
        """
        job_api = self.setup_job_api(1)

        mock_response = MagicMock()
        mock_response.json.return_value = self.job_response_payload
        mock_requests.get.return_value = mock_response
        job = job_api.get_job()
        args, kwargs = mock_requests.get.call_args
        self.assertEqual(args[0], 'APIURL/admin/jobs/1/')

        self.assertEqual(1, job.id)
        self.assertEqual(23, job.user_id)
        self.assertEqual('joe@joe.com', job.username)
        self.assertEqual('N', job.state)
        self.assertEqual('m1.tiny', job.job_flavor_name)
        self.assertEqual(1, job.job_flavor_cpus)
        self.assertEqual('200MB', job.job_flavor_memory)
        self.assertEqual('', job.vm_instance_name)
        self.assertEqual('', job.vm_volume_name)
        self.assertEqual(True, job.cleanup_vm)
        args, kwargs = mock_vm_settings.call_args
        # Should call VMSettings() with contents of data['vm_settings']
        self.assertEqual(args[0], 'mock_job_settings')
        self.assertEqual('{ "value": 1 }', job.workflow.job_order)
        self.assertEqual('file:///mnt/fastqc.cwl', job.workflow.workflow_url)
        self.assertEqual('#main', job.workflow.workflow_path)
        self.assertEqual('packed', job.workflow.workflow_type)

    def test_set_job_state(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        job_api = self.setup_job_api(2)
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_requests.put.return_value = mock_response
        job_api.set_job_state('E')
        args, kwargs = mock_requests.put.call_args
        self.assertEqual(args[0], 'APIURL/admin/jobs/2/')
        self.assertEqual(kwargs.get('json'), {'state': 'E'})

    def test_set_job_step(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        job_api = self.setup_job_api(2)
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_requests.put.return_value = mock_response
        job_api.set_job_step('N')
        args, kwargs = mock_requests.put.call_args
        self.assertEqual(args[0], 'APIURL/admin/jobs/2/')
        self.assertEqual(kwargs.get('json'), {'step': 'N'})

    def test_set_vm_instance_name(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        job_api = self.setup_job_api(3)
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response
        mock_requests.put.return_value = mock_response
        job_api.set_vm_instance_name('worker_123')
        args, kwargs = mock_requests.put.call_args
        self.assertEqual(args[0], 'APIURL/admin/jobs/3/')
        self.assertEqual(kwargs.get('json'), {'vm_instance_name': 'worker_123'})

    def test_set_vm_volume_name(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        job_api = self.setup_job_api(3)
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response
        mock_requests.put.return_value = mock_response
        job_api.set_vm_volume_name('volume_765')
        args, kwargs = mock_requests.put.call_args
        self.assertEqual(args[0], 'APIURL/admin/jobs/3/')
        self.assertEqual(kwargs.get('json'), {'vm_volume_name': 'volume_765'})

    def test_get_input_files(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        self.job_response_payload['stage_group'] = '4'
        stage_group_response_payload = {
                'dds_files': [
                    {
                        'file_id': 123,
                        'destination_path': 'seq1.fasta',
                        'dds_user_credentials': 823,
                        'size': 1234,
                    }
                ],
                'url_files': [
                    {
                        'url': "https://stuff.com/file123.model",
                        'destination_path': "file123.model",
                        'size': 5678,
                    }
                ],
        }
        get_job_response = MagicMock()
        get_job_response.json.return_value = self.job_response_payload
        stage_group_response = MagicMock()
        stage_group_response.json.return_value = stage_group_response_payload
        mock_requests.get.side_effect = [
            get_job_response,
            stage_group_response
        ]
        job_api = self.setup_job_api(4)
        files = job_api.get_input_files()
        args, kwargs = mock_requests.get.call_args
        self.assertEqual(args[0], 'APIURL/admin/job-file-stage-groups/4')

        self.assertEqual(1, len(files.dds_files))
        dds_file = files.dds_files[0]
        self.assertEqual(123, dds_file.file_id)
        self.assertEqual('seq1.fasta', dds_file.destination_path)
        self.assertEqual(823, dds_file.user_id)
        self.assertEqual(1234, dds_file.size)
        self.assertEqual(1, len(files.url_files))
        url_file = files.url_files[0]
        self.assertEqual('https://stuff.com/file123.model', url_file.url)
        self.assertEqual('file123.model', url_file.destination_path)
        self.assertEqual(5678, url_file.size)

    def test_get_credentials(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        """
        The only stored credentials are the bespin system credentials.
        """
        job_response_payload = {
            'id': 4,
            'user': {
                'id': 1,
                'username': 'joe@joe.com'
            },
            'state': 'N',
            'step': '',
            'job_flavor': {
                'name': 'm1.tiny',
                'cpus': 8,
                'memory': '1G',
            },
            'vm_instance_name': '',
            'vm_volume_name': '',
            'vm_volume_mounts': '{}',
            'name': 'myjob',
            'created': '2017-03-21T13:29:09.123603Z',
            'job_order': '{ "value": 1 }',
            'workflow_version': {
                'url': 'file:///mnt/fastqc.cwl',
                'workflow_path': '#main',
                'type': 'packed',
                'name': 'SomeWorkflow',
                'version': 1,
                "methods_document": 7,
            },
            'job_settings': {
                'job_runtime_openstack': {},
                'job_runtime_k8s': {},
            },
            'output_project': {
                'id': 5,
                'dds_user_credentials': 123
            },
            'stage_group': None,
            'volume_size': 200,
        }
        user_credentials_response = [
            {
                'id': 5,
                'user': 1,
                'token': '1239109',
                'endpoint': {
                    'id': 3,
                    'name': 'dukeds',
                    'agent_key': '2191230',
                    'api_root': 'localhost/api/v1/',
                }
            }
        ]
        mock_response = MagicMock()
        mock_response.json.side_effect = [job_response_payload, user_credentials_response]
        mock_requests.get.return_value = mock_response
        job_api = self.setup_job_api(4)

        user_credentials = job_api.get_credentials()
        args, kwargs = mock_requests.get.call_args
        self.assertEqual(args[0], 'APIURL/admin/dds-user-credentials/')

        user_cred = user_credentials.dds_user_credentials[5]
        self.assertEqual('1239109', user_cred.token)
        self.assertEqual('2191230', user_cred.endpoint_agent_key)
        self.assertEqual('localhost/api/v1/', user_cred.endpoint_api_root)

    def test_get_jobs_for_vm_instance_name(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        jobs_response = [
            {
                'id': 1,
                'user': {
                    'id': 1,
                    'username': 'joe@joe.com'
                },
                'state': 'N',
                'step': '',
                'name': 'SomeJob',
                'created': '2017-03-21T13:29:09.123603Z',
                'job_flavor': {
                    'name': 'm1.tiny',
                    'cpus': 2,
                    'memory': '1G',
                },
                'vm_instance_name': '',
                'vm_volume_name': '',
                'vm_volume_mounts': '{}',
                'job_order': '{ "value": 1 }',
                'workflow_version': {
                    'url': 'file:///mnt/fastqc.cwl',
                    'workflow_path': '#main',
                    'type': 'packed',
                    'name': 'myworkflow',
                    'version': 1,
                    "methods_document": 7,
                },
                'job_settings': {
                    'job_runtime_openstack': None,
                    'job_runtime_k8s': None
                },
                'output_project': {
                    'id': 5,
                    'dds_user_credentials': 123
                },
                'stage_group': None,
                'volume_size': 200,
            }
        ]

        mock_config = MagicMock()
        mock_config.bespin_api_settings.url = 'APIURL'

        mock_response = MagicMock()
        mock_response.json.side_effect = [jobs_response]
        mock_requests.get.return_value = mock_response
        jobs = JobApi.get_jobs_for_vm_instance_name(mock_config, 'joe')
        self.assertEqual(1, len(jobs))

    def test_post_error(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_requests.get.return_value = mock_response
        job_api = self.setup_job_api(4)
        job_api.save_error_details('V', 'Out of memory')
        args, kwargs = mock_requests.post.call_args
        self.assertEqual(args[0], 'APIURL/admin/job-errors/')
        self.assertEqual(kwargs['json']['job'], 4)
        self.assertEqual(kwargs['json']['job_step'], 'V')
        self.assertEqual(kwargs['json']['content'], 'Out of memory')

    def test_job_constructor_volume_size(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        payload = dict(self.job_response_payload)
        payload['volume_size'] = 1000
        job = Job(payload)
        self.assertEqual(job.volume_size, 1000,
                         "A job payload with volume_size should result in that volume size.")

    def test_get_store_output_job_data(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        """
        Test requesting job status, etc
        """
        job_api = self.setup_job_api(1)

        mock_job_get_response = MagicMock()
        mock_job_get_response.json.return_value = self.job_response_payload

        mock_share_group_response = MagicMock()
        mock_share_group_response.json.return_value = {
            'users': [
                {
                    'dds_id': '123'
                }
            ]
        }

        mock_requests.get.side_effect = [
            mock_job_get_response,
            mock_share_group_response
        ]
        store_output_data = job_api.get_store_output_job_data()

        self.assertEqual(1, store_output_data.id)
        self.assertEqual(23, store_output_data.user_id)
        self.assertEqual('joe@joe.com', store_output_data.username)
        self.assertEqual('N', store_output_data.state)
        self.assertEqual('', store_output_data.vm_instance_name)

        self.assertEqual('{ "value": 1 }', store_output_data.workflow.job_order)
        self.assertEqual('file:///mnt/fastqc.cwl', store_output_data.workflow.workflow_url)
        self.assertEqual('#main', store_output_data.workflow.workflow_path)
        self.assertEqual('packed', store_output_data.workflow.workflow_type)

        self.assertEqual(['123'], store_output_data.share_dds_ids)

    def test_get_run_job_data(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        mock_response1 = MagicMock()
        mock_response1.json.return_value = self.job_response_payload
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {'content': '#Markdown data'}
        mock_requests.get.side_effect = [mock_response1, mock_response2]
        job_api = self.setup_job_api(4)
        run_job_data = job_api.get_run_job_data()
        self.assertEqual('myjob', run_job_data.name)
        self.assertEqual('#Markdown data', run_job_data.workflow_methods_document.content)
        mock_requests.get.assert_has_calls([
            call('APIURL/admin/jobs/4/', headers={}),
            call('APIURL/admin/workflow-methods-documents/7', headers={})
        ])
        #args, kwargs = mock_requests.get.call_args
        #self.assertEqual(args[0], 'APIURL/admin/workflow-methods-documents/123')

    def test_get_workflow_methods_document(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        mock_response = MagicMock()
        mock_response.json.return_value = {'content': '#Markdown'}
        mock_requests.get.return_value = mock_response
        job_api = self.setup_job_api(4)
        workflow_methods_document = job_api.get_workflow_methods_document('123')
        self.assertEqual('#Markdown', workflow_methods_document.content)
        args, kwargs = mock_requests.get.call_args
        self.assertEqual(args[0], 'APIURL/admin/workflow-methods-documents/123')

    def test_save_project_details(self, mock_requests, mock_k8s_settings, mock_vm_settings):
        mock_response = MagicMock()
        mock_response.json.return_value = self.job_response_payload
        mock_requests.get.return_value = mock_response
        output_project_id = 5
        dds_project_id = '123'
        dds_readme_file_id = '456'
        job_api = self.setup_job_api(1)
        job_api.save_project_details(dds_project_id, dds_readme_file_id)
        mock_requests.put.assert_has_calls([
            call('APIURL/admin/job-dds-output-projects/{}/'.format(output_project_id), headers={},
                 json={
                     'readme_file_id': dds_readme_file_id,
                     'job': 1,
                     'project_id': dds_project_id,
                     'id': output_project_id
                 })
        ])


class TestJob(TestCase):
    def setUp(self):
        job_data = {
            'id': 1,
            'user': {
                'id': 23,
                'username': 'joe@joe.com'
            },
            'state': 'N',
            'step': '',
            'name': 'myjob',
            'created': '2017-03-21T13:29:09.123603Z',
            'job_flavor': {
                'name': 'm1.tiny',
                'cpus': 1,
                'memory': '200MB',
            },
            'vm_instance_name': '',
            'vm_volume_name': '',
            'vm_volume_mounts': '{}',
            'job_order': '{ "value": 1 }',
            'workflow_version': {
                'name': 'SomeWorkflow',
                'version': 1,
                'url': 'file:///mnt/fastqc.cwl',
                'workflow_path': '#main',
                'type': 'packed',
                "methods_document": 7,
            },
            'job_settings': {
                'job_runtime_openstack': None,
                'job_runtime_k8s': None
            },
            'output_project': {
                'id': 5,
                'dds_user_credentials': 123
            },
            'stage_group': None,
            'share_group': 42,
            'volume_size': 100,
        }
        self.vm_job_data = copy.deepcopy(job_data)
        self.vm_job_data['job_settings']['name'] = 'vm'
        self.vm_job_data['job_settings']['job_runtime_openstack'] = {
            "image_name": "myimage",
            "cwl_base_command": [
                "cwltool"
            ],
            "cwl_post_process_command": [
                "cleanup.sh"
            ],
            "cwl_pre_process_command": [
                "prep.sh"
            ],
        }
        self.k8s_job_data = copy.deepcopy(job_data)
        self.k8s_job_data['job_settings']['name'] = 'k8s'
        self.k8s_job_data['job_settings']['job_runtime_k8s'] = {
            "id": 1,
            "steps": [
                {
                    "id": 1,
                    "flavor": {
                        "id": 1,
                        "name": "small",
                        "cpus": 1,
                        "memory": "1Gi"
                    },
                    "step_type": "stage_data",
                    "image_name": "lando-util:latest",
                    "base_command": [
                        "download"
                    ]
                },
                {
                    "id": 2,
                    "flavor": {
                        "id": 2,
                        "name": "large",
                        "cpus": 32,
                        "memory": "64Gi"
                    },
                    "step_type": "run_workflow",
                    "image_name": "dukegcb/calrissian:0.2.1",
                    "base_command": [
                        "calrissian"
                    ]
                },
                {
                    "id": 3,
                    "flavor": {
                        "id": 1,
                        "name": "small",
                        "cpus": 1,
                        "memory": "1Gi"
                    },
                    "step_type": "organize_output",
                    "image_name": "lando-util:latest",
                    "base_command": [
                        "sort"
                    ]
                },
                {
                    "id": 4,
                    "flavor": {
                        "id": 1,
                        "name": "small",
                        "cpus": 1,
                        "memory": "1Gi"
                    },
                    "step_type": "save_output",
                    "image_name": "lando-util:latest",
                    "base_command": [
                        "upload"
                    ]
                },
                {
                    "id": 5,
                    "flavor": {
                        "id": 1,
                        "name": "small",
                        "cpus": 1,
                        "memory": "1Gi"
                    },
                    "step_type": "record_output_project",
                    "image_name": "lando-util:latest",
                    "base_command": [
                        "saveoutput"
                    ]
                }
            ]
        }

    @patch('lando.server.jobapi.VMSettings')
    def test_cleanup_vm_default(self, mock_vm_settings):
        mock_data = MagicMock()
        job = Job(self.vm_job_data)
        self.assertEqual(job.cleanup_vm, True)

    @patch('lando.server.jobapi.VMSettings')
    def test_cleanup_vm_true(self, mock_vm_settings):
        self.vm_job_data['cleanup_vm'] = True
        mock_data = MagicMock()
        job = Job(self.vm_job_data)
        self.assertEqual(job.cleanup_vm, True)

    @patch('lando.server.jobapi.VMSettings')
    def test_cleanup_vm_false(self, mock_vm_settings):
        self.vm_job_data['cleanup_vm'] = False
        mock_data = MagicMock()
        job = Job(self.vm_job_data)
        self.assertEqual(job.cleanup_vm, False)


class CWLCommandTests(TestCase):

    def setUp(self):
        self.only_base_command_data = {
            "cwl_base_command": ["base", "command"],
        }
        self.pre_and_post_data = {
            "cwl_base_command": ["base", "command"],
            "cwl_post_process_command": ["post", "process", "command"],
            "cwl_pre_process_command": ["pre", "process", "command"]
        }

    def test_loads_base_command(self):
        command = CWLCommand(self.only_base_command_data)
        self.assertEqual(command.base_command, ['base', 'command'])

    def test_requires_base_command(self):
        with self.assertRaises(Exception):
            CWLCommand({})

    def test_defaults_pre_and_post(self):
        command = CWLCommand(self.only_base_command_data)
        self.assertEqual(command.pre_process_command, [])
        self.assertEqual(command.post_process_command, [])

    def test_loads_pre_and_post(self):
        command = CWLCommand(self.pre_and_post_data)
        self.assertEqual(command.base_command, ['base', 'command'])
        self.assertEqual(command.pre_process_command, ['pre', 'process', 'command'])
        self.assertEqual(command.post_process_command, ['post', 'process', 'command'])


class VMSettingsTests(TestCase):

    def setUp(self):
        self.data = {
            "cloud_settings": {
                "vm_project": {
                    "name": "test_project"
                },
                "ssh_key_name": "test_ssh_key",
                "network_name": "test_network",
                "allocate_floating_ips": True,
                "floating_ip_pool_name": "test_pool_name",
            },
            "image_name": "test_image",
        }

    @patch('lando.server.jobapi.CWLCommand')
    def test_loads_vmsettings(self, mock_cwl_command):
        loaded_cwl_command = MagicMock()
        mock_cwl_command.return_value = loaded_cwl_command
        vm_settings = VMSettings(self.data)
        self.assertEqual(vm_settings.vm_project_name, 'test_project')
        self.assertEqual(vm_settings.ssh_key_name, 'test_ssh_key')
        self.assertEqual(vm_settings.network_name, 'test_network')
        self.assertEqual(vm_settings.allocate_floating_ips, True)
        self.assertEqual(vm_settings.floating_ip_pool_name, 'test_pool_name')
        self.assertEqual(vm_settings.image_name, 'test_image')
        self.assertEqual(vm_settings.cwl_commands, loaded_cwl_command)
        args, kwargs = mock_cwl_command.call_args
        self.assertEqual(args[0], self.data)
