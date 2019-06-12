# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0002_auto_20160206_1103'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='achievementprogress',
            unique_together=set([('user', 'achievementId')]),
        ),
        migrations.AlterUniqueTogether(
            name='gameplayer',
            unique_together=set([('game', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='playerkills',
            unique_together=set([('game', 'killer', 'killee')]),
        ),
    ]
