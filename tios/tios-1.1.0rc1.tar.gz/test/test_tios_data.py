import unittest
from tios import communication
import warnings
import sys

class TestTiosDataMethods(unittest.TestCase):

    def setUp(self):
        try:
            self.te = communication.TiosAgent('abc123', new=True)
        except ValueError:
            self.te = communication.TiosAgent('abc123')
        if sys.version_info[0] > 2:
            warnings.simplefilter("ignore", ResourceWarning)

    def test_initialize_new_tios_entry(self):
        self.assertIsInstance(self.te, communication.TiosAgent)

    def test_set_title(self):
        title = 'New Tios Simulation'
        self.te.title = title
        self.te.sync()
        self.assertEqual(title, self.te.title)

    def test_sync(self):
        self.te.status = "Testing"
        self.assertEqual(self.te.updates, {'status' : 'Testing'})
        self.te.sync()
        self.assertEqual(self.te.updates, {})
