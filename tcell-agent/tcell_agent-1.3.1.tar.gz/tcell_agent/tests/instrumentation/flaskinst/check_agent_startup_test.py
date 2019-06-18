from __future__ import print_function

import unittest

from mock import call, patch

from django import get_version

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.djangoinst.check_agent_startup import \
     ensure_agent_started, start_agent, AGENT_STARTED_LOCK

try:
    from django.conf import settings
    settings.configure()
except RuntimeError:
    print("Django already setup")


class CheckAgentStartupTest(unittest.TestCase):
    def test_agent_has_already_started_ensure_agent_started(self):
        with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.has_agent_started",
                   return_value=True) as patched_has_agent_started:
            with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.update_default_charset") \
                    as patched_update_default_charset:
                with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.start_agent",
                           return_value=False) as patched_start_agent:
                    ensure_agent_started()
                    self.assertTrue(patched_has_agent_started.called)
                    self.assertFalse(patched_update_default_charset.called)
                    self.assertFalse(patched_start_agent.called)

    def test_agent_has_not_started_ensure_agent_started(self):
        with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.has_agent_started",
                   return_value=False) as patched_has_agent_started:
            with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.update_default_charset") \
                    as patched_update_default_charset:
                with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.start_agent",
                           return_value=True) as patched_start_agent:
                    with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                        with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.send_django_setting_events",
                                   return_value=True) as patched_send_django_setting_events:
                            ensure_agent_started()
                            self.assertTrue(patched_has_agent_started.called)
                            self.assertTrue(patched_update_default_charset.called)
                            self.assertTrue(patched_start_agent.called)
                            self.assertTrue(patched_send_django_setting_events.called)
                            self.assertTrue(patched_send.called)

                            patched_send.assert_has_calls(
                                [
                                    call({
                                        "event_type": "server_agent_details",
                                        "app_framework": "Django",
                                        "app_framework_version": get_version()
                                    })
                                ]
                            )

    def test_other_thread_has_started_agent_start_agent(self):
        with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.has_agent_started",
                   return_value=True) as patched_has_agent_started:
            with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.set_agent_has_started",
                       return_value=None) as patched_set_agent_has_started:
                with patch.object(TCellAgent, "startup", return_value=None) as patched_startup:

                    self.assertFalse(
                        start_agent(),
                        "start_agent() should return False when started by a different thread")

                    self.assertTrue(patched_has_agent_started.called)
                    self.assertFalse(patched_set_agent_has_started.called)
                    self.assertFalse(patched_startup.called)
                    try:
                        self.assertTrue(
                            AGENT_STARTED_LOCK.acquire(False),
                            "Lock should have been released")
                    finally:
                        AGENT_STARTED_LOCK.release()

    def test_agent_has_not_started_start_agent(self):
        with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.has_agent_started",
                   return_value=False) as patched_has_agent_started:
            with patch("tcell_agent.instrumentation.djangoinst.check_agent_startup.set_agent_has_started",
                       return_value=None) as patched_set_agent_has_started:
                with patch.object(TCellAgent, "startup", return_value=None) as patched_startup:

                    self.assertTrue(
                        start_agent(),
                        "start_agent() should return True if it triggers agent startup")

                    self.assertTrue(patched_has_agent_started.called)
                    self.assertTrue(patched_set_agent_has_started.called)
                    self.assertTrue(patched_startup.called)
                    try:
                        self.assertTrue(
                            AGENT_STARTED_LOCK.acquire(False),
                            "Lock should have been released")
                    finally:
                        AGENT_STARTED_LOCK.release()
