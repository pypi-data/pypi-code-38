#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import json, pytz, os, time
from PIL import Image, ImageFont, ImageDraw

from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from django.http import HttpResponse
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Grade, GradeCertField, UserExamRecord

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')
User = get_user_model()
CERT_FIELD_LIST = [{"name": "考级名称", "field": "bee_django_exam_grade_name"},
                   {"name": "通过日期", "field": "bee_django_exam_passed_date"},
                   {"name": "年度", "field": "bee_django_exam_year"},
                   {"name": "其他", "field": "bee_django_exam_info"}
                   ]


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")


# ====dt====
# 获取本地当前时间
def get_now(tz=LOCAL_TIMEZONE):
    return datetime.now(tz)


def get_timestamp():
    return int(time.time())


#
# def get_user_model():
#     if settings.EXAM_USER_TABLE in ["", None]:
#         user_model = User
#     else:
#         app_name = settings.EXAM_USER_TABLE.split(".")[0]
#         model_name = settings.EXAM_USER_TABLE.split(".")[1]
#         app = apps.get_app_config(app_name)
#         user_model = app.get_model(model_name)
#     return user_model


# 获取登录用户
# def get_login_user(request):
#     if settings.COIN_USER_TABLE in ["", None]:
#         return request.user
#
#     token = request.COOKIES.get('cookie_token', '')
#     # 没有登录
#     if not token:
#         return None
#
#     try:
#         user_table = get_user_model()
#         user = user_table.objects.get(token=token)
#         return user
#     except:
#         return None


# 获取自定义user的自定义name
def get_user_name(user_id):
    try:
        user = User.objects.get(user_id=user_id)
        return getattr(user, settings.USER_NAME_FIELD)
    except:
        return None


# # 获取user
# def get_user(user_id):
#     model = get_user_model()
#     try:
#         return model.objects.get(id=user_id)
#     except:
#         return None


#
# def get_default_name():
#     return settings.COIN_DEFAULT_NAME

def get_cert_form_list():
    field_list = CERT_FIELD_LIST
    try:
        field_list += settings.EXAM_CERT_FIELD_LIST
    except:
        field_list = field_list
    form_list = []
    for obj in field_list:
        try:
            form_list.append((obj["field"], obj["name"]))
        except:
            continue
    return form_list


def get_cert_field_name(field):
    field_list = CERT_FIELD_LIST + settings.EXAM_CERT_FIELD_LIST
    for obj in field_list:
        try:
            if field == obj["field"]:
                return obj["name"]
        except:
            return None
    return None


