"""
OaiMetadataFormat model
"""

from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions


class OaiMetadataFormat(Document):
    """Represents a metadata format for Oai-Pmh"""
    metadata_prefix = fields.StringField()
    schema = fields.StringField()
    xml_schema = fields.StringField(blank=True)
    metadata_namespace = fields.StringField()

    meta = {'allow_inheritance': True}

    @staticmethod
    def get_by_id(oai_metadata_format_id):
        """ Get an OaiMetadataFormat by its id.

        Args:
            oai_metadata_format_id: OaiMetadataFormat id.

        Returns: The OaiMetadataFormat instance.

        Raises:
            DoesNotExist: The metadata format doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return OaiMetadataFormat.objects().get(pk=str(oai_metadata_format_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_by_metadata_prefix(metadata_prefix):
        """ Get an OaiMetadataFormat by its metadata prefix.

        Args:
            metadata_prefix: OaiMetadataFormat metadata prefix.

        Returns: The OaiMetadataFormat instance.

        Raises:
            DoesNotExist: The metadata format doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return OaiMetadataFormat.objects().get(metadata_prefix=metadata_prefix)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_all():
        """ Return all OaiMetadataFormat

        Returns:
            List of OaiMetadataFormat.

        """
        return OaiMetadataFormat.objects().all()

    @staticmethod
    def get_all_by_list_ids(list_oai_metadata_format_ids):
        """ Get all OaiMetadataFormat by a list of ids.

        Args:
            list_oai_metadata_format_ids:  List of ids.

        Returns:
            List of OaiMetadataFormat.

        """
        return OaiMetadataFormat.objects(pk__in=list_oai_metadata_format_ids).all()
