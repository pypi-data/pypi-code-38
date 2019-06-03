""" Privacy policy api
"""
import core_main_app.components.web_page.api as web_page_api
from core_main_app.commons.exceptions import ApiError
from core_website_app.commons.enums import WEB_PAGE_TYPES

PRIVACY_PAGE_NAME = "privacy_policy"
PRIVACY_PAGE_TYPE = WEB_PAGE_TYPES[PRIVACY_PAGE_NAME]


def get():
    """ Get the privacy policy if exist

        Returns: privacy policy web page
    """
    return web_page_api.get(PRIVACY_PAGE_NAME)


def upsert(privacy_policy_page):
    """ Post the privacy policy

        Parameters:
            privacy_policy_page (WebPage): WebPage for the privacy policy

        Returns: privacy policy web page
    """
    if privacy_policy_page.type != PRIVACY_PAGE_TYPE:
        raise ApiError(
            "Webpage type not coherent (expected: %s; actual %s" % (str(PRIVACY_PAGE_TYPE),
                                                                    str(privacy_policy_page.type))
        )

    return web_page_api.upsert(privacy_policy_page)
