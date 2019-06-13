# -*- coding: utf-8 -*-

from django.db import models
from django.apps import apps
from django.db import models
from django.contrib.auth import get_user_model
from simple_history import register, models as sh_models
from simple_history.models import _default_get_user
from django.conf import settings

DEFAULT_AUDIT_TRACKED_APPS = ('quartet_masterdata',
                              'quartet_output',
                              'quartet_capture',
                              'serialbox',
                              'list_based_flavorpack',
                              'random_flavorpack',
                              'quartet_templates',)

DEFAULT_EXCLUDE_MODELS_TRACKING = ('quartet_capture.models.Task',
                                   'quartet_capture.models.TaskHistory',
                                   'quartet_capture.models.TaskMessage',)

tracked_app_list = getattr(settings,
                           'AUDIT_TRACKED_APPS',
                           DEFAULT_AUDIT_TRACKED_APPS)

exclude_models = getattr(settings,
                         'EXCLUDE_MODELS_TRACKING',
                         DEFAULT_EXCLUDE_MODELS_TRACKING)


def _history_user_getter(historical_instance):
    User = get_user_model()
    try:
        return User.objects.get(username=historical_instance.history_user_id)
    except User.DoesNotExist:
        return None

def _history_user_setter(historical_instance, user):
    if user is not None:
        historical_instance.history_user_id = user.username

class HistoricalRecords(sh_models.HistoricalRecords):

    def __init__(self, verbose_name=None, bases=(models.Model,),
                 user_related_name="+", table_name=None, inherit=False,
                 excluded_fields=None, history_id_field=None,
                 history_change_reason_field=None, user_model=None,
                 get_user=_default_get_user, cascade_delete_history=False,
                 custom_model_name=None, app=None, history_user_id_field=None,
                 history_user_getter=_history_user_getter,
                 history_user_setter=_history_user_setter, related_name=None,
                 use_base_model_db=False):
        history_user_id_field = models.CharField(null=True, verbose_name='username',
                                                 max_length=200)
        super().__init__(verbose_name, bases, user_related_name, table_name,
                         inherit, excluded_fields, history_id_field,
                         history_change_reason_field, user_model, get_user,
                         cascade_delete_history, custom_model_name, app,
                         history_user_id_field, history_user_getter,
                         history_user_setter, related_name, use_base_model_db)


def register_models(app_list, exclude_models):
    '''
    Registers all models for given app name.
    Ties the model to quartet_trail rather than
    the original app for table creation. No db/model
    changes are done on the original app.
    '''
    for app_name in app_list:
        app = apps.get_app_config(app_name)
        for model in list(app.models.values()):
            if get_model_fullname(model) not in exclude_models:
                register(model, app=__package__,
                         records_class=HistoricalRecords)


def get_model_fullname(model):
    '''
    gets the full name of the model.
    '''
    return model.__module__ + '.' + model.__qualname__


# register all the models. You will need to run makemigrations/migrate if the
# list changes.
register_models(tracked_app_list, exclude_models)
