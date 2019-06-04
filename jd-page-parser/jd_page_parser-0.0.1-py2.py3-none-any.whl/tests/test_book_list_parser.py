# -*- coding: utf-8 -*-

# Copyright © 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from jd_page_parser.product_list_parsers import BookListParser

import pytest


def test_parse(book_list_page_source, target_book_list):
    parser = BookListParser(book_list_page_source)
    result = parser.parse()

    assert len(result['links']) == 63
    assert result['next_page_uri'] == target_book_list['next_page_uri']

    for link in target_book_list['links']:
        assert link in result['links']
