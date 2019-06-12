# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0018_auto_20180504_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.TextField(default='Tournament')),
                ('showOnHomePage', models.BooleanField(default=True)),
                ('matches', models.ManyToManyField(blank=True, to='trosnoth.GameRecord')),
            ],
        ),
        migrations.AddField(
            model_name='trosnotharena',
            name='currentTournament',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.SET_NULL, null=True, to='trosnoth.Tournament'),
        ),
    ]
