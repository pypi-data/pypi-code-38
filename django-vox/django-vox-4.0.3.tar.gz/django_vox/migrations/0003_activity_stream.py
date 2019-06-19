# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import django_vox.registry


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("django_vox", "0002_attachments"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notification", old_name="target_model", new_name="target_type"
        ),
        migrations.RenameField(
            model_name="notification", old_name="source_model", new_name="actor_type"
        ),
        migrations.RenameField(
            model_name="notification", old_name="content_type", new_name="object_type"
        ),
        migrations.AlterField(
            model_name="notification",
            name="actor_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                limit_choices_to=django_vox.registry.channel_type_limit,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="contenttypes.ContentType",
                verbose_name="actor model",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="target_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                limit_choices_to=django_vox.registry.channel_type_limit,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="contenttypes.ContentType",
                verbose_name="target model",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="object_type",
            field=models.ForeignKey(
                limit_choices_to=django_vox.registry.channel_type_limit,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.ContentType",
                verbose_name="object type",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="activity_type",
            field=models.URLField(
                blank=True,
                default="",
                help_text="Full URL for activity type (i.e. "
                "https://www.w3.org/ns/activitystreams#Object)",
                verbose_name="activity type",
            ),
        ),
        migrations.AlterField(
            model_name="templateattachment",
            name="template",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attachments",
                to="django_vox.Template",
                verbose_name="template",
            ),
        ),
        migrations.CreateModel(
            name="InboxItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="timestamp"
                    ),
                ),
                ("json", models.TextField()),
                (
                    "owner_id",
                    models.CharField(
                        verbose_name="owner id", db_index=True, max_length=2048
                    ),
                ),
                (
                    "owner_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="contenttypes.ContentType",
                        verbose_name="owner type",
                    ),
                ),
                (
                    "actor_id",
                    models.CharField(
                        verbose_name="actor id", db_index=True, max_length=2048
                    ),
                ),
                (
                    "object_id",
                    models.CharField(
                        verbose_name="object id", db_index=True, max_length=2048
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        verbose_name="type", db_index=True, max_length=512
                    ),
                ),
            ],
        ),
    ]
