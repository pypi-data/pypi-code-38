# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='time', db_index=True)),
                ('message', models.CharField(max_length=128, verbose_name='message', db_index=True)),
            ],
            options={
                'ordering': ('-id',),
                'verbose_name': 'journal entry',
                'verbose_name_plural': 'journal entries',
            },
        ),
        migrations.CreateModel(
            name='ObjectData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='object id', db_index=True)),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
                ('journal', models.ForeignKey(verbose_name='journal entry', to='django_journal.Journal')),
            ],
            options={
                'verbose_name': 'linked object',
            },
        ),
        migrations.CreateModel(
            name='StringData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='content')),
                ('journal', models.ForeignKey(verbose_name='journal entry', to='django_journal.Journal')),
            ],
            options={
                'verbose_name': 'linked text string',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32, verbose_name='name', db_index=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'tag',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(unique=True, verbose_name='content', db_index=True)),
            ],
            options={
                'ordering': ('content',),
            },
        ),
        migrations.AddField(
            model_name='stringdata',
            name='tag',
            field=models.ForeignKey(verbose_name='tag', to='django_journal.Tag'),
        ),
        migrations.AddField(
            model_name='objectdata',
            name='tag',
            field=models.ForeignKey(verbose_name='tag', to='django_journal.Tag'),
        ),
        migrations.AddField(
            model_name='journal',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='tag', to='django_journal.Tag'),
        ),
        migrations.AddField(
            model_name='journal',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='template', to='django_journal.Template'),
        ),
        migrations.AlterUniqueTogether(
            name='stringdata',
            unique_together=set([('journal', 'tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='objectdata',
            unique_together=set([('journal', 'tag')]),
        ),
    ]
