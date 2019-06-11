#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import pytz, os, json, qrcode
import unicodecsv as csv
from django.http import HttpResponse
from django.conf import settings
from bee_django_crm.models import PreUser, PreUserTrack, PreUserContract,PreUserFee
from datetime import datetime
from distutils.sysconfig import get_python_lib
from django.http import StreamingHttpResponse
from PIL import Image, ImageFont, ImageDraw
from django.apps import apps
from django.contrib.auth import get_user_model

from .models import get_user_name_field
LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')
User = get_user_model()

# 获取转介人姓名
def get_referral_user_name_with_preuser(preuser_id):
    try:
        preuser = PreUser.objects.get(pk=preuser_id)
        referral_user = preuser.referral_user
        if referral_user:
            return get_user_name(referral_user)
        return None
    except Exception as e:
        return None


# 获取转介人姓名
def get_referral_user_name_with_user(user_id):
    try:
        referral_user = User.objects.get(pk=user_id)
        if referral_user:
            return get_user_name(referral_user)
        return None
    except Exception as e:
        return None


# 获取来源id
def get_preuser_source(preuser_id):
    try:
        user = PreUser.objects.get(id=preuser_id)
        return user.source
    except Exception as e:
        return None


# 获取自定义user的自定义name
def get_user_name(user):
    try:
        return getattr(user, get_user_name_field())
    except:
        return None


# 获取联络list
def get_track_list(preuser_id):
    if not preuser_id:
        return None
    track_list = PreUserTrack.objects.filter(user__id=preuser_id)
    return track_list


# 获取缴合同list
def get_contract_list(preuser_id):
    if not preuser_id:
        return None
    track_list = PreUserContract.objects.filter(preuser__id=preuser_id)
    return track_list

# 获取缴费list
def get_fee_list(preuser_id):
    if not preuser_id:
        return None
    fee_list = PreUserFee.objects.filter(preuser__id=preuser_id)
    return fee_list

# 获取本地当前时间
def get_now(tz=LOCAL_TIMEZONE):
    return datetime.now(tz)


# 时区转换
# curtime 为带时区时间
def change_tz(_datetime, tz):
    # return tz.localize(curtime)
    if not _datetime:
        return None
    return _datetime.astimezone(tz=tz)


# 读取json文件
def loadJson(filename):
    file_path = os.path.join(os.getcwd(), 'bee_django_crm', 'static', 'data', filename + ".json")
    if not os.path.exists(file_path):
        file_path = os.path.join(get_python_lib(), 'bee_django_crm', 'static', 'bee_django_crm', 'data',
                                 filename + ".json")
        if not os.path.exists(file_path):
            return None
    f = open(file_path, "r")
    json_data = json.load(f)
    return json_data


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")


# 导出csv
def export_csv(filename, headers, rows):
    response = StreamingHttpResponse((row for row in csv_itertor(headers, rows)), content_type="text/csv;charset=utf-8")
    response['Content-Disposition'] = 'attachment;filename="' + filename + '.csv"'
    return response


def csv_itertor(headers, rows):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(headers)
    for column in rows:
        yield writer.writerow(column)


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


# 完
# 制作二维码
def create_qrcode(url="", color="#000000"):
    image = qrcode.make(url)
    image = image.convert("RGBA")
    datas = image.getdata()
    newData = []
    # print(color)
    color = toRgb(color)
    # print(color)
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            item = color
            newData.append(item)
        else:
            newData.append(item)
    image.putdata(newData)
    return image


# 合并二维码，生成带用户名和二维码的转介图片
# 返回image对象
def merge_img(referral_base_path, qrcode_img, qrcode_pos, qrcode_size):
    if not referral_base_path:
        return 1, u'没有图片', None

    try:
        referral_img = Image.open(referral_base_path)
        qrcode_img = qrcode_img.resize(qrcode_size, Image.ANTIALIAS)
        referral_img.paste(qrcode_img, qrcode_pos)

    except Exception as e:
        return 1, str(e), None
    return 0, '', referral_img


def toRgb(qrcode_color):
    import re
    qrcode_color = qrcode_color.replace('#', '')
    opt = re.findall(r'(.{2})', qrcode_color)  # 将字符串两两分割
    color_tuple = ()  # 用以存放最后结果
    for i in range(0, len(opt)):  # for循环，遍历分割后的字符串列表
        t = (int(opt[i], 16),)
        color_tuple += t  # 将结果拼接成12，12，12格式
    # print("转换后的RGB数值为：")
    color_tuple += (255,)
    return color_tuple


# def get_user_model():
#     if settings.CRM_USER_TABLE in ["", None]:
#         user_model = User
#     else:
#         app_name = settings.CRM_USER_TABLE.split(".")[0]
#         model_name = settings.CRM_USER_TABLE.split(".")[1]
#         app = apps.get_app_config(app_name)
#         user_model = app.get_model(model_name)
#     return user_model


def get_landing_url_list():
    url = settings.CRM_LANDING_URL
    url_list = []
    if isinstance(url, list):
        if len(url) == 0:
            return None
        for u in url:
            if not u in ["", None]:
                url_list.append(u)
        if len(url_list) == 0:
            return None
        else:
            return url_list
    else:
        if url in ["", None]:
            return None
        else:
            url_list.append(url)
            return url_list


# 获取审核的后续操作的url
# 如果没有后续操作的权限，也返回空
def get_after_check_url(cookie_user, preuser_fee):
    if settings.CRM_AFTER_CHECK_URL in ["", None]:
        return None
    else:
        if not cookie_user.has_perm("bee_django_crm.can_after_checked_fee"):
            return None
    url = settings.CRM_AFTER_CHECK_URL + "?preuser_id=" + preuser_fee.preuser.id.__str__() + "&preuser_contract_id=" + preuser_fee.preuser_contract.id.__str__() + "&preuser_fee_id=" + preuser_fee.id.__str__()
    return url
