# -*- coding:utf-8 -*-

import six
import re
from django.db import models
from django.contrib.auth import get_user_model


def update_model(obj, info, fields=None):
    """
    Updates an object of Django model instance with given info, optionally limited to certain fields only.
    :param obj: a Django model instance
    :param info: a dict
    :param fields: optional, only update these fields.
    :return: updated obj (saved)
    """
    update_fields = set()
    for key, val in six.iteritems(info):
        if fields is None or key in fields:
            setattr(obj, key, val)
        update_fields.add(key)

    if update_fields:
        obj.save(update_fields=list(update_fields))

    return obj


def get_model_class(model):
    """
    Deduct the model class from given input.
    :param model: may be one of the following format:
        * a '<app>.<model>' string
        * 'AUTH_USER_MODEL'
        * a django model instance,
        * a model class
    :return: django model class
    """
    # Special cases
    if model is None:
        return None

    if model == 'AUTH_USER_MODEL':
        return get_user_model()

    from django.contrib.contenttypes.models import ContentType
    if isinstance(model, six.string_types):
        if '.' in model:
            app_label, model_name = model.split('.')
            model_name = model_name.lower()
            return ContentType.objects.get(app_label=app_label, model=model_name).model_class()
        else:
            model_name = model.lower()
            return ContentType.objects.get(model=model_name).model_class()
    elif isinstance(model, six.class_types) and issubclass(model, models.Model):
        return model
    elif isinstance(model, models.Model):
        return model.__class__
    else:
        raise ValueError(u"Not a valid model representation: {}".format(repr(model)))


def get_model_instance(model_class, instance_or_id, raise_on_error=True):
    """
    Get model's instance by id.
    :param model_class:
    :param instance_or_id:
    :param raise_on_error: if False, return None instead of raise.
    :return:
    """
    if isinstance(instance_or_id, model_class):
        return instance_or_id
    else:
        try:
            return model_class.objects.get(pk=instance_or_id)
        except Exception as e:
            if raise_on_error:
                raise
            else:
                return None


def get_model_instances(model_class, instances_or_ids, sep=',', ignore_invalid=True, raise_on_error=True):
    """
    Get model instances by ids.
    :param model_class:
    :param instances_or_ids:
    :param sep:
    :param ignore_invalid:
    :param raise_on_error: only effective when ignore_invalid is False. if True, raise error; else add None to results.
    :return:
    """
    results = []
    if isinstance(instances_or_ids, six.string_types):
        instances_or_ids = instances_or_ids.split(sep)

    for item in instances_or_ids:
        if isinstance(item, model_class):
            results.append(item)
        else:
            try:
                results.append(model_class.objects.get(pk=item))
            except Exception as e:
                if not ignore_invalid:
                    if raise_on_error:
                        raise e
                    else:
                        results.append(None)

    return results


def get_model_field(model, field, raise_on_error=True):
    try:
        fields = re.split(r'__', field)
        cur = model
        for f in fields:
            cur = getattr(cur, f)
        return cur
    except Exception as e:
        if not raise_on_error:
            return None
        raise


def model_has_field(model, field, strict=False):
    if '__' in field:
        fields = re.split(r'__', field)
        cur = model
        for f in fields:
            if strict and not isinstance(cur, models.Model):
                return False

            if cur is None:  # a null FK etc
                return True
            elif not hasattr(cur, f):
                return False

            cur = getattr(cur, f)
        return True
    else:
        return hasattr(model, field)
