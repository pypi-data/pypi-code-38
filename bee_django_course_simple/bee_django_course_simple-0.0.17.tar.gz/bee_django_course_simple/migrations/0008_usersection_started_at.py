# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-04-21 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bee_django_course_simple', '0007_auto_20190418_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersection',
            name='started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
