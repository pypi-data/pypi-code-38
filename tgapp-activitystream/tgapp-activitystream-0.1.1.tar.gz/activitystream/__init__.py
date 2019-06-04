# -*- coding: utf-8 -*-
"""The activitystream package"""

from tg.configuration import milestones
from activitystream.model import import_models
from activitystream.lib.managers import ActionManager, am


def plugme(app_config, options):
    milestones.config_ready.register(import_models)
    return dict(appid='activitystream', global_helpers=False)
