"""Bucket model
"""
from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

from core_composer_app.components.type_version_manager.models import TypeVersionManager
from core_main_app.commons import exceptions


class Bucket(Document):
    """Bucket class to store types by domain.
    """
    label = fields.StringField(unique=True)
    color = fields.StringField(unique=True)
    types = fields.ListField(fields.ReferenceField(TypeVersionManager), blank=True)

    @staticmethod
    def get_by_id(bucket_id):
        """Return a bucket given its id.

        Args:
            bucket_id:

        Returns:

        """
        try:
            return Bucket.objects.get(pk=str(bucket_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_all():
        """Return all buckets.

        Returns:

        """
        return Bucket.objects().all()

    @staticmethod
    def get_colors():
        """Return all colors.

        Returns:

        """
        return Bucket.objects.values_list('color')

    def save_object(self):
        """Custom save

        Returns:

        """
        try:
            return self.save()
        except mongoengine_errors.NotUniqueError as e:
            raise exceptions.NotUniqueError(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)
