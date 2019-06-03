# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-06 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import i18nfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0009_auto_20171004_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='help_text',
            field=i18nfield.fields.I18nCharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='target',
            field=models.CharField(default='submission', max_length=10),
        ),
        migrations.AlterField(
            model_name='question',
            name='variant',
            field=models.CharField(default='string', max_length=15),
        ),
    ]
