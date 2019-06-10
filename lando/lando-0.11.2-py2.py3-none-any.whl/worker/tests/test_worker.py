from unittest import TestCase
from unittest.mock import Mock, patch, ANY, call
from lando.worker.worker import LandoWorker, LandoWorkerActions, JobStep, Names
from lando.common.names import WorkflowTypes


class LandoWorkerActionsTestCase(TestCase):
    def setUp(self):
        self.config = Mock()
        self.client = Mock()
        self.paths = Mock()
        self.names = Mock()
        self.payload = Mock()
        self.payload.input_files.dds_files = []
        self.payload.credentials.dds_user_credentials = {'123': 'credentials'}
        self.payload.job_details.output_project.dds_user_credentials = "123"

    @patch('lando.worker.worker.os')
    @patch('lando.worker.worker.StageDataCommand')
    def test_stage_files_no_files(self, mock_stage_data_command, mock_os):
        self.payload = Mock(input_files=Mock(dds_files=[]))
        actions = LandoWorkerActions(self.config, self.client)
        with self.assertRaises(ValueError) as raised_exception:
            actions.stage_files(self.paths, self.names, self.payload)
        self.assertEqual(str(raised_exception.exception), 'ERROR: No user_id found in input files.')

    @patch('lando.worker.worker.os')
    @patch('lando.worker.worker.StageDataCommand')
    def test_stage_files_with_files(self, mock_stage_data_command, mock_os):
        self.mock_file = Mock(user_id="123")
        self.payload.input_files.dds_files = [self.mock_file]
        actions = LandoWorkerActions(self.config, self.client)
        actions.stage_files(self.paths, self.names, self.payload)
        mock_stage_data_command.assert_called_with(self.payload.job_details.workflow, self.names, self.paths)
        mock_stage_data_command.return_value.run.assert_called_with(
            self.config.commands.stage_data_command,
            'credentials',
            self.payload.input_files
        )
        self.client.job_step_complete.assert_called_with(self.payload)

    @patch('lando.worker.worker.os')
    @patch('lando.worker.worker.StageDataCommand')
    def test_stage_files_multiple_users_files(self, mock_stage_data_command, mock_os):
        self.payload.input_files.dds_files = [Mock(user_id="1"), Mock(user_id="123")]
        actions = LandoWorkerActions(self.config, self.client)
        with self.assertRaises(ValueError) as raised_exception:
            actions.stage_files(self.paths, self.names, self.payload)
        self.assertEqual(str(raised_exception.exception), 'ERROR: Found multiple user ids 1,123.')

    @patch('lando.worker.worker.os')
    @patch('lando.worker.worker.RunWorkflowCommand')
    def test_run_workflow(self, mock_run_workflow_command, mock_os):
        actions = LandoWorkerActions(self.config, self.client)
        actions.run_workflow(self.paths, self.names, self.payload)
        mock_run_workflow_command.assert_called_with(self.payload.job_details, self.names, self.paths)
        mock_run_workflow_command.return_value.run.assert_called_with(
            self.config.cwl_base_command,
            self.config.cwl_post_process_command,
        )
        self.client.job_step_complete.assert_called_with(self.payload)

    @patch('lando.worker.worker.os')
    @patch('lando.worker.worker.OrganizeOutputCommand')
    def test_organize_output(self, mock_organize_output_command, mock_os):
        actions = LandoWorkerActions(self.config, self.client)
        actions.organize_output(self.paths, self.names, self.payload)
        mock_organize_output_command.assert_called_with(self.payload.job_details, self.names, self.paths)
        mock_organize_output_command.return_value.run.assert_called_with(
            self.config.commands.organize_output_command,
            self.payload.job_details.workflow.methods_document
        )
        self.client.job_step_complete.assert_called_with(self.payload)

    @patch('lando.worker.worker.os')
    @patch('lando.worker.worker.SaveOutputCommand')
    @patch('lando.worker.worker.ProjectDetails')
    def test_save_output(self, mock_project_details, mock_save_output_command, mock_os):
        actions = LandoWorkerActions(self.config, self.client)
        actions.save_output(self.paths, self.names, self.payload)
        mock_save_output_command.assert_called_with(
            self.names, self.paths, self.names.activity_name, self.names.activity_description
        )
        mock_save_output_command.return_value.run.assert_called_with(
            self.config.commands.save_output_command,
            'credentials',
            self.payload.job_details.share_dds_ids,
            started_on="", ended_on=""
        )
        self.client.job_step_store_output_complete.assert_called_with(self.payload, mock_project_details.return_value)


