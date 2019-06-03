""" Contact messages models
"""
from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions


class ContactMessage(Document):
    """Represents a message sent via the Contact form"""
    name = fields.StringField(max_length=100)
    email = fields.EmailField()
    content = fields.StringField()

    @staticmethod
    def get_by_id(message_id):
        """ Get a message using its primary key

        Args:
            message_id: 

        Returns:
        """
        try:
            return ContactMessage.objects().get(pk=str(message_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)

    @staticmethod
    def get_all():
        """ Get all messages

        Returns:
        """
        return ContactMessage.objects.all()
