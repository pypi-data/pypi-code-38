from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)

from src.silver_surfer_models.resources.LongTask import LongTask
from src.silver_surfer_models.resources.LongTask.schemas import (
    LONG_TASK_STATES,
    LONG_TASK_NAMES,
)
from test.backendtestcase import TestCase
from test.mixins.BasicDataMixin import BasicDataMixin
from test.utils import second_equals_first


class LongTaskResourceTestCase(BasicDataMixin, TestCase):
    def setUp(self):
        super(LongTaskResourceTestCase, self).setUp()
        self.inst = LongTask()

        self.long_task1 = self.inst.create({
            'trial_id': self.trial1['id'],
            'name': LONG_TASK_NAMES['PROCESS_PETITION_DOC'],
            'state': LONG_TASK_STATES['NOT_STARTED'],
            'progress': 0,
            'celery_task_id': '99999999-9999-9999-9999-999999999999',
        })
        self.long_task2 = self.inst.create({
            'trial_id': self.trial2['id'],
            'name': LONG_TASK_NAMES['PROCESS_PETITION_DOC'],
            'state': LONG_TASK_STATES['IN_PROGRESS'],
            'progress': 0,
            'celery_task_id': '88888888-8888-8888-8888-888888888888',
        })

    def test_create(self):
        data = {
            'trial_id': self.trial1['id'],
            'name': LONG_TASK_NAMES['PROCESS_PETITION_DOC'],
            'state': LONG_TASK_STATES['NOT_STARTED'],
            'progress': 0,
            'celery_task_id': '11111111-1111-1111-1111-111111111111'
        }
        resp = self.inst.create(data)
        second_equals_first(
            {
                'trial_id': self.trial1['id'],
                'name': data['name'],
                'state': data['state'],
                'progress': data['progress'],
                'celery_task_id': data['celery_task_id'],
            },
            resp,
        )

    def test_create_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    def test_read_w_params(self):
        resp = self.inst.read({
            'trial_id': self.trial1['id'],
        })
        self.assertEqual(len(resp), 1)
        second_equals_first(
            self.long_task1,
            resp[0],
        )

        resp = self.inst.read({
            'state': LONG_TASK_STATES['IN_PROGRESS'],
        })
        self.assertEqual(len(resp), 1)
        second_equals_first(
            self.long_task2,
            resp[0],
        )

        resp = self.inst.read({
            'celery_task_id': self.long_task2['celery_task_id'],
        })
        self.assertEqual(len(resp), 1)
        second_equals_first(
            self.long_task2,
            resp[0],
        )

    def test_one(self):
        resp = self.inst.one({
            'trial_id': self.trial1['id'],
        })
        second_equals_first(
            self.long_task1,
            resp,
        )

    def test_one_raises_NoResultFound(self):
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': 999},
        )

    def test_one_raises_MultipleResultsFound(self):
        self.assertRaises(
            MultipleResultsFound,
            self.inst.one,
            {'name': LONG_TASK_NAMES['PROCESS_PETITION_DOC']},
        )

    def test_update(self):
        new_data = {
            'trial_id': self.trial1['id'],
            'name': LONG_TASK_NAMES['PROCESS_PETITION_DOC'],
            'state': LONG_TASK_STATES['IN_PROGRESS'],
            'progress': 0.50,
            'celery_task_id': 'some new',
            'result': 'something'
        }
        resp = self.inst.update(
            id=self.long_task1['id'],
            params=new_data,
        )
        second_equals_first(
            {
                'id': self.long_task1['id'],
                'trial_id': self.long_task1['trial_id'],
                'name': self.long_task1['name'],
                'state': new_data['state'],
                'progress': new_data['progress'],
                'celery_task_id': self.long_task1['celery_task_id'],
                'result': new_data['result'],
            },
            resp,
        )

    def test_delete(self):
        response = self.inst.read({'id': self.long_task1['id']})
        self.assertEqual(len(response), 1)
        response = self.inst.delete(id=self.long_task1['id'])
        self.assertEqual(response, 'Successfully deleted')
        response = self.inst.read({'id': self.long_task1['id']})
        self.assertEqual(len(response), 0)
