# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0008_trosnothgamerecord_storezonecount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameplayer',
            old_name='starsEarned',
            new_name='coinsEarned',
        ),
        migrations.RenameField(
            model_name='gameplayer',
            old_name='starsUsed',
            new_name='coinsUsed',
        ),
        migrations.RenameField(
            model_name='gameplayer',
            old_name='starsWasted',
            new_name='coinsWasted',
        ),
    ]
