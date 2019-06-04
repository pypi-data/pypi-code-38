# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.permissions import BasePermission

__author__ = 'denishuang'


class IsSaasWorker(BasePermission):
    message = "没有权限, 不是有效saas用户"

    def has_permission(self, request, view):
        user = request.user
        valid = hasattr(user, "as_saas_worker")
        if valid:
            view.worker = user.as_saas_worker
            view.party = view.worker.party
            valid = view.worker.is_active
        return valid
