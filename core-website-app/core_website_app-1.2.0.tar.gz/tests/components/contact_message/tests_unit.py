""" Tests of contact message API
"""
from unittest.case import TestCase

from mock import Mock, patch

from core_main_app.commons import exceptions
from core_website_app.components.contact_message import api as contact_message_api
from core_website_app.components.contact_message.models import ContactMessage


class TestsContactMessageGet(TestCase):
    """
    """

    def setUp(self):
        self.message_id = 1

    @patch('core_website_app.components.contact_message.models.ContactMessage.get_by_id')
    def test_contact_message_get_by_id_return_object(self, mock_get_by_id):
        # Arrange
        mock_message = _create_mock_contact_message()
        mock_get_by_id.return_value = mock_message

        # Act
        result = contact_message_api.get(self.message_id)

        # Assert
        self.assertIsInstance(result, ContactMessage)

    @patch('core_website_app.components.contact_message.models.ContactMessage.get_by_id')
    def test_contact_message_get_raise_api_error_if_not_found(self, mock_get_by_id):
        # Arrange
        mock_get_by_id.side_effect = Exception()

        # Act # Assert
        with self.assertRaises(exceptions.ApiError):
            contact_message_api.get(self.message_id)


class TestContactMessageGetAll(TestCase):

    @patch('core_website_app.components.contact_message.models.ContactMessage.get_all')
    def test_contact_message_get_all_contains_contact_message_only(self, mock_get_all):
        # Arrange
        mock_message_1 = _create_mock_contact_message()
        mock_message_2 = _create_mock_contact_message(mock_pk=2, mock_name="message name 2", mock_email="e2@mail.com",
                                                      mock_content="content message 2")

        mock_get_all.return_value = [mock_message_1, mock_message_2]

        # Act
        result = contact_message_api.get_all()

        # Assert
        self.assertTrue(all(isinstance(item, ContactMessage) for item in result))


class TestsContactMessageDelete(TestCase):

    @patch('core_website_app.components.contact_message.models.ContactMessage.delete')
    def test_message_delete_raise_api_error_if_message_does_not_exist(self, mock_message_delete):
        # Arrange
        mock_message = _create_contact_message()
        mock_message_delete.side_effect = Exception()

        # Act # Assert
        with self.assertRaises(exceptions.ApiError):
            contact_message_api.delete(mock_message)


class TestsContactMessageUpsert(TestCase):

    def setUp(self):
        self.mock_message = _create_contact_message()

    @patch('core_website_app.components.contact_message.models.ContactMessage.save')
    def test_message_upsert_return_message(self, mock_save):
        # Arrange
        mock_save.return_value = self.mock_message

        # Act
        result = contact_message_api.upsert(self.mock_message)

        # Assert
        self.assertIsInstance(result, ContactMessage)

    @patch('core_website_app.components.contact_message.models.ContactMessage.save')
    def test_message_upsert_raise_api_error_if_save_failed(self, mock_save):
        # Arrange
        mock_save.side_effect = Exception()

        # Act # Assert
        with self.assertRaises(exceptions.ApiError):
            contact_message_api.upsert(self.mock_message)


def _create_mock_contact_message(mock_pk=1, mock_name="message name", mock_email="sender@mail.com",
                                 mock_content="lorem ipsum dolor sit amet "):
    """

    :param mock_pk:
    :param mock_name:
    :param mock_email:
    :param mock_content:

    :return:
    """
    mock_message = Mock(spec=ContactMessage)
    mock_message.id = mock_pk
    mock_message.name = mock_name
    mock_message.email = mock_email
    mock_message.content = mock_content

    return mock_message


def _create_contact_message(pk=1, name="message name", email="sender@mail.com",
                            content="lorem ipsum dolor sit amet "):
    """

    :param pk:
    :param name:
    :param email:
    :param content:

    :return:
    """

    return ContactMessage(
        pk=pk,
        name=name,
        email=email,
        content=content
    )
