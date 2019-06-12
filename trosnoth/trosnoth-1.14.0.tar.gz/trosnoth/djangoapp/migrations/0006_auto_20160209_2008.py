# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0005_auto_20160208_2340'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpgradesUsedInGameRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upgrade', models.CharField(max_length=1)),
                ('count', models.IntegerField(default=0)),
                ('gamePlayer', models.ForeignKey(to='trosnoth.GamePlayer', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='upgradesusedingamerecord',
            unique_together={('gamePlayer', 'upgrade')},
        ),
        migrations.RemoveField(
            model_name='gameplayer',
            name='upgradesUsed',
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='botName',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gamerecord',
            name='replayName',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gamerecord',
            name='winningTeam',
            field=models.CharField(max_length=1, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gameplayer',
            name='team',
            field=models.CharField(max_length=1, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gameplayer',
            name='user',
            field=models.ForeignKey(to='trosnoth.TrosnothUser', null=True, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='playerkills',
            name='killee',
            field=models.ForeignKey(related_name='+', to='trosnoth.GamePlayer', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='playerkills',
            name='killer',
            field=models.ForeignKey(related_name='+', to='trosnoth.GamePlayer', null=True, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='playerkills',
            unique_together=set([('killer', 'killee')]),
        ),
        migrations.RemoveField(
            model_name='playerkills',
            name='game',
        ),
    ]
