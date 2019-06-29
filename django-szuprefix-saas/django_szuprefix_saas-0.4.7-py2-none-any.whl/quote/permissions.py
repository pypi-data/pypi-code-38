# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.permissions import BasePermission
from . import choices
__author__ = 'denishuang'

class CanDeleteRequestItem(BasePermission):
    message = "非询价中状态, 不能删除"

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE' and obj.request.status not in (choices.REQUEST_STATUS_REQUEST,choices.REQUEST_STATUS_QUOTE):
            return False
        return True
