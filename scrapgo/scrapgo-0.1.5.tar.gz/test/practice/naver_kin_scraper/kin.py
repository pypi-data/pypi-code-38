import os
import re
import json
import math
from pprint import pprint
from urllib.parse import unquote

import pandas as pd

from scrapgo import LinkRelayScraper, urlpattern, url, root
from scrapgo import settings
from scrapgo.utils import mkdir_p, cp, queryjoin


MAX_RESULT_PAGE = 150
COMMENT_PAGE_COUNT = 5


class NaverKinScraper(LinkRelayScraper):
    ROOT_URL = 'https://kin.naver.com/search/list.nhn'
    CRAWL_TARGET_ATTRS = settings.CRAWL_TARGET_ATTRS + ('content', )
    REQUEST_DELAY = 0, 1
    REQUEST_LOGGING = True

    LINK_RELAY = [
        url(
            '/search/list.nhn',
            generator='question_page_urlrenderer',
            fields=['query', 'page'],
            name='results'
        ),
        urlpattern(
            r'^https://kin.naver.com/qna/detail.nhn\?d1id=(?P<d1id>\d+)&dirId=(?P<dirId>\d+)&docId=(?P<docId>\d+).+$',
            fields=['d1id', 'dirId', 'docId'],
            parser='question_parser',
            name='question'
        ),
        urlpattern(
            r'^https://kin-phinf.pstatic.net/(?P<date>.+)/.+/(?P<filename>.+)\?type=(?P<type>.+)$',
            parser='image_parser',
            referer='question',
            name='image',
        ),
        url(
            'https://kin.naver.com/ajax/detail/commentListAjax.nhn',
            fields=['answerNo', 'count', 'dirId', 'docId', 'page'],
            generator='comment_urlrenderer',
            referer='question',
            parser='comment_parser',
            refresh=True,
            name='comment',
        )
    ]

    def question_page_urlrenderer(self, parent_response, path, **kwargs):
        soup = parent_response.scrap.soup
        query = parent_response.scrap.query

        def get_result_count(soup):
            soup_count = soup.select_one('.number > em')
            count = 0
            if soup_count:
                count_text = soup_count.text
                count_text = count_text.replace(',', '')
                step, count = count_text.split('/')
                count = int(count)
            return count

        def get_page_size(soup):
            action = self.get_action('question')
            links = set(a['href'] for a in soup(href=action.regex))
            link_count = len(links)
            return link_count

        result_count = get_result_count(soup)
        page_size = get_page_size(soup)
        end_page = math.ceil(result_count/page_size) + 1
        end_page = min(MAX_RESULT_PAGE, end_page)
        for page in range(1, end_page+1):
            yield dict(
                query=query['query'],
                page=page
            )

    def question_parser(self, response, context, answer_list=None):
        soup = response.scrap.soup
        match = response.scrap.match

        def get_question_title(soup):
            title = soup.select_one('div.title')
            text = self.prettify_textarea(title)
            return text

        def get_question_content(soup):
            content_soup = soup.select_one('div.c-heading__content')
            content = self.prettify_textarea(content_soup)
            return content

        def get_answer_list(soup):
            answers = [{'answer_no': 0, 'answer_content': ''}]
            prefix = 'answer_'
            answer_areas = soup.select('div[id^={}]'.format(prefix))
            for answer_area in answer_areas:
                no = answer_area['id'].replace(prefix, '')
                answer_content = soup.select_one(
                    'div.c-heading-answer__content-user')
                content = self.prettify_textarea(answer_content)
                answer = dict(
                    answer_no=no,
                    answer_content=content
                )
                answers.append(answer)
            return answers

        question = dict(
            dirId=match('dirId'),
            docId=match('docId'),
            question_url=response.url,
            question_title=get_question_title(soup),
            question_content=get_question_content(soup)
        )

        answer_list = get_answer_list(soup)

        for answer in answer_list:
            answer.update(question)

        return answer_list

    def image_parser(self, response, context):
        query = response.parent.scrap.query
        image = dict(
            dirId=query['dirId'],
            docId=query['docId'],
            image_src=response.url
        )
        print('image_parser:image', image)
        if image['docId'] == '300939037':
            self.stop()
        yield image

    def comment_urlrenderer(self, parent_response, path, context):
        query = parent_response.scrap.query
        dirId = query['dirId']
        docId = query['docId']

        soup = parent_response.scrap.soup
        prefix = 'cmtstr_'
        selector = 'a[id^={}]'.format(prefix)
        soup_comment_buttons = soup.select(selector)
        answer_no_list = []
        for soup_button in soup_comment_buttons:
            button_id = soup_button['id']
            answer_no = button_id.replace(prefix, '')
            comment_counter = soup_button.select_one('.button_compose_count')
            if comment_counter:
                count = comment_counter.text.strip()
                if count:
                    count = int(count)
                    end_page = math.ceil(count/COMMENT_PAGE_COUNT) + 1
                    page_range = range(1, end_page+1)
                    for page in page_range:
                        yield dict(
                            answerNo=answer_no,
                            count=COMMENT_PAGE_COUNT,
                            dirId=dirId,
                            docId=docId,
                            page=page
                        )

    def comment_parser(self, response, context):
        print('comment_parser:', response.url)
        comment_list = response.json()['result']['commentList']
        return comment_list


def naver_kin_with_image(params, context):
    nk = NaverKinScraper(root_params=params)
    r = nk.scrap(context=context, until='comment')
    # for row in r['question']:
    #     print(row)
    #     # break
    # for row in r['comment']:
    #     print(row)
    #     # break
