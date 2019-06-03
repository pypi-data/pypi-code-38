""" Unit Test Saved Query
"""
from unittest.case import TestCase

from bson.objectid import ObjectId
from mock import patch
from mock.mock import Mock

from core_explore_example_app.components.saved_query.models import SavedQuery
from core_explore_example_app.components.saved_query import api as saved_query_api
from core_main_app.commons import exceptions


class TestSavedQueryGetById(TestCase):

    @patch.object(SavedQuery, 'get_by_id')
    def test_saved_query_get_by_id_raises_api_error_if_not_found(self, mock_get):
        # Arrange
        mock_get.side_effect = exceptions.DoesNotExist('')
        # Act # Assert
        with self.assertRaises(exceptions.DoesNotExist):
            saved_query_api.get_by_id(1)

    @patch.object(SavedQuery, 'get_by_id')
    def test_saved_query_get_by_id_returns_saved_query_if_found(self, mock_get):
        # Arrange
        mock_data = _create_saved_query()
        mock_get.return_value = mock_data
        # Act
        result = saved_query_api.get_by_id(mock_data.id)
        # Assert
        self.assertIsInstance(result, SavedQuery)


class TestSavedQueryGetAllByUserAndTemplate(TestCase):

    @patch.object(SavedQuery, 'get_all_by_user_and_template')
    def test_saved_queries_get_all_by_user_and_template_returns_saved_queries_from_user(self,
                                                                                        mock_get_by_user_and_template):
        user_id = ObjectId()
        template_id = ObjectId()
        mock_data_1 = _create_saved_query(user_id=user_id, template=template_id)
        mock_data_2 = _create_saved_query(user_id=user_id, template=template_id)
        mock_get_by_user_and_template.return_value = [mock_data_1, mock_data_2]
        # Act
        result = saved_query_api.get_all_by_user_and_template(user_id, template_id=template_id)
        # Assert
        self.assertTrue(all(item.user_id == user_id for item in result))


def _create_saved_query(user_id=None, template=None):
    """Returns a saved query

    Args:
        user_id:
        template:

    Returns:

    """
    if user_id is None:
        user_id = ObjectId()
    if template is None:
        template = ObjectId()

    return SavedQuery(
        id=ObjectId(),
        user_id=user_id,
        template=template,
        query="{}",
        displayed_query="query"
    )


def _create_mock_saved_query(user_id=None, template=None):
    """Returns a mock saved query

    Args:
        user_id:
        template:

    Returns:

    """
    if user_id is None:
        user_id = ObjectId()
    if template is None:
        template = ObjectId()
    mock_saved_query = Mock(spec=SavedQuery)
    mock_saved_query.user_id = user_id
    mock_saved_query.template = template
    mock_saved_query.id = ObjectId()

    return mock_saved_query
