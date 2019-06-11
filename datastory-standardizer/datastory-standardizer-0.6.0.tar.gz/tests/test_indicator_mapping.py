import unittest
import standardizer as sd


class TestIndicatorMapping(unittest.TestCase):
    def test_id_to_name(self):
        mapping = sd.indicator.id_to_name(source="wb")
        self.assertEqual(mapping["gdp_usd_current"], "GPD (current USD)")

    def test_id_to_name_swedish(self):
        mapping = sd.indicator.id_to_name(source="wb", lang="sv")
        self.assertEqual(mapping["gdp_usd_current"], "BNP (nuvarande USD)")
