"""Curate Data Structure models
"""
from django_mongoengine import fields
from mongoengine import errors as mongoengine_errors
from mongoengine.errors import NotUniqueError
from mongoengine.queryset.base import CASCADE
from core_main_app.commons import exceptions
from core_main_app.components.data.models import Data
from core_parser_app.components.data_structure.models import DataStructure
from core_parser_app.tools.parser import parser
from signals_utils.signals.mongo import connector, signals


class CurateDataStructure(DataStructure):
    """ Curate data structure.
    """
    form_string = fields.StringField(blank=True)
    data = fields.ReferenceField(Data, blank=True, reverse_delete_rule=CASCADE)

    def save_object(self):
        """ Custom save

        Returns:

        """
        try:
            return self.save()
        except NotUniqueError:
            raise exceptions.ModelError("Unable to save the document: not unique.")
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_by_id(data_structure_id):
        """ Return the object with the given id.

        Args:
            data_structure_id:

        Returns:
            Curate Data Structure (obj): CurateDataStructure object with the given id

        """
        try:
            return CurateDataStructure.objects.get(pk=str(data_structure_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_none():
        """ Return None object, used by forms.

        Returns:

        """
        return CurateDataStructure.objects().none()

    @staticmethod
    def get_all():
        """ Return all curate data structure api.

        Returns:

        """
        return CurateDataStructure.objects.all()

    @staticmethod
    def get_all_by_user_id_and_template_id(user_id, template_id):
        """Return all template version managers with user set to None.

        Returns:

        """
        return CurateDataStructure.objects(user=str(user_id), template=str(template_id)).all()

    @staticmethod
    def get_by_user_id_and_template_id_and_name(user_id, template_id, name):
        """Return the curate data structure with user, template id and name.

        Returns:

        """
        try:
            return CurateDataStructure.objects.get(user=str(user_id), template=str(template_id), name=name)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_all_by_user_id_with_no_data(user_id):
        """
        Return all the curate date structure of the user, with no data.

        Args: user_id:
        Return:
        """
        return CurateDataStructure.objects(user=str(user_id), data__exists=False).all()

    @staticmethod
    def get_all_except_user_id_with_no_data(user_id):
        """Return all the curate date structure except the one of the user, with no data.

        Args: user_id:
        Return:
        """
        return CurateDataStructure.objects(user__ne=str(user_id), data__exists=False).all()

    @staticmethod
    def get_all_by_user_id_and_template_id_with_no_data(user_id, template_id):
        """

        Args:
            user_id:
            template_id:

        Returns:

        """
        return CurateDataStructure.objects(user=str(user_id),
                                           template=str(template_id),
                                           data__exists=False).all()

    @staticmethod
    def get_all_with_no_data():
        """ Returns all curate data structure api with no link to a data.

        Args:

        Returns:

        """
        return CurateDataStructure.objects(data__exists=False).all()

    @staticmethod
    def get_by_data_id(data_id):
        """ Return the curate data structure with the given data id

        Args:
            data_id:

        Returns:

        """
        try:
            return CurateDataStructure.objects.get(data=str(data_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)


# Connect signals
connector.connect(DataStructure.pre_delete, signals.pre_delete, CurateDataStructure)
