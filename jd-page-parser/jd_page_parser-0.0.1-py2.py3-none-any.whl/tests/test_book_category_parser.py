# -*- coding: utf-8 -*-

# Copyright © 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from jd_page_parser.category_parsers import BookCategoryParser

import pytest


def test_parse(book_categories_page_source, target_book_categories):
    parser = BookCategoryParser(book_categories_page_source)
    categories = parser.parse()

    assert len(categories) == 52

    categories_by_name = {category['name']:category for category in categories}

    for target_book_category in target_book_categories:
        name = target_book_category['name']
        assert name in categories_by_name

        category = categories_by_name[name]

        assert target_book_category['url'] == category['url']

        subcategories_by_name = \
            {subcategory['name']:subcategory for subcategory in category['children']}
        for child in target_book_category['children']:
            assert child['name'] in subcategories_by_name
            assert child['url'] == subcategories_by_name[child['name']]['url']
