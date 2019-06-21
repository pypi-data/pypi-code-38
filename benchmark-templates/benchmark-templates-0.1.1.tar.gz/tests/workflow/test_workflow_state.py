"""Simple tests to ensure correctness of the workflow state classes."""

import datetime as dt

from unittest import TestCase

from benchtmpl.workflow.state import StateError, StatePending, StateRunning, StateSuccess
from benchtmpl.workflow.resource.base import FileResource


LOCAL_FILE = 'tests/files/schema.json'


class TestWorkflowStates(TestCase):
    """Test instantiating the different workflow state classes."""
    def test_error_state(self):
        """Test creating instances of the error state class."""
        created_at = dt.datetime.now()
        started_at = created_at + dt.timedelta(seconds=10)
        stopped_at = started_at + dt.timedelta(seconds=10)
        state = StateError(
            created_at=created_at,
            started_at=started_at,
            stopped_at=stopped_at
        )
        self.assertTrue(state.is_error())
        self.assertFalse(state.is_pending())
        self.assertFalse(state.is_running())
        self.assertFalse(state.is_success())
        self.assertFalse(state.is_active())
        self.assertEqual(state.created_at, created_at)
        self.assertEqual(state.started_at, started_at)
        self.assertEqual(state.stopped_at, stopped_at)
        self.assertEqual(len(state.messages), 0)
        state = StateError(
            created_at=created_at,
            started_at=started_at,
            stopped_at=stopped_at,
            messages=['A', 'B', 'C']
        )
        self.assertEqual(state.created_at, created_at)
        self.assertEqual(state.started_at, started_at)
        self.assertEqual(state.stopped_at, stopped_at)
        self.assertEqual(len(state.messages), 3)

    def test_pending_state(self):
        """Test creating instances of the pending state class."""
        created_at = dt.datetime.now()
        state = StatePending(created_at)
        self.assertTrue(state.is_pending())
        self.assertTrue(state.is_active())
        self.assertFalse(state.is_error())
        self.assertFalse(state.is_running())
        self.assertFalse(state.is_success())
        self.assertEqual(state.created_at, created_at)
        running = state.start()
        self.assertEqual(state.created_at, running.created_at)
        self.assertIsNotNone(running.started_at)

    def test_running_state(self):
        """Test creating instances of the running state class."""
        created_at = dt.datetime.now()
        started_at = created_at + dt.timedelta(seconds=10)
        state = StateRunning(created_at=created_at, started_at=started_at)
        self.assertTrue(state.is_active())
        self.assertTrue(state.is_running())
        self.assertFalse(state.is_pending())
        self.assertFalse(state.is_error())
        self.assertFalse(state.is_success())
        self.assertEqual(state.created_at, created_at)
        self.assertEqual(state.started_at, started_at)
        # Create an exception to get error state fromrunning state
        error = state.error(messages=['Error', 'State'])
        self.assertEqual(error.created_at, state.created_at)
        self.assertEqual(error.started_at, state.started_at)
        self.assertEqual(len(error.messages), 2)
        self.assertEqual(error.messages[0], 'Error')
        self.assertEqual(error.messages[1], 'State')

    def test_success_state(self):
        """Test creating instances of the success state class."""
        created_at = dt.datetime.now()
        started_at = created_at + dt.timedelta(seconds=10)
        finished_at = started_at + dt.timedelta(seconds=10)
        state = StateSuccess(
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at
        )
        self.assertTrue(state.is_success())
        self.assertFalse(state.is_error())
        self.assertFalse(state.is_pending())
        self.assertFalse(state.is_running())
        self.assertFalse(state.is_active())
        self.assertEqual(state.created_at, created_at)
        self.assertEqual(state.started_at, started_at)
        self.assertEqual(state.finished_at, finished_at)
        self.assertEqual(len(state.resources), 0)
        state = StateSuccess(
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            resources=[FileResource('myfile', LOCAL_FILE)]
        )
        self.assertEqual(state.created_at, created_at)
        self.assertEqual(state.started_at, started_at)
        self.assertEqual(state.finished_at, finished_at)
        self.assertEqual(len(state.resources), 1)


if __name__ == '__main__':
    import unittest
    unittest.main()
