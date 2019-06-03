"""
OaiProviderSet model
"""
from django_mongoengine import fields
from mongoengine.queryset.base import PULL
from core_oaipmh_common_app.components.oai_set.models import OaiSet
from core_main_app.components.template_version_manager.models import TemplateVersionManager
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions
from bson.objectid import ObjectId


class OaiProviderSet(OaiSet):
    """Represents a set for Oai-Pmh Provider"""
    templates_manager = fields.ListField(fields.ReferenceField(TemplateVersionManager, reverse_delete_rule=PULL),
                                         unique_with='set_spec')
    description = fields.StringField(blank=True)

    @staticmethod
    def get_all(order_by_field=None):
        """ Return all OaiProviderSet.
        Args:
            order_by_field: Order by field.
        Returns:
            List of OaiProviderSet.

        """
        return OaiProviderSet.objects().order_by(order_by_field)

    @staticmethod
    def get_all_by_templates_manager(templates_manager):
        """ Get all OaiProviderSet used by a list of templates_manager

        Args:
            templates_manager: List of templates manager

        Returns:
            List of OaiProviderSet.

        """
        return OaiProviderSet.objects(templates_manager__in=templates_manager).all()

    @staticmethod
    def get_by_set_spec(set_spec):
        """ Get an OaiProviderSet by its set_spec.

        Args:
            set_spec: OaiProviderSet set_spec.

        Returns:
            The OaiProviderSet instance.

        Raises:
            DoesNotExist: The set doesn't exist
            ModelError: Internal error during the process

        """
        try:
            return OaiProviderSet.objects().get(set_spec=set_spec)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)
