# Generated by Django 2.1.2 on 2018-10-09 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0028_auto_20180922_0511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='override_vote',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
