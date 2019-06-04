# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

app_name = 'common'
urlpatterns = [
    url(r'^attachment/upload/', login_required(csrf_exempt(views.AttachmentUploadView.as_view())),name="attachment-upload"),
    url(r'^image/upload/', login_required(csrf_exempt(views.ImageUploadView.as_view())),name="image-upload"),
    url(r'^excel/read/', login_required(csrf_exempt(views.ExcelReadView.as_view())),name="excel-read"),
    url(r'^excel/write/', login_required(csrf_exempt(views.ExcelWriteView.as_view())),name="excel-write"),
    url(r'^exceltask/(?P<pk>\d+)/', login_required(views.ExcelTaskDetailView.as_view()),name="excel-task-detail"),
    url(r'^async_result/(?P<task_id>[\w-]+)/', views.async_result),
]