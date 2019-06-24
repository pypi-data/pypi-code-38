# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('taglabel', models.CharField(unique=True, max_length=30, verbose_name='Tag', help_text='Maximum 30 characters.')),
                ('tagtype', models.CharField(db_index=True, default='', max_length=255, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Tags',
                'verbose_name': 'Tag',
            },
        ),
        migrations.CreateModel(
            name='TaggedObject',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
                ('tag', models.ForeignKey(to='ievv_tagframework.Tag', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Tagged objects',
                'verbose_name': 'Tagged object',
            },
        ),
    ]
