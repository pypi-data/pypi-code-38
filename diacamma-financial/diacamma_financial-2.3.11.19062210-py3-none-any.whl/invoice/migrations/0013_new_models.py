# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils import translation
from django.conf import settings

from lucterios.CORE.models import PrintModel


def print_values(*args):
    translation.activate(settings.LANGUAGE_CODE)
    PrintModel().load_model('diacamma.invoice', "Article_0002", is_default=False)
    PrintModel().load_model('diacamma.invoice', "Article_0003", is_default=False)


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0012_print_article'),
    ]

    operations = [
        migrations.RunPython(print_values),
    ]
