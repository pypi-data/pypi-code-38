# -*- coding: utf-8 -*-

import pytest

from promium.test_case import WebDriverTestCase
from tests.urls import collect_url
from tests.pages.catalog_404_page import Catalog404Page


MAIN_404_PAGE_TITLE = (
    u'К сожалению, такой страницы больше нет, или вы ввели неверный адрес.'
)
SUGGEST_404_PAGE_TITLE = (
    u'Воспользуйтесь поиском или перейдите на главную страницу.'
)

SEARCH_TERM = 'search?search_term='


def get_expected_search_term_url(search_target):
    return collect_url('{search_term}{search_target}'.format(
        search_term=SEARCH_TERM,
        search_target=search_target
    ))


@pytest.mark.se
class Test404CatalogPage(WebDriverTestCase):
    test_case_url = 'some url with test case'

    def test_catalog_404_page_check_elements(self):
        catalog_404_page = Catalog404Page(self.driver)
        catalog_404_page.open()
        wrapper_block = catalog_404_page.wrapper_block
        self.soft_assert_equals(
            wrapper_block.logo_link.get_status_code,
            200,
            u'Не возможен переход на главную через лого.'
        )
        self.soft_assert_equals(
            wrapper_block.main_404_title.text,
            MAIN_404_PAGE_TITLE,
            u'Не правильно указан основной title на странице 404.'
        )
        self.soft_assert_equals(
            wrapper_block.suggest_404_title.text,
            SUGGEST_404_PAGE_TITLE,
            u'Не правильно указан suggest title на странице 404.'
        )
        self.soft_assert_equals(
            wrapper_block.suggest_404_title_link.get_status_code,
            200,
            u'Не возможен переход на главную через ссылку в suggest title.'
        )
        fake_search_query = 666
        search_input = wrapper_block.search_block.search_input
        search_input.send_keys(fake_search_query)
        wrapper_block.search_block.search_button.click()
        self.soft_assert_current_url(
            get_expected_search_term_url(fake_search_query)
        )
