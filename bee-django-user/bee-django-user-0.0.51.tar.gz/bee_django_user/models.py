# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime, pytz
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps
from django.conf import settings
from bee_django_crm.models import PreUser
from .signals import update_user_expire_signal, create_user_signal

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')


# Create your models here.


# def get_crm_preuser():
#     if settings.CRM_PREUSER:
#         return settings.CRM_PREUSER
#     return None


# 用户，扩展的user
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    student_id = models.IntegerField(verbose_name='学号', unique=True, null=True)  # 拼接成用户名
    sn = models.IntegerField(verbose_name='统一缦客号', unique=True, null=True, help_text='只需填写数字')  # 各项目统一使用
    room_id = models.CharField(max_length=180, verbose_name='习琴室ID', null=True, blank=True)
    user_class = models.ForeignKey('bee_django_user.UserClass', verbose_name='用户班级', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='开课日期')
    expire_date = models.DateTimeField(null=True, blank=True, verbose_name='结课日期')
    preuser = models.OneToOneField(settings.CRM_PREUSER, verbose_name='crm用户', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = ProcessedImageField(null=True, blank=True, verbose_name='头像', upload_to='avatars',
                                 processors=[ResizeToFill(50, 50)],
                                 format='JPEG',
                                 default='avatars/default.jpg')
    is_pause = models.BooleanField(default=False, blank=True, verbose_name='暂停')

    class Meta:
        db_table = 'bee_django_user_profile'
        app_label = 'bee_django_user'
        ordering = ['-created_at']
        permissions = (
            ('can_manage', '可以访问后台管理'),
            ('can_change_user_group', '可以修改用户组'),
            ('can_change_user_sn', '可以修改sn号'),
            ('reset_user_password', '可以重置用户密码'),
            ('view_all_users', '可以查看所有用户'),
            ('view_manage_users', '可以查看管理的用户'),
            ('view_teach_users', '可以查看教的用户'),
        )

    def __str__(self):
        return self.user.username

    def has_group(self, group_name):
        group_name_list = []
        for group in self.user.groups.all():
            group_name_list.append(group.name)
        print(group_name_list)
        if group_name in group_name_list:
            return True
        return False

    @classmethod
    def fix_cc_room_id(cls):
        try:
            from bee_django_course.cc import create_room
            for e in cls.objects.all():
                if not e.room_id:
                    room_id = create_room(e.preuser.name + '的直播间')
                    if room_id:
                        e.room_id = room_id
                        e.save()
        except:
            return

    @classmethod
    def init_sn(cls, start=0):

        user_profile_list = cls.objects.all().order_by('student_id')
        for user_profile in user_profile_list:
            user_profile.sn = UserSN.get_next_sn(start)
            user_profile.save()
            start += 1
        return

    def get_sn(self):
        if self.sn:
            return "MK" + self.sn.__str__()
        return ''


class UserSN(models.Model):
    start = models.IntegerField(verbose_name='起', unique=True)
    end = models.IntegerField(verbose_name='止', unique=True)
    is_used = models.BooleanField(verbose_name='是否正在使用', default=False)

    def __str__(self):
        return self.start.__str__() + '-' + self.end.__str__()

    class Meta:
        db_table = 'bee_django_user_sn'
        app_label = 'bee_django_user'
        ordering = ['start']

    @classmethod
    def get_next_sn(cls, sn=0):
        if sn == None:
            return None
        new_sn = sn + 1
        sn_list = cls.objects.filter(is_used=True).order_by('start')
        if not sn_list.exists():
            return None
        i = sn_list.first()

        if new_sn <= i.start:
            new_sn = i.start
        elif i.start < new_sn < i.end:
            pass
        elif new_sn == i.end:
            i.is_used = False
            i.save()
        else:
            return None
        return new_sn


@receiver(post_save, sender=UserProfile)
def create_user(sender, **kwargs):
    user_pofile = kwargs['instance']
    if kwargs['created']:
        user = User.objects.create_user(username=settings.USER_EX_USERNAME + user_pofile.student_id.__str__(),
                                        password=settings.USER_DEFAULT_PASSWORD)
        user.first_name = user_pofile.preuser.name
        user.save()
        # 发送信号
        create_user_signal.send(sender=User, user=user)
        #
        user_pofile.user = user
        user_pofile.save()
        try:
            group = Group.objects.get(name='学生')
            user.groups.add(group)
        except Exception as e:
            print(e)

            # user_profile_list = UserProfile.objects.all().order_by("-student_id")
            # if user_profile_list.count() >= 1:
            #     max_student_id = user_profile_list.first().student_id
            # else:
            #     max_student_id = 0

    return


# @receiver(post_save, sender=User)
# def create_user_profile(sender, **kwargs):
#     user = kwargs['instance']
#     if kwargs['created']:
#         user_profile_list = UserProfile.objects.all().order_by("-student_id")
#         if user_profile_list.count() >= 1:
#             max_student_id = user_profile_list.first().student_id
#         else:
#             max_student_id = 0
#         user_profile = UserProfile(user=user)
#         user_profile.student_id = max_student_id + 1
#         user_profile.save()
#     return
# 如果有crm，则创建并关联crm用户
# res = apps.is_installed("bee_django_crm")
# if not res:
#     return
# try:
#     from bee_django_crm.models import PreUser
#     preuser = PreUser(user=user)
#     preuser.save()
# except:
#     return

USER_LEAVE_TYPE_CHOICES = ((1, '请假'), (2, "请假有销假"), (3, '延期'), (4, '提前'))


class UserLeaveRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='leave_user')
    type = models.IntegerField(choices=USER_LEAVE_TYPE_CHOICES, default=1, verbose_name='类型')
    start = models.DateTimeField(null=True, blank=True, verbose_name='开始日期')
    end = models.DateTimeField(null=True, blank=True, verbose_name='结束日期')
    old_expire = models.DateTimeField(blank=True, verbose_name='原结课日期', null=True)
    new_expire = models.DateTimeField(blank=True, verbose_name='新结课日期')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='create_user')
    created_at = models.DateTimeField(auto_now_add=True)
    is_check = models.BooleanField(default=False, verbose_name='通过审核')
    check_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='check_user')
    check_at = models.DateTimeField(null=True)
    info = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        db_table = 'bee_django_user_leave_record'
        app_label = 'bee_django_user'
        ordering = ['-created_at']
        permissions = (
            ('update_type_cancel', "可以销假"),
            ('change_check', '可以审核用户的请假'),
        )

    def __str__(self):
        return self.pk.__str__()

    def get_type(self):
        if not self.type:
            return ""
        for g in USER_LEAVE_TYPE_CHOICES:
            if self.type == g[0]:
                return g[1]
        return ""

    # 审核请假记录后，自动更新用户的结课日期
    def update_user_expire(self):
        if self.is_check == True:
            user = self.user
            user.userprofile.expire_date = self.new_expire
            user.userprofile.save()
        return


