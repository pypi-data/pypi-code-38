# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django_szuprefix.utils import modelutils, excelutils
__author__ = 'denishuang'
import logging

log = logging.Logger("django")


@shared_task()
def dump_excel_task(id):
    from .models import ExcelTask, Attachment
    import tempfile
    from django.core.files import File
    task = ExcelTask.objects.get(id=id)
    params = task.params
    task.status = 2
    task.save()
    attach = Attachment()
    attach.content_object = task
    f = open(tempfile.mkstemp()[1], "w")
    ids = params.get("object_ids")
    headers = params.get("headers")
    excel = excelutils.ColorExcelResponse([[]])
    excel.set_output(f)
    data = modelutils.get_objects_accessor_data(params.get("accessors"),
                                  params.get("content_type_id"),
                                  ids
                                  )
    if len(ids) >= excelutils.ColorExcelResponse.ROW_LIMIT:
        excel.encoding = 'gbk'
        excel.write_csv(data, headers)
        ext_name = 'csv'
    else:
        excel.write_xls(data,headers)
        ext_name = 'xls'

    f.close()
    attach.file.save(u"%s.%s" % (task.name, ext_name), File(open(f.name)))
    attach.save()
    task.status = 4
    task.save()