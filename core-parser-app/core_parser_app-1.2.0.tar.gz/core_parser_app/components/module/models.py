"""Module models
"""
from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors
from core_main_app.commons import exceptions


class Module(Document):
    """Represents a module, that will replace the default rendering of an element"""
    name = fields.StringField(unique=True)
    url = fields.StringField(unique=True)
    view = fields.StringField()
    multiple = fields.BooleanField(default=False)

    @staticmethod
    def get_by_id(module_id):
        """Returns a module by its id

        Args:
            module_id:

        Returns:

        """
        try:
            return Module.objects().get(pk=str(module_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_by_url(module_url):
        """Returns a module by its id

        Args:
            module_url:

        Returns:

        """
        try:
            return Module.objects().get(url=module_url)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as e:
            raise exceptions.ModelError(e.message)

    @staticmethod
    def get_all():
        """Returns all modules

        Returns:

        """
        return Module.objects.all()

    @staticmethod
    def get_all_urls():
        """Returns all modules urls

        Returns:

        """
        return Module.objects.all().values_list('url')

    @staticmethod
    def delete_all():
        """Deletes all modules

        Returns:

        """
        Module.objects.all().delete()