# 学生请假状态表
class UserLeaveStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.IntegerField(default=0)  # 1请假中，2正常-请假期未到，3正常-请假期已处理完成
    leave_start = models.DateTimeField(null=True, blank=True, verbose_name='请假开始日期')
    leave_end = models.DateTimeField(null=True, blank=True, verbose_name='请假结束日期')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    record = models.ForeignKey(UserLeaveRecord, null=True)  #

    class Meta:
        db_table = 'bee_django_user_leave_status'
        app_label = 'bee_django_user'
        ordering = ['-created_at']

    def __str__(self):
        return self.user.username + ",status:" + self.status.__str__()

    def update_status(self):
        now = timezone.now()
        # 请假中的学生
        if self.status == 1:
            if self.leave_end <= now:
                self.status = 3
                self.save()
        # 新添加的学生，或未到请假期的学生
        elif self.status in [0, 2]:
            if self.leave_start <= now:
                self.status = 1
                self.save()
            if self.leave_end <= now:
                self.status = 3
                self.save()
        return

    def get_status(self):
        if self.status == 1:
            return '请假中'
        elif self.status == 2:
            return '请假期未到'
        elif self.status == 3:
            return '请假期已处理完成'

        return ''


# 审核请假记录后
# 1.自动更新用户的结课日期
# 2.自动更新到用户状态表
# 3.发送信号，创建一条足迹
@receiver(post_save, sender=UserLeaveRecord)
def update_user_expire(sender, **kwargs):
    record = kwargs['instance']
    if kwargs['created'] == False and record.is_check == True:
        # 自动更新用户的结课日期
        user = record.user
        user.userprofile.expire_date = record.new_expire
        user.userprofile.save()
        # 发送信号
        update_user_expire_signal.send(sender=UserLeaveRecord, leave_record=record)
        # 请假
        if record.type == 1:
            n = UserLeaveStatus()
            n.user = record.user
            n.leave_start = record.start
            n.leave_end = record.end
            n.record = record
            n.save()
            # 更新状态
            n.update_status()
        # 销假
        elif record.type == 2:
            try:
                n = UserLeaveStatus.objects.get(record=record)
            except:
                return
            n.leave_start = record.start
            n.leave_end = record.end
            n.save()
            # 更新状态
            n.update_status()
    return


