"""Explore Data Structure
"""
from django_mongoengine import fields
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions as exceptions
from core_parser_app.components.data_structure.models import DataStructure


class ExploreDataStructure(DataStructure):
    """ Explore data structure
    """

    selected_fields_html_tree = fields.StringField(blank=True, default=None)

    @staticmethod
    def get_by_user_id_and_template_id(user_id, template_id):
        """ Return explore data structure given its id and template id

        Returns:

        """
        try:
            return ExploreDataStructure.objects.get(user=str(user_id), template=str(template_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_by_id(data_structure_id):
        """ Return the object with the given id.

        Args:
            data_structure_id:

        Returns:
            Explore Data Structure (obj): ExploreDataStructure object with the given id

        """
        try:
            return ExploreDataStructure.objects.get(pk=str(data_structure_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)
