#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from django import template
from bee_django_course_simple.models import UserQuestion,Question


register = template.Library()

# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)

# 用户答题
@register.simple_tag
def get_user_answer_option(user, question_id):
    question = Question.objects.get(id=question_id)
    try:
        user_question = UserQuestion.objects.get(question=question,user_part__user_section__user_course__user=user)
        answer_option=user_question.answer_option
        return answer_option.id
    except:
        return None