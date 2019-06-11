import unittest
import standardizer as sd


class TestCountryMapping(unittest.TestCase):
    def test_name_to_id(self):
        mapping = sd.entity.country.name_to_id()
        self.assertEqual(mapping["Sweden"], "swe")

    def test_id_to_name(self):
        mapping = sd.entity.country.id_to_name()
        self.assertEqual(mapping["swe"], "Sweden")

    def test_id_to_name_swedish(self):
        mapping = sd.entity.country.id_to_name(lang="sv")
        self.assertEqual(mapping["swe"], "Sverige")
