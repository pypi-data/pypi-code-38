# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from django.db import models


class MezzanineSyncPages(models.Model):
    """This is a fake model, just to trick Django's admin to
       have an easy changelist view"""

    class Meta:
        managed = False
        app_label = 'mezzanine_sync_pages'
        verbose_name = 'Sync Pages'
        verbose_name_plural = 'Sync Pages'
