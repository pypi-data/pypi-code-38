import unittest
from datetime import datetime
from ttlab.sample import Sample


class SampleTestCases(unittest.TestCase):
    class SampleDataExample:
        name = 'test_sample'
        owner = 'ttlab'
        identifier = 0
        batch_nr = 1
        description = 'A ttlab test sample'
        fabrication_date = '180627'
        history = [
            {
                'description': 'fabrication',
                'date': fabrication_date
            }
        ]
        metadata = {
            'name': name,
            'owner': owner,
            'identifier': identifier,
            'batch_nr': batch_nr,
            'description': description,
            'history': history,
            'extra': None
        }
        history_event = {
            'description': 'annealing',
            'date': '180628'
        }
        history_with_added_event = [history[0], history_event]

    def test_create_sample(self):
        sample = Sample()
        sample.set_name(self.SampleDataExample.name)
        sample.set_owner(self.SampleDataExample.owner)
        sample.set_identifier(self.SampleDataExample.identifier)
        sample.set_batch_nr(self.SampleDataExample.batch_nr)
        sample.set_description(self.SampleDataExample.description)
        sample.set_fabrication_date(self.SampleDataExample.fabrication_date)

        self.assertEqual(sample.get_name(), self.SampleDataExample.name)
        self.assertEqual(sample.get_batch_nr(), self.SampleDataExample.batch_nr)
        self.assertEqual(sample.get_identifier(), self.SampleDataExample.identifier)
        self.assertEqual(sample.get_batch_nr(), self.SampleDataExample.batch_nr)
        self.assertEqual(sample.get_description(), self.SampleDataExample.description)
        self.assertEqual(sample.get_fabrication_date(), self.SampleDataExample.fabrication_date)
        self.assertEqual(sample.get_history(), self.SampleDataExample.history)
        self.assertEqual(sample.get_metadata(), self.SampleDataExample.metadata)

        sample.add_event_to_history(self.SampleDataExample.history_event)
        self.assertEqual(sample.get_history(), self.SampleDataExample.history_with_added_event)
