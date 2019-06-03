# Generated by Django 2.0.5 on 2018-06-05 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genomix_workflows', '0005_auto_20180604_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskinstance',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Pending'), (2, 'Complete'), (3, 'Running'), (4, 'Hold'), (5, 'Skip'), (6, 'Failed')], default=None, null=True),
        ),
    ]
