# -*- coding: utf-8 -*-

# Copyright © 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from jd_page_parser.detail_parsers import BookDetailParser

import pytest


def test_parse(book_detail_page_source, target_book_detail):
    parser = BookDetailParser(book_detail_page_source)
    result = parser.parse()

    assert result['title'] == target_book_detail['title']
    assert result['author'] == target_book_detail['author']
    assert len(result['images']) == 4
    assert set(result['images']) == set(target_book_detail['images'])
    assert result['detail'] == target_book_detail['detail']
