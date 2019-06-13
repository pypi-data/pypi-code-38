# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import os
import time
from six.moves import queue
from unittest import TestCase

from mock import Mock, patch, call
from fixture import TempIO

from rattail.config import make_config, RattailConfig
from rattail.filemon import actions
from rattail.filemon.config import Profile, ProfileAction


class TestAction(TestCase):

    def test_callable_must_be_implemented_in_subclass(self):
        config = make_config([])
        action = actions.Action(config)
        self.assertRaises(NotImplementedError, action)


@patch(u'rattail.filemon.actions.noop')
class TestPerformActions(TestCase):

    def setUp(self):
        self.tmp = TempIO()
        self.config = make_config([])
        self.config.set(u'rattail.filemon', u'monitor', u'foo')
        self.config.set(u'rattail.filemon', u'foo.dirs', self.tmp)
        self.config.set(u'rattail.filemon', u'foo.actions', u'noop')
        self.config.set(u'rattail.filemon', u'foo.action.noop.func', u'rattail.filemon.actions:noop')
        # Must delay creating the profile since doing it here would bypass our mock of noop.

    def get_profile(self, stop_on_error=False):
        profile = Profile(self.config, u'foo')
        profile.stop_on_error = stop_on_error
        profile.queue = Mock()
        profile.queue.get_nowait.side_effect = [
            queue.Empty, # for coverage sake; will be effectively skipped
            self.tmp.putfile(u'file1', u''),
            self.tmp.putfile(u'file2', u''),
            self.tmp.putfile(u'file3', u''),
            actions.StopProcessing,
            ]
        return profile

    def test_action_is_invoked_for_each_file_in_queue(self, noop):
        profile = self.get_profile()
        actions.perform_actions(profile)
        self.assertEqual(noop.call_count, 3)
        noop.assert_has_calls([
                call(self.tmp.join(u'file1')),
                call(self.tmp.join(u'file2')),
                call(self.tmp.join(u'file3')),
                ])

    def test_action_is_skipped_for_nonexistent_file(self, noop):
        profile = self.get_profile()
        os.remove(self.tmp.join(u'file2'))
        actions.perform_actions(profile)
        self.assertEqual(noop.call_count, 2)
        # no call for file2
        noop.assert_has_calls([
                call(self.tmp.join(u'file1')),
                call(self.tmp.join(u'file3')),
                ])

    def test_action_which_raises_error_causes_subsequent_actions_to_be_skipped_for_same_file(self, noop):
        self.config.set(u'rattail.filemon', u'foo.actions', u'noop, delete')
        self.config.set(u'rattail.filemon', u'foo.action.delete.func', u'os:remove')
        profile = self.get_profile()
        # processing second file fails, so it shouldn't be deleted
        noop.side_effect = [None, RuntimeError, None]
        actions.perform_actions(profile)
        self.assertFalse(os.path.exists(self.tmp.join(u'file1')))
        self.assertTrue(os.path.exists(self.tmp.join(u'file2')))
        self.assertFalse(os.path.exists(self.tmp.join(u'file3')))

    def test_action_which_raises_error_causes_all_processing_to_stop_if_so_configured(self, noop):
        self.config.set(u'rattail.filemon', u'foo.actions', u'noop, delete')
        self.config.set(u'rattail.filemon', u'foo.action.delete.func', u'os:remove')
        profile = self.get_profile(stop_on_error=True)
        # processing second file fails; third file shouldn't be processed at all
        noop.side_effect = [None, RuntimeError, None]
        actions.perform_actions(profile)
        self.assertEqual(noop.call_count, 2)
        noop.assert_has_calls([
                call(self.tmp.join(u'file1')),
                call(self.tmp.join(u'file2')),
                ])
        self.assertFalse(os.path.exists(self.tmp.join(u'file1')))
        self.assertTrue(os.path.exists(self.tmp.join(u'file2')))
        self.assertTrue(os.path.exists(self.tmp.join(u'file3')))


class TestInvokeAction(TestCase):

    def setUp(self):
        self.action = ProfileAction()
        self.action.config = RattailConfig()
        self.action.action = Mock(return_value=None)
        self.action.retry_attempts = 6
        self.tmp = TempIO()
        self.file = self.tmp.putfile(u'file', u'')

    def test_action_which_succeeds_is_only_called_once(self):
        actions.invoke_action(self.action, self.file)
        self.assertEqual(self.action.action.call_count, 1)

    def test_action_with_no_delay_does_not_pause_between_attempts(self):
        self.action.retry_attempts = 3
        self.action.action.side_effect = [RuntimeError, RuntimeError, None]
        start = time.time()
        actions.invoke_action(self.action, self.file)
        self.assertEqual(self.action.action.call_count, 3)
        self.assertTrue(time.time() - start < 1.0)

    def test_action_with_delay_pauses_between_attempts(self):
        self.action.retry_attempts = 3
        self.action.retry_delay = 1
        self.action.action.side_effect = [RuntimeError, RuntimeError, None]
        start = time.time()
        actions.invoke_action(self.action, self.file)
        self.assertEqual(self.action.action.call_count, 3)
        self.assertTrue(time.time() - start >= 2.0)

    def test_action_which_fails_is_only_attempted_the_specified_number_of_times(self):
        self.action.action.side_effect = RuntimeError
        # Last attempt will not handle the exception; assert that as well.
        with patch('rattail.filemon.actions.send_email') as send_email:
            self.assertRaises(RuntimeError, actions.invoke_action, self.action, self.file)
        self.assertEqual(self.action.action.call_count, 6)

    def test_action_which_fails_then_succeeds_stops_retrying(self):
        # First 2 attempts fail, third succeeds.
        self.action.action.side_effect = [RuntimeError, RuntimeError, None]
        actions.invoke_action(self.action, self.file)
        self.assertEqual(self.action.action.call_count, 3)

    def test_action_which_fails_with_different_errors_stops_retrying(self):
        self.action.action.side_effect = [ValueError, TypeError, None]
        # Second attempt will not handle the exception; assert that as well.
        self.assertRaises(TypeError, actions.invoke_action, self.action, self.file)
        self.assertEqual(self.action.action.call_count, 2)


class TestRaiseException(TestCase):

    def test_exception_is_raised(self):
        # this hardly deserves a test, but what the hell
        self.assertRaises(Exception, actions.raise_exception, '/dev/null')
