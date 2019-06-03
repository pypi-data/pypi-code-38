""" Terms of use api
"""
import core_main_app.components.web_page.api as web_page_api
from core_main_app.commons.exceptions import ApiError
from core_website_app.commons.enums import WEB_PAGE_TYPES

TERMS_PAGE_NAME = "terms_of_use"
TERMS_PAGE_TYPE = WEB_PAGE_TYPES[TERMS_PAGE_NAME]


def get():
    """ Get the terms of use if exist

        Returns: Terms of use web page
    """
    return web_page_api.get(TERMS_PAGE_NAME)


def upsert(terms_of_use_page):
    """ Post the terms of use

        Parameters:
            terms_of_use_page (WebPage): content of the web page

        Returns: Terms of use web page
    """
    if terms_of_use_page.type != TERMS_PAGE_TYPE:
        raise ApiError(
            "Webpage type not coherent (expected: %s; entered: %s)" % (str(TERMS_PAGE_TYPE),
                                                                       str(terms_of_use_page.type))
        )

    return web_page_api.upsert(terms_of_use_page)
