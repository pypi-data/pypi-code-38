"""Composer models
"""
from django.db import models
from core_main_app.permissions.utils import get_formatted_name
from core_composer_app.permissions import rights


class Composer(models.Model):
    class Meta:
        verbose_name = 'core_composer_app'
        default_permissions = ()
        permissions = (
            (rights.composer_access, get_formatted_name(rights.composer_access)),
            (rights.composer_save_template, get_formatted_name(rights.composer_save_template)),
            (rights.composer_save_type, get_formatted_name(rights.composer_save_type)),
        )
