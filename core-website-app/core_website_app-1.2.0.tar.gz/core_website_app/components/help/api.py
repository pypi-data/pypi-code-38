""" Help page api
"""
import core_main_app.components.web_page.api as web_page_api
from core_main_app.commons.exceptions import ApiError
from core_website_app.commons.enums import WEB_PAGE_TYPES

HELP_PAGE_NAME = "help"
HELP_PAGE_TYPE = WEB_PAGE_TYPES[HELP_PAGE_NAME]


def get():
    """ Get the help if exist

        Returns: help web page
    """
    return web_page_api.get(HELP_PAGE_NAME)


def upsert(help_page):
    """ Post the help

        Parameters:
            help_page (WebPage): Webpage for the help

        Returns: help web page
    """
    if help_page.type != HELP_PAGE_TYPE:
        raise ApiError(
            "Webpage type not coherent (expected: %s; actual %s" % (str(HELP_PAGE_TYPE), str(help_page.type))
        )

    return web_page_api.upsert(help_page)
