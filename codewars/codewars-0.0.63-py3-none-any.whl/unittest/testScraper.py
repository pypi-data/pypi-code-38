from codewars.scraper import Scraper
from codewars.surf import Surfer
from asyncio import get_event_loop
import unittest

class TestScraper(unittest.TestCase):

    def setUp(self):
        """Executes before EACH test"""
        self.scraper = Scraper()
        self.surf = Surfer(get_event_loop())

    def tearDown(self):
        """Executes after EACH test"""
        del self.scraper
        del self.surf

    def test_ScrapeHREF(self):
        data = self.scraper.hrefs(
            data=self.surf.get(url='https://codewars.nl/static/docs/index.html')[1].decode()
            )

        self.assertEqual(
            type(data),
            list,
            "The webpage does not return a 200 response code"
        )
        self.assertEqual(
            len(data),
            3,
            "The webpage did not returned bytes"
        )