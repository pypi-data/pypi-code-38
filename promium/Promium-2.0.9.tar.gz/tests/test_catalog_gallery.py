
import pytest

from promium.device_config import ANDROID_360_640
from promium.test_case import WebDriverTestCase
from tests.pages.catalog_gallery_page import CatalogGalleryPage


@pytest.mark.se
class TestCatalogGallery(WebDriverTestCase):
    test_case_url = 'some url with test case'

    def test_view_products_gallery_blocks(self):
        catalog_gallery_page = CatalogGalleryPage(self.driver)
        catalog_gallery_page.open(query=u'Komplekty-nizhnego-belya')
        products_block = catalog_gallery_page.products_block
        products_block.wait_to_display()
        products = products_block.product_blocks
        product = products.first_item.wait_to_display()
        product.hover_over()
        show_all_phones_link = product.show_all_phones_link
        show_all_phones_link.wait_to_display()
        catalog_gallery_page.show_more_button.wait_to_display()

    @pytest.mark.device(ANDROID_360_640)
    def test_mobile_view_products_gallery_blocks(self):
        catalog_gallery_page = CatalogGalleryPage(self.driver)
        catalog_gallery_page.open(query=u'Komplekty-nizhnego-belya')
        products_block = catalog_gallery_page.products_block.wait_to_display()
        products_block.product_blocks.first_item.wait_to_display()
