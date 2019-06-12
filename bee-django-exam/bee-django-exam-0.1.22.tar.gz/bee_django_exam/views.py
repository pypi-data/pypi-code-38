#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import json, qrcode, os, shutil, urllib
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.six import BytesIO
from django.apps import apps

from django.utils.decorators import method_decorator
from django import forms

from .decorators import cls_decorator, func_decorator
from .models import Grade, Notice, UserExamRecord, GradeCertField, UserStartExam, get_user_name_field
from .forms import GradeForm, NoticeForm, UserExamRecordCreateForm, UserExamRecordSearchForm, UserExamRecordUpdateForm, \
    GradeCertFieldForm, \
    UserExamRecordCertUploadForm, UserExamNoticeForm
# from .exports import before_user_exam, after_user_passed
from .signals import send_message_signal, add_user_track_signal
from .utils import get_cert_field_name, JSONResponse, Cert, check_user_record, get_user_name

User = get_user_model()


# Create your views here.
def test(request):
    return


# ========grade===========
@method_decorator(cls_decorator(cls_name='GradeList'), name='dispatch')
class GradeList(ListView):
    model = Grade
    template_name = 'bee_django_exam/grade/grade_list.html'
    context_object_name = 'grade_list'
    paginate_by = 20


@method_decorator(cls_decorator(cls_name='GradeDetail'), name='dispatch')
class GradeDetail(DetailView):
    model = Grade
    template_name = 'bee_django_exam/grade/grade_detail.html'
    context_object_name = 'grade'


