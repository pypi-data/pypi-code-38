# -*- coding: utf-8 -*-

# Copyright © 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import io

import pytest


@pytest.fixture(scope='session')
def pages_dir():
    return os.path.join(os.path.dirname(__file__), 'pages')

@pytest.fixture(scope='session')
def book_pages_dir(pages_dir):
    return os.path.join(pages_dir, 'book')

@pytest.fixture(scope='session')
def book_categories_page_source(book_pages_dir):
    categories_file_path = os.path.join(book_pages_dir, 'categories.html')
    with io.open(categories_file_path, 'rb') as fh:
        content = fh.read().decode('gb2312', 'ignore')

    return content

@pytest.fixture(scope='session')
def book_list_page_source(book_pages_dir):
    book_list_file_path = os.path.join(book_pages_dir, 'list.html')
    with io.open(book_list_file_path, 'rb') as fh:
        content = fh.read().decode('utf-8', 'ignore')

    return content

@pytest.fixture(scope='session')
def book_detail_page_source(book_pages_dir):
    book_detail_file_path = os.path.join(book_pages_dir, 'book.html')
    with io.open(book_detail_file_path, 'rb') as fh:
        content = fh.read().decode('gbk', 'ignore')

    return content

@pytest.fixture(scope='session')
def target_book_detail():
    return {
        'title': u'张爱玲经典小说集（全五卷）',
        'author': u'张爱玲',
        'images': [
            'https://img14.360buyimg.com/n1/jfs/t1/31378/22/14300/191396/5cbd78faEba0bafc2/3742fba488593285.jpg',
            'https://img14.360buyimg.com/n1/jfs/t1/39879/29/1561/135991/5cbd78feEc25d59a6/9923e85e7d666f01.jpg',
            'https://img14.360buyimg.com/n1/jfs/t1/40122/40/1521/127894/5cbd7901Eb784d9b5/d4bfccf7c898f0a7.jpg',
            'https://img14.360buyimg.com/n1/jfs/t1/31617/15/14062/162231/5cbd7904E350db864/5ed99e676a08e4cd.jpg'
        ],
        'detail': {
            u'出版社': u'北京十月文艺出版社',
            'ISBN': '9787530219225',
            u'版次': '1',
            u'商品编码': '12592414',
            u'品牌': u'新经典',
            u'包装': u'精装',
            u'开本': u'32开',
            u'出版时间': '2019-03-01',
            u'用纸': u'书写纸',
            u'套装数量': '5'
        }
    }

@pytest.fixture(scope='session')
def target_book_list():
    next_page_uri = '/list.html' + \
        '?cat=1713,3258,3297&tid=3297&page=2&sort=sort_rank_asc&trans=1&JL=6_0_0'
    return {
        'links': [
            {
                'url': 'https://item.jd.com/12449755.html',
                'title': u'余华经典作品集（全5册）'
            },
            {
                'url': 'https://item.jd.com/11757834.html',
                'title': u'中国科幻基石丛书：三体（套装1-3册）'
            },
        ],
        'next_page_uri': next_page_uri
    }

@pytest.fixture(scope='session')
def target_book_categories():
    return [
        {
            'name': u'小说',
            'url': 'https://channel.jd.com/1713-3258.html',
            'children': [
                {
                    'name': u'中国当代小说',
                    'url': 'https://list.jd.com/1713-3258-3297.html'
                },
                {
                    'name': u'中国近现代小说',
                    'url': 'https://list.jd.com/1713-3258-3298.html'
                },
                {
                    'name': u'中国古典小说',
                    'url': 'https://list.jd.com/1713-3258-3299.html'
                },
                {
                    'name': u'四大名著',
                    'url': 'https://list.jd.com/1713-3258-3300.html'
                },
                {
                    'name': u'港澳台小说',
                    'url': 'https://list.jd.com/1713-3258-3301.html'
                },
                {
                    'name': u'穿越/重生/架空',
                    'url': 'https://list.jd.com/1713-3258-3302.html'
                },
                {
                    'name': u'外国小说',
                    'url': 'https://list.jd.com/1713-3258-3303.html'
                },
            ]
        },
        {
            'name': u'文学',
            'url': 'https://channel.jd.com/1713-3259.html',
            'children': [
                {
                    'name': u'散文/随笔/书信',
                    'url': 'https://list.jd.com/1713-3259-3333.html'
                },
                {
                    'name': u'诗歌词曲',
                    'url': 'https://list.jd.com/1713-3259-3334.html'
                },
                {
                    'name': u'中国文学',
                    'url': 'https://list.jd.com/1713-3259-3336.html'
                },
                {
                    'name': u'外国文学',
                    'url': 'https://list.jd.com/1713-3259-3337.html'
                },
                {
                    'name': u'名家作品',
                    'url': 'https://list.jd.com/1713-3259-3328.html'
                },
                {
                    'name': u'儿童文学',
                    'url': 'https://list.jd.com/1713-3259-3329.html'
                },
                {
                    'name': u'作品集',
                    'url': 'https://list.jd.com/1713-3259-3327.html'
                },
            ]
        }
    ]
