from selenium.webdriver.common.by import By

from promium import Page, Block, Link, InputField

from tests.urls import collect_url


class HeaderRegistration(Block):
    pass


class TopSearchesBlock(Block):
    pass


class EmptyOrderPopup(Block):
    pass


class SearchBlock(Block):
    search_input = InputField(
        By.CSS_SELECTOR,
        '[data-qaid="search_input"]'
    )


class HeaderBlock(Block):

    header_reg_popup = HeaderRegistration(
        By.CSS_SELECTOR,
        '[data-qaid="header_registration_popup"]'
    )
    search_block = SearchBlock(
        By.CSS_SELECTOR,
        '[data-qaid="search_input_block"]'
    )
    logo_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="header_logo_link"]'
    )
    favourite_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="favorite"]'
    )
    shopping_cart_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="shopping_cart"]'
    )
    authorization_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="auth_element"][href*="sign-in"]'
    )
    registration_link = Link(
        By.CSS_SELECTOR,
        "[data-qaid='reg_element']"
    )


class CatalogMainPage(Page):

    url = collect_url('')

    top_searches_block = TopSearchesBlock(
        By.CSS_SELECTOR,
        '[data-qaid="top-searches"]'
    )
    header_block = HeaderBlock(
        By.CSS_SELECTOR,
        '[data-qaid="header"]'
    )
    empty_order_popup = EmptyOrderPopup(
        By.CSS_SELECTOR,
        '[data-qaid="overlay"]'
    )
