#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.contrib.auth.models import User
from .models import CourseSectionMid, UserCourseSection, UserCourse
from .utils import get_user_live_data


# django前台显示本地时间
def filter_local_datetime(_datetime):
    return _datetime


# 获取一个助教，所教的所有学生
def get_teach_users(mentor):
    return User.objects.all()


# 获取用户所学课程的课件列表，排序
def get_user_course_section_list(user_course, section_type_list=None):
    m_list = CourseSectionMid.objects.filter(course=user_course.course).order_by('order_by')
    section_list = user_course.usercoursesection_set.filter(section__coursesectionmid__in=m_list) \
        .order_by('section__coursesectionmid__order_by')
    if section_type_list:
        section_list = section_list.filter(section__type__in=section_type_list)
    return section_list


# 获取直播的分钟数，和次数
def get_user_live_mins_count_days(user, start_dt=None, end_dt=None):
    return get_user_live_data(user, start_dt, end_dt)


def get_user_last_course_section(user, start_dt=None, end_dt=None):
    ucs_list = UserCourseSection.objects.filter(user_course__user=user).order_by('-updated_at')

    if ucs_list.exists():
        if start_dt:
            ucs_list = ucs_list.filter(updated_at__gte=start_dt)
        if end_dt:
            ucs_list = ucs_list.filter(updated_at__lte=end_dt)
        list = ucs_list.filter(status=1)
        if list.exists():
            return list.first()
        else:
            finished = ucs_list.filter(status__in=[2, 4])
            if finished.exists():
                return finished.first()
            else:
                return None
    else:
        return None


def get_current_user_course(user):
    uc_list = UserCourse.objects.filter(user=user).order_by('-created_at')
    if uc_list.exists():
        return uc_list.first()
    else:
        return None