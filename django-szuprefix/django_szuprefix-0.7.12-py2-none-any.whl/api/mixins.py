# -*- coding:utf-8 -*-
from rest_framework import decorators, response, status

__author__ = 'denishuang'


class BatchCreateModelMixin(object):
    @decorators.list_route(['POST'])
    def batch_create(self, request):
        errors = []
        ss = []
        for d in request.data:
            serializer = self.get_serializer(data=d)
            if not serializer.is_valid():
                errors.append({"object": d, "errors": serializer.errors})
            else:
                ss.append(serializer)
        if errors:
            return response.Response(errors, status=status.HTTP_400_BAD_REQUEST)
        for s in ss:
            self.perform_create(s)
        return response.Response({"success": len(ss)}, status=status.HTTP_201_CREATED)


class ModelSearchOptionsMixin(object):
    @decorators.list_route(['OPTION'])
    def search(self, request):
        search_fields = getattr(self, 'search_fields', [])
        from ..utils import modelutils
        cf = lambda f: f[0] in ['^', '@', '='] and f[1:] or f
        return [modelutils.get_related_field(self.queryset.model, cf(f)).verbose_name for f in
                search_fields]


class RestCreateMixin(object):
    def get_serializer_save_args(self):
        return {}

    def perform_create(self, serializer):
        serializer.save(**self.get_serializer_save_args())


class UserApiMixin(RestCreateMixin):
    user_field_name = 'user'

    def get_serializer_save_args(self):
        d = super(UserApiMixin, self).get_serializer_save_args()
        d[self.user_field_name] = self.request.user
        return d

    # def get_queryset(self):
    #     return super(UserApiMixin, self).get_queryset().filter(**{self.user_field_name: self.request.user})


class IDAndStrFieldSerializerMixin(object):
    def get_field_names(self, declared_fields, info):
        fns = super(IDAndStrFieldSerializerMixin, self).get_field_names(declared_fields, info)
        fns += ('id', '__str__')
        return fns
