"""Explore Keyword models
"""
from django.db import models
from core_main_app.permissions.utils import get_formatted_name
from core_explore_keyword_app.permissions import rights


class ExploreKeyword(models.Model):
    class Meta:
        verbose_name = 'core_explore_keyword_app'
        default_permissions = ()
        permissions = (
            (rights.explore_keyword_access, get_formatted_name(rights.explore_keyword_access)),
        )
