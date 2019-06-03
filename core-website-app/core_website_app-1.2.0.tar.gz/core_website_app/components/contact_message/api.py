"""contact message API
"""
import logging
from core_main_app.commons import exceptions
from core_website_app.components.contact_message.models import ContactMessage

logger = logging.getLogger("core_website_app.components.contact_message.api")


def get_all():
    """
        List all messages
        :return:
    """
    return ContactMessage.get_all()


def get_count():
    """ Count number of contact messages currently in the database.

    Returns:
        int: number of contact messages
    """
    return len(get_all())


def get(message_id):
    """
        Get a message
        :param message_id:
        :return:
    """
    try:
        return ContactMessage.get_by_id(message_id)
    except Exception as e:
        logger.error(e.message)
        raise exceptions.ApiError('No message could be found with the given id.')


def upsert(contact_message):
    """ Insert or update a given message

        :param contact_message:
        :return: message's pk
    """
    try:
        # save method return self
        return contact_message.save()
    except Exception as e:
        logger.error(e.message)
        raise exceptions.ApiError('Save message failed')


def delete(contact_message):
    """
        Delete a message
        :param contact_message:
        :return:
    """
    try:
        contact_message.delete()
    except Exception as e:
        logger.error(e.message)
        raise exceptions.ApiError("Impossible to delete contact message.")
