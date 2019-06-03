"""
OaiData model
"""

from django_mongoengine import fields, Document
from core_main_app.components.data.models import Data
from core_main_app.components.template.models import Template
from core_main_app.commons import exceptions
from mongoengine import errors as mongoengine_errors
from mongoengine.queryset.visitor import Q
import operator


class OaiData(Document):
    """Represents a data for Oai-Pmh Provider"""
    data = fields.ReferenceField(Data, blank=False)
    oai_date_stamp = fields.DateTimeField(blank=False, default=None)
    status = fields.StringField(blank=False)
    template = fields.ReferenceField(Template, blank=False)

    @property
    def data_id(self):
        """ Get data id even if the reference is broken (Deleted Data).

            Returns:
                ObjectId: Data id.

        """
        return self._data["data"].id

    @staticmethod
    def get_by_id(oai_data_id):
        """ Returns the object with the given id

        Args:
            oai_data_id:

        Returns:
            OaiData (obj): OaiData object with the given id

        Raises:
            DoesNotExist: The OaiData doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return OaiData.objects.get(pk=str(oai_data_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_by_data(data):
        """ Get an OaiData by its data.

        Args:
            data: Data instance.

        Returns:
            OaiData instance.

        Raises:
            DoesNotExist: The OaiData doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return OaiData.objects.get(data=data)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_all():
        """ Return all OaiData.

        Returns:
            List of OaiData.

        """
        return OaiData.objects().all()

    @staticmethod
    def get_all_by_template(template, from_date, until_date):
        """ Get all OaiData used by a template.

        Args:
            template: The template.
            from_date:
            until_date:

        Returns:
            List of OaiData.

        """
        q_list = {Q(template=template)}
        if from_date:
            q_list.add(Q(oai_date_stamp__gte=from_date))
        if until_date:
            q_list.add(Q(oai_date_stamp__lte=until_date))

        return OaiData.objects(reduce(operator.and_, q_list)).all()

    @staticmethod
    def get_all_by_status(status):
        """ Get all OaiData by their status.
        Args:
            status: Status.

        Returns:
            List of OaiData.

        """
        return OaiData.objects(status=status).all()

    @staticmethod
    def get_earliest_data_date():
        """ Get the earliest OaiData date
        Returns:
            Date of the earliest OaiData.

        """
        try:
            earliest_record = OaiData.objects().order_by("oai_date_stamp").first()

            return earliest_record.oai_date_stamp
        except Exception as ex:
            raise exceptions.ModelError(ex.message)
