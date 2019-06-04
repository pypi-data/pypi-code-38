# Generated by Django 2.1.8 on 2019-04-19 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0003_auto_20190418_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_guid', models.CharField(max_length=20)),
                ('event', models.CharField(max_length=32)),
                ('processed_flag', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
