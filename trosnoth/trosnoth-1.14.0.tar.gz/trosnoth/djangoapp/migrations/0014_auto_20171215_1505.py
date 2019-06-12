# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0013_trosnothuser_ownselephant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trosnotharena',
            options={'permissions': (('pause_arena', 'Can pause and resume arenas'), ('enable_arena', 'Can enable and disable arenas'), ('set_arena_level', 'Can control what level an arena is running'))},
        ),
    ]
