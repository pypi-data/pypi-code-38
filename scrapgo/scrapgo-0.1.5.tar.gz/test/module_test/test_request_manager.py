from scrapgo.modules import RequestsManager


test_url1 = 'https://comic.naver.com/webtoon/list.nhn?titleId=703846&weekday=tue'
test_url2 = 'https://image-comic.pstatic.net/webtoon/703846/48/20190225210901_bb6b8e3cf2b04f797165a7ba7eefb171_IMAG01_1.jpg'

test = RequestsManager()

r = test._get(test_url1)
test._get(test_url2)
print(r.content[:100])
