# -*- coding: utf-8 -*-


from django.db import migrations, models


def create_default_arena(apps, schema_editor):
    TrosnothArena = apps.get_registered_model('trosnoth', 'TrosnothArena')
    arena = TrosnothArena(
        name='Main arena',
    )
    arena.save()


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0011_gameplayer_zonescore'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrosnothArena',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(default='New arena')),
                ('enabled', models.BooleanField(default=True)),
                ('autoStartCountDown', models.IntegerField(default=30, verbose_name='Automatically start new game after (seconds, negative to disable)')),
                ('gamePort', models.IntegerField(default=6789, unique=True)),
            ],
        ),

        migrations.RunPython(create_default_arena),
    ]
