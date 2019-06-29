from django.contrib.auth.models import Group

from ..constants import PII, PII_VIEW
from ..pii_updater import PiiUpdater
from .generic import remove_permissions_by_model, remove_historical_group_permissions


def get_pii_models(extra_pii_models=None):
    pii = PiiUpdater(extra_pii_models=extra_pii_models)
    return pii.pii_models


def remove_pii_permissions_from_group(group, extra_pii_models=None):
    pii = PiiUpdater(extra_pii_models=extra_pii_models)
    for model in pii.pii_models:
        remove_permissions_by_model(group, model)


def update_pii_group_permissions(extra_pii_models=None):
    group_name = PII
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    updater = PiiUpdater(extra_pii_models=extra_pii_models)
    updater.add_pii_permissions(group)
    remove_historical_group_permissions(group)


def update_pii_view_group_permissions(extra_pii_models=None):
    group_name = PII_VIEW
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    updater = PiiUpdater(extra_pii_models=extra_pii_models)
    updater.add_pii_permissions(group, view_only=True)
    remove_historical_group_permissions(group)
