""" Tests of the account request API
"""
from unittest.case import TestCase

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from mock import Mock, patch

from core_main_app.commons.exceptions import ApiError
from core_website_app.components.account_request import api as account_request_api
from core_website_app.components.account_request.models import AccountRequest


class TestsAccountRequestGet(TestCase):

    @patch('core_website_app.components.account_request.models.AccountRequest.get_by_id')
    def test_account_request_get_return_request_object(self, mock_get_by_id):
        # Arrange
        request_id = "1"
        mock_get_by_id.return_value = _create_account_request()
        # Act
        result = account_request_api.get(request_id)
        # Assert
        self.assertIsInstance(result, AccountRequest)

    @patch('core_website_app.components.account_request.models.AccountRequest.get_by_id')
    def test_account_request_get_raise_ApiError_if_request_not_found(self, mock_get_by_id):
        # Arrange
        request_id = "1"
        mock_get_by_id.side_effect = Exception()
        # Act # Assert
        with self.assertRaises(ApiError):
            account_request_api.get(request_id)


class TestsAccountRequestAccept(TestCase):

    def setUp(self):
        self.account_request = _create_account_request()

    @patch('core_website_app.components.account_request.models.AccountRequest.delete')
    @patch('core_website_app.components.account_request.api._get_user_by_username')
    def test_account_request_accept_raise_ApiError_if_user_does_not_exist(self, mock_get_user_by_username, mock_delete):
        # Arrange
        mock_get_user_by_username.side_effect = ObjectDoesNotExist()

        # Act # Assert
        with self.assertRaises(ApiError):
            account_request_api.accept(self.account_request, False)

    @patch('core_website_app.components.account_request.models.AccountRequest.delete')
    @patch('core_website_app.components.account_request.api._create_and_save_user')
    @patch('core_website_app.components.account_request.api._get_user_by_username')
    def test_account_request_accept_return_user(self, mock_get_by_username, mock_create_and_save, mock_delete):
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_get_by_username.return_value = mock_user
        mock_create_and_save.return_value = mock_user
        mock_delete.return_value = None

        # Act
        result = account_request_api.accept(self.account_request, False)

        #  Assert
        self.assertIsInstance(result, User)


class TestsAccountRequestInsert(TestCase):

    def setUp(self):
        self.mock_account_request = _create_account_request()

    @patch('core_website_app.components.account_request.api._get_user_by_username')
    def test_account_request_insert_raise_ApiError_if_username_already_exist(self, mock_get_user_by_username):
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.username = "username"
        mock_get_user_by_username.return_value = mock_user

        # Act # Assert
        with self.assertRaises(ApiError):
            account_request_api.insert(mock_user)

    @patch('core_website_app.components.account_request.models.AccountRequest.save')
    @patch('core_website_app.components.account_request.api._get_user_by_username')
    def test_account_request_insert_return_request(self, mock_get_user_by_username, mock_save):
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.username = "username"
        mock_get_user_by_username.side_effect = ObjectDoesNotExist()
        mock_save.return_value = self.mock_account_request

        # Act
        result = account_request_api.insert(mock_user)

        # Assert
        self.assertIsInstance(result, AccountRequest)


def _create_account_request(username="username"):
    """
        Create an AccountRequest object using default parameters

        Parameters:
            username (str):

        Returns:
            AccountRequest object
    """
    return AccountRequest(username)
