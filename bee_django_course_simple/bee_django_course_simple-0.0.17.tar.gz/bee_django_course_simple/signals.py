# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.dispatch import Signal
# 完成答题后，发出的奖励信号
add_prize_coin = Signal(providing_args=["user", "coin", "reason"])

# 小节视频写笔记
user_part_note_created = Signal(providing_args=['user_part_note_id'])