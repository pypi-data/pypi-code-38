from unittest import TestCase
from unittest.mock import Mock, call, patch
from lando.k8s.jobmanager import JobManager, JobStepTypes, StageDataConfig, RunWorkflowConfig, \
    OrganizeOutputConfig, SaveOutputConfig, RecordOutputProjectConfig, Names, Paths
from lando.common.names import WorkflowTypes
import json


class TestJobManager(TestCase):
    def setUp(self):
        mock_job_order = {
            'threads': 2
        }
        self.mock_job = Mock(
            username='jpb',
            created='2019-03-11T12:30',
            workflow=Mock(workflow_url='someurl.cwl', job_order=mock_job_order, version=1,
                          workflow_type=WorkflowTypes.PACKED,
                          workflow_path='#main'),
            volume_size=3,
            job_flavor_cpus=2,
            job_flavor_memory='1G',
        )
        self.mock_job.name = "myjob"
        self.mock_job.workflow.name = "myworkflow"
        self.mock_job.id = '51'
        self.mock_job.vm_settings = None
        self.mock_job.k8s_settings.stage_data = Mock(
            image_name='image1',
            cpus=1,
            memory='1Gi',
            base_command=["python", "-m", "lando_util.download"],
        )
        self.mock_job.k8s_settings.run_workflow = Mock(
            image_name='image2',
            cpus=2,
            memory='2Gi',
            base_command=["cwltool"],
        )
        self.mock_job.k8s_settings.organize_output = Mock(
            image_name='image3',
            cpus=3,
            memory='3Gi',
            base_command=["python", "-m", "lando_util.organize_project"],
        )
        self.mock_job.k8s_settings.save_output = Mock(
            image_name='image4',
            cpus=4,
            memory='4Gi',
            base_command=["python", "-m", "lando_util.upload"],
        )
        self.mock_job.k8s_settings.record_output_project = Mock(
            image_name='image5',
            cpus=5,
            memory='5Gi'
        )
        self.expected_metadata_labels = {'bespin-job': 'true', 'bespin-job-id': '51'}

    def test_make_job_labels(self):
        manager = JobManager(cluster_api=Mock(), config=Mock(), job=self.mock_job)
        expected_label_dict = {
            'bespin-job': 'true',
            'bespin-job-id': '51',
            'bespin-job-step': 'stage_data'
        }
        self.assertEqual(manager.make_job_labels(job_step_type=JobStepTypes.STAGE_DATA), expected_label_dict)

    def test_create_stage_data_persistent_volumes(self):
        manager = JobManager(cluster_api=Mock(), config=Mock(), job=self.mock_job)
        manager.create_stage_data_persistent_volumes(stage_data_size_in_g=10)
        manager.cluster_api.create_persistent_volume_claim.assert_has_calls([
            call('job-data-51-jpb',
                 storage_class_name=manager.storage_class_name,
                 storage_size_in_g=10,
                 labels=self.expected_metadata_labels)
        ])

    def test_create_stage_data_job_packed_workflow(self):
        mock_cluster_api = Mock()
        mock_config = Mock()
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)
        mock_input_files = Mock(dds_files=[
            Mock(destination_path='file1.txt', file_id='myid')
        ])
        manager.create_stage_data_job(input_files=mock_input_files)

        # it should have created a config map of what needs to be staged
        config_map_payload = {
            'stagedata.json': json.dumps({
                "items": [
                    {
                        "type": "url",
                        "source": "someurl.cwl",
                        "dest": "/bespin/job-data/workflow/someurl.cwl"
                    },
                    {
                        "type": "write",
                        "source": {"threads": 2},
                        "dest": "/bespin/job-data/job-order.json"
                    },
                    {
                        "type": "DukeDS",
                        "source": "myid",
                        "dest": "/bespin/job-data/file1.txt"
                    }
                ]
            })
        }
        mock_cluster_api.create_config_map.assert_called_with(name='stage-data-51-jpb',
                                                              data=config_map_payload,
                                                              labels=self.expected_metadata_labels)

        # it should have created a job
        args, kwargs = mock_cluster_api.create_job.call_args
        name, batch_spec = args
        self.assertEqual(name, 'stage-data-51-jpb')  # job name
        self.assertEqual(batch_spec.name, 'stage-data-51-jpb')  # job spec name
        self.assertEqual(batch_spec.labels['bespin-job-id'], '51')  # Bespin job id stored in a label
        self.assertEqual(batch_spec.labels['bespin-job-step'], 'stage_data')  # store the job step in a label
        job_container = batch_spec.container
        self.assertEqual(job_container.name, 'stage-data-51-jpb')  # container name
        self.assertEqual(job_container.image_name, self.mock_job.k8s_settings.stage_data.image_name,
                         'stage data image name is based on a job setting')
        self.assertEqual(job_container.command, self.mock_job.k8s_settings.stage_data.base_command,
                         'stage data command is based on a job setting')
        self.assertEqual(job_container.args, ['/bespin/config/stagedata.json',
                                              '/bespin/job-data/workflow-input-files-metadata.json'],
                         'stage data command should receive config file as an argument')
        self.assertEqual(job_container.env_dict, {'DDSCLIENT_CONF': '/etc/ddsclient/config'},
                         'DukeDS environment variable should point to the config mapped config file')
        self.assertEqual(job_container.requested_cpu, self.mock_job.k8s_settings.stage_data.cpus,
                         'stage data requested cpu is based on a config setting')
        self.assertEqual(job_container.requested_memory, self.mock_job.k8s_settings.stage_data.memory,
                         'stage data requested memory is based on a config setting')
        self.assertEqual(len(job_container.volumes), 3)

        user_data_volume = job_container.volumes[0]
        self.assertEqual(user_data_volume.name, 'job-data-51-jpb')
        self.assertEqual(user_data_volume.mount_path, '/bespin/job-data')
        self.assertEqual(user_data_volume.volume_claim_name, 'job-data-51-jpb')
        self.assertEqual(user_data_volume.read_only, False)

        config_map_volume = job_container.volumes[1]
        self.assertEqual(config_map_volume.name, 'stage-data-51-jpb')
        self.assertEqual(config_map_volume.mount_path, '/bespin/config')
        self.assertEqual(config_map_volume.config_map_name, 'stage-data-51-jpb')
        self.assertEqual(config_map_volume.source_key, 'stagedata.json')
        self.assertEqual(config_map_volume.source_path, 'stagedata.json')

        secret_volume = job_container.volumes[2]
        self.assertEqual(secret_volume.name, 'data-store-51-jpb')
        self.assertEqual(secret_volume.mount_path, '/etc/ddsclient')
        self.assertEqual(secret_volume.secret_name, mock_config.data_store_settings.secret_name,
                         'name of DukeDS secret is based on a config setting')

    def test_create_stage_data_job_zipped_workflow(self):
        mock_cluster_api = Mock()
        mock_config = Mock()
        self.mock_job.workflow.workflow_type = WorkflowTypes.ZIPPED
        self.mock_job.workflow.workflow_url = 'someurl.zip'
        self.mock_job.workflow.workflow_path = 'workflows/some.cwl'
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)
        mock_input_files = Mock(dds_files=[
            Mock(destination_path='file1.txt', file_id='myid')
        ])
        manager.create_stage_data_job(input_files=mock_input_files)

        # it should have created a config map of what needs to be staged
        config_map_payload = {
            'stagedata.json': json.dumps({
                "items": [
                    {
                        "type": "url",
                        "source": "someurl.zip",
                        "dest": "/bespin/job-data/workflow/someurl.zip",
                        "unzip_to": "/bespin/job-data/workflow"
                    },
                    {
                        "type": "write",
                        "source": {"threads": 2},
                        "dest": "/bespin/job-data/job-order.json"
                    },
                    {
                        "type": "DukeDS",
                        "source": "myid",
                        "dest": "/bespin/job-data/file1.txt"
                    }
                ]
            })
        }
        mock_cluster_api.create_config_map.assert_called_with(name='stage-data-51-jpb',
                                                              data=config_map_payload,
                                                              labels=self.expected_metadata_labels)

        # it should have created a job
        args, kwargs = mock_cluster_api.create_job.call_args
        name, batch_spec = args
        self.assertEqual(name, 'stage-data-51-jpb')  # job name
        self.assertEqual(batch_spec.name, 'stage-data-51-jpb')  # job spec name
        self.assertEqual(batch_spec.labels['bespin-job-id'], '51')  # Bespin job id stored in a label
        self.assertEqual(batch_spec.labels['bespin-job-step'], 'stage_data')  # store the job step in a label
        job_container = batch_spec.container
        self.assertEqual(job_container.name, 'stage-data-51-jpb')  # container name
        self.assertEqual(job_container.image_name, self.mock_job.k8s_settings.stage_data.image_name,
                         'stage data image name is based on a job setting')
        self.assertEqual(job_container.command, self.mock_job.k8s_settings.stage_data.base_command,
                         'stage data command is based on a job setting')
        self.assertEqual(job_container.args, ['/bespin/config/stagedata.json',
                                              '/bespin/job-data/workflow-input-files-metadata.json'],
                         'stage data command should receive config file as an argument')
        self.assertEqual(job_container.env_dict, {'DDSCLIENT_CONF': '/etc/ddsclient/config'},
                         'DukeDS environment variable should point to the config mapped config file')
        self.assertEqual(job_container.requested_cpu, self.mock_job.k8s_settings.stage_data.cpus,
                         'stage data requested cpu is based on a config setting')
        self.assertEqual(job_container.requested_memory, self.mock_job.k8s_settings.stage_data.memory,
                         'stage data requested memory is based on a config setting')
        self.assertEqual(len(job_container.volumes), 3)

        user_data_volume = job_container.volumes[0]
        self.assertEqual(user_data_volume.name, 'job-data-51-jpb')
        self.assertEqual(user_data_volume.mount_path, '/bespin/job-data')
        self.assertEqual(user_data_volume.volume_claim_name, 'job-data-51-jpb')
        self.assertEqual(user_data_volume.read_only, False)

        config_map_volume = job_container.volumes[1]
        self.assertEqual(config_map_volume.name, 'stage-data-51-jpb')
        self.assertEqual(config_map_volume.mount_path, '/bespin/config')
        self.assertEqual(config_map_volume.config_map_name, 'stage-data-51-jpb')
        self.assertEqual(config_map_volume.source_key, 'stagedata.json')
        self.assertEqual(config_map_volume.source_path, 'stagedata.json')

        secret_volume = job_container.volumes[2]
        self.assertEqual(secret_volume.name, 'data-store-51-jpb')
        self.assertEqual(secret_volume.mount_path, '/etc/ddsclient')
        self.assertEqual(secret_volume.secret_name, mock_config.data_store_settings.secret_name,
                         'name of DukeDS secret is based on a config setting')

    def test_cleanup_stage_data_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock()
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.cleanup_stage_data_job()

        mock_cluster_api.delete_job.assert_called_with('stage-data-51-jpb')
        mock_cluster_api.delete_config_map.assert_called_with('stage-data-51-jpb')

    def test_create_run_workflow_persistent_volumes(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.create_run_workflow_persistent_volumes()

        mock_cluster_api.create_persistent_volume_claim.assert_called_with(
            'output-data-51-jpb', storage_class_name='nfs', storage_size_in_g=3, labels=self.expected_metadata_labels)

    def test_create_run_workflow_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.create_run_workflow_job()

        # it should have created a job to run the workflow with several volumes mounted
        args, kwargs = mock_cluster_api.create_job.call_args
        name, batch_spec = args
        self.assertEqual(name, 'run-workflow-51-jpb')  # job name
        self.assertEqual(batch_spec.name, 'run-workflow-51-jpb')  # job spec name
        self.assertEqual(batch_spec.labels['bespin-job-id'], '51')  # Bespin job id stored in a label
        self.assertEqual(batch_spec.labels['bespin-job-step'], 'run_workflow')  # store the job step in a label
        job_container = batch_spec.container
        self.assertEqual(job_container.name, 'run-workflow-51-jpb')  # container name
        self.assertEqual(job_container.image_name, self.mock_job.k8s_settings.run_workflow.image_name,
                         'run workflow image name is based on job settings')
        expected_bash_command = 'cwltool --cachedir /bespin/output-data/tmpout/ ' \
                                '--outdir /bespin/output-data/results/ ' \
                                '--max-ram 1G --max-cores 2 ' \
                                '--usage-report /bespin/output-data/job-51-jpb-resource-usage.json ' \
                                '--stdout /bespin/output-data/bespin-workflow-output.json ' \
                                '--stderr /bespin/output-data/bespin-workflow-output.log ' \
                                '/bespin/job-data/workflow/someurl.cwl#main ' \
                                '/bespin/job-data/job-order.json'.split(' ')
        self.assertEqual(job_container.command, expected_bash_command,
                         'run workflow command combines job settings and staged files')
        self.assertEqual(job_container.env_dict['CALRISSIAN_POD_NAME'].field_path, 'metadata.name',
                         'We should store the pod name in a CALRISSIAN_POD_NAME environment variable')
        self.assertEqual(job_container.requested_cpu, self.mock_job.k8s_settings.run_workflow.cpus,
                         'run workflow requested cpu is based on a job setting')
        self.assertEqual(job_container.requested_memory, self.mock_job.k8s_settings.run_workflow.memory,
                         'run workflow requested memory is based on a job setting')

        self.assertEqual(len(job_container.volumes), 3)

        job_data_volume = job_container.volumes[0]
        self.assertEqual(job_data_volume.name, 'job-data-51-jpb')
        self.assertEqual(job_data_volume.mount_path, '/bespin/job-data')
        self.assertEqual(job_data_volume.volume_claim_name, 'job-data-51-jpb')
        self.assertEqual(job_data_volume.read_only, True, 'job data should be a read only volume')

        output_data_volume = job_container.volumes[1]
        self.assertEqual(output_data_volume.name, 'output-data-51-jpb')
        self.assertEqual(output_data_volume.mount_path, '/bespin/output-data')
        self.assertEqual(output_data_volume.volume_claim_name, 'output-data-51-jpb')
        self.assertEqual(output_data_volume.read_only, False)

        system_data_volume = job_container.volumes[2]
        self.assertEqual(system_data_volume.name, 'system-data-51-jpb')
        self.assertEqual(system_data_volume.mount_path,
                         mock_config.run_workflow_settings.system_data_volume.mount_path,
                         'mount path for the system volume is based on a config setting')
        self.assertEqual(system_data_volume.volume_claim_name,
                         mock_config.run_workflow_settings.system_data_volume.volume_claim_name,
                         'pvc name for the system volume is based on a config setting')
        self.assertEqual(system_data_volume.read_only, True,
                         'system data should be read only for running workflow')

    def test_cleanup_run_workflow_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.cleanup_run_workflow_job()

        mock_cluster_api.delete_job.assert_called_with('run-workflow-51-jpb')
        mock_cluster_api.delete_persistent_volume_claim.assert_not_called()

    def test_create_organize_output_project_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.create_organize_output_project_job(methods_document_content='markdown')

        # it should have created a job to run the workflow with several volumes mounted
        args, kwargs = mock_cluster_api.create_job.call_args
        name, batch_spec = args
        self.assertEqual(name, 'organize-output-51-jpb')  # job name
        self.assertEqual(batch_spec.name, 'organize-output-51-jpb')  # job spec name
        self.assertEqual(batch_spec.labels['bespin-job-id'], '51')  # Bespin job id stored in a label
        self.assertEqual(batch_spec.labels['bespin-job-step'], 'organize_output')  # store the job step in a label
        job_container = batch_spec.container
        self.assertEqual(job_container.name, 'organize-output-51-jpb')  # container name
        self.assertEqual(job_container.image_name, self.mock_job.k8s_settings.organize_output.image_name,
                         'organize output image name is based on job settings')
        self.assertEqual(job_container.command, self.mock_job.k8s_settings.organize_output.base_command,
                         'organize output command is based on job settings')
        self.assertEqual(job_container.requested_cpu, self.mock_job.k8s_settings.organize_output.cpus,
                         'organize output requested cpu is based on a job setting')
        self.assertEqual(job_container.requested_memory, self.mock_job.k8s_settings.organize_output.memory,
                         'organize output requested memory is based on a job setting')

        mock_cluster_api.create_config_map.assert_called_with(
            name='organize-output-51-jpb',
            data={
                'organizeoutput.json':
                    json.dumps({
                        "bespin_job_id": '51',
                        "destination_dir": "/bespin/output-data/results",
                        "downloaded_workflow_path": "/bespin/job-data/workflow/someurl.cwl",
                        "workflow_to_read": "/bespin/job-data/workflow/someurl.cwl",
                        "workflow_type": "packed",
                        "job_order_path": "/bespin/job-data/job-order.json",
                        "bespin_workflow_stdout_path": "/bespin/output-data/bespin-workflow-output.json",
                        "bespin_workflow_stderr_path": "/bespin/output-data/bespin-workflow-output.log",
                        "methods_template": "markdown",
                        "additional_log_files": ["/bespin/output-data/job-51-jpb-resource-usage.json"]
                    })
                },
            labels={'bespin-job': 'true', 'bespin-job-id': '51'}
        )

        self.assertEqual(len(job_container.volumes), 3)

        job_data_volume = job_container.volumes[0]
        self.assertEqual(job_data_volume.name, 'job-data-51-jpb')
        self.assertEqual(job_data_volume.mount_path, '/bespin/job-data')
        self.assertEqual(job_data_volume.volume_claim_name, 'job-data-51-jpb')
        self.assertEqual(job_data_volume.read_only, True, 'job data should be a read only volume')

        output_data_volume = job_container.volumes[1]
        self.assertEqual(output_data_volume.name, 'output-data-51-jpb')
        self.assertEqual(output_data_volume.mount_path, '/bespin/output-data')
        self.assertEqual(output_data_volume.volume_claim_name, 'output-data-51-jpb')
        self.assertEqual(output_data_volume.read_only, False)

        config_map_volume = job_container.volumes[2]
        self.assertEqual(config_map_volume.name, 'organize-output-51-jpb')
        self.assertEqual(config_map_volume.mount_path, '/bespin/config')
        self.assertEqual(config_map_volume.config_map_name, 'organize-output-51-jpb')
        self.assertEqual(config_map_volume.source_key, 'organizeoutput.json')
        self.assertEqual(config_map_volume.source_path, 'organizeoutput.json')

    def test_cleanup_organize_output_project_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.cleanup_organize_output_project_job()

        mock_cluster_api.delete_config_map.assert_called_with('organize-output-51-jpb')
        mock_cluster_api.delete_job.assert_called_with('organize-output-51-jpb')

    def test_create_save_output_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.create_save_output_job(share_dds_ids=['123','456'])

        # it should have created a config map of what needs to be staged
        config_map_payload = {
            'saveoutput.json': json.dumps({
                "destination": "Bespin myworkflow v1 myjob 2019-03-11",
                "readme_file_path": "results/docs/README.md",
                "paths": ["/bespin/output-data/results"],
                "share": {"dds_user_ids": ["123", "456"]},
                "activity": {
                    "name": "myjob - Bespin Job 51",
                    "description": "Bespin Job 51 - Workflow myworkflow v1",
                    "started_on": "",
                    "ended_on": "",
                    "input_file_versions_json_path": "/bespin/job-data/workflow-input-files-metadata.json",
                    "workflow_output_json_path": "/bespin/output-data/bespin-workflow-output.json"
                }
            })
        }
        mock_cluster_api.create_config_map.assert_called_with(name='save-output-51-jpb',
                                                              data=config_map_payload,
                                                              labels=self.expected_metadata_labels)

        # it should have created a job
        args, kwargs = mock_cluster_api.create_job.call_args
        name, batch_spec = args
        self.assertEqual(name, 'save-output-51-jpb')  # job name
        self.assertEqual(batch_spec.name, 'save-output-51-jpb')  # job spec name
        self.assertEqual(batch_spec.labels['bespin-job-id'], '51')  # Bespin job id stored in a label
        self.assertEqual(batch_spec.labels['bespin-job-step'], 'save_output')  # store the job step in a label
        job_container = batch_spec.container
        self.assertEqual(job_container.name, 'save-output-51-jpb')  # container name
        self.assertEqual(job_container.image_name, self.mock_job.k8s_settings.save_output.image_name,
                         'save output image name is based on a job setting')
        self.assertEqual(job_container.command, self.mock_job.k8s_settings.save_output.base_command,
                         'save output command is based on a job setting')
        self.assertEqual(job_container.args,
                         ['/bespin/config/saveoutput.json', '/bespin/output-data/annotate_project_details.sh'],
                         'save output command should receive config file and output filenames as arguments')
        self.assertEqual(job_container.env_dict, {'DDSCLIENT_CONF': '/etc/ddsclient/config'},
                         'DukeDS environment variable should point to the config mapped config file')
        self.assertEqual(job_container.requested_cpu, self.mock_job.k8s_settings.save_output.cpus,
                         'stage data requested cpu is based on a job setting')
        self.assertEqual(job_container.requested_memory, self.mock_job.k8s_settings.save_output.memory,
                         'stage data requested memory is based on a job setting')
        self.assertEqual(len(job_container.volumes), 4)

        job_data_volume = job_container.volumes[0]
        self.assertEqual(job_data_volume.name, 'job-data-51-jpb')
        self.assertEqual(job_data_volume.mount_path, '/bespin/job-data')
        self.assertEqual(job_data_volume.volume_claim_name, 'job-data-51-jpb')
        self.assertEqual(job_data_volume.read_only, True)

        job_data_volume = job_container.volumes[1]
        self.assertEqual(job_data_volume.name, 'output-data-51-jpb')
        self.assertEqual(job_data_volume.mount_path, '/bespin/output-data')
        self.assertEqual(job_data_volume.volume_claim_name, 'output-data-51-jpb')
        self.assertEqual(job_data_volume.read_only, False)  # writable so we can write project_details file

        config_map_volume = job_container.volumes[2]
        self.assertEqual(config_map_volume.name, 'stage-data-51-jpb')
        self.assertEqual(config_map_volume.mount_path, '/bespin/config')
        self.assertEqual(config_map_volume.config_map_name, 'save-output-51-jpb')
        self.assertEqual(config_map_volume.source_key, 'saveoutput.json')
        self.assertEqual(config_map_volume.source_path, 'saveoutput.json')

        secret_volume = job_container.volumes[3]
        self.assertEqual(secret_volume.name, 'data-store-51-jpb')
        self.assertEqual(secret_volume.mount_path, '/etc/ddsclient')
        self.assertEqual(secret_volume.secret_name, mock_config.data_store_settings.secret_name,
                         'name of DukeDS secret is based on a config setting')

    def test_cleanup_save_output_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.cleanup_save_output_job()

        mock_cluster_api.delete_job.assert_called_with('save-output-51-jpb')
        mock_cluster_api.delete_config_map.assert_called_with('save-output-51-jpb')
        mock_cluster_api.delete_persistent_volume_claim.assert_has_calls([
            call('job-data-51-jpb'),
        ], 'delete job data volume once running workflow completes')

    def test_create_record_output_project_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        mock_config.record_output_project_settings.service_account_name = 'annotation-writer-sa'
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.create_record_output_project_job()

        args, kwargs = mock_cluster_api.create_job.call_args
        name, batch_spec = args
        self.assertEqual(name, 'record-output-project-51-jpb')  # job name
        self.assertEqual(batch_spec.name, 'record-output-project-51-jpb')  # job spec name
        self.assertEqual(batch_spec.service_account_name, 'annotation-writer-sa')  # service account to use for the job
        self.assertEqual(batch_spec.labels['bespin-job-id'], '51')  # Bespin job id stored in a label
        self.assertEqual(batch_spec.labels['bespin-job-step'], 'record_output_project')  # store the job step in a label
        job_container = batch_spec.container
        self.assertEqual(job_container.name, 'record-output-project-51-jpb')  # container name
        self.assertEqual(job_container.image_name, self.mock_job.k8s_settings.record_output_project.image_name,
                         'record output project image name is based on a config setting')
        self.assertEqual(job_container.command, ['sh'],
                         'record output project base command is sh')
        self.assertEqual(job_container.args, ['/bespin/output-data/annotate_project_details.sh'],
                         'runs annotate_project_details script')
        self.assertEqual(job_container.env_dict['MY_POD_NAME'].field_path, 'metadata.name',
                         'record output project receives pod name in MY_POD_NAME')
        self.assertEqual(len(job_container.volumes), 1)

        job_data_volume = job_container.volumes[0]
        self.assertEqual(job_data_volume.name, 'output-data-51-jpb')
        self.assertEqual(job_data_volume.mount_path, '/bespin/output-data')
        self.assertEqual(job_data_volume.volume_claim_name, 'output-data-51-jpb')
        self.assertEqual(job_data_volume.read_only, True)

    def test_read_record_output_project_details(self):
        mock_cluster_api = Mock()
        mock_pod = Mock()
        mock_pod.metadata.annotations = {'project_id': '123', 'readme_file_id': '456'}
        mock_cluster_api.list_pods.return_value = [mock_pod]
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        project_id, readme_file_id = manager.read_record_output_project_details()

        self.assertEqual(project_id, '123')
        self.assertEqual(readme_file_id, '456')
        mock_cluster_api.list_pods.assert_called_with(
            label_selector='bespin-job=true,bespin-job-id=51,bespin-job-step=record_output_project')

    def test_read_record_output_project_details_pod_not_found(self):
        mock_cluster_api = Mock()
        mock_cluster_api.list_pods.return_value = []
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        with self.assertRaises(ValueError) as raised_exception:
            manager.read_record_output_project_details()

        self.assertEqual(str(raised_exception.exception), 'Incorrect number of pods for record output step: 0')

    def test_read_record_output_project_details_missing_fields(self):
        mock_cluster_api = Mock()
        mock_pod = Mock()
        mock_pod.metadata.name = 'mypod'
        mock_pod.metadata.annotations = {'project_id': '123'}
        mock_cluster_api.list_pods.return_value = [mock_pod]
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        with self.assertRaises(ValueError) as raised_exception:
            manager.read_record_output_project_details()
        self.assertEqual(str(raised_exception.exception), 'Missing readme_file_id in pod annotations: mypod')

        mock_pod.metadata.annotations = {'readme_file_id': '456'}
        with self.assertRaises(ValueError) as raised_exception:
            manager.read_record_output_project_details()
        self.assertEqual(str(raised_exception.exception), 'Missing project_id in pod annotations: mypod')

        mock_pod.metadata.annotations = {}
        with self.assertRaises(ValueError) as raised_exception:
            manager.read_record_output_project_details()
        self.assertEqual(str(raised_exception.exception), 'Missing project_id in pod annotations: mypod')

    def test_cleanup_record_output_project_job(self):
        mock_cluster_api = Mock()
        mock_config = Mock(storage_class_name='nfs')
        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)

        manager.cleanup_record_output_project_job()

        mock_cluster_api.delete_job.assert_called_with('record-output-project-51-jpb')
        mock_cluster_api.delete_persistent_volume_claim.assert_has_calls([
            call('output-data-51-jpb')
        ])

    def test_cleanup_all(self):
        self.mock_job.id = 1
        self.mock_job.metadata.name = 'job_1'
        mock_config_map = Mock()
        mock_config_map.metadata.name = 'config_map_1'
        mock_pvc = Mock()
        mock_pvc.metadata.name = 'pvc_1'

        mock_cluster_api = Mock()
        mock_cluster_api.list_jobs.return_value = [self.mock_job]
        mock_cluster_api.list_config_maps.return_value = [mock_config_map]
        mock_cluster_api.list_persistent_volume_claims.return_value = [mock_pvc]
        mock_config = Mock(storage_class_name='nfs')

        manager = JobManager(cluster_api=mock_cluster_api, config=mock_config, job=self.mock_job)
        manager.cleanup_all()

        mock_cluster_api.delete_job.assert_called_with('job_1')
        mock_cluster_api.delete_config_map.assert_called_with('config_map_1')
        mock_cluster_api.delete_persistent_volume_claim.assert_called_with('pvc_1')

        mock_cluster_api.list_persistent_volume_claims.assert_called_with(
            label_selector='bespin-job=true,bespin-job-id=1')
        mock_cluster_api.list_jobs.assert_called_with(
            label_selector='bespin-job=true,bespin-job-id=1')
        mock_cluster_api.list_config_maps.assert_called_with(
            label_selector='bespin-job=true,bespin-job-id=1')


