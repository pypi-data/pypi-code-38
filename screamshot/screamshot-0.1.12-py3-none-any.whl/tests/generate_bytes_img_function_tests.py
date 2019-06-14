# import os
import unittest
# import asyncio

import pyppeteer

from screamshot.utils import get_browser_sync, goto_page_sync
# from screamshot import generate_bytes_img, generate_bytes_img_prom


class GenerateBytesImgFunctionTests(unittest.TestCase):

    def setUp(self):
        self.browser = get_browser_sync(
            is_headless=False, write_websocket=True)
        # self.browser = asyncio.get_event_loop().run_until_complete(
        #     launch(options={'headless': True, 'onClose': False}))
        # os.environ['WS_ENDPOINT_SCREAMSHOT'] = self.browser.wsEndpoint

    def test_goto_page_sync_basic(self):
        page = goto_page_sync(
            'http://0.0.0.0:8000/website_test/', self.browser)
        self.assertIsInstance(page, pyppeteer.page.Page)

    def test_goto_page_sync_basic_same_page(self):
        page1 = goto_page_sync(
            'http://0.0.0.0:8000/website_test/', self.browser)
        self.assertIsInstance(page1, pyppeteer.page.Page)

        page2 = goto_page_sync(
            'http://0.0.0.0:8000/website_test/', self.browser)
        self.assertIsInstance(page2, pyppeteer.page.Page)

        self.assertEqual(page1, page2)

    def test_goto_page_sync_basic_different_page(self):
        page1 = goto_page_sync(
            'http://0.0.0.0:8000/website_test/', self.browser)
        self.assertIsInstance(page1, pyppeteer.page.Page)

        page2 = goto_page_sync(
            'http://0.0.0.0:8000/website_test/other.html', self.browser)
        self.assertIsInstance(page2, pyppeteer.page.Page)

        self.assertNotEqual(page1, page2)

    def test_goto_page_sync_wait_until_incorrect(self):
        page = goto_page_sync(
            'http://0.0.0.0:8000/website_test/', self.browser, wait_until='Godot')
        self.assertNotIsInstance(page, pyppeteer.page.Page)

    def test_goto_page_sync_wait_until_domcontentloaded(self):
        page1 = goto_page_sync(
            'http://0.0.0.0:8000/website_test/', self.browser)
        self.assertIsInstance(page1, pyppeteer.page.Page)

        page2 = goto_page_sync(
            'http://0.0.0.0:8000/website_test/', self.browser, wait_until='domcontentloaded')
        self.assertIsInstance(page2, pyppeteer.page.Page)

        self.assertNotEqual(page1, page2)

    # def test_function_without_promise_without_optional_parameters(self):
    #     img = asyncio.get_event_loop().run_until_complete(
    #         generate_bytes_img('http://0.0.0.0:8000/website_test/')
    #     )
    #     self.assertTrue(img and isinstance(img, bytes))

    # def test_function_with_promise_without_optional_parameters(self):
    #     loop = asyncio.get_event_loop()
    #     future = asyncio.Future()
    #     asyncio.ensure_future(
    #         generate_bytes_img_prom('http://0.0.0.0:8000/website_test/', future))
    #     loop.run_until_complete(future)
    #     img = future.result()
    #     self.assertTrue(img and isinstance(img, bytes))

    def tearDown(self):
        pass
        # to_sync(self.browser.close())


if __name__ == '__main__':
    unittest.main()
