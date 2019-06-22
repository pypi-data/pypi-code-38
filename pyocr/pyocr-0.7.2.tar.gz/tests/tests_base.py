import os
import unittest


class BaseTest(unittest.TestCase):
    tool = None

    def _get_file_handle(self, filename):
        return open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "data", filename),
                    encoding="utf-8")

    def _get_file_content(self, filename):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", filename), encoding="utf-8") as fh:
            content = fh.read()
        return content