class TestNames(TestCase):
    def test_constructor_packed(self):
        mock_job = Mock(username='jpb', created='2019-03-11T12:30',
                        workflow=Mock(workflow_url='https://somewhere.com/someworkflow.cwl', version=1,
                                      workflow_type=WorkflowTypes.PACKED, workflow_path='#main'))
        mock_job.name = 'myjob'
        mock_job.workflow.name = 'myworkflow'
        mock_job.id = '123'
        names = Names(mock_job, Paths(base_directory='/'))
        self.assertEqual(names.job_data, 'job-data-123-jpb')
        self.assertEqual(names.output_data, 'output-data-123-jpb')
        self.assertEqual(names.tmpout, 'tmpout-123-jpb')
        self.assertEqual(names.tmp, 'tmp-123-jpb')

        self.assertEqual(names.stage_data, 'stage-data-123-jpb')
        self.assertEqual(names.run_workflow, 'run-workflow-123-jpb')
        self.assertEqual(names.organize_output, 'organize-output-123-jpb')
        self.assertEqual(names.save_output, 'save-output-123-jpb')
        self.assertEqual(names.record_output_project, 'record-output-project-123-jpb')

        self.assertEqual(names.user_data, 'user-data-123-jpb')
        self.assertEqual(names.data_store_secret, 'data-store-123-jpb')
        self.assertEqual(names.output_project_name, 'Bespin myworkflow v1 myjob 2019-03-11')
        self.assertEqual(names.workflow_download_dest, '/bespin/job-data/workflow/someworkflow.cwl')
        self.assertEqual(names.workflow_to_run, '/bespin/job-data/workflow/someworkflow.cwl#main')
        self.assertEqual(names.workflow_to_read, '/bespin/job-data/workflow/someworkflow.cwl')
        self.assertEqual(names.job_order_path, '/bespin/job-data/job-order.json')
        self.assertEqual(names.system_data, 'system-data-123-jpb')
        self.assertEqual(names.run_workflow_stdout_path, '/bespin/output-data/bespin-workflow-output.json')
        self.assertEqual(names.run_workflow_stderr_path, '/bespin/output-data/bespin-workflow-output.log')
        self.assertEqual(names.annotate_project_details_path, '/bespin/output-data/annotate_project_details.sh')

    def test_constructor_zipped(self):
        mock_job = Mock(username='jpb', created='2019-03-11T12:30',
                        workflow=Mock(workflow_url='https://somewhere.com/someworkflow.zip', version=1,
                                      workflow_type=WorkflowTypes.ZIPPED, workflow_path='dir/workflow.cwl'))
        mock_job.name = 'myjob'
        mock_job.workflow.name = 'myworkflow'
        mock_job.id = '123'
        names = Names(mock_job, Paths(base_directory='/'))
        self.assertEqual(names.job_data, 'job-data-123-jpb')
        self.assertEqual(names.output_data, 'output-data-123-jpb')
        self.assertEqual(names.tmpout, 'tmpout-123-jpb')
        self.assertEqual(names.tmp, 'tmp-123-jpb')

        self.assertEqual(names.stage_data, 'stage-data-123-jpb')
        self.assertEqual(names.run_workflow, 'run-workflow-123-jpb')
        self.assertEqual(names.organize_output, 'organize-output-123-jpb')
        self.assertEqual(names.save_output, 'save-output-123-jpb')
        self.assertEqual(names.record_output_project, 'record-output-project-123-jpb')

        self.assertEqual(names.user_data, 'user-data-123-jpb')
        self.assertEqual(names.data_store_secret, 'data-store-123-jpb')
        self.assertEqual(names.output_project_name, 'Bespin myworkflow v1 myjob 2019-03-11')
        self.assertEqual(names.workflow_download_dest, '/bespin/job-data/workflow/someworkflow.zip')
        self.assertEqual(names.workflow_to_run, '/bespin/job-data/workflow/dir/workflow.cwl')
        self.assertEqual(names.workflow_to_read, '/bespin/job-data/workflow/dir/workflow.cwl')
        self.assertEqual(names.job_order_path, '/bespin/job-data/job-order.json')
        self.assertEqual(names.system_data, 'system-data-123-jpb')
        self.assertEqual(names.run_workflow_stdout_path, '/bespin/output-data/bespin-workflow-output.json')
        self.assertEqual(names.run_workflow_stderr_path, '/bespin/output-data/bespin-workflow-output.log')
        self.assertEqual(names.annotate_project_details_path, '/bespin/output-data/annotate_project_details.sh')

    def test_constructor_unknown(self):
        mock_job = Mock(username='jpb', created='2019-03-11T12:30',
                        workflow=Mock(workflow_url='https://somewhere.com/someworkflow.zip', version=1,
                                      workflow_type='faketype', workflow_path='dir/workflow.cwl'))
        mock_job.name = 'myjob'
        mock_job.workflow.name = 'myworkflow'
        mock_job.id = '123'
        with self.assertRaises(ValueError) as raised_exception:
            Names(mock_job, Paths(base_directory='/'))
        self.assertEqual(str(raised_exception.exception), 'Unknown workflow type faketype')

    def test_strips_username_after_at_sign(self):
        mock_job = Mock(username='tom@tom.com', created='2019-03-11T12:30',
                        workflow=Mock(workflow_url='https://somewhere.com/someworkflow.cwl', version=1,
                                      workflow_path='#main', workflow_type=WorkflowTypes.PACKED))
        mock_job.name = 'myjob'
        mock_job.workflow.name = 'myworkflow'
        mock_job.id = '123'
        names = Names(mock_job, Paths(base_directory='/'))
        self.assertEqual(names.job_data, 'job-data-123-tom')
        self.assertEqual(names.output_data, 'output-data-123-tom')
        self.assertEqual(names.tmpout, 'tmpout-123-tom')
        self.assertEqual(names.tmp, 'tmp-123-tom')

        self.assertEqual(names.stage_data, 'stage-data-123-tom')
        self.assertEqual(names.run_workflow, 'run-workflow-123-tom')
        self.assertEqual(names.organize_output, 'organize-output-123-tom')
        self.assertEqual(names.save_output, 'save-output-123-tom')

        self.assertEqual(names.user_data, 'user-data-123-tom')
        self.assertEqual(names.data_store_secret, 'data-store-123-tom')
        self.assertEqual(names.output_project_name, 'Bespin myworkflow v1 myjob 2019-03-11')
        self.assertEqual(names.workflow_download_dest, '/bespin/job-data/workflow/someworkflow.cwl')
        self.assertEqual(names.workflow_to_run, '/bespin/job-data/workflow/someworkflow.cwl#main')
        self.assertEqual(names.job_order_path, '/bespin/job-data/job-order.json')
        self.assertEqual(names.system_data, 'system-data-123-tom')
        self.assertEqual(names.run_workflow_stdout_path, '/bespin/output-data/bespin-workflow-output.json')
        self.assertEqual(names.run_workflow_stderr_path, '/bespin/output-data/bespin-workflow-output.log')


