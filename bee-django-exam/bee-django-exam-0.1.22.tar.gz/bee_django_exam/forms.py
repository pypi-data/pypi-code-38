# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Grade, Notice, UserExamRecord, GradeCertField, GRADE_FEILD_TEXT_ALIGN_CHOICES, EXAM_STATUS_CHOICES
from .utils import get_cert_form_list


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['name', 'coin',"order_by", "is_show", "notice", "cert_image", 'icon']


class GradeCertFieldForm(forms.ModelForm):
    field = forms.ChoiceField(choices=get_cert_form_list(), label='字段名')
    text_align = forms.ChoiceField(choices=GRADE_FEILD_TEXT_ALIGN_CHOICES, label='文字对齐方式',help_text='文字在填写区域中的对齐方式')

    class Meta:
        model = GradeCertField
        fields = ['field', "font_color", "font_size", "text_width", "text_height","text_post_x", "text_post_y", "text_bg_color",
                  "text_align"]


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', "is_require", "context"]


# 学生申请考级
class UserExamRecordCreateForm(forms.ModelForm):
    grade = forms.ModelChoiceField(queryset=Grade.objects.filter(is_show=True), label='考级名称')

    class Meta:
        model = UserExamRecord
        fields = ['grade']


class UserExamRecordSearchForm(forms.ModelForm):
    # exam_stutas_choices = ((0, "全部"), (-1, '未报名'), (1, '通过'), (2, '未通过'), (3, '关闭'))
    user_name = forms.CharField(label='姓名', required=False)
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(), label='考级名称', required=False)
    # status = forms.ChoiceField(choices=exam_stutas_choices, label='状态', required=False)

    class Meta:
        model = UserExamRecord
        fields = ['user_name', 'grade', "status"]
        # fields = ['user_name', 'grade']


class UserExamNoticeForm(forms.Form):
    is_agree = forms.BooleanField(required=True)


# 后台修改考级成绩
class UserExamRecordUpdateForm(forms.ModelForm):
    exam_status_choices = ((1, '通过'), (2, '未通过'), (3, '关闭'))
    status = forms.ChoiceField(required=False, choices=exam_status_choices, label='状态')
    year = forms.CharField(required=False, help_text="（此字段用于证书显示）", label="年度")
    passed_date = forms.CharField(required=False, help_text="（此字段用于证书显示）", label="通过日期")

    class Meta:
        model = UserExamRecord
        fields = ['status', 'year', "passed_date", "result", "info"]


class UserExamRecordCertUploadForm(forms.ModelForm):
    class Meta:
        model = UserExamRecord
        fields = ['cert']
