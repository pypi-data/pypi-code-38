# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_named_menus', '0002_auto_20150227_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cmsnamedmenu',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, populate_from='name', editable=False),
        ),
    ]
