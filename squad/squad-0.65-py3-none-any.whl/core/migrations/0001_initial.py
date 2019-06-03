# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-25 11:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.FloatField()),
                ('measurements', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='core.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Suite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suites', to='core.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.BooleanField()),
                ('suite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Suite')),
            ],
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('build', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_runs', to='core.Build')),
                ('environment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_runs', to='core.Environment')),
            ],
        ),
        migrations.AddField(
            model_name='test',
            name='test_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='core.TestRun'),
        ),
        migrations.AddField(
            model_name='environment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='environments', to='core.Project'),
        ),
        migrations.AddField(
            model_name='build',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='builds', to='core.Project'),
        ),
        migrations.AddField(
            model_name='metric',
            name='suite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Suite'),
        ),
        migrations.AddField(
            model_name='metric',
            name='test_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='core.TestRun'),
        ),
        migrations.AlterUniqueTogether(
            name='suite',
            unique_together=set([('project', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('group', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='environment',
            unique_together=set([('project', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='build',
            unique_together=set([('project', 'version')]),
        ),
    ]
