"""
OaiXslTemplate model
"""

from django_mongoengine import fields, Document
from core_main_app.components.template.models import Template
from core_main_app.components.xsl_transformation.models import XslTransformation
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import OaiProviderMetadataFormat
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions
from mongoengine.queryset.base import CASCADE


class OaiXslTemplate(Document):
    """Relation between a template, an OaiProviderMetadataFormat and a XSLT."""
    template = fields.ReferenceField(Template, blank=False, reverse_delete_rule=CASCADE)
    xslt = fields.ReferenceField(XslTransformation, blank=False, reverse_delete_rule=CASCADE)
    oai_metadata_format = fields.ReferenceField(OaiProviderMetadataFormat, blank=False,
                                                unique_with=['xslt', 'template'], reverse_delete_rule=CASCADE)

    @staticmethod
    def get_by_id(oai_xslt_template_id):
        """ Returns the object with the given id

        Args:
            oai_xslt_template_id: Object id.

        Returns:
            OaiXslTemplate (obj): OaiXslTemplate object with the given id.

        Raises:
            DoesNotExist: The OaiXslTemplate doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return OaiXslTemplate.objects.get(pk=str(oai_xslt_template_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_by_template_id_and_metadata_format_id(template_id, metadata_format_id):
        """ Returns an OaiXslTemplate by its template and metadata_format.
        Args:
            template_id: Template id.
            metadata_format_id: Metadata format id.

        Returns:
            OaiXslTemplate instance.

        Raises:
            DoesNotExist: The metadata format doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return OaiXslTemplate.objects().get(template=template_id, oai_metadata_format=metadata_format_id)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_all_by_templates(templates):
        """ Returns all OaiXslTemplate used by a list of templates.

           Args:
               templates: List of templates.

           Returns:
               List of OaiXslTemplate.

           """
        return OaiXslTemplate.objects(template__in=templates).all()

    @staticmethod
    def get_all_by_metadata_format(metadata_format):
        """ Returns all OaiXslTemplate used by a metadata format.

           Args:
               metadata_format: OaiProviderMetadataFormat.

           Returns:
               List of OaiXslTemplate.

           """
        return OaiXslTemplate.objects(oai_metadata_format=metadata_format).all()

    def save_object(self):
        """ Custom save.

        Returns:
            Saved Instance.

        """
        try:
            return self.save()
        except mongoengine_errors.NotUniqueError as e:
            raise exceptions.NotUniqueError(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)