class TestStageDataConfig(TestCase):
    def test_constructor(self):
        mock_job = Mock()
        mock_job.k8s_settings.stage_data.image_name = 'someimage'
        mock_job.k8s_settings.stage_data.cpus = 6
        mock_job.k8s_settings.stage_data.memory = '6Gi'
        mock_job.k8s_settings.stage_data.base_command = ['upload']
        mock_config = Mock()
        config = StageDataConfig(job=mock_job, config=mock_config, paths=Paths(base_directory='/'))
        self.assertEqual(config.path, '/bespin/config/stagedata.json')
        self.assertEqual(config.data_store_secret_name, mock_config.data_store_settings.secret_name)
        self.assertEqual(config.data_store_secret_path, '/etc/ddsclient')
        self.assertEqual(config.env_dict, {'DDSCLIENT_CONF': '/etc/ddsclient/config'})
        self.assertEqual(config.image_name, 'someimage')
        self.assertEqual(config.command, ['upload'])
        self.assertEqual(config.requested_cpu, 6)
        self.assertEqual(config.requested_memory, '6Gi')


class TestRunWorkflowConfig(TestCase):
    def test_constructor(self):
        mock_job = Mock()
        mock_job.k8s_settings.run_workflow.image_name = 'someimage'
        mock_job.k8s_settings.run_workflow.cpus = 16
        mock_job.k8s_settings.run_workflow.memory = '4Gi'
        mock_job.k8s_settings.run_workflow.base_command = ['cwltool']
        mock_config = Mock()
        config = RunWorkflowConfig(job=mock_job, config=mock_config)
        self.assertEqual(config.image_name, 'someimage')
        self.assertEqual(config.command, ['cwltool'])
        self.assertEqual(config.requested_cpu, 16)
        self.assertEqual(config.requested_memory, '4Gi')
        self.assertEqual(config.system_data_volume, mock_config.run_workflow_settings.system_data_volume)


