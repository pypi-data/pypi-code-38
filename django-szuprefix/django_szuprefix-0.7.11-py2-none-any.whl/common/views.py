from django.views.generic.edit import FormView

from . import models, forms
# Create your views here.
from django.views.generic import CreateView, DetailView, View
from django.http import JsonResponse
from ..utils import excelutils

from dwebsocket.decorators import accept_websocket
from django.http import HttpResponse
from celery.result import AsyncResult
from django.shortcuts import render
import logging

log = logging.getLogger("django")


class AttachmentUploadView(CreateView):
    model = models.Attachment
    fields = ("file",)

    def form_valid(self, form):
        self.object = r = form.save(False)
        r.owner = self.request.user
        r.name = r.file.name
        r.save()
        return JsonResponse({"id": r.id, "name": r.name, "url": r.file.url})

    def form_invalid(self, form):
        return JsonResponse({"errors": form.errors}, status=400)


class ImageUploadView(CreateView):
    model = models.Image
    fields = ("file",)

    def form_valid(self, form):
        self.object = r = form.save(False)
        r.owner = self.request.user
        r.save()
        from sorl.thumbnail import get_thumbnail
        thumb = get_thumbnail(self.object.file, self.request.GET.get("thumb", "100x100"))
        return JsonResponse({"error_code": 0, "file": {"id": r.id, "url": r.file.url, "thumb_url": thumb.url}})

    def form_invalid(self, form):
        return JsonResponse({"error_code": -1, "errors": form.errors})


class ExcelReadView(FormView):
    form_class = forms.FileUploadForm

    def form_valid(self, form):
        data = excelutils.excel2json(form.cleaned_data["file"].file)
        return JsonResponse({'data': data})

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)


class ExcelWriteView(View):
    def post(self, request, **kwargs):
        import json
        body = json.loads(request.body)
        data = body.get("data")
        file_name = body.get("file_name", "export_data.xlsx")
        # print data
        from excel_response import ExcelResponse
        return ExcelResponse(data, output_filename=file_name)


class ExcelTaskDetailView(DetailView):
    model = models.ExcelTask

    def get_queryset(self):
        return super(ExcelTaskDetailView, self).get_queryset().filter(owner=self.request.user)


import json


@accept_websocket
def async_result(request, task_id):
    def pm(body):
        try:
            if body['status'] in ['FAILURE', 'REVOKED']:
                body['result'] = unicode(body['result'])
            # print body
            request.websocket.send(('%s\r' % json.dumps(body)).encode('utf8'))
        except Exception, e:
            log.error("async_result dump json error, body: %s; exception: %s", body, e)

    rs = AsyncResult(task_id)
    if not request.is_websocket():
        body = {'status': rs.state, 'result': unicode(rs.result)}
        return HttpResponse(json.dumps(body))

    else:
        d = dict(
            task_id=rs.task_id,
            state=rs.state,
            status=rs.status,
            result=rs.status == 'FAILURE' and unicode(rs.result) or rs.result,
            traceback=rs.traceback
        )
        pm(d)
        try:
            r = rs.get(on_message=pm, propagate=False)
        except Exception, e:
            body = {'status': 'FAILURE', 'result': unicode(e)}
            request.websocket.send(('%s\r' % json.dumps(body)).encode('utf8'))
