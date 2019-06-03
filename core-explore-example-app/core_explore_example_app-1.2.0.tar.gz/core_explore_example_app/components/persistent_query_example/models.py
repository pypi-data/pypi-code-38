""" Persistent Query Example model
"""
from mongoengine import errors as mongoengine_errors

from core_explore_common_app.components.abstract_persistent_query.models import AbstractPersistentQuery
from core_main_app.commons import exceptions


class PersistentQueryExample(AbstractPersistentQuery):
    """ Persistent Query Example
    """

    @staticmethod
    def get_by_id(query_id):
        """Get a persistent query example

        Args:
            query_id:

        Returns:

        """
        try:
            return PersistentQueryExample.objects().get(pk=query_id)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)
