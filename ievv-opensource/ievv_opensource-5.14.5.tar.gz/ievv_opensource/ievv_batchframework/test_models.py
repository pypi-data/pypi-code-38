from django import test
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_cradmin import datetimeutils
from model_mommy import mommy

from ievv_opensource.ievv_batchframework.models import BatchOperation
from ievv_opensource.python2_compatibility import mock


class TestBatchOperationModel(test.TestCase):
    def test_clean_status_finished_result_not_available(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       status=BatchOperation.STATUS_FINISHED,
                                       result=BatchOperation.RESULT_NOT_AVAILABLE)
        with self.assertRaisesMessage(ValidationError,
                                      'Must be "successful" or "failed" when status is "finished".'):
            batchoperation.clean()

    def test_clean_status_running_no_started_running_datetime(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       status=BatchOperation.STATUS_RUNNING,
                                       started_running_datetime=None)
        with self.assertRaisesMessage(ValidationError,
                                      'Can not be None when status is "running" or "finished".'):
            batchoperation.clean()

    def test_clean_status_finished_no_started_running_datetime(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       status=BatchOperation.STATUS_FINISHED,
                                       result=BatchOperation.RESULT_SUCCESSFUL,
                                       started_running_datetime=None)
        with self.assertRaisesMessage(ValidationError,
                                      'Can not be None when status is "running" or "finished".'):
            batchoperation.clean()

    def test_input_data_setter(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation')
        batchoperation.input_data = {'hello': 'world'}
        self.assertEqual(
            '{"hello": "world"}',
            batchoperation.input_data_json)

    def test_input_data_getter_emptystring(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       input_data_json='')
        self.assertEqual(
            None,
            batchoperation.input_data)

    def test_input_data_getter_nonemptystring(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       input_data_json='{"hello": "world"}')
        self.assertEqual(
            {'hello': 'world'},
            batchoperation.input_data)

    def test_output_data_setter(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation')
        batchoperation.output_data = {'hello': 'world'}
        self.assertEqual(
            '{"hello": "world"}',
            batchoperation.output_data_json)

    def test_output_data_getter_emptystring(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       output_data_json='')
        self.assertEqual(
            None,
            batchoperation.output_data)

    def test_output_data_getter_nonemptystring(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       output_data_json='{"hello": "world"}')
        self.assertEqual(
            {'hello': 'world'},
            batchoperation.output_data)

    def test_finish_successful(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       status=BatchOperation.STATUS_RUNNING,
                                       started_running_datetime=timezone.now())
        batchoperation.finish()
        self.assertEqual(BatchOperation.RESULT_SUCCESSFUL, batchoperation.result)

    def test_finish_failed(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       status=BatchOperation.STATUS_RUNNING,
                                       started_running_datetime=timezone.now())
        mocknow = datetimeutils.default_timezone_datetime(2016, 1, 1)
        with mock.patch('ievv_opensource.ievv_batchframework.models.timezone.now', lambda: mocknow):
            batchoperation.finish(failed=True)
        self.assertEqual(BatchOperation.RESULT_FAILED, batchoperation.result)
        self.assertEqual('', batchoperation.output_data_json)
        self.assertEqual(batchoperation.finished_datetime, mocknow)

    def test_finish_with_output_data(self):
        batchoperation = mommy.make('ievv_batchframework.BatchOperation',
                                    status=BatchOperation.STATUS_RUNNING,
                                    started_running_datetime=timezone.now())
        batchoperation.finish(output_data={'hello': 'world'})
        batchoperation = BatchOperation.objects.get(id=batchoperation.id)
        self.assertEqual(
            '{"hello": "world"}',
            batchoperation.output_data_json)

    def test_mark_as_running(self):
        batchoperation = mommy.prepare('ievv_batchframework.BatchOperation',
                                       status=BatchOperation.STATUS_UNPROCESSED,
                                       started_running_datetime=None)
        mocknow = datetimeutils.default_timezone_datetime(2016, 1, 1)
        with mock.patch('ievv_opensource.ievv_batchframework.models.timezone.now', lambda: mocknow):
            batchoperation.mark_as_running()
        self.assertEqual(BatchOperation.STATUS_RUNNING,
                         batchoperation.status)
        self.assertEqual(batchoperation.started_running_datetime, mocknow)


class TestBatchOperationManager(test.TestCase):
    def test_create_synchronous(self):
        batchoperation = BatchOperation.objects.create_synchronous()
        self.assertEqual(BatchOperation.STATUS_RUNNING, batchoperation.status)

    def test_create_synchronous_with_inputdata(self):
        batchoperation = BatchOperation.objects.create_synchronous(
            input_data={'hello': 'world'})
        self.assertEqual(
            '{"hello": "world"}',
            batchoperation.input_data_json)

    def test_create_asynchronous(self):
        batchoperation = BatchOperation.objects.create_asynchronous()
        self.assertEqual(BatchOperation.STATUS_UNPROCESSED, batchoperation.status)

    def test_create_asynchronous_with_inputdata(self):
        batchoperation = BatchOperation.objects.create_asynchronous(
            input_data={'hello': 'world'})
        self.assertEqual(
            '{"hello": "world"}',
            batchoperation.input_data_json)
