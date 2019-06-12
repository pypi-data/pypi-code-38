# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0009_auto_20170205_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='trosnothserversettings',
            name='autoStartCountDown',
            field=models.IntegerField(default=30,
                verbose_name=b'Automatically start new game after (seconds, negative to disable)'),
        ),
    ]
