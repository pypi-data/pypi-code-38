from ftw.copymovepatches.tests import test_move_updates_modified_date
from DateTime import DateTime


class TestMoveUpdatesDateDate(test_move_updates_modified_date.TestMoveUpdatesModifiedDate):

    date_name = 'Date'

    def assert_date_metadata(self, expected_date, metadata_date):
        zone = DateTime().timezone()
        self.assertEqual(expected_date, DateTime(metadata_date).toZone(zone))
