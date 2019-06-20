import unittest
import os
from DKPathHelper import DKPathHelper


class DKCommonUnitTestSettings(unittest.TestCase):
    if DKPathHelper.is_windows_os():
        _TEMPFILE_LOCATION = 'c:\\temp'
    else:
        _TEMPFILE_LOCATION = '/var/tmp'

    def assert_response(self, assertions, output):
        total_stages = len(assertions)
        splitted_output = output.split('\n')

        index = 0
        stage = 0
        while stage < total_stages and index < len(splitted_output):
            if assertions[stage] in splitted_output[index]:
                stage += 1
            index += 1
        message = 'Could only reach stage %d of %d %s' % (stage, total_stages, os.linesep)
        expected = ''
        for assertion in assertions:
            expected += '%s%s' % (assertion, os.linesep)
        message += 'Expected Array: %s %s' % (str(assertions), os.linesep)
        message += 'Expected Values: %s %s' % (expected, os.linesep)
        message += 'Actual Values: %s %s' % (str(output), os.linesep)
        self.assertEqual(total_stages, stage, message)


class MockBackendResponse:
    def __init__(self, status_code=200, response_dict=None):
        self.status_code = status_code
        self.text = str(response_dict)
        self.response_dict = response_dict

    def json(self):
        return self.response_dict
