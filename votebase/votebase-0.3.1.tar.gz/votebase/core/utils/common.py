import os
import re

from django.apps import apps
from django.conf import settings
from django.db.models.deletion import Collector
from django.db.models.fields.files import FileField
from django.db.models.fields.related import ForeignKey
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from python_pragmatic.strings import generate_hash


def generate_slug_for_user(first_name='', last_name=''):
    # get swappable profile model
    from votebase.core.accounts.helpers import get_profile_model
    profile_model = get_profile_model()

    first_name = first_name or ''
    last_name = last_name or ''
    slug = slugify(first_name + ' ' + last_name)
    new_slug = slug
    suffix = 1

    while profile_model.objects.filter(slug=new_slug).exists():
        new_slug = slug + generate_token()
        suffix += 1

    return new_slug


def generate_token():
    return generate_hash()


def generate_tiers():
    result = list()
    tiers = settings.VOTEHUB_PAYMENT_TIERS
    for tier in tiers:
        result.append(
            (tier, render_to_string('backend/payments/tier.html', {
                'price': tier,
                'voters': tiers[tier],
                'currency': settings.VOTEHUB_CURRENCY_SYMBOL,
            })),
        )
    return result


def decode(string):
    response = dict()
    for part in string.split('&'):
        parts = part.split('=')
        response[parts[0]] = parts[1]

    return response


def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


def remove_files(dir, filename, is_prefix=False):
    if filename == '':
        return

    try:
        pattern = filename + '*' if is_prefix else filename
        purge(dir, pattern)
    except IOError:
        pass


def duplicate(obj, value=None, field=None, duplicate_order=None):
    """
    Duplicate all related objects of obj setting
    field to value. If one of the duplicate
    objects has an FK to another duplicate object
    update that as well. Return the duplicate copy
    of obj.
    duplicate_order is a list of models which specify how
    the duplicate objects are saved. For complex objects
    this can matter. Check to save if objects are being
    saved correctly and if not just pass in related objects
    in the order that they should be saved.
    """
    collector = Collector({})
    collector.collect([obj])
    collector.sort()
    related_models = collector.data.keys()
    data_snapshot = {}
    for key in collector.data.keys():
        data_snapshot.update({ key: dict(zip([item.pk for item in collector.data[key]], [item for item in collector.data[key]])) })
    root_obj = None

    # Sometimes it's good enough just to save in reverse deletion order.
    if duplicate_order is None:
        duplicate_order = reversed(related_models)

    for model in duplicate_order:
        # Find all FKs on model that point to a related_model.
        fks = []
        for f in model._meta.fields:
            if isinstance(f, ForeignKey) and f.rel.to in related_models:
                fks.append(f)
                # Replace each `sub_obj` with a duplicate.
        if model not in collector.data:
            continue
        sub_objects = collector.data[model]
        for obj in sub_objects:
            for fk in fks:
                fk_value = getattr(obj, "%s_id" % fk.name)
                # If this FK has been duplicated then point to the duplicate.
                fk_rel_to = data_snapshot[fk.rel.to]
                if fk_value in fk_rel_to:
                    dupe_obj = fk_rel_to[fk_value]
                    setattr(obj, fk.name, dupe_obj)
                    # Duplicate files related to image fields and file fields
                for mfield in obj._meta.fields:
                    if isinstance(mfield, FileField):
                        field_instance = mfield.value_from_object(obj)
                        if field_instance:
                            field_instance.save(field_instance.name, field_instance.file, save=False)
                            # Duplicate the object and save it.
            obj.id = None
            if field is not None:
                setattr(obj, field, value)
            obj.save()
            if root_obj is None:
                root_obj = obj
    return root_obj
