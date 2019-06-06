# -*- coding:utf-8 -*-
from django.dispatch import Signal

# 日志创建的信号
user_feed_created = Signal(providing_args=["feed_id"])

# 日志删除的信号
user_feed_delete = Signal(providing_args=["feed_publisher", "feed_type"])

# 日志加精的信号, first_star 指明是否是第一次加精，True 是，False 否
user_feed_star = Signal(providing_args=['feed', 'first_star'])

# 日志取消加精的信号
user_feed_unstar = Signal(providing_args=['feed'])

# 美好生活审核的信号
user_album_checked = Signal(providing_args=["album_id"])

# 有人回复日志的信号
user_feed_replied = Signal(providing_args=['feed_id', 'replier'])

# 有人赞日志的信号
user_feed_emojied = Signal(providing_args=['feed_id', 'emojier'])

# 有人回复日志的评论信号
user_feedcomment_replied = Signal(providing_args=['feedcomment_id', 'replier'])