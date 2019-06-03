""" TemplateXslRendering model
"""
from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions
from core_main_app.components.template.models import Template
from core_main_app.components.xsl_transformation.models import XslTransformation
from mongoengine.queryset.base import CASCADE, NULLIFY


class TemplateXslRendering(Document):
    """ TemplateXslRendering object
    """
    template = fields.ReferenceField(Template, blank=False, reverse_delete_rule=CASCADE, unique=True)
    list_xslt = fields.ReferenceField(XslTransformation, reverse_delete_rule=NULLIFY, blank=True)
    detail_xslt = fields.ReferenceField(XslTransformation, reverse_delete_rule=NULLIFY, blank=True)

    @staticmethod
    def get_by_id(template_xsl_rendering_id):
        """ Get a TemplateXslRendering document by its id.

        Args:
            template_xsl_rendering_id: Id.

        Returns:
            TemplateXslRendering object.

        Raises:
            DoesNotExist: The TemplateXslRendering doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return TemplateXslRendering.objects.get(pk=str(template_xsl_rendering_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_by_template_id(template_id):
        """Get TemplateXslRendering by its template id.

        Args:
            template_id: Template id.

        Returns:
            The TemplateXslRendering instance.

        Raises:
            DoesNotExist: The TemplateXslRendering doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return TemplateXslRendering.objects.get(template=template_id)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_all():
        """Get all TemplateXslRendering.

        Returns:
            List of TemplateXslRendering.

        """
        return TemplateXslRendering.objects.all()
