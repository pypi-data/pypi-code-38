#!/usr/bin/env python
# -*- coding:utf-8 -*-


__author__ = 'bee'

from django.contrib.auth import get_user_model
from .models import UserExamRecord, UserStartExam
from utils import get_user_exam_record
User = get_user_model()


#
#
# # django前台显示本地时间
# def filter_local_datetime(_datetime):
#     return _datetime
#
#
# # 学生报名后续操作
# def after_user_exam_add(record):
#     return True, ""
#
#
# # 学生报名前操作
# def before_user_exam(user_id):
#     return True, ""
#
#
# # 通过考级后操作
# def after_user_passed(record):
#     return True, ""


# # 是否开启了考级
# def get_is_start_exam(user):
#     if not user:
#         return None
#     record_list = UserStartExam.objects.filter(user=user, is_start_exam=True)
#     if record_list.exists():
#         return True
#     return False


def get_user_icon(user_id):
    if not user_id:
        return None
    record_list = UserExamRecord.objects.filter(user__id=user_id, status=1).order_by("-created_at")
    if record_list.count() >= 1:
        record = record_list.first()
        try:
            icon = record.grade.icon
            return icon.url
        except:
            return None
    else:
        return None


# 获取最近一次通过的的考级名称
def get_user_lasteat_exam_grade_name(user_id):
    if not user_id:
        return None
    user = User.objects.get(id=user_id)
    record = get_exam(user, 1)
    if record:
        return record.grade_name
    else:
        return ''



