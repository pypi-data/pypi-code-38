from unittest import TestCase
from unittest.mock import Mock, patch
from lando.k8s.watcher import JobWatcher, JobLabels, JobStepTypes, JobCommands, JobConditionType, ApiException, \
    EventTypes


class TestJobWatcher(TestCase):
    @patch('lando.k8s.watcher.ClusterApi')
    def test_run(self, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.run()

        wait_for_job_events = mock_cluster_api.return_value.wait_for_job_events
        wait_for_job_events.assert_called_with(
            watcher.on_job_change,
            label_selector='bespin-job=true')

    @patch('lando.k8s.watcher.ClusterApi')
    def test_on_job_change_with_failed_job(self, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.on_job_succeeded = Mock()
        watcher.on_job_failed = Mock()
        job = Mock()
        job.metadata.name = 'job1'
        job.metadata.labels = {
            JobLabels.JOB_ID: '32',
            JobLabels.STEP_TYPE: JobStepTypes.STAGE_DATA,
        }
        job.status.conditions = [Mock(type=JobConditionType.FAILED, status="True")]
        watcher.on_job_change({
            'type': EventTypes.ADDED,
            'object': job
        })

        watcher.on_job_succeeded.assert_not_called()
        watcher.on_job_failed.assert_called_with('job1', '32', JobStepTypes.STAGE_DATA)

    @patch('lando.k8s.watcher.ClusterApi')
    def test_on_job_change_with_complete_job(self, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.on_job_succeeded = Mock()
        watcher.on_job_failed = Mock()
        job = Mock()
        job.metadata.name = 'job1'
        job.metadata.labels = {
            JobLabels.JOB_ID: '32',
            JobLabels.STEP_TYPE: JobStepTypes.STAGE_DATA,
        }
        job.status.conditions = [Mock(type=JobConditionType.COMPLETE, status="True")]
        watcher.on_job_change({
            'type': EventTypes.MODIFIED,
            'object': job
        })

        watcher.on_job_succeeded.assert_called_with('32', 'stage_data')
        watcher.on_job_failed.assert_not_called()

    @patch('lando.k8s.watcher.ClusterApi')
    @patch('lando.k8s.watcher.logging')
    def test_on_job_change_with_delete_event(self, mock_logging, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.on_job_succeeded = Mock()
        watcher.on_job_failed = Mock()
        job = Mock()
        job.metadata.name = 'job1'
        job.metadata.labels = {
            JobLabels.JOB_ID: '32',
            JobLabels.STEP_TYPE: JobStepTypes.STAGE_DATA,
        }
        job.status.conditions = [Mock(type=JobConditionType.COMPLETE, status="True")]
        watcher.on_job_change({
            'type': EventTypes.DELETED,
            'object': job
        })

        watcher.on_job_succeeded.assert_not_called()
        watcher.on_job_failed.assert_not_called()
        mock_logging.debug.assert_called_with('Ignoring event DELETED')

    @patch('lando.k8s.watcher.ClusterApi')
    def test_on_job_change_with_ignored_conditions(self, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.on_job_succeeded = Mock()
        watcher.on_job_failed = Mock()
        job = Mock()
        job.metadata.name = 'job1'
        job.metadata.labels = {
            JobLabels.JOB_ID: '32',
            JobLabels.STEP_TYPE: JobStepTypes.STAGE_DATA,
        }
        job.status.conditions = [
            Mock(type=JobConditionType.COMPLETE, status="False"),
            Mock(type=JobConditionType.FAILED, status="False"),
            Mock(type="other", status="True"),
        ]
        watcher.on_job_change({
            'type': EventTypes.ADDED,
            'object': job
        })

        watcher.on_job_succeeded.assert_not_called()
        watcher.on_job_failed.assert_not_called()

    @patch('lando.k8s.watcher.ClusterApi')
    def test_on_job_change_missing_labels(self, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.on_job_succeeded = Mock()
        watcher.on_job_failed = Mock()
        job = Mock()
        job.metadata.name = 'job1'
        job.metadata.labels = {}
        job.status.conditions = [
            Mock(type=JobConditionType.COMPLETE, status="True"),
            Mock(type=JobConditionType.FAILED, status="True"),
        ]
        watcher.on_job_change({
            'type': EventTypes.ADDED,
            'object': job
        })

        watcher.on_job_succeeded.assert_not_called()
        watcher.on_job_failed.assert_not_called()

    @patch('lando.k8s.watcher.ClusterApi')
    def test_on_job_succeeded(self, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.lando_client = Mock()

        watcher.on_job_succeeded('31', JobStepTypes.STAGE_DATA)
        watcher.lando_client.job_step_store_output_complete.assert_not_called()
        payload = watcher.lando_client.job_step_complete.call_args[0][0]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.success_command, JobCommands.STAGE_JOB_COMPLETE)

        watcher.lando_client.job_step_complete.reset_mock()

        watcher.on_job_succeeded('31', JobStepTypes.RUN_WORKFLOW)
        watcher.lando_client.job_step_store_output_complete.assert_not_called()
        payload = watcher.lando_client.job_step_complete.call_args[0][0]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.success_command, JobCommands.RUN_JOB_COMPLETE)

        watcher.lando_client.job_step_complete.reset_mock()

        watcher.on_job_succeeded('31', JobStepTypes.ORGANIZE_OUTPUT)
        watcher.lando_client.job_step_store_output_complete.assert_not_called()
        payload = watcher.lando_client.job_step_complete.call_args[0][0]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.success_command, JobCommands.ORGANIZE_OUTPUT_COMPLETE)

        watcher.lando_client.job_step_complete.reset_mock()

        watcher.on_job_succeeded('31', JobStepTypes.SAVE_OUTPUT)
        watcher.lando_client.job_step_complete.assert_not_called()
        payload = watcher.lando_client.job_step_store_output_complete.call_args[0][0]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.success_command, JobCommands.STORE_JOB_OUTPUT_COMPLETE)

    @patch('lando.k8s.watcher.ClusterApi')
    def test_on_job_succeeded_record_output(self, mock_cluster_api):
        watcher = JobWatcher(config=Mock())
        watcher.lando_client = Mock()

        watcher.on_job_succeeded('31', JobStepTypes.RECORD_OUTPUT_PROJECT)
        watcher.lando_client.job_step_store_output_complete.assert_not_called()
        payload = watcher.lando_client.job_step_complete.call_args[0][0]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.success_command, JobCommands.RECORD_OUTPUT_PROJECT_COMPLETE)

    @patch('lando.k8s.watcher.ClusterApi')
    def test_on_job_failed(self, mock_cluster_api):
        mock_cluster_api.return_value.read_job_logs.return_value = "Error details"
        watcher = JobWatcher(config=Mock())
        watcher.lando_client = Mock()

        watcher.on_job_failed('myjob', '31', JobStepTypes.STAGE_DATA)
        mock_cluster_api.return_value.read_job_logs.assert_called_with('myjob')
        payload = watcher.lando_client.job_step_error.call_args[0][0]
        message = watcher.lando_client.job_step_error.call_args[0][1]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.error_command, JobCommands.STAGE_JOB_ERROR)
        self.assertEqual(message, 'Error details')

        watcher.lando_client.job_step_complete.reset_mock()

        watcher.on_job_failed('myjob', '31', JobStepTypes.RUN_WORKFLOW)
        payload = watcher.lando_client.job_step_error.call_args[0][0]
        message = watcher.lando_client.job_step_error.call_args[0][1]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.error_command, JobCommands.RUN_JOB_ERROR)
        self.assertEqual(message, 'Error details')

        watcher.lando_client.job_step_complete.reset_mock()

        watcher.on_job_failed('myjob', '31', JobStepTypes.ORGANIZE_OUTPUT)
        payload = watcher.lando_client.job_step_error.call_args[0][0]
        message = watcher.lando_client.job_step_error.call_args[0][1]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.error_command, JobCommands.ORGANIZE_OUTPUT_ERROR)
        self.assertEqual(message, 'Error details')

        watcher.lando_client.job_step_complete.reset_mock()

        watcher.on_job_failed('myjob', '31', JobStepTypes.SAVE_OUTPUT)
        payload = watcher.lando_client.job_step_error.call_args[0][0]
        message = watcher.lando_client.job_step_error.call_args[0][1]
        self.assertEqual(payload.job_id, '31')
        self.assertEqual(payload.error_command, JobCommands.STORE_JOB_OUTPUT_ERROR)
        self.assertEqual(message, 'Error details')

    @patch('lando.k8s.watcher.ClusterApi')
    @patch('lando.k8s.watcher.logging')
    def test_on_job_failed_reading_logs_failed(self, mock_logging, mock_cluster_api):
            mock_cluster_api.return_value.read_job_logs.side_effect = ApiException(status=404, reason='Logs not found')
            watcher = JobWatcher(config=Mock())
            watcher.get_most_recent_pod_for_job = Mock()
            watcher.get_most_recent_pod_for_job.return_value = Mock()
            watcher.lando_client = Mock()

            watcher.on_job_failed('myjob', '31', JobStepTypes.STAGE_DATA)
            payload = watcher.lando_client.job_step_error.call_args[0][0]
            message = watcher.lando_client.job_step_error.call_args[0][1]
            self.assertEqual(payload.job_id, '31')
            self.assertEqual(payload.error_command, JobCommands.STAGE_JOB_ERROR)
            self.assertEqual(message, 'Unable to read logs.')
            mock_logging.error.assert_called_with('Unable to read logs (404)\nReason: Logs not found\n')
