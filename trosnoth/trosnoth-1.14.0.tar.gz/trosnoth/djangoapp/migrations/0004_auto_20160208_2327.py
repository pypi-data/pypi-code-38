# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0003_auto_20160207_0026'),
    ]

    operations = [
        migrations.AddField(
            model_name='trosnothserversettings',
            name='iceEnabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trosnothserversettings',
            name='iceHost',
            field=models.TextField(default='127.0.0.1'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trosnothserversettings',
            name='icePort',
            field=models.IntegerField(default=6502),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trosnothserversettings',
            name='iceProxyStringOverride',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trosnothserversettings',
            name='iceSecret',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