class TestOrganizeOutputConfig(TestCase):
    def test_constructor(self):
        mock_job = Mock()
        mock_job.k8s_settings.organize_output.image_name = 'someimage'
        mock_job.k8s_settings.organize_output.base_command = ['organizeit']
        mock_job.k8s_settings.organize_output.cpus = 8
        mock_job.k8s_settings.organize_output.memory = '1Gi'
        mock_config = Mock()
        config = OrganizeOutputConfig(job=mock_job, config=mock_config, paths=Paths(base_directory='/'))
        self.assertEqual(config.filename, "organizeoutput.json")
        self.assertEqual(config.path, "/bespin/config/organizeoutput.json")
        self.assertEqual(config.image_name, 'someimage')
        self.assertEqual(config.command, ['organizeit'])
        self.assertEqual(config.requested_cpu, 8)
        self.assertEqual(config.requested_memory, '1Gi')


class TestSaveOutputConfig(TestCase):
    def test_constructor(self):
        mock_job = Mock()
        mock_job.k8s_settings.save_output.image_name = 'someimage'
        mock_job.k8s_settings.save_output.base_command = ['upload']
        mock_job.k8s_settings.save_output.cpus = 4
        mock_job.k8s_settings.save_output.memory = '2Gi'
        mock_config = Mock()
        config = SaveOutputConfig(job=mock_job, config=mock_config, paths=Paths(base_directory='/'))
        self.assertEqual(config.path, '/bespin/config/saveoutput.json')
        self.assertEqual(config.data_store_secret_name, mock_config.data_store_settings.secret_name)
        self.assertEqual(config.data_store_secret_path, '/etc/ddsclient')
        self.assertEqual(config.env_dict, {'DDSCLIENT_CONF': '/etc/ddsclient/config'})
        self.assertEqual(config.image_name, 'someimage')
        self.assertEqual(config.command, ['upload'])
        self.assertEqual(config.requested_cpu, 4)
        self.assertEqual(config.requested_memory, '2Gi')


class TestRecordOutputProjectConfig(TestCase):
    def test_constructor(self):
        mock_job = Mock()
        mock_job.k8s_settings.record_output_project.image_name = 'someimage'
        mock_job.k8s_settings.record_output_project.cpus = 1
        mock_job.k8s_settings.record_output_project.memory = '1MB'
        mock_config = Mock()
        config = RecordOutputProjectConfig(job=mock_job, config=mock_config)
        self.assertEqual(config.image_name, 'someimage')
        self.assertEqual(config.requested_cpu, 1)
        self.assertEqual(config.requested_memory, '1MB')
        self.assertEqual(config.service_account_name, mock_config.record_output_project_settings.service_account_name)
        self.assertEqual(config.project_id_fieldname, 'project_id')
        self.assertEqual(config.readme_file_id_fieldname, 'readme_file_id')
