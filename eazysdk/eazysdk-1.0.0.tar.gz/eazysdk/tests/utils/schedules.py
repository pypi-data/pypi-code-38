from ... import main
import unittest
from ...settings import Settings as s
from pathlib import Path
from datetime import datetime
from os import remove

base_path = Path(__file__).parent
sandbox_schedules = (base_path / '../../includes/sandbox.csv').resolve()
ecm3_schedules = (base_path / '../../includes/ecm3.csv').resolve()


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().get

    def test_get_schedules_sandbox_write_to_sandbox_csv(self):
        s.current_environment['env'] = 'sandbox'
        s.other['force_schedule_updates'] = True
        self.eazy.schedules()
        with open(sandbox_schedules, 'r') as f:
            x = f.readline()
        self.assertIn(str(datetime.now().date()), str(x))

    def test_get_schedules_ecm3_write_to_ecm3_csv(self):
        s.current_environment['env'] = 'ecm3'
        s.other['force_schedule_updates'] = False
        self.eazy.schedules()
        with open(ecm3_schedules, 'r') as f:
            x = f.readline()
        self.assertIn(str(datetime.now().date()), str(x))

    def test_get_schedules_sandbox_create_file_if_none_exists(self):
        remove(sandbox_schedules)
        s.current_environment['env'] = 'sandbox'
        s.other['force_schedule_updates'] = True
        self.eazy.schedules()
        with open(sandbox_schedules, 'r') as f:
            x = f.readline()
        self.assertIn(str(datetime.now().date()), str(x))

    def test_get_schedules_ecm3_create_file_if_none_exists(self):
        remove(ecm3_schedules)
        s.current_environment['env'] = 'ecm3'
        s.other['force_schedule_updates'] = True
        self.eazy.schedules()
        with open(sandbox_schedules, 'r') as f:
            x = f.readline()
        self.assertIn(str(datetime.now().date()), str(x))
