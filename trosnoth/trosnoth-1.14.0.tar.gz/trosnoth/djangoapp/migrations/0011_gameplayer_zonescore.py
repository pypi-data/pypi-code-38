# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0010_trosnothserversettings_autostartcountdown'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameplayer',
            name='zoneScore',
            field=models.FloatField(default=0),
        ),
    ]
