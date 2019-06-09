import os
import re
import json
import math
from io import BytesIO
from collections import namedtuple, OrderedDict
import pandas as pd

from scrapgo import LinkRelayScraper, url, urlpattern, root
from scrapgo.utils import mkdir_p, cp, parse_query, queryjoin, parse_root, parse_jsonp


COMMENT_PAGE_SIZE = 100


class NaverWebToonScraper(LinkRelayScraper):
    ROOT_URL = 'https://comic.naver.com/webtoon/weekday.nhn'
    REQUEST_DELAY = 0
    LINK_RELAY = [
        urlpattern(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w+)$',
            parser='toon_parser',
            name='toon',
        ),
        urlpattern(  # 이미지, 파일등 과같은 source 항목을 다운로드 필터링등 처리할 수 있다
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$',
            parser='toon_thumb_parser',
            referer='toon',
            # refresh=True,
            name='toon_thumb',
        ),
        url(
            'https://comic.naver.com/webtoon/list.nhn?titleId={titleId}&weekday=tue&page={page}',
            generator='toon_page_urlrenderer',
            name='toon_page',
        ),
        urlpattern(
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser='episode_thumb_parser',
            name='episode_thumb',
            referer='toon_page',
        ),
        urlpattern(
            r'^/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w*)$',
            parser='episode_parser',
            name='episode'
        ),
        urlpattern(
            r'^https://image-comic.pstatic.net/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser='episode_cut_parser',
            referer='episode',
            name='episode_cut',
        ),
        url(
            'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json',
            generator='comment_urlrenderer',
            breaker='comment_page_breaker',
            parser='comment_parser',
            referer='episode',
            refresh=True,
        )
    ]

    def main_filter(self, link, query, match, context):
        if not match:
            return True
        titleId = context['titleId']
        return titleId and titleId == match('titleId')

    def toon_parser(self, response, context):
        match = response.scrap.match
        soup = response.scrap.soup

        def get_title(soup):
            titlebar = soup.title.text.split('::')
            title = titlebar[0].strip()
            return title

        def get_author(soup):
            author = soup.select_one('div.detail .wrt_nm')
            text = self.prettify_textarea(author)
            return text

        def get_description(soup):
            description = soup.select_one('div.detail > p')
            text = self.prettify_textarea(description)
            return text

        toon = dict(
            titleId=match('titleId'),
            title=get_title(soup),
            author=get_author(soup),
            description=get_description(soup)
        )
        return toon

    def toon_thumb_parser(self, response, context):
        toon_thumb = dict(
            titleId=response.scrap.match('titleId'),
            toon_thumb_src=response.url,
            # toon_thumb_content=response.content
        )
        return toon_thumb

    def toon_page_urlrenderer(self, parent_response, template, context):
        soup = parent_response.scrap.soup
        match = parent_response.scrap.match

        def get_page_range(soup):
            action = self.get_action('episode')
            pattern = action.regex
            no_set = set()
            for a in soup('a', href=pattern):
                href = a['href']
                match = pattern.match(href)
                no = int(match.group('no'))
                no_set.add(no)
            page_count = max(no_set) // len(no_set) + 1
            page_range = range(1, page_count + 1)
            return page_range

        page_range = get_page_range(soup)

        for page in page_range:
            yield template.format(titleId=context['titleId'], page=page)

    def episode_thumb_parser(self, response, context):
        episode_thumb = dict(
            titleId=response.scrap.match('titleId'),
            no=response.scrap.match('no'),
            episode_thumb_src=response.url
        )
        return episode_thumb

    def episode_parser(self, response, context):
        soup = response.scrap.soup
        match = response.scrap.match

        def get_episode_title(soup):
            title = soup.select_one('div.view > h3')
            text = title.text.strip()
            return text

        episode = dict(
            titleId=match('titleId'),
            no=match('no'),
            episode_title=get_episode_title(soup)
        )
        context['comment_kwargs'] = {
            'titleId': match('titleId'),
            'no': match('no')
        }
        return episode

    def episode_cut_parser(self, response, context):
        match = response.scrap.match
        episode_cut = dict(
            titleId=match('titleId'),
            no=match('no'),
            episode_cut_src=response.url
        )
        return episode_cut

    def _get_comment_url(self, path, titleId, no, page=1):
        params = dict(
            ticket='comic',
            templateId='webtoon',
            pool='cbox3',
            lang='ko',
            country='KR',
            objectId='{}_{}'.format(titleId, no),
            pageSize=COMMENT_PAGE_SIZE,
            indexSize='10',
            listType='OBJECT',
            page=page,
            refresh='false',
            sort='NEW'
        )
        url = queryjoin(path, params)
        return url

    def comment_urlrenderer(self, parent_response, path, context):
        match = parent_response.scrap.match
        titleId = match('titleId')
        no = match('no')
        for page in range(1, 100000):
            url = self._get_comment_url(path, titleId, no, page)
            yield url

    def comment_page_breaker(self, response, context):
        query = response.scrap.query
        json = parse_jsonp(response.text)
        total_comment_count = json['result']['count']['total']
        end_page = math.ceil(total_comment_count/COMMENT_PAGE_SIZE)
        page = int(query['page'])
        return page == end_page

    def comment_parser(self, response, context):
        titleId = context['comment_kwargs']['titleId']
        no = context['comment_kwargs']['no']
        json = parse_jsonp(response.text)
        comment_list = json['result']['commentList']
        for comment in comment_list:
            cmt = dict(
                titleId=titleId,
                no=no,
                comment_content=comment['contents'],
                comment_no=comment['commentNo']
            )
            comment['titleId'] = titleId
            comment['no'] = no
            yield comment


def retrive_webtoon(context):
    comment_save_to = os.path.join(context['save_to'], 'comment.csv')
    n = NaverWebToonScraper()
    r = n.scrap(context=context)
    toon = pd.DataFrame(r['toon'])
    toon_thumb = pd.DataFrame(r['toon_thumb'])
    episode_thumb = pd.DataFrame(r['episode_thumb'])
    episode = pd.DataFrame(r['episode'])
    episode_cut = pd.DataFrame(r['episode_cut'])
    comment = pd.DataFrame(r['comment'])

    # df_toon = pd.merge(toon, toon_thumb)
    # df_episode = pd.merge(episode, episode_thumb, on=['titleId', 'no'])
    # df_episode = pd.merge(df_episode, episode_cut, on=['titleId', 'no'])
    # df = pd.merge(df_toon, df_episode)
    # df.to_csv(comment_save_to)
    # comment.to_csv(comment_save_to)