@patch('lando.worker.worker.os')
@patch('lando.worker.worker.LandoClient')
@patch('lando.worker.worker.LandoWorkerActions')
@patch('lando.worker.worker.JobStep')
class LandoWorkerTestCase(TestCase):
    def setUp(self):
        self.config = Mock()
        self.outgoing_queue_name = 'somequeue'
        self.payload = Mock(job_id=1)

    def test_stage_job(self, mock_job_step, mock_lando_worker_actions, mock_lando_client, mock_os):
        LandoWorker(self.config, self.outgoing_queue_name).stage_job(self.payload)

        mock_job_step.assert_called_with(mock_lando_client.return_value, self.payload,
                                         mock_lando_worker_actions.return_value.stage_files)
        mock_job_step.return_value.run.assert_called_with('data_for_job_1')

    def test_run_job(self, mock_job_step, mock_lando_worker_actions, mock_lando_client, mock_os):
        LandoWorker(self.config, self.outgoing_queue_name).run_job(self.payload)

        mock_job_step.assert_called_with(mock_lando_client.return_value, self.payload,
                                         mock_lando_worker_actions.return_value.run_workflow)
        mock_job_step.return_value.run.assert_called_with('data_for_job_1')

    def test_store_job_output(self, mock_job_step, mock_lando_worker_actions, mock_lando_client, mock_os):
        LandoWorker(self.config, self.outgoing_queue_name).organize_output(self.payload)

        mock_job_step.assert_called_with(mock_lando_client.return_value, self.payload,
                                         mock_lando_worker_actions.return_value.organize_output)
        mock_job_step.return_value.run.assert_called_with('data_for_job_1')

    def test_store_job_output(self, mock_job_step, mock_lando_worker_actions, mock_lando_client, mock_os):
        LandoWorker(self.config, self.outgoing_queue_name).store_job_output(self.payload)

        mock_job_step.assert_called_with(mock_lando_client.return_value, self.payload,
                                         mock_lando_worker_actions.return_value.save_output)
        mock_job_step.return_value.run.assert_called_with('data_for_job_1')


class JobStepTestCase(TestCase):
    def setUp(self):
        self.client = Mock()
        self.payload = Mock(job_id=1, job_description='myjob')

    @patch('lando.worker.worker.Paths')
    @patch('lando.worker.worker.Names')
    @patch('lando.worker.worker.logging')
    def test_run(self, mock_logging, mock_names, mock_paths):
        self.func_params = ()

        def myfunc(paths, names, payload):
            self.func_params = (paths, names, payload)

        job_step = JobStep(self.client, self.payload, myfunc)
        job_step.run(working_directory='/work')

        self.assertEqual(mock_paths.return_value, self.func_params[0])
        mock_paths.assert_called_with(base_directory='/work/')
        self.assertEqual(mock_names.return_value, self.func_params[1])
        self.assertEqual(self.payload, self.func_params[2])
        mock_logging.info.assert_has_calls([
            call('myjob started for job 1'),
            call('myjob complete for job 1.')
        ])
        self.client.job_step_error.assert_not_called()

    @patch('lando.worker.worker.Paths')
    @patch('lando.worker.worker.Names')
    @patch('lando.worker.worker.logging')
    def test_run_raises(self, mock_logging, mock_names, mock_paths):
        def myfunc(paths, names, payload):
            raise ValueError("Nope")

        job_step = JobStep(self.client, self.payload, myfunc)
        job_step.run(working_directory='/work')

        log_message = mock_logging.info.call_args[0][0]
        self.assertTrue('Job failed' in log_message)
        self.client.job_step_error.assert_called_with(self.payload, ANY)


