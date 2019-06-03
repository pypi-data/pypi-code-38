"""
OaiSet model
"""

from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions


class OaiSet(Document):
    """Represents a set for Oai-Pmh"""
    set_spec = fields.StringField()
    set_name = fields.StringField()

    meta = {'allow_inheritance': True}

    @staticmethod
    def get_by_id(oai_set_id):
        """ Get an OaiSet by its id.

        Args:
            oai_set_id: OaiSet id.

        Returns: The OaiSet instance.

        Raises:
            DoesNotExist: The set doesn't exist
            ModelError: Internal error during the process

        """
        try:
            return OaiSet.objects().get(pk=str(oai_set_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_by_set_spec(set_spec):
        """ Get an OaiSet by its set_spec.

        Args:
            set_spec: OaiSet set_spec.

        Returns: The OaiSet instance.

        Raises:
            DoesNotExist: The set doesn't exist
            ModelError: Internal error during the process

        """
        try:
            return OaiSet.objects().get(set_spec=set_spec)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_all():
        """ Return all OaiSet

        Returns:
            List of OaiSet

        """
        return OaiSet.objects().all()

    @staticmethod
    def get_all_by_list_ids(list_oai_set_ids):
        """ Return all OaiSet by a list of ids.

        Returns:
            List of OaiSet

        """
        return OaiSet.objects(pk__in=list_oai_set_ids).all()
