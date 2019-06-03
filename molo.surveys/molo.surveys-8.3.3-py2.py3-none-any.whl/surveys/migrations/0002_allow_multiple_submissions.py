# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='molosurveypage',
            name='allow_multiple_submissions_per_user',
            field=models.BooleanField(default=False, help_text=b'Check this to allow users to complete a survey more than once.'),
        ),
    ]
