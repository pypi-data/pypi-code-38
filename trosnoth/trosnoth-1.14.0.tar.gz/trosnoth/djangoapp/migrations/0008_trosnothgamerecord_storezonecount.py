# -*- coding: utf-8 -*-


from django.db import migrations, models


def calculate_map_size(apps, schema_editor):
    GameRecord = apps.get_registered_model('trosnoth', 'GameRecord')
    for record in GameRecord.objects.all():
        halfCount = record.mapHeight * record.halfMapWidth + (
            (record.mapHeight + 1) * (record.halfMapWidth // 2))
        if record.halfMapWidth % 2 == 0:
            midCount = record.mapHeight + 2
        else:
            midCount = record.mapHeight + 1
        record.zoneCount = 2 * halfCount + midCount
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0007_trosnothserversettings_allowremotegameregistration'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamerecord',
            name='zoneCount',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),

        migrations.RunPython(calculate_map_size),

        migrations.RemoveField(
            model_name='gamerecord',
            name='halfMapWidth',
        ),
        migrations.RemoveField(
            model_name='gamerecord',
            name='mapHeight',
        ),

    ]
