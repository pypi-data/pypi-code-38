import pytest
from bs4 import BeautifulSoup

from promium.test_case import RequestTestCase
from tests.urls import collect_url

from .pages.catalog_main_page import CatalogMainPage


BLOCKS = [
    'footer_customers',
    'footer_vendors',
    'footer_about_as',
    'footer_partners',
    'footer_countries',
    'top-searches',
    'footer_social_links'
]


@pytest.mark.request
class TestMainPage(RequestTestCase):
    test_case_url = 'some url with test case'

    @pytest.mark.parametrize('block', BLOCKS)
    def test_main_page_links(self, block):
        page_text = self.get_response(CatalogMainPage.url).text
        soup = BeautifulSoup(page_text, 'html.parser')
        needful_block = soup.find(attrs={'data-qaid': block})
        links = needful_block.findAll('a')
        for link in links:
            href = link.get('href')
            url = collect_url(href.strip('/')) if '://' not in href else href
            if "https://vk.com" not in url:
                response = self.get_response(url)
                self.soft_assert_equals(
                    response.status_code,
                    200,
                    u'Не доступна страница по url={} на главной'.format(url)
                )
