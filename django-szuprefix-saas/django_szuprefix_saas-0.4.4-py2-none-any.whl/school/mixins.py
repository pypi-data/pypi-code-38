# -*- coding:utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.db.models.fields.related import RelatedField

from ..saas.mixins import PartyMixin, PartySerializerMixin
from . import permissions


class SchoolMixin(PartyMixin): 

    def get_permissions(self):
        return super(SchoolMixin, self).get_permissions()+[permissions.IsSchoolUser()]

    # def get_user_contexts(self, request, *args, **kwargs):
    #     ctx = super(SchoolMixin, self).get_user_contexts(request, *args, **kwargs)
    #     if not hasattr(self.party, "as_school"):
    #         raise PermissionDenied(u"当前网站用户不属于任何学校.")
    #     self.school = self.party.as_school
    #     return ctx + ["school"]

    # def perform_create(self, serializer):
    #     serializer.save(school=self.school)

    def get_serializer(self, *args, **kwargs):
        kwargs['school'] = self.school
        return super(SchoolMixin, self).get_serializer(*args, **kwargs)


class SchoolSerializerMixin(PartySerializerMixin):
    school = None

    def __init__(self, *args, **kwargs):
        if 'school' in kwargs:
            self.school = kwargs.pop('school')
        super(SchoolSerializerMixin, self).__init__(*args, **kwargs)

    def to_internal_value(self,value):
        d = super(SchoolSerializerMixin, self).to_internal_value(value)
        d['school'] = self.school
        return d

    def addFilter2RelativeFields(self):
        super(SchoolSerializerMixin, self).addFilter2RelativeFields()
        for n, f in self.fields.iteritems():
            if isinstance(f, RelatedField) and f.queryset and hasattr(f.queryset.model, 'school'):
                f.queryset = f.queryset.filter(school=self.school)

    def save(self, **kwargs):
        kwargs["school"] = self.school
        return super(SchoolSerializerMixin, self).save(**kwargs)
