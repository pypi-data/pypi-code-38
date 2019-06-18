# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.response import Response

from django_szuprefix.utils import excelutils
from ..api.mixins import UserApiMixin
from . import serializers, models
from rest_framework import viewsets, decorators, response, status
from ..api.helper import register
from dwebsocket.decorators import accept_websocket

__author__ = 'denishuang'


class ExcelViewSet(viewsets.ViewSet):
    @decorators.list_route(['post'], authentication_classes=[], permission_classes=[])
    def read(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file', None)
        orient = request.data.get('orient', '')
        if orient == 'blocks':
            return Response(excelutils.pandas_read(file_obj))
        else:
            return Response({'data': excelutils.excel2json(file_obj)})

    @decorators.list_route(['post'], authentication_classes=[], permission_classes=[])
    def write(self, request, *args, **kwargs):
        body = request.data
        data = body.get("data")
        file_name = body.get("file_name", "export_data.xlsx")
        from excel_response import ExcelResponse
        return ExcelResponse(data, output_filename=file_name)


register(__package__, 'excel', ExcelViewSet, 'excel')


# class ImageUploadView(viewsets.ViewSet):
#     model = models.Image
#     fields = ("file",)
#
#     def form_valid(self, form):
#         self.object = r = form.save(False)
#         r.owner = self.request.user
#         r.save()
#         from sorl.thumbnail import get_thumbnail
#         thumb = get_thumbnail(self.object.file, self.request.GET.get("thumb", "100x100"))
#         return Response({"error_code": 0, "file": {"id": r.id, "url": r.file.url, "thumb_url": thumb.url}})
#
#     def form_invalid(self, form):
#         return Response({"error_code": -1, "errors": form.errors})

class ImageViewSet(UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.ImageSerializer
    queryset = models.Image.objects.all()
    user_field_name = 'owner'
    filter_fields = {'content_type__app_label': ['exact'], 'content_type__model': ['exact']}


register(__package__, 'image', ImageViewSet)


class TempFileViewSet(UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.TempFileSerializer
    queryset = models.TempFile.objects.all()
    user_field_name = 'owner'


register(__package__, 'tempfile', TempFileViewSet)

# class AsyncResultViewSet(viewsets.GenericViewSet):
#
#     @accept_websocket
#     def retrieve(self, request, *args, **kwargs):
#         from celery.result import AsyncResult
#         rs=AsyncResult(kwargs['pk'])
#         d = dict(
#             task_id=rs.task_id,
#             state=rs.state,
#             status=rs.status,
#             result=rs.status == 'FAILURE' and unicode(rs.result) or rs.result,
#             traceback=rs.traceback
#         )
#         return Response(d)
#
#
#
#
# register(__package__, 'async_result', AsyncResultViewSet, base_name='async_result')
