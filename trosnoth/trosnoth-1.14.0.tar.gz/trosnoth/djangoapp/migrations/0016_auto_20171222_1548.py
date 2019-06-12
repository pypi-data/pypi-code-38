# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0015_remove_trosnothserversettings_autostartcountdown'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trosnotharena',
            options={'permissions': (('pause_arena', 'Can pause and resume arenas'), ('enable_arena', 'Can enable and disable arenas'), ('set_arena_level', 'Can control what level an arena is running'), ('restart_arena', 'Can restart an arena process'), ('change_team_abilities', 'Can enable/disable shooting and zone caps for teams.'))},
        ),
    ]
