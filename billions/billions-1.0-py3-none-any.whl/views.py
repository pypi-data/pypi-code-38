#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import copy
from datetime import datetime
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage


def image_verify(file_object):
    """
    判断是否是图片
    :param file_object:
    :return:
    """
    result = True
    try:
        Image.open(file_object).verify()
    except IOError:
        result = False

    return result


def get_upload_filename(file_name):
    date_path = datetime.now().strftime('%Y/%m/%d')
    upload_path = os.path.join(settings.EDITORMD_UPLOAD_PATH, date_path)
    return default_storage.get_available_name(
        os.path.join(upload_path, file_name)
    )


@csrf_exempt
def billions_upload_image(request):
    """
    markdown上传图片
    返回值：
        {
            success : 0 | 1,           // 0 表示上传失败，1 表示上传成功
            message : "提示的信息，上传成功或上传失败及错误信息等。",
            url     : "图片地址"        // 上传成功时才返回
        }
    :param request:
    :return:
    """
    response = {
        'success': 0,
        'message': None,
        'url': None
    }
    if request.method != 'POST':
        response['message'] = "请求方式错误！"
        return JsonResponse

    uploaded_file = request.FILES.get('billions-image-file')
    """
    # 暂时不进行上传格式的判断
    if not image_verify(verify_upload_file):
        response['message'] = "请上传图片！"
        return JsonResponse(response)
    """
    file_name = get_upload_filename(uploaded_file.name)
    saved_path = default_storage.save(file_name, uploaded_file)

    response['success'] = 1
    response['url'] = default_storage.url(saved_path)

    return JsonResponse(response)
