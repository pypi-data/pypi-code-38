# -*- coding: utf-8 -*-
from congo.utils.models import get_model
from django.conf import settings
from django.utils.module_loading import import_string

# def get_xxx_model():
#    return get_model('CONGO_XXX_MODEL')

def get_email_sender_model():
    return get_model('CONGO_EMAIL_SENDER_MODEL')

def get_email_recipient_group_model():
    return get_model('CONGO_EMAIL_RECIPIENT_GROUP_MODEL')

def get_sms_recipient_group_model():
    return get_model('CONGO_SMS_RECIPIENT_GROUP_MODEL')

def get_email_recipient_model():
    return get_model('CONGO_EMAIL_RECIPIENT_MODEL')

def get_sms_recipient_model():
    return get_model('CONGO_SMS_RECIPIENT_MODEL')

def get_email_message_model():
    return get_model('CONGO_EMAIL_MESSAGE_MODEL')

def get_sms_message_model():
    return get_model('CONGO_SMS_MESSAGE_MODEL')

def get_email_message_queue_model():
    return get_model('CONGO_EMAIL_MESSAGE_QUEUE_MODEL')

def get_sms_message_queue_model():
    return get_model('CONGO_SMS_MESSAGE_QUEUE_MODEL')

def get_connection(backend = None, fail_silently = False, **kwargs):
    backend_class = import_string(backend or settings.CONGO_SMS_BACKEND)
    return backend_class(fail_silently = fail_silently, **kwargs)

def get_full_email(email, name = None):
    if name:
        return u"\"%s\" <%s>" % (name.replace("\"", "'"), email)
    return email
