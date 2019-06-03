"""
Type models
"""
from core_main_app.commons import exceptions
from core_main_app.components.template.models import Template
from django_mongoengine import fields
from mongoengine import errors as mongoengine_errors


class Type(Template):
    """Type class.
    """
    is_complex = fields.BooleanField(blank=False)

    @staticmethod
    def get_by_id(type_id):
        """Return a type given its id.

        Args:
            type_id:

        Returns:

        """
        try:
            return Type.objects().get(pk=str(type_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_all():
        """Return all types.

        Returns:

        """
        return Type.objects().all()

    @staticmethod
    def get_all_complex_type():
        """List all complex types.

        Returns:

        """
        return Type.objects(is_complex=True).all()
