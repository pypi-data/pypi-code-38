# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-14 18:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0015_question_contains_personal_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='override_vote',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
