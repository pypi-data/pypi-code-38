""" Tests of the web page API
"""

from unittest.case import TestCase

from mock import Mock, patch

import core_main_app.components.web_page.api as web_page_api
from core_main_app.commons.exceptions import ApiError
from core_main_app.components.web_page.models import WebPage
from core_website_app.commons.enums import WEB_PAGE_TYPES
from core_website_app.commons.exceptions import WebsiteWebPageDoesNotExistError


class TestsWebPageApiGet(TestCase):

    @patch.object(WebPage, 'get_by_type')
    def test_web_page_get_policy_privacy(self, mock_get_web_page_by_type):
        # Arrange
        content = "content web page privacy"
        mock_get_web_page_by_type.return_value = _create_mock_web_page(WEB_PAGE_TYPES["privacy_policy"], content)
        # Act
        result = web_page_api.get("privacy_policy")
        # Assert
        self.assertEqual("content web page privacy", result.content)

    @patch.object(WebPage, 'get_by_type')
    def test_web_page_get_term_of_use(self, mock_get_web_page_by_type):
        # Arrange
        content = "content web page terms"
        mock_get_web_page_by_type.return_value = _create_mock_web_page(WEB_PAGE_TYPES["terms_of_use"], content)
        # Act
        result = web_page_api.get("terms_of_use")
        # Assert
        self.assertEqual("content web page terms", result.content)

    @patch.object(WebPage, 'get_by_type')
    def test_web_page_get_help(self, mock_get_web_page_by_type):
        # Arrange
        content = "content web page help"
        mock_get_web_page_by_type.return_value = _create_mock_web_page(WEB_PAGE_TYPES["help"], content)
        # Act
        result = web_page_api.get("help")
        # Assert
        self.assertEqual("content web page help", result.content)

    @patch.object(WebPage, 'get_by_type')
    def test_web_page_get_not_in_database_return_none(self, mock_get_web_page_by_type):
        # Arrange
        mock_get_web_page_by_type.side_effect = WebsiteWebPageDoesNotExistError
        # Act
        result = web_page_api.get("fake_type")
        # Assert
        self.assertEqual(None, result)

    def test_web_page_get_with_wrong_type_return_none(self):
        # Arrange
        # Act
        page = web_page_api.get("wrong_type")
        # Assert
        self.assertEqual(None, page)


class TestsWebPageApiUpsert(TestCase):

    def test_web_page_upsert_type_does_not_exist(self):
        # Arrange
        web_page = WebPage(4, "test")
        # Act # Assert
        with self.assertRaises(ApiError):
            web_page_api.upsert(web_page)

    @patch.object(WebPage, 'save')
    def test_web_page_upsert_type_exist(self, mock_save):
        # Arrange
        web_page_type = WEB_PAGE_TYPES["help"]
        content = "content"
        web_page = WebPage(web_page_type, content)
        mock_save.return_value = WebPage(web_page_type, content)
        # Act
        result = web_page_api.upsert(web_page)
        # Assert
        self.assertEquals(content, result.content)


def _create_mock_web_page(page_type=-1, content="content"):
    mock_web_page = Mock(spec=WebPage)
    mock_web_page.type = page_type
    mock_web_page.content = content
    return mock_web_page
