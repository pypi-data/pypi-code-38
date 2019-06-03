# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_surveys_index(apps, schema_editor):
    from molo.core.models import Main
    from molo.surveys.models import SurveysIndexPage
    main = Main.objects.all().first()

    if main:
        surveys_index = SurveysIndexPage(title='Surveys', slug='surveys')
        main.add_child(instance=surveys_index)
        surveys_index.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_surveysindexpage'),
    ]

    operations = [
        migrations.RunPython(create_surveys_index),
    ]
