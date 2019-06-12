# -*- coding: utf-8 -*-


import datetime
import json
import os

from django.db import migrations

from trosnoth import data




def migrate_old_user_info(apps, schema_editor):
    User = apps.get_registered_model('auth', 'User')
    TrosnothUser = apps.get_model('trosnoth', 'TrosnothUser')
    AchievementProgress = apps.get_model('trosnoth', 'AchievementProgress')

    dataPath = data.getPath(data.user, 'authserver')
    path = os.path.join(dataPath, 'accounts')
    if not os.path.isdir(path):
        return

    for username in os.listdir(path):
        userpath = os.path.join(path, username)
        user = User(username=username, email='')
        user.save()

        with open(os.path.join(userpath, 'nick'), 'rb') as f:
            nick = f.read().decode()
        with open(os.path.join(userpath, 'stats'), 'rU') as f:
            stats = json.load(f)
        with open(os.path.join(userpath, 'password'), 'rb') as f:
            passwordHash = f.read()
        lastSeen = datetime.datetime.fromtimestamp(stats.get('lastSeen'))
        trosnothUser = TrosnothUser(
            user=user, nick=nick, lastSeen=lastSeen,
            oldPasswordHash=passwordHash)
        trosnothUser.save()

        achievementPath = os.path.join(userpath, 'achievements')
        if os.path.exists(achievementPath):
            with open(os.path.join(userpath, 'achievements'), 'rU') as f:
                achievements = json.load(f)

            for achId, achData in achievements.items():
                progress = None
                extra = ''
                if 'progress' in achData:
                    if isinstance(achData['progress'], int):
                        progress = achData['progress']
                    else:
                        extra = json.dumps(achData['progress'])

                record = AchievementProgress(
                    user=trosnothUser, achievementId=achId,
                    unlocked=achData.get('unlocked', False),
                    progress=progress, data=extra)
                record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_old_user_info),
    ]