@method_decorator(cls_decorator(cls_name='GradeCreate'), name='dispatch')
class GradeCreate(CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'bee_django_exam/grade/grade_form.html'
    success_url = reverse_lazy('bee_django_exam:grade_list')


@method_decorator(cls_decorator(cls_name='GradeUpdate'), name='dispatch')
class GradeUpdate(UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'bee_django_exam/grade/grade_form.html'
    success_url = reverse_lazy('bee_django_exam:grade_list')

    # def get_context_data(self, **kwargs):
    #     context = super(GradeUpdate, self).get_context_data(**kwargs)
    #     grade_id = self.kwargs["pk"]
    #     grade = Grade.objects.get(id=grade_id)
    #     context["cert"] = grade.cert_image
    #     return context


@method_decorator(cls_decorator(cls_name='GradeDelete'), name='dispatch')
class GradeDelete(DeleteView):
    model = Grade
    success_url = reverse_lazy('bee_django_exam:grade_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='GradeCertFieldCreate'), name='dispatch')
class GradeCertFieldCreate(CreateView):
    model = GradeCertField
    form_class = GradeCertFieldForm
    template_name = 'bee_django_exam/grade/cert/cert_field_form.html'
    success_url = None

    # def get_cert_img(self):


    def get_context_data(self, **kwargs):
        context = super(GradeCertFieldCreate, self).get_context_data(**kwargs)
        grade_id = self.kwargs["pk"]
        grade = Grade.objects.get(id=grade_id)
        context["grade"] = grade
        return context

    def form_valid(self, form):
        f = form.save(commit=False)
        grade_id = self.kwargs["pk"]
        grade = Grade.objects.get(id=grade_id)
        field_name = get_cert_field_name(form.cleaned_data['field'])
        f.name = field_name
        f.grade = grade
        f.save()
        self.success_url = reverse_lazy("bee_django_exam:grade_detail", kwargs=self.kwargs)
        return super(GradeCertFieldCreate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='GradeCertFieldCreate'), name='dispatch')
class GradeCertFieldUpdate(UpdateView):
    model = GradeCertField
    form_class = GradeCertFieldForm
    template_name = 'bee_django_exam/grade/cert/cert_field_form.html'
    success_url = None

    def form_valid(self, form):
        field_id = self.kwargs["pk"]
        grade = Grade.objects.get(gradecertfield__id=field_id)
        self.success_url = reverse_lazy("bee_django_exam:grade_detail", kwargs={"pk": grade.id})
        return super(GradeCertFieldUpdate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='GradeCertFieldDelete'), name='dispatch')
class GradeCertFieldDelete(DeleteView):
    model = GradeCertField
    success_url = reverse_lazy('bee_django_exam:grade_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='GradeCertModify'), name='dispatch')
class GradeCertModify(DetailView):
    model = Grade
    template_name = 'bee_django_exam/grade/cert/cert_modify.html'
    context_object_name = 'grade'

    def get_context_data(self, **kwargs):
        context = super(GradeCertModify, self).get_context_data(**kwargs)
        grade_id = self.kwargs["pk"]
        grade = Grade.objects.get(id=grade_id)
        res, msg, cert_path = Cert().create_cert(grade=grade, record=None)
        # print(msg)
        # print(res, msg, cert_path)
        context["cert_path"] = cert_path
        return context


# ========notice===========
@method_decorator(cls_decorator(cls_name='NoticeList'), name='dispatch')
class NoticeList(ListView):
    model = Notice
    template_name = 'bee_django_exam/notice/notice_list.html'
    context_object_name = 'notice_list'
    paginate_by = 20


@method_decorator(cls_decorator(cls_name='NoticeDetail'), name='dispatch')
class NoticeDetail(DetailView):
    model = Notice
    template_name = 'bee_django_exam/notice/notice_detail.html'
    context_object_name = 'notice'


@method_decorator(cls_decorator(cls_name='NoticeCreate'), name='dispatch')
class NoticeCreate(CreateView):
    model = Notice
    form_class = NoticeForm
    template_name = 'bee_django_exam/notice/notice_form.html'
    success_url = reverse_lazy('bee_django_exam:notice_list')


@method_decorator(cls_decorator(cls_name='NoticeUpdate'), name='dispatch')
class NoticeUpdate(UpdateView):
    model = Notice
    form_class = NoticeForm
    template_name = 'bee_django_exam/notice/notice_form.html'


@method_decorator(cls_decorator(cls_name='UserExamRecordCreate'), name='dispatch')
class UserExamRecordCreate(CreateView):
    model = UserExamRecord
    form_class = UserExamRecordCreateForm
    template_name = 'bee_django_exam/record/user_record_add.html'
    success_url = None

    def get_success_url(self):
        return reverse('bee_django_exam:user_exam_record_list', kwargs=self.kwargs)

    def form_valid(self, form):
        user_id = self.kwargs["user_id"]
        error_msg = check_user_record(user_id)
        if error_msg:
            messages.error(self.request, error_msg)
            return redirect(reverse('bee_django_exam:user_exam_record_list', kwargs=self.kwargs))

        record = form.save(commit=False)
        record.user_id = user_id
        grade = form.instance.grade
        record.grade_name = grade.name
        record.save()
        messages.success(self.request, '添加成功')
        return super(UserExamRecordCreate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='UserExamNotice'), name='dispatch')
class UserExamNotice(TemplateView):
    template_name = "bee_django_exam/record/notice_detail.html"

    def get(self, request, *args, **kwargs):
        record = self.get_record()
        if not record.status == -1:
            messages.error(self.request, "已报过名，无需重复报名")
            return redirect(reverse("bee_django_exam:user_exam_record_done"))
        return super(UserExamNotice, self).get(request)

    def get_record(self):
        record_id = self.kwargs["user_record_id"]
        record = UserExamRecord.objects.get(id=record_id)
        return record

    def get_context_data(self, **kwargs):
        context = super(UserExamNotice, self).get_context_data(**kwargs)
        record = self.get_record()
        context["form"] = UserExamNoticeForm()
        context["record"] = record
        return context

    def post(self, request, *args, **kwargs):
        form = UserExamNoticeForm(request.POST)
        if form.is_valid():
            record = self.get_record()
            user = record.user
            grade = record.grade
            # 检查m币数量，扣m币
            coin = user.get_coin_count()
            if grade.coin:
                if coin < grade.coin:
                    messages.error(self.request, settings.COIN_NAME.decode("utf-8") + u"不足，无法报名")
                    return redirect(reverse('bee_django_exam:user_exam_record_done'))
                else:
                    res = user.add_coin_record('考级报名', 'exam_record', -grade.coin, 1, request.user)
                    if not res:
                        messages.error(self.request, '扣除' + settings.COIN_NAME.decode("utf-8") + "失败")
                        return redirect(reverse('bee_django_exam:user_exam_record_done'))
            # 更新考级状态
            record.status = -2
            record.save()
            messages.success(self.request, "报名成功")
            return redirect(reverse('bee_django_exam:user_exam_record_done'))


@method_decorator(cls_decorator(cls_name='UserExamRecordDone'), name='dispatch')
class UserExamRecordDone(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'bee_django_exam/record/record_done.html')


# 某个学生自己的考级申请记录
@method_decorator(cls_decorator(cls_name='UserExamRecordList'), name='dispatch')
class UserExamRecordList(ListView):
    model = UserExamRecord
    template_name = 'bee_django_exam/record/user_record_list.html'
    paginate_by = 20
    context_object_name = 'record_list'
    queryset = None

    def get(self, request, *args, **kwargs):
        if not self.kwargs.has_key("user_id"):
            self.kwargs["user_id"] = 0
        return super(UserExamRecordList, self).get(request)

    def get_user(self):
        user_id = self.kwargs["user_id"]
        if not user_id in [None, '0', 0]:
            user = User.objects.get(id=user_id)
        else:
            user = None
        return user

    def search(self):
        user_name = self.request.GET.get("user_name")
        grade = self.request.GET.get("grade")
        status = self.request.GET.get("status")
        user = self.get_user()

        if user:
            self.queryset = UserExamRecord.objects.filter(user=user)
        else:
            if not self.request.user.has_perm("bee_django_exam.view_all_user_exam_record_list"):
                return UserExamRecord.objects.none()
            else:
                self.queryset = UserExamRecord.objects.all()

        if not grade in ["", 0, None]:
            self.queryset = self.queryset.filter(grade__id=grade)
        if not status in ["", '0', 0, None]:
            self.queryset = self.queryset.filter(status=status)
        if not user_name in ["", 0, None]:
            try:
                kwargs = {}  # 动态查询的字段
                name_field = get_user_name_field()
                kwargs["user__" + name_field + '__icontains'] = user_name
                self.queryset = self.queryset.filter(**kwargs)
            except:
                self.queryset = self.queryset
        return self.queryset

    def get_queryset(self):
        return self.search()

    def get_context_data(self, **kwargs):
        context = super(UserExamRecordList, self).get_context_data(**kwargs)
        user_name = self.request.GET.get("user_name")
        grade = self.request.GET.get("grade")
        status = self.request.GET.get("status")
        context['search_form'] = UserExamRecordSearchForm(
            {"user_name": user_name, "grade": grade, "status": status})
        context["user"] = self.get_user()
        return context


class CustomUserExamRecordList(UserExamRecordList):
    template_name = 'bee_django_exam/record/custom_user_record_list.html'


@method_decorator(cls_decorator(cls_name='UserExamRecordDetail'), name='dispatch')
class UserExamRecordDetail(DetailView):
    model = UserExamRecord
    template_name = 'bee_django_exam/record/record_detail.html'
    context_object_name = 'record'


@method_decorator(cls_decorator(cls_name='UserExamRecordUpdate'), name='dispatch')
class UserExamRecordUpdate(UpdateView):
    model = UserExamRecord
    form_class = UserExamRecordUpdateForm
    template_name = 'bee_django_exam/record/admin_record_update.html'
    success_url = reverse_lazy("bee_django_exam:user_exam_record_list")

    def get_context_data(self, **kwargs):
        context = super(UserExamRecordUpdate, self).get_context_data(**kwargs)
        record = UserExamRecord.objects.get(id=self.kwargs["pk"])
        context["record"] = record
        return context

    def form_valid(self, form):
        old_record = UserExamRecord.objects.get(id=self.kwargs["pk"])
        old_status = old_record.status
        new_status = form.cleaned_data['status']
        if not old_status == new_status:
            if new_status in [1, "1"]:
                title = "【" + old_record.grade_name + "】考试已通过"
            elif new_status in [2, "2"]:
                title = "【" + old_record.grade_name + "】考试未通过"
            elif new_status in [3, "3"]:
                title = "【" + old_record.grade_name + "】考试已关闭"
            else:
                title = "【" + old_record.grade_name + '】考级状态变更'
            send_message_signal.send(sender=UserExamRecord, user_exam_record=old_record, title=title)
            add_user_track_signal.send(sender=UserExamRecord, user_exam_record=old_record, title=title)
        self.success_url = reverse_lazy("bee_django_exam:user_exam_record_list", kwargs={"user_id": old_record.user.id})
        return super(UserExamRecordUpdate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='UserCertCreate'), name='dispatch')
class UserCertCreate(TemplateView):
    def post(self, request, *args, **kwargs):
        record_id = self.kwargs["record_id"]
        record = UserExamRecord.objects.get(id=record_id)
        res, msg, cert_path = Cert().create_cert(grade=record.grade, record=record)
        return JSONResponse(json.dumps({"res": res, "msg": msg}, ensure_ascii=False))
        # return super(UserCertCreate,self).post(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='UserCertUpload'), name='dispatch')
class UserCertUpload(CreateView):
    model = UserExamRecord
    form_class = UserExamRecordCertUploadForm
    template_name = 'bee_django_exam/record/user_record_cert_upload.html'
    success_url = None

    def form_valid(self, form):
        cert = form.cleaned_data['cert']

        self.success_url = reverse_lazy("bee_django_exam:user_exam_record_detail", kwargs=self.kwargs)
        return super(UserCertUpload, self).form_valid(form)
