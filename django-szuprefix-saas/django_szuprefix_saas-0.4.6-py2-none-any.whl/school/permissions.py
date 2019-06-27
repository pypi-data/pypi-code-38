# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django_szuprefix_saas.saas.permissions import IsSaasWorker

class IsSchoolUser(IsSaasWorker):
    message = "没有权限, 不是学校用户"

    def has_permission(self, request, view):
        valid = super(IsSchoolUser, self).has_permission(request, view)
        if valid:
            party = view.party
            valid = hasattr(party, "as_school")
            if valid:
                view.school = party.as_school
        return valid


class IsStudent(IsSchoolUser):
    message = "没有权限, 不是有效学生"

    def has_permission(self, request, view):
        valid = super(IsStudent, self).has_permission(request, view)
        if valid:
            user = request.user
            valid = hasattr(user, "as_school_student")
            if valid:
                view.student = user.as_school_student
                valid = view.student.is_active
        return valid

class IsTeacher(IsSchoolUser):
    message = "没有权限, 不是学校老师"

    def has_permission(self, request, view):
        valid = super(IsTeacher, self).has_permission(request, view)
        if valid:
            user = request.user
            valid = hasattr(user, "as_school_teacher")
            if valid:
                view.teacher = user.as_school_teacher
        return valid
