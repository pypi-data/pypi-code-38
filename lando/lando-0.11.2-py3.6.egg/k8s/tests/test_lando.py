from lando.k8s.lando import K8sJobSettings, K8sJobActions, K8sLando, JobStates, JobSteps
from lando.server.jobapi import InputFiles
from unittest import TestCase
from unittest.mock import patch, Mock, call


class TestK8sJobSettings(TestCase):
    @patch('lando.k8s.lando.ClusterApi')
    def test_get_cluster_api(self, mock_cluster_api):
        mock_config = Mock()
        settings = K8sJobSettings(job_id=1, config=mock_config)
        cluster_api = settings.get_cluster_api()
        self.assertEqual(cluster_api, mock_cluster_api.return_value)
        mock_cluster_api.assert_called_with(
            mock_config.cluster_api_settings.host,
            mock_config.cluster_api_settings.token,
            mock_config.cluster_api_settings.namespace,
            verify_ssl=mock_config.cluster_api_settings.verify_ssl,
        )


class TestK8sJobActions(TestCase):
    def setUp(self):
        self.mock_config = Mock(base_stage_data_volume_size_in_g=1)
        self.mock_settings = Mock(job_id='49', config=self.mock_config)
        self.mock_job = Mock(state=JobStates.AUTHORIZED, step=JobSteps.NONE, created='2019-03-11T12:30',
                             workflow=Mock(workflow_url='someurl.cwl', version='2'))
        self.mock_job.name = 'myjob'
        self.mock_job.workflow.name = 'myworkflow'
        self.mock_job.workflow.workflow_type = 'packed'
        self.mock_job.id = '49'
        self.mock_job.username = 'joe@joe.com'
        self.mock_job_api = self.mock_settings.get_job_api.return_value
        self.mock_job_api.get_job.return_value = self.mock_job

    def create_actions(self):
        actions = K8sJobActions(self.mock_settings)
        actions.job_api = self.mock_job_api
        return actions

    @patch('lando.k8s.lando.ClusterApi')
    @patch('lando.k8s.lando.JobManager')
    def test_constructor(self, mock_job_manager, mock_cluster_api):
        actions = self.create_actions()
        self.assertEqual(actions.cluster_api, self.mock_settings.get_cluster_api.return_value)
        self.assertEqual(actions.manager, mock_job_manager.return_value)

    def test_job_is_at_state_and_step(self):
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.STAGING
        actions = self.create_actions()

        self.assertTrue(actions.job_is_at_state_and_step(JobStates.RUNNING, JobSteps.STAGING))
        self.assertFalse(actions.job_is_at_state_and_step(JobStates.RUNNING, JobSteps.RUNNING))
        self.assertFalse(actions.job_is_at_state_and_step(JobStates.ERRORED, JobSteps.STAGING))

    @patch('lando.k8s.lando.JobManager', autospec=True)
    def test_start_job(self, mock_job_manager):
        mock_input_file = InputFiles(
            {
                'dds_files': [{
                    'file_id': '123',
                    'destination_path': '/somepath/123.dat',
                    'size': 3 * 1024 * 1024 * 1024,  # 3 GiB
                    'dds_user_credentials': {}
                }],
                'url_files': [{
                    'url': 'someurl',
                    'destination_path': '/somepath/456.dat',
                    'size': 1 * 1024 * 1024 * 1024,  # 1 GiB
                }]
            }
        )
        self.mock_job_api.get_input_files.return_value = mock_input_file
        mock_manager = mock_job_manager.return_value
        k8s_job = Mock()
        k8s_job.metadata.name = 'job1'
        mock_manager.create_stage_data_job.return_value = k8s_job

        actions = self.create_actions()
        actions._show_status = Mock()

        actions.start_job(None)

        self.mock_job_api.set_job_state.assert_called_with(JobStates.RUNNING)
        self.assertEqual(actions.bespin_job.state, JobStates.RUNNING)
        self.mock_job_api.set_job_step.assert_has_calls([
            call(JobSteps.CREATE_VM),
            call(JobSteps.STAGING),
        ])
        mock_manager.create_stage_data_persistent_volumes.assert_called_with(5.0)
        mock_manager.create_stage_data_job.assert_called_with(mock_input_file)
        actions._show_status.assert_has_calls([
            call('Creating stage data persistent volumes'),
            call('Creating Stage data job'),
            call('Launched stage data job: job1'),
        ])

    @patch('lando.k8s.lando.JobManager')
    @patch('lando.k8s.lando.logging')
    def test_stage_job_complete_ignores_wrong_state_step(self, mock_logging, mock_job_manager):
        self.mock_job.state = JobStates.AUTHORIZED
        self.mock_job.step = JobSteps.NONE

        actions = self.create_actions()
        actions.stage_job_complete(None)

        mock_logging.info.assert_called_with("Ignoring request to run job:49 wrong step/state")
        self.mock_job_api._set_job_step.assert_not_called()

    @patch('lando.k8s.lando.JobManager')
    def test_stage_job_complete_with_valid_state_and_step(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.STAGING
        actions = self.create_actions()
        actions._show_status = Mock()
        k8s_job = Mock()
        k8s_job.metadata.name = 'job-45-john'
        mock_manager.create_run_workflow_job.return_value = k8s_job

        actions.stage_job_complete(None)

        self.mock_job_api.set_job_step.assert_called_with(JobSteps.RUNNING)
        self.assertEqual(actions.bespin_job.step, JobSteps.RUNNING)
        mock_manager.cleanup_stage_data_job.assert_called_with()
        mock_manager.create_run_workflow_persistent_volumes.assert_called_with()
        mock_manager.create_run_workflow_job.assert_called_with()

        actions._show_status.assert_has_calls([
            call('Cleaning up after stage data'),
            call('Creating volumes for running workflow'),
            call('Creating run workflow job'),
            call('Launched run workflow job: job-45-john')
        ])

    @patch('lando.k8s.lando.JobManager')
    @patch('lando.k8s.lando.logging')
    def test_run_job_complete_ignores_wrong_state_step(self, mock_logging, mock_job_manager):
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.STORING_JOB_OUTPUT

        actions = self.create_actions()
        actions.run_job_complete(None)

        mock_logging.info.assert_called_with("Ignoring request to store output for job:49 wrong step/state")
        self.mock_job_api._set_job_step.assert_not_called()

    @patch('lando.k8s.lando.JobManager')
    def test_run_job_complete_valid_state_step(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.RUNNING
        actions = self.create_actions()
        actions._show_status = Mock()
        k8s_job = Mock()
        k8s_job.metadata.name = 'job-45-john'
        mock_manager.create_organize_output_project_job.return_value = k8s_job

        actions.run_job_complete(None)

        mock_manager.cleanup_run_workflow_job.assert_called_with()
        self.mock_job_api.set_job_step.assert_called_with(JobSteps.ORGANIZE_OUTPUT_PROJECT)
        mock_manager.create_organize_output_project_job.assert_called_with(
            self.mock_job_api.get_workflow_methods_document.return_value.content
        )
        self.mock_job_api.get_workflow_methods_document.assert_called_with(
            self.mock_job_api.get_job.return_value.workflow.methods_document
        )
        actions._show_status.assert_has_calls([
            call('Creating organize output project job'),
            call('Launched organize output project job: job-45-john'),
        ])

    @patch('lando.k8s.lando.JobManager')
    @patch('lando.k8s.lando.logging')
    def test_organize_output_complete_ignores_wrong_state_step(self, mock_logging, mock_job_manager):
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.STORING_JOB_OUTPUT

        actions = self.create_actions()
        actions.organize_output_complete(None)

        mock_logging.info.assert_called_with("Ignoring request to organize output project for job:49 wrong step/state")
        self.mock_job_api._set_job_step.assert_not_called()

    @patch('lando.k8s.lando.JobManager')
    def test_organize_output_complete_valid_state_step(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.ORGANIZE_OUTPUT_PROJECT
        actions = self.create_actions()
        actions._show_status = Mock()
        k8s_job = Mock()
        k8s_job.metadata.name = 'job-45-john'
        mock_manager.create_save_output_job.return_value = k8s_job

        actions.organize_output_complete(None)

        mock_manager.cleanup_organize_output_project_job.assert_called_with()
        mock_manager.create_save_output_job.assert_called_with(
            self.mock_job_api.get_store_output_job_data.return_value.share_dds_ids
        )
        actions._show_status.assert_has_calls([
            call('Creating store output job'),
            call('Launched save output job: job-45-john'),
        ])

    @patch('lando.k8s.lando.JobManager')
    @patch('lando.k8s.lando.logging')
    def test_store_job_output_complete_ignores_wrong_state_step(self, mock_logging, mock_job_manager):
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.NONE

        actions = self.create_actions()
        actions.store_job_output_complete(None)

        mock_logging.info.assert_called_with("Ignoring request to cleanup for job:49 wrong step/state")
        self.mock_job_api._set_job_step.assert_not_called()

    @patch('lando.k8s.lando.JobManager')
    def test_store_job_output_complete_valid_state_step(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.STORING_JOB_OUTPUT
        actions = self.create_actions()
        actions._show_status = Mock()
        k8s_job = Mock()
        k8s_job.metadata.name = 'job-45-john'
        mock_manager.create_record_output_project_job.return_value = k8s_job

        actions.store_job_output_complete(None)

        mock_manager.cleanup_save_output_job.assert_called_with()
        actions._show_status.assert_has_calls([
            call('Creating record output project job'),
            call('Launched record output project job: job-45-john'),
        ])
        self.mock_job_api.set_job_step.assert_called_with(JobSteps.RECORD_OUTPUT_PROJECT)

    @patch('lando.k8s.lando.JobManager')
    @patch('lando.k8s.lando.logging')
    def test_record_output_project_complete_ignores_wrong_state_step(self, mock_logging, mock_job_manager):
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.NONE
        actions = self.create_actions()

        actions.record_output_project_complete(None)

        mock_logging.info.assert_called_with("Ignoring request to cleanup for job:49 wrong step/state")
        self.mock_job_api._set_job_step.assert_not_called()

    @patch('lando.k8s.lando.JobManager')
    def test_record_output_project_complete(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.RUNNING
        self.mock_job.step = JobSteps.RECORD_OUTPUT_PROJECT
        actions = self.create_actions()
        actions._show_status = Mock()
        mock_manager.read_record_output_project_details.return_value = '123', '456'

        actions.record_output_project_complete(None)

        mock_manager.cleanup_record_output_project_job.assert_called_with()
        self.mock_job_api.save_project_details.assert_called_with('123', '456')
        self.mock_job_api.set_job_step.assert_called_with(JobSteps.NONE)

    @patch('lando.k8s.lando.JobManager')
    def test_restart_job_when_canceled_starts_from_beginning(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.CANCELED
        self.mock_job.step = JobSteps.RUNNING
        actions = self.create_actions()
        actions.start_job = Mock()

        actions.restart_job(None)

        mock_manager.cleanup_all.assert_called_with()
        actions.start_job.assert_called_with(None)

    @patch('lando.k8s.lando.JobManager')
    def test_restart_job_continues_staging(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.ERRORED
        self.mock_job.step = JobSteps.STAGING
        actions = self.create_actions()

        actions.restart_job(None)

        mock_manager.cleanup_jobs_and_config_maps.assert_called_with()
        self.mock_job_api.set_job_state.assert_called_with(JobStates.RUNNING)
        mock_manager.create_stage_data_job.assert_called_with(
            self.mock_job_api.get_input_files.return_value
        )

    @patch('lando.k8s.lando.JobManager')
    def test_restart_job_continues_running(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.ERRORED
        self.mock_job.step = JobSteps.RUNNING
        actions = self.create_actions()

        actions.restart_job(None)

        mock_manager.cleanup_jobs_and_config_maps.assert_called_with()
        self.mock_job_api.set_job_state.assert_called_with(JobStates.RUNNING)
        mock_manager.create_run_workflow_job.assert_called_with()

    @patch('lando.k8s.lando.JobManager')
    def test_restart_job_continues_organizing_output_project(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.ERRORED
        self.mock_job.step = JobSteps.ORGANIZE_OUTPUT_PROJECT
        actions = self.create_actions()

        actions.restart_job(None)

        mock_manager.cleanup_jobs_and_config_maps.assert_called_with()
        self.mock_job_api.set_job_state.assert_called_with(JobStates.RUNNING)
        mock_manager.create_organize_output_project_job.assert_called_with(
            self.mock_job_api.get_workflow_methods_document.return_value.content
        )

    @patch('lando.k8s.lando.JobManager')
    def test_restart_job_continues_save_output(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value
        self.mock_job.state = JobStates.ERRORED
        self.mock_job.step = JobSteps.STORING_JOB_OUTPUT
        actions = self.create_actions()

        actions.restart_job(None)

        mock_manager.cleanup_jobs_and_config_maps.assert_called_with()
        self.mock_job_api.set_job_state.assert_called_with(JobStates.RUNNING)
        mock_manager.create_save_output_job.assert_called_with(
            self.mock_job_api.get_store_output_job_data.return_value.share_dds_ids
        )

    @patch('lando.k8s.lando.JobManager')
    def test_restart_job_record_output_step_not_allowed(self, mock_job_manager):
        self.mock_job.state = JobStates.ERRORED
        self.mock_job.step = JobSteps.RECORD_OUTPUT_PROJECT
        actions = self.create_actions()
        actions.cannot_restart_step_error = Mock()

        actions.restart_job(None)

        actions.cannot_restart_step_error.assert_called_with(step_name='record output project')

    @patch('lando.k8s.lando.JobManager')
    def test_cancel_job(self, mock_job_manager):
        mock_manager = mock_job_manager.return_value

        actions = self.create_actions()
        actions.cancel_job(None)

        self.mock_job_api.set_job_step.assert_called_with(JobSteps.NONE)
        self.assertEqual(actions.bespin_job.step, JobSteps.NONE)
        self.mock_job_api.set_job_state.assert_called_with(JobStates.CANCELED)
        self.assertEqual(actions.bespin_job.state, JobStates.CANCELED)
        mock_manager.cleanup_all.assert_called_with()

    def test_record_output_project_error(self):
        actions = self.create_actions()
        actions._show_status = Mock()
        actions._log_error = Mock()
        actions.record_output_project_error(Mock(message='Oops'))
        self.mock_job_api.set_job_state.assert_called_with(JobStates.ERRORED)
        actions._show_status.assert_called_with('Recording output project failed')
        actions._log_error.assert_called_with(message='Oops')

    @patch('lando.k8s.lando.JobManager')
    def test_organize_output_project(self, mock_job_manager):
        actions = self.create_actions()
        self.mock_job_api.get_workflow_methods_document.return_value = Mock(content='abc')
        actions.organize_output_project()
        mock_job_manager.return_value.create_organize_output_project_job.assert_called_with(
            'abc'
        )

    @patch('lando.k8s.lando.JobManager')
    def test_organize_output_project_with_no_methods_document(self, mock_job_manager):
        actions = self.create_actions()
        self.mock_job_api.get_workflow_methods_document.return_value = None
        actions.organize_output_project()
        mock_job_manager.return_value.create_organize_output_project_job.assert_called_with(None)


class TestK8sLando(TestCase):
    @patch('lando.k8s.lando.ClusterApi')
    @patch('lando.k8s.lando.K8sJobSettings')
    @patch('lando.k8s.lando.JobManager')
    def test_constructor_creates_appropriate_job_actions(self, mock_job_manager, mock_k8s_job_settings,
                                                         mock_cluster_api):
        mock_config = Mock()
        lando = K8sLando(mock_config)
        job_actions = lando._make_actions(job_id=2)
        self.assertEqual(job_actions.__class__.__name__, 'K8sJobActions')

    @patch('lando.k8s.lando.MessageRouter')
    def test_listen_for_messages(self, mock_message_router):
        mock_config = Mock()
        lando = K8sLando(mock_config)
        lando.listen_for_messages()
        mock_message_router.make_k8s_lando_router.assert_called_with(
            mock_config, lando, mock_config.work_queue_config.listen_queue
        )
