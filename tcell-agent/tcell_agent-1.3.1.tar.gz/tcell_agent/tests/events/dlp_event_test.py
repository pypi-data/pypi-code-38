import unittest

from tcell_agent.events.dlp import DlpEvent


class DlpEventTest(unittest.TestCase):
    def test_dlp_event_create_framework(self):
        dlpe = DlpEvent("routeid", "/rawuri?y=z&d=f", DlpEvent.FOUND_IN_LOG).for_framework(
            DlpEvent.FRAMEWORK_VARIABLE_SESSION_ID)
        self.assertEqual(dlpe["event_type"], "dlp")
        self.assertEqual(dlpe["type"], "framework")
        self.assertEqual(dlpe["variable"], DlpEvent.FRAMEWORK_VARIABLE_SESSION_ID)

    def test_dlp_event_create_request(self):
        dlpe = DlpEvent("routeid", "/rawuri?y=z&d=f", DlpEvent.FOUND_IN_LOG).for_request(DlpEvent.REQUEST_CONTEXT_FORM,
                                                                                         "passwd")
        self.assertEqual(dlpe["event_type"], "dlp")
        self.assertEqual(dlpe["type"], "request")
        self.assertEqual(dlpe["context"], "form")
        self.assertEqual(dlpe["variable"], "passwd")
