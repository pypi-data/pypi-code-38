from selenium.webdriver.common.by import By

from promium import Page, Block, Element, Link, InputField
from tests.urls import collect_url


class CheckBoxBlock(Block):
    pass


class WithCheckBoxesBlock(Block):

    in_category_block = CheckBoxBlock(
        By.CSS_SELECTOR,
        '[data-qaid="category_line"]'
    )
    in_tag_block = CheckBoxBlock(
        By.CSS_SELECTOR,
        '[data-qaid="tag_line"]'
    )
    in_company_block = CheckBoxBlock(
        By.CSS_SELECTOR,
        '[data-qaid="company_line"]'
    )


class SearchTermBlock(Block):

    hits_term = Element(
        By.CSS_SELECTOR,
        '[data-qaid="term_hits_text"]'
    )
    main_term = Element(
        By.CSS_SELECTOR,
        '[data-qaid="term_main_text"]'
    )


class SuggestItemBlock(Block):

    category_term_link = Element(
        By.CSS_SELECTOR,
        '[data-qaid="category_term_link"]'
    )
    search_term_link = SearchTermBlock(
        By.CSS_SELECTOR,
        '[data-qaid="search_term_link"]'
    )


class SuggestItemsBlock(Block):

    suggest_item_block = SuggestItemBlock.as_list(
        By.CSS_SELECTOR,
        '[data-qaid="suggest_item"]'
    )


class SuggesterBlock(Block):

    checkbox_block = WithCheckBoxesBlock(
        By.CSS_SELECTOR,
        '[data-qaid="group_with_checkbox"]'
    )
    all_results_block = Block(
        By.CSS_SELECTOR,
        '[data-qaid="all_results_list"]'
    )
    suggest_items_block = SuggestItemsBlock.as_list(
        By.CSS_SELECTOR,
        '[data-qaid="autocomplete_list"]'
    )


class SearchBlock(Block):

    search_input = InputField(
        By.CSS_SELECTOR,
        '[data-qaid="search_input"]'
    )
    search_button = Element(
        By.CSS_SELECTOR,
        '[data-qaid="search_button"]'
    )
    suggester_block = SuggesterBlock(
        By.CSS_SELECTOR,
        '[data-qaid="autocomplete_block"]'
    )


class Catalog404WrapperBlock(Block):

    search_block = SearchBlock(
        By.CSS_SELECTOR,
        '[data-qaid="search_input_block"]'
    )
    logo_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="404_logo_href"]'
    )
    main_404_title = Element(
        By.CSS_SELECTOR,
        '[data-qaid="404_main_title"]'
    )
    suggest_404_title = Element(
        By.CSS_SELECTOR,
        '[data-qaid="404_suggest_title"]'
    )
    suggest_404_title_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="404_suggest_title_link"]'
    )


class Catalog404Page(Page):

    url = collect_url('xxx')

    wrapper_block = Catalog404WrapperBlock(
        By.CSS_SELECTOR,
        '[data-qaid="404_wrapper_block"]'
    )
