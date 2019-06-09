from scrapgo.modules import SoupParserMixin, RequestsManager


test_url1 = 'https://comic.naver.com/webtoon/weekday.nhn'

test_patterns = [
    r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)$',
    r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$'
]

rm = RequestsManager()

requests = rm._get(test_url1)

content = requests.content

test = SoupParserMixin()

soup = test._get_soup(requests)

r = test._collect_link(soup, test_patterns)

for link in r:
    print('collected_link:', link)
    # break
