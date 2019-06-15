import unittest
from alex import NaverNews

class NaverNewsTestCase(unittest.TestCase):
    def test_empty_news(self):
        crawler = NaverNews(url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001') 
        news_list = crawler.crawl()

        self.assertEqual(len(news_list), 0)
    
    def test_single_news(self):
        crawler = NaverNews(url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001') # url 화
        news_list = crawler.crawl()

        first_news = news_list[0]

        self.assertEqual(first_news['title'], "1번째 뉴스")
#         self.assertEqual(first_news['url'], "news1.html")
        # self.assertEqual(first_news['company'], "신문사 이름")
        # self.assertEqual(first_news['written at'], "날짜 작성 일자와 시간(datetime 형식으로)")
        # self.assertEqual(first_news['content'], "뉴스 내용")

    def test_original_news(self):
        crawler = NaverNews(url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001')
        news_list = crawler.crawl()

        first_news = news_list[0]
        self.assertEqual(first_news['title'], "1번째 뉴스")
#         self.assertEqual(first_news['url'], "news1.html")
        # self.assertEqual(first_news['company'], "신문사 이름")
        # self.assertEqual(first_news['written at'], "날짜 작성 일자와 시간(datetime 형식으로)")
        # self.assertEqual(first_news['content'], "뉴스 내용")

        last_news = news_list[19]
        self.assertEqual(last_news['title'], "20번째 뉴스")
#         self.assertEqual(last_news['url'], "news20.html")
        # self.assertEqual(last_news['company'], "신문사 이름")
        # self.assertEqual(last_news['written at'], "날짜 작성 일자와 시간(datetime 형식으로)")
        # self.assertEqual(last_news['content'], "뉴스 내용")


if __name__ == '__main__':
    unittest.main()
unittest.main()
