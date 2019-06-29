from unittest import TestCase
from json import load
from mt_scraper import Scraper

class HelloworldTestCase(TestCase):
    def test_Scraper(self):
        filename = 'testout.json'
        scraper = Scraper()
        scraper.run(['-f', filename, ])

        with open(filename) as infile:
            obj_list = load(infile)


        self.assertEqual(
            len(obj_list),
            1
        )
        self.assertEqual(
            obj_list[0]['header'],
            "Example Domain"
        )
        self.assertEqual(
            obj_list[0]['link'],
            "http://www.iana.org/domains/example"
        )
        self.assertEqual(
            obj_list[0]['article'],
            "This domain is established to be used for illustrative examples in "\
            "documents. You may use this\n    domain in examples without prior "\
            "coordination or asking for permission."
        )

        #self.assertEqual(get_message(), 'Hello World!')
