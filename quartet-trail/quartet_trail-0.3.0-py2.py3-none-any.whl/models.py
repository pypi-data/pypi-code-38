# -*- coding: utf-8 -*-

from django.db import models
from django.apps import apps
from model_utils.models import TimeStampedModel
from simple_history import register
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
                register(model, app=__package__)


def get_model_fullname(model):
    '''
    gets the full name of the model.
    '''
    return model.__module__ + '.' + model.__qualname__


# register all the models. You will need to run makemigrations/migrate if the
# list changes.
register_models(tracked_app_list, exclude_models)