class NamesTestCase(TestCase):
    @patch('lando.common.names.dateutil')
    def test_packed_workflow(self, mock_dateutil):
        mock_dateutil.parser.parse.return_value.strftime.return_value = 'somedate'
        paths, job = Mock(), Mock()
        paths.JOB_DATA = '/job-data'
        paths.OUTPUT_DATA = '/output-data'
        paths.CONFIG_DIR = '/config'
        paths.WORKFLOW = '/workflowdir'
        job.id = 49
        job.name = 'myjob'
        job.username = 'joe'
        job.workflow.name = 'myworkflow'
        job.workflow.version = 2
        job.workflow.workflow_url = 'someurl'
        job.workflow.workflow_type = WorkflowTypes.PACKED
        job.workflow.workflow_path = 'workflow.cwl'
        names = Names(job, paths)

        self.assertEqual(names.job_order_path, '/job-data/job-order.json')
        self.assertEqual(names.run_workflow_stdout_path, '/output-data/bespin-workflow-output.json')
        self.assertEqual(names.run_workflow_stderr_path, '/output-data/bespin-workflow-output.log')
        self.assertEqual(names.output_project_name, 'Bespin myworkflow v2 myjob somedate')
        self.assertEqual(names.workflow_input_files_metadata_path, '/job-data/workflow-input-files-metadata.json')
        self.assertEqual(names.usage_report_path, '/output-data/job-49-joe-resource-usage.json')
        self.assertEqual(names.activity_name, 'myjob - Bespin Job 49')
        self.assertEqual(names.activity_description, 'Bespin Job 49 - Workflow myworkflow v2')

        self.assertEqual(names.stage_data_command_filename, '/config/stage_data.json')
        self.assertEqual(names.organize_output_command_filename, '/config/organize_output.json')
        self.assertEqual(names.save_output_command_filename, '/config/save_output.json')
        self.assertEqual(names.output_project_details_filename, '/config/output_project_details.json')
        self.assertEqual(names.dds_config_filename, '/config/ddsclient.conf')

        self.assertEqual(names.workflow_download_dest, '/workflowdir/someurl')
        self.assertEqual(names.workflow_to_run, '/workflowdir/someurlworkflow.cwl')
        self.assertEqual(names.workflow_to_read, '/workflowdir/someurl')
        self.assertEqual(names.unzip_workflow_url_to_path, None)

    @patch('lando.common.names.dateutil')
    def test_zipped_workflow(self, mock_dateutil):
        mock_dateutil.parser.parse.return_value.strftime.return_value = 'somedate'
        paths, job = Mock(), Mock()
        paths.JOB_DATA = '/job-data'
        paths.OUTPUT_DATA = '/output-data'
        paths.CONFIG_DIR = '/config'
        paths.WORKFLOW = '/workflowdir'
        job.id = 49
        job.name = 'myjob'
        job.username = 'joe'
        job.workflow.name = 'myworkflow'
        job.workflow.version = 2
        job.workflow.workflow_url = 'someurl'
        job.workflow.workflow_type = WorkflowTypes.ZIPPED
        job.workflow.workflow_path = 'workflow.cwl'
        names = Names(job, paths)

        self.assertEqual(names.workflow_download_dest, '/workflowdir/someurl')
        self.assertEqual(names.workflow_to_run, '/workflowdir/workflow.cwl')
        self.assertEqual(names.workflow_to_read, '/workflowdir/workflow.cwl')
        self.assertEqual(names.unzip_workflow_url_to_path, '/workflowdir')
