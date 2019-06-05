# -*- coding:utf-8 -*-
from django.dispatch import Signal

# 作业被评分前发出的信号
assignment_will_be_scored = Signal(providing_args=["user_course_section", "request"])

# 作业评分后发出的信号
assignment_was_scored = Signal(providing_args=["user_course_section", "request"])

# 课程通过后发送的信号
ucs_passed = Signal(providing_args=['user_course_section'])

# 直播回调后发出的信号
live_callback_finished = Signal(providing_args=["user_live", "coin_multiple"])
# 直播删除后发送信号
user_live_delete =  Signal(providing_args=["user_live"])


# 笔记创建的信号
section_note_created = Signal(providing_args=["user_section_note_id"])


# 直播评论后发出的信号
user_live_comment = Signal(providing_args=['user_live', 'comment_user'])