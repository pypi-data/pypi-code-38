# Generated by Django 2.0.13 on 2019-05-16 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audittrails', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audittrail',
            name='applicatie_id',
            field=models.CharField(blank=True, help_text='Unieke identificatie van de applicatie, binnen de organisatie', max_length=100),
        ),
        migrations.AddField(
            model_name='audittrail',
            name='applicatie_weergave',
            field=models.CharField(blank=True, help_text='Vriendelijke naam van de applicatie', max_length=200),
        ),
    ]
