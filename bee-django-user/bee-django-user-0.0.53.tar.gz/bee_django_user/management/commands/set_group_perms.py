# coding=utf-8
__author__ = 'zhangyue'
import os, datetime, urllib2, json, time
from django.core.management.base import BaseCommand, CommandError
from django.db.models.signals import post_save
from django.db import transaction
from django.contrib.auth.models import User, Group,Permission
from bee_django_user.models import UserProfile, create_user


class Command(BaseCommand):
    help = 'set group permissions'

    permission_list = [
        {
            "group_name": u"管理员",
            "perms": ['can_manage', 'can_change_user_group', 'view_all_users',
                      'view_all_classes']
        },
        {
            "group_name": u"老师",
            "perms": []
        },
        {
            "group_name": u"客服",
            "perms": []
        },
        {
            "group_name": u"助教",
            "perms": ['can_manage', 'view_teach_users',
                      'view_teach_classes']
        },

    ]

    @transaction.atomic
    def handle(self, *args, **options):
        groups = Group.objects.all()

        for group in groups:
            for perm_dict in self.permission_list:
                if group.name == perm_dict["group_name"]:
                    perms = Permission.objects.filter(codename__in=perm_dict["perms"])
                    group.permissions = perms
                    break
