# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AchievementProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('achievementId', models.TextField()),
                ('unlocked', models.BooleanField(default=False)),
                ('progress', models.IntegerField(null=True, blank=True)),
                ('data', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Achievement progress records',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bot', models.BooleanField(default=False)),
                ('team', models.CharField(max_length=1)),
                ('upgradesUsed', models.TextField(default=b'', blank=True)),
                ('starsEarned', models.IntegerField(default=0)),
                ('starsWasted', models.IntegerField(default=0)),
                ('starsUsed', models.IntegerField(default=0)),
                ('kills', models.IntegerField(default=0)),
                ('deaths', models.IntegerField(default=0)),
                ('zoneTags', models.IntegerField(default=0)),
                ('zoneAssists', models.IntegerField(default=0)),
                ('shotsFired', models.IntegerField(default=0)),
                ('shotsHit', models.IntegerField(default=0)),
                ('timeAlive', models.FloatField(default=0)),
                ('timeDead', models.FloatField(default=0)),
                ('killStreak', models.IntegerField(default=0)),
                ('tagStreak', models.IntegerField(default=0)),
                ('aliveStreak', models.FloatField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField()),
                ('finished', models.DateTimeField()),
                ('gameSeconds', models.FloatField(default=0)),
                ('mapHeight', models.IntegerField()),
                ('halfMapWidth', models.IntegerField()),
                ('serverVersion', models.TextField()),
                ('blueTeamName', models.TextField()),
                ('redTeamName', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlayerKills',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=0)),
                ('game', models.ForeignKey(to='trosnoth.GameRecord', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Player kills records',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrosnothServerSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serverName', models.TextField(default='My First Trosnoth Server')),
                ('welcomeText', models.TextField(default='Congratulations! You have successfully installed your Trosnoth server. <a href="admin/trosnoth/trosnothserversettings/1/change/">Click here</a> to configure it.')),
            ],
            options={
                'verbose_name_plural': 'Trosnoth server setting',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrosnothUser',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
                ('nick', models.TextField(unique=True)),
                ('lastSeen', models.DateTimeField(null=True, blank=True)),
                ('oldPasswordHash', models.BinaryField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='playerkills',
            name='killee',
            field=models.ForeignKey(related_name='+', to='trosnoth.TrosnothUser', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='playerkills',
            name='killer',
            field=models.ForeignKey(related_name='+', to='trosnoth.TrosnothUser', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='game',
            field=models.ForeignKey(to='trosnoth.GameRecord', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='user',
            field=models.ForeignKey(to='trosnoth.TrosnothUser', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='achievementprogress',
            name='user',
            field=models.ForeignKey(to='trosnoth.TrosnothUser', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