# 班级
class UserClass(models.Model):
    name = models.CharField(max_length=180, verbose_name='班级名称')
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='助教', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'bee_django_user_class'
        app_label = 'bee_django_user'
        ordering = ['-created_at']
        permissions = (
            ('view_all_classes', '可以查看所有班级'),
            ('view_manage_classes', '可以查看管理的班级'),
            ('view_teach_classes', '可以查看教的班级'),
        )

    def get_students(self):
        user_profile_list = self.userprofile_set.all()
        user_list = User.objects.filter(userprofile__in=user_profile_list)
        return user_list


def get_user_name(self):
    return self.first_name


# 学生列表页根据student_id搜索
def get_user_search_link(self):
    ex_link = "/user/list/?student_id="
    search = self.userprofile.student_id
    if not self.userprofile.student_id:
        search = ''
    else:
        search = search.__str__()
    return ex_link + search


# 获取用户的coin数量
def get_coin_count(self):
    try:
        from bee_django_coin.exports import get_user_coin
        coin = get_user_coin(self)
        return coin
    except:
        return 0


# 增加/扣除m币
def add_coin_record(self, reason, identity, coin, count, created_by):
    try:
        from bee_django_coin.exports import add_coin_record as _add_coin_record
        coin = _add_coin_record(self, reason, identity, coin, count, created_by)
        if coin:
            return True
    except:
        return False


User.add_to_class("__unicode__", get_user_name)
User.add_to_class("get_user_name", get_user_name)
User.add_to_class("get_user_search_link", get_user_search_link)
User.add_to_class("get_coin_count", get_coin_count)
User.add_to_class("add_coin_record", add_coin_record)


# 获取学生是否暂停
def get_is_pause(self):
    if self.userprofile:
        return self.userprofile.is_pause
    return None


User.add_to_class("is_pause", get_is_pause)


# 获取学生结课日期
def get_expire_date(self):
    if self.userprofile:
        return self.userprofile.expire_date
    return None


User.add_to_class("get_expire_date", get_expire_date)


# 日志用户的头像地址获取
def get_user_profile_image(self):
    if self.userprofile:
        try:
            avatar = self.userprofile.avatar
            if avatar:
                return avatar.url
            else:
                return None
        except AttributeError:
            return None
    else:
        return None
User.add_to_class('get_user_profile_image', get_user_profile_image)

# 终身缦客
def is_unlimited(self):
    if self.userprofile.expire_date:
        if int(self.userprofile.expire_date.strftime("%Y")) >= 2999:
            return True
    return False
User.add_to_class('is_unlimited', is_unlimited)

# def create(self, preuser, student_id, room_id=None, start_date=None, expire_date=None):
#     user_profile = UserProfile()
#     user_profile.preuser = preuser
#     user_profile.student_id = student_id
#     user_profile.start_date = start_date
#     user_profile.expire_date = expire_date
#     user_profile.room_id = room_id
#     user_profile.save()
#     user = user_profile.user
#     return user

    # User.add_to_class('create', create)
