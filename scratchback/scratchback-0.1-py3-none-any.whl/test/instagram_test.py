import instagram
import unittest

class InstagramTestCase(unittest.TestCase):
    def test_single_account(self):
        
        crawler = instagram.Instagram()
        post_list = crawler.crawl("dsschoolkr")

        
        self.assertEqual(len(post_list), 2)



if __name__ == '__main__':
    unittest.main()