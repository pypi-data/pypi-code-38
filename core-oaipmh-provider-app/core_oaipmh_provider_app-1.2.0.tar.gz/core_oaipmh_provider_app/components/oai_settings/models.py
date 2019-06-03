"""
OaiSettings model
"""

from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions


class OaiSettings(Document):
    """Represents the settings for Oai-Pmh Provider"""
    repository_name = fields.StringField()
    repository_identifier = fields.StringField()
    enable_harvesting = fields.BooleanField()

    @staticmethod
    def get():
        """ Get the settings.

        Returns: The OaiSettings instance.

        Raises:
            DoesNotExist: The settings doesn't exist.
            ModelError: Internal error during the process.

        """
        try:
            return OaiSettings.objects.get()
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)
