# coding=utf-8
__author__ = 'zhangyue'
import os, datetime, urllib2, json, time
from django.core.management.base import BaseCommand, CommandError
from django.db.models.signals import post_save
from django.db import transaction
from django.contrib.auth.models import User, Group
from bee_django_user.models import UserProfile, create_user


class Command(BaseCommand):
    help = 'create superuser [userename] [passowrd]'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            from bee_django_crm.models import PreUser
        except:
            return
        username = options["username"]
        password = options["password"]
        mobile = int(time.time())

        preuser = PreUser()
        preuser.nickname = username
        preuser.name = username
        preuser.mobile = mobile
        preuser.save()

        user = User.objects.create_user(username=username, password=password)
        user.first_name = username
        user.is_staff = True
        user.is_superuser = True
        user.save()

        post_save.disconnect(create_user, sender=UserProfile)
        user_profile = UserProfile()
        user_profile.preuser = preuser
        user_profile.user = user
        user_profile.save()

        groups = ["超级管理员", "管理员", "老师", "客服", "助教", '学生']
        for group_name in groups:
            g = Group.objects.filter(name=group_name)
            if g.count() == 0:
                group = Group(name=group_name)
                group.save()

        try:
            group = Group.objects.get(name='超级管理员')
            user.groups.add(group)
        except Exception as e:
            print(e)
