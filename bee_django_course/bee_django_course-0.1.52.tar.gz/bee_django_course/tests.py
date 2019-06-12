# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from bee_django_course.models import Course, Section, UserCourseSection, CourseSectionMid

# Create your tests here.

def create_user(name):
    pass

def create_course(name):
    return Course.objects.create(name=name)

def create_section(name):
    return Section.objects.create(name=name)


class UserCourseSectionTest(TestCase):
    def setUp(self):
        # 创建 course
        course = create_course('test_course')
        # 创建 section
        for i in range(0,5):
            section = create_section(name='section'+str(i))
            CourseSectionMid.objects.create(course=course, section=section, order_by=i)

        # 创建用户
        # 分配课程

    def video_length_section_automatic_pass(self):
        pass