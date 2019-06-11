# -*- coding:utf-8 -*-
from django.dispatch import Signal

# 费用审核后的信号
fee_checked = Signal(providing_args=["preuser_fee","user"])
