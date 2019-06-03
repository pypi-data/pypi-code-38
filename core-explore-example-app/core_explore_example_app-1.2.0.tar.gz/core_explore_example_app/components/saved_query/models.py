"""Saved query model
"""

from django_mongoengine import fields, Document
from core_main_app.components.template.models import Template
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions


class SavedQuery(Document):
    """Represents a query saved by the user (Query by Example)"""
    user_id = fields.StringField(blank=False)
    template = fields.ReferenceField(Template)
    query = fields.StringField(blank=False)
    displayed_query = fields.StringField(blank=False)

    @staticmethod
    def get_all():
        """ Get all Saved Query.

        Args:

        Returns:

        """
        return SavedQuery.objects.all()

    @staticmethod
    def get_by_id(query_id):
        """Get a saved query

        Args:
            query_id:

        Returns:

        """
        try:
            return SavedQuery.objects().get(pk=query_id)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_all_by_user_and_template(user_id, template_id):
        """Gets a saved query by user id and template id

        Args:
            user_id:
            template_id:

        Returns:

        """
        return SavedQuery.objects(user_id=str(user_id), template=template_id)
