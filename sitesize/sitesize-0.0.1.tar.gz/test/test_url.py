
import sitesize
import unittest

test_url1 = 'http://www.google.com'
test_url2 = 'www.google.com'

class MyTestCase(unittest.TestCase):

    def test_url_checker(self):
        self.assertEqual(sitesize.url_checker(test_url1), test_url1)
        self.assertEqual(sitesize.url_checker(test_url2), test_url1)


    def test_get_webpage_size(self):
        self.assertIsNotNone(sitesize.get_webpage_size(test_url1))

if __name__ == '__main__':
    unittest.main()