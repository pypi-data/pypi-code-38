# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('source', models.FileField(upload_to='reports')),
                ('convert_to', models.CharField(blank=True, choices=[('pdf', 'pdf'), ('doc', 'doc'), ('docx', 'docx'), ('xls', 'xls'), ('xlsx', 'xlsx')], max_length=5, null=True)),
                ('merge_with_tos', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.deletion.CASCADE)),
            ],
        ),
    ]
