# Generated by Django 2.1.4 on 2019-03-19 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("app_correct", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="a", name="new_null_field", field=models.IntegerField(null=True)
        )
        # migrations.RemoveField(model_name="a", name="new_null_field")
    ]
