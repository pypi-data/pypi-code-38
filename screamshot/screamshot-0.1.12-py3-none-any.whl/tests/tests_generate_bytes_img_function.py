import unittest
from PIL import Image

import pyppeteer

from screamshot.utils import get_browser_sync, goto_page_sync, to_sync
from screamshot import generate_bytes_img


class GenerateBytesImgFunctionTests(unittest.TestCase):

    def setUp(self):
        self.browser = get_browser_sync()
        self.img_dog = Image.open('tests/server/static/OtherPage/aww_dog.jpg')

    # def test_goto_page_sync_basic(self):
    #     page1 = goto_page_sync(
    #         'http://server:5000/', self.browser)
    #     self.assertIsInstance(page1, pyppeteer.page.Page)

    # def test_goto_page_sync_basic_same_page(self):
    #     page1 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser)
    #     self.assertIsInstance(page1, pyppeteer.page.Page)
    #     page2 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser)
    #     self.assertIsInstance(page2, pyppeteer.page.Page)
    #     self.assertEqual(page1, page2)

    # def test_goto_page_sync_basic_different_page(self):
    #     page1 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser)
    #     self.assertIsInstance(page1, pyppeteer.page.Page)
    #     page2 = goto_page_sync(
    #         'http://server:5000/other.html', self.browser)
    #     self.assertIsInstance(page2, pyppeteer.page.Page)
    #     self.assertNotEqual(page1, page2)

    # def test_goto_page_sync_wait_until_incorrect(self):
    #     page = goto_page_sync(
    #         'http://server:5000/index.html', self.browser, wait_until='The end of the world')
    #     self.assertNotIsInstance(page, pyppeteer.page.Page)

    # def test_goto_page_sync_wait_until_domcontentloaded(self):
    #     page1 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser)
    #     self.assertIsInstance(page1, pyppeteer.page.Page)
    #     page2 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser, wait_until='domcontentloaded')
    #     self.assertIsInstance(page2, pyppeteer.page.Page)
    #     self.assertNotEqual(page1, page2)

    # def test_goto_page_sync_wait_until_networkidle0(self):
    #     page1 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser)
    #     self.assertIsInstance(page1, pyppeteer.page.Page)
    #     page2 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser, wait_until='networkidle0')
    #     self.assertIsInstance(page2, pyppeteer.page.Page)
    #     self.assertNotEqual(page1, page2)

    # def test_goto_page_sync_wait_until_load_and_domcontentloaded(self):
    #     page1 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser)
    #     self.assertIsInstance(page1, pyppeteer.page.Page)
    #     page2 = goto_page_sync(
    #         'http://server:5000/index.html', self.browser, wait_until=['load', 'domcontentloaded'])
    #     self.assertIsInstance(page2, pyppeteer.page.Page)
    #     self.assertNotEqual(page1, page2)

    # def test_goto_page_sync_wait_for(self):
    #     page = goto_page_sync(
    #         'http://server:5000/other.html', self.browser, wait_for='#godot')
    #     self.assertIsInstance(page, pyppeteer.page.Page)

    def test_screamshot(self):
        to_sync(generate_bytes_img(
            url='http://server:5000/other.html', selector='#godot', path='img.jpg'))
        img = Image.open('img.jpg')
        self.assertEqual(img, self.img_dog)
        self.assertTrue(False, str(type(img)))

    def tearDown(self):
        pass


if __name__ == '__main__':
    dog_img = Image.open('tests/server/static/OtherPage/aww_dog.jpg')
    unittest.main()
