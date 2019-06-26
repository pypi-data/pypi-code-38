import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_vox", "0004_activity_fields"),
    ]

    operations = [
        migrations.DeleteModel("InboxItem"),
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=True,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=512, verbose_name="name"),
                ),
                ("summary", models.TextField(blank=True)),
                (
                    "type",
                    models.CharField(
                        db_index=True, max_length=512, verbose_name="type"
                    ),
                ),
                (
                    "actor_id",
                    models.CharField(
                        db_index=True, max_length=2048, verbose_name="actor id"
                    ),
                ),
                ("actor_json", models.TextField(blank=True)),
                (
                    "target_id",
                    models.CharField(
                        db_index=True, max_length=2048, verbose_name="target id"
                    ),
                ),
                ("target_json", models.TextField(blank=True)),
                (
                    "object_id",
                    models.CharField(
                        db_index=True, max_length=2048, verbose_name="object id"
                    ),
                ),
                ("object_json", models.TextField(blank=True)),
                (
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="timestamp"
                    ),
                ),
            ],
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
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="django_vox.Activity",
                        verbose_name="activity",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="owner",
                    ),
                ),
                ("read", models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="inboxitem", unique_together=set([("owner", "activity")])
        ),
    ]