class Cert(object):
    grade = None
    record = None
    text_padding = 2

    # def __init__(self, grade):
    #     # self.record = record
    #     self.grade = grade
    #     self.text_img_list = self.get_cert_field()

    def create_cert(self, grade, record=None):
        self.record = record
        self.grade = grade
        text_img_list = self.get_cert_field()
        if not self.grade:
            return False, u'考试级别错误', None
        cert_image = self.grade.cert_image
        if not cert_image:
            return False, u'没有证书图片', None

        cert_dir = os.path.join(settings.BASE_DIR, settings.EXAM_CERT_PATH)

        if record:
            cert_dir = os.path.join(cert_dir, self.grade.id.__str__())
            cert_path = os.path.join(cert_dir, self.record.user.id.__str__() + ".jpg")
            web_cert_path = os.path.join(settings.EXAM_CERT_PATH, self.record.grade.id.__str__(),
                                         self.record.user.id.__str__() + ".jpg")
        else:
            cert_dir = os.path.join(cert_dir, "temp")
            filename = get_timestamp().__str__() + '.jpg'
            cert_path = os.path.join(cert_dir, filename)
            web_cert_path = os.path.join(settings.EXAM_CERT_PATH, "temp", filename)
        web_cert_path = "/" + web_cert_path
        if not os.path.exists(cert_dir):
            os.mkdir(cert_dir)

        img = Image.open(cert_image)
        for text_img_dict in text_img_list:
            text_img = text_img_dict["text_img"]
            pos = text_img_dict["pos"]
            r, g, b, a = text_img.split()
            img.paste(text_img, tuple(pos), a)
        img.save(cert_path, quality=70)
        self.update_record(web_cert_path)
        return True, u"成功", web_cert_path

    def get_cert_field(self):
        field_list = GradeCertField.objects.filter(grade=self.grade)
        text_img_list = []
        for f in field_list:
            text_img = self.create_text_img(f)
            if text_img:
                text_img_list.append({"text_img": text_img, "pos": (f.text_post_x, f.text_post_y)})
        return text_img_list

    # 生成文字图片
    def create_text_img(self, field):
        text = self.get_text(field)
        if not text:
            return None

        if not field.text_height:
            field.text_height = field.font_size
        img_size = (field.text_width + self.text_padding, field.text_height + self.text_padding)
        font_path = settings.EXAM_CERT_FONT
        font_size = field.font_size
        font_color = field.font_color
        if field.text_bg_color in ["", None]:
            text_bg_color = toRgb(field.font_color) + (0,)
        else:
            text_bg_color = field.text_bg_color
        text_img = Image.new("RGBA", img_size, text_bg_color)
        dr = ImageDraw.Draw(text_img)
        font = ImageFont.truetype(font_path, font_size)
        a = text.split("\r")
        text = "".join(a)
        text_lines = text.split("\n")
        for i,line in enumerate(text_lines):
            w, h = dr.textsize(line, font=font)
            pos = self.get_text_pos_tuple(field.text_align,i,w,h,img_size[0])
            dr.text(pos, line, font=font, fill=font_color)
        return text_img

    # 获取文字
    def get_text(self, field):
        text = None
        if self.record:
            if field.field == CERT_FIELD_LIST[0]["field"]:
                text = self.record.grade_name
            elif field.field == CERT_FIELD_LIST[1]["field"]:
                text = self.record.passed_date
            elif field.field == CERT_FIELD_LIST[2]["field"]:
                text = self.record.year
            elif field.field == CERT_FIELD_LIST[3]["field"]:
                text = self.record.info
            else:
                user = self.record.user
                for f in settings.EXAM_CERT_FIELD_LIST:
                    if f["field"] == field.field:
                        text = getattr(user, field.field)
                        break
        else:
            text = "[" + field.name + "]"
        return text

    # 获取文字在文字图片中的坐标
    def get_text_pos_tuple(self, text_align,i,font_width,font_height,img_width):
        y=0
        x=0
        if text_align == 'left':
            x=0
        if text_align == 'right':
            x=img_width-font_width
        if text_align == 'center':
            x=img_width / 2 - font_width / 2
        y=i*font_height
        # print(i,line, w, h)
        # font_width = field.font_size * len(text)
        # img_width = field.text_width + self.text_padding
        # x = 0
        # y = 0
        #
        # if field.text_align == 'left':
        #     x = 0
        # elif field.text_align == 'right':
        #     x = img_width - font_width
        # elif field.text_align == 'center':
        #     x = img_width / 2 - font_width / 2

        return (x, y)

    def update_record(self, user_cert_path):
        if self.record and user_cert_path:
            self.record.cert = user_cert_path
            self.record.save()
        return


'''
img_path：原始证书图片
pos：坐标
cert_img_path：输出用户证书
'''


# def a(img_path, pos, cert_img_path):
#     img = Image.open(img_path)
#     str_img = create_str_img({})
#     r, g, b, a1 = str_img.split()
#     img.paste(str_img, tuple(pos), a1)
#     img.save(cert_img_path, quality=70)
#     return
#
#
# # 生成文字图片
# def create_str_img(d):
#     str = d["str"]
#     size = d["size"]
#     font_path = d["font_path"]
#     font_size = d["font_size"]
#     font_color = d["font_color"]
#     font_bg_color = d["font_bg_color"]
#     img = Image.new("RGBA", size, font_bg_color)
#     dr = ImageDraw.Draw(img)
#     font_base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     font_path = os.path.join(font_base_path, font_path)
#     font = ImageFont.truetype(font_path, font_size)
#     dr.text(get_offset(d), str, font=font, fill=font_color)
#     return img

def toRgb(color):
    import re
    qrcode_color = color.replace('#', '')
    opt = re.findall(r'(.{2})', qrcode_color)  # 将字符串两两分割
    color_tuple = ()  # 用以存放最后结果
    for i in range(0, len(opt)):  # for循环，遍历分割后的字符串列表
        t = (int(opt[i], 16),)
        color_tuple += t  # 将结果拼接成12，12，12格式
    # print("转换后的RGB数值为：")
    return color_tuple


def check_user_record(user_id):
    user_records = UserExamRecord.objects.filter(user__id=user_id).filter(status__in=[-1, -2, 0])
    if user_records.exists():
        return "当前已有一个未完成考级"
    else:
        return None
        # messages.error(self.request, "您当前已有一个未完成考级")
        # return redirect(reverse('bee_django_exam:user_exam_record_done'))


# 获取学生的考级
def get_user_exam_record(user, status):
    if not user:
        return None
    if not isinstance(status, list):
        status = [status]
    user_records = UserExamRecord.objects.filter(user=user).filter(status__in=status)
    if user_records.exists():
        return user_records.first()
    return None
