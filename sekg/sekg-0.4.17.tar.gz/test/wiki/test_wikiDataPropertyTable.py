from unittest import TestCase

from sekg.wiki.wiki_util import WikiDataPropertyTable


class TestWikiDataPropertyTable(TestCase):
    def test_property_id_2_name(self):
        table = WikiDataPropertyTable()
        self.assertEqual("subclass of", table.property_id_2_name("P279"))
        self.assertEqual(None, table.property_id_2_name("xxx"))

    def test_property_name_2_id(self):
        table = WikiDataPropertyTable()
        self.assertEqual("P279", table.property_name_2_id("subclass of"))
        self.assertEqual(None, table.property_name_2_id("xxx"))
