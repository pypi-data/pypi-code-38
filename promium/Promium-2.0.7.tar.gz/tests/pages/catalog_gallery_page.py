from selenium.webdriver.common.by import By

from promium import Page, Block, Element
from tests.urls import collect_url


class FilterHintBlock(Block):

    close_hint_link = Element(
        By.CSS_SELECTOR,
        '[data-qaid="close_hint"]'
    )


class ProductTilBlock(Block):

    PRODUCT_ID_SELECTOR_ATTR = 'data-product-qaid'
    PRODUCT_POSITION_SELECTOR_ATTR = 'data-position-qaid'

    product_name = Element(
        By.CSS_SELECTOR,
        '[data-qaid="product_name"]'
    )
    presence = Element(
        By.CSS_SELECTOR,
        '[data-qaid="product_presence"]'
    )
    price = Element(
        By.CSS_SELECTOR,
        '[data-qaid="product_price"]'
    )
    old_price = Element(
        By.CSS_SELECTOR,
        '[data-qaid="old_price"]'
    )
    prosale_icon = Element(
        By.CSS_SELECTOR,
        '[data-qaid="prosale_icon"]'
    )
    add_favorite_icon = Element(
        By.CSS_SELECTOR,
        '[data-qaid="favorite"] svg'
    )
    flash_message = Element(
        By.CSS_SELECTOR,
        '[data-qaid="flash-message-text"]'
    )
    show_all_phones_link = Element(
        By.CSS_SELECTOR,
        '[data-qaid="show-all-phones-link"]'
    )


class ProductsBlock(Block):

    product_blocks = ProductTilBlock.as_list(
        By.CSS_SELECTOR,
        '[data-qaid="product_block"]'
    )

    def get_target_product_block(self, product_id):
        """
        Finds product block on products block by product id and return it.
        :param int product_id: "id" of the product which block you want to get.
        :return: product block
        """
        product_block = self.product_blocks.find(
            by=By.CSS_SELECTOR,
            locator='[{attribute}="{product_id}"]'.format(
                attribute=self.product_blocks.PRODUCT_ID_SELECTOR_ATTR,
                product_id=product_id
            )
        )
        return product_block


class CatalogGalleryPage(Page):

    url = collect_url('{query}')

    products_block = ProductsBlock(
        By.CSS_SELECTOR,
        '[data-qaid="product_gallery"]'
    )
    filter_hint_block = FilterHintBlock(
        By.CSS_SELECTOR,
        '[data-qaid="filter_hint"]'
    )
    show_more_button = Element(
        By.CSS_SELECTOR,
        '[data-qaid="show_more"]'
    )
