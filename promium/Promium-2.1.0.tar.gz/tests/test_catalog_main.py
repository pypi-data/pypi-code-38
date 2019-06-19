import pytest

from promium.test_case import WebDriverTestCase
from tests.pages.catalog_main_page import CatalogMainPage


@pytest.mark.se
class TestCatalogHeader(WebDriverTestCase):
    test_case_url = 'some url with test case'

    def test_check_catalog_header_elements(self):
        main_page = CatalogMainPage(self.driver)
        main_page.open()
        header_block = main_page.header_block
        header_block.registration_link.hover_over()
        header_block.header_reg_popup.wait_to_display()
        header_block.logo_link.hover_over()
        self.soft_assert_equals(
            header_block.logo_link.get_status_code,
            200
        )
        self.soft_assert_equals(
            header_block.favourite_link.get_status_code,
            200
        )
        header_block.shopping_cart_link.click()
        main_page.empty_order_popup.wait_to_display()
        self.soft_assert_equals(
            main_page.header_block.authorization_link.get_status_code,
            200
        )
