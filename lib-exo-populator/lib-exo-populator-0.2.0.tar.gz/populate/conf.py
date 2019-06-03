# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # NOQA

logger = logging.getLogger(__name__)


class PopulateConfig(AppConf):
    APP_NAME = 'populate'

    ALLOWED_DATA_FOLDERS = []

    ALLOWED_POPULATE_ENTITIES = []

    REQUIRED_SEQUENCE_RESET_MODELS = []
