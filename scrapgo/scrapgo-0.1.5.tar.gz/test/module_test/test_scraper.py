from scrapgo.scraper import LinkRelayScraper

import re

REGX_TOON_HREF = re.compile(
    r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)&page=(?P<page>\d+)$')


class NaverWebToonScraper(LinkRelayScraper):
    ROOT_URL = 'https://comic.naver.com/webtoon/weekday.nhn'

    def main_filter(self, link, match, query, context):
        p = match('page')
        return int(p) < 10


nw = NaverWebToonScraper()
r'https://comic.naver.com/webtoon/list.nhn?titleId=642653&weekday=tue&page={page}'
res = nw.get(
    'https://comic.naver.com/webtoon/list.nhn?titleId=626907&weekday=wed&page=1')
responses = nw._crawl_link_pattern(res, REGX_TOON_HREF, recursive=True)
# for r in responses:
# print(r.url)
list(responses)
