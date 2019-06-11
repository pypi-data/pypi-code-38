#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import json, qrcode, os, shutil, urllib
from datetime import timedelta

from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.six import BytesIO
from django.apps import apps
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model, get_user
from django.utils import timezone

from .forms import PreuserCreateForm, PreuserCouponCreateForm, PreuserUpdateAdminForm, PreuserUpdateUserForm, \
    RegCodeCheckForm, \
    ApplicationQuestionCreateForm, \
    ApplicationOptionCreateForm, SourceForm, SourceUpdateForm, SourceSearchForm, PreuserTrackForm, PreuserSearchForm, \
    ContractForm, \
    ContractUpdateAgreementForm, \
    PreuserContractForm, \
    PosterCreateForm, PosterUpdateForm, PreuserFeeForm, PreuserFeeSearchForm, PreuserContractAgreementForm, \
    PreuserContractSearchForm
from .models import PreUser, RegCode, ApplicationQuestion, ApplicationOption, PreUserApplication, Source, PreUserTrack, \
    Contract, \
    PreUserContract, Poster, PreUserFee
from .models import get_user_name_field
from .decorators import cls_decorator, func_decorator
from utils import get_referral_user_name_with_user, JSONResponse, get_now, get_track_list, get_contract_list, \
    get_fee_list, \
    export_csv, create_qrcode, merge_img, get_landing_url_list, get_after_check_url, change_tz, LOCAL_TIMEZONE
from exports import get_poster_show_list
from django.contrib.auth.decorators import login_required, permission_required
# from .signals import contrack_checked

User = get_user_model()


# Create your views here.
@func_decorator("test")
def test(request):
    # PreUserContract.migrate_to_fee()
    preuser_list = PreUser.objects.all()
    return HttpResponse("ok")
    # preuser_id = request.GET.get("preuser_id")
    # preuser_contract_id = request.GET.get("preuser_contract_id")
    # from exports import after_check_callback
    # after_check_callback(preuser_contract_id)
    # return HttpResponse("success:preuser_id=" + preuser_id + ",preuser_contract_id=" + preuser_contract_id)


def migrate_to_fee(request):
    PreUserContract().migrate_to_fee()
    return HttpResponse('OK')


# =======preuser=======
@method_decorator(cls_decorator(cls_name='PreuserList'), name='dispatch')
class PreuserList(ListView):
    template_name = 'bee_django_crm/preuser/preuser_list.html'
    context_object_name = 'preuser_list'
    paginate_by = 20
    http_method_names = [u'get', u"post"]
    queryset = None

    def search(self):
        level = self.request.GET.get("level")
        name = self.request.GET.get("name")
        mobile = self.request.GET.get("mobile")
        contract = self.request.GET.get("contract")
        source_name = self.request.GET.get("source_name")
        referral_name1 = self.request.GET.get("referral_name1")
        province = self.request.GET.get("province")
        city = self.request.GET.get("city")
        grade = self.request.GET.get("grade")

        # 检查权限
        if not self.request.user.has_perm("bee_django_crm.view_crm_preuser"):
            return []
        queryset=PreUser.objects.all().order_by("-created_at")
        if not level in ["", 0, None, "0"]:
            queryset = queryset.filter(level=level)
        if not name in ["", 0, None]:
            queryset = queryset.filter(name__icontains=name)
        if not mobile in ["", 0, None]:
            queryset = queryset.filter(mobile__icontains=mobile)
        if not contract in ["", 0, None]:
            queryset = queryset.filter(preusercontract__contract=contract).distinct()
        if not source_name in ["", 0, None]:
            queryset = queryset.filter(source__name__icontains=source_name)
        if not province in ["", 0, None]:
            queryset = queryset.filter(province=province)
        if not city in ["", 0, None]:
            queryset = queryset.filter(city=city)
        if not referral_name1 in ["", 0, None]:
            try:
                kwargs = {}  # 动态查询的字段
                name_field = get_user_name_field()
                kwargs["referral_user1__" + name_field + '__icontains'] = referral_name1
                queryset = queryset.filter(**kwargs)
            except:
                queryset = queryset
        if not grade in ["-1", None, ""]:
            if grade in ["0"]:
                queryset = queryset.filter(Q(grade=0) | Q(grade__isnull=True))
            else:
                queryset = queryset.filter(grade=grade)
        return queryset

    def get_queryset(self):
        super(PreuserList, self).get_queryset()
        return self.search()

    def get_context_data(self, **kwargs):
        context = super(PreuserList, self).get_context_data(**kwargs)
        level = self.request.GET.get("level")
        name = self.request.GET.get("name")
        mobile = self.request.GET.get("mobile")
        contract = self.request.GET.get("contract")
        source_name = self.request.GET.get("source_name")
        referral_name1 = self.request.GET.get("referral_name1")
        province = self.request.GET.get("province")
        city = self.request.GET.get("city")
        grade = self.request.GET.get("grade")
        context['level'] = level
        context['search_form'] = PreuserSearchForm(
            {"level": level, "name": name, "mobile": mobile, "contract": contract, "source_name": source_name,
             "referral_name1": referral_name1,
             "province": province, "city": city, "grade": grade})
        return context

    def get(self, request, *args, **kwargs):
        self.queryset = self.search()
        if request.GET.get("export"):
            rows = ([
                        (i + 1).__str__(),
                        preuser.get_level(),
                        preuser.name,
                        preuser.get_gender(),
                        preuser.mobile,
                        preuser.wx,
                        preuser.birthday,
                        preuser.get_source(),
                        get_referral_user_name_with_user(preuser.referral_user1_id) if get_referral_user_name_with_user(
                            preuser.referral_user1_id) else "",
                        preuser.province,
                        preuser.city,
                        preuser.address
                    ] for i, preuser in enumerate(self.queryset))
            headers = [
                '序号'.encode('utf-8'),
                '级别'.encode('utf-8'),
                '姓名'.encode('utf-8'),
                '性别'.encode('utf-8'),
                '电话'.encode('utf-8'),
                '微信'.encode('utf-8'),
                '生日'.encode('utf-8'),
                '来源'.encode('utf-8'),
                '推荐人'.encode('utf-8'),
                '省'.encode('utf-8'),
                '市'.encode('utf-8'),
                '地址'.encode('utf-8')
            ]
            return export_csv('crm用户'.encode('utf-8'), headers, rows)
        else:

            self.queryset = self.search()
            return super(PreuserList, self).get(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='PreuserDetail'), name='dispatch')
class PreuserDetail(DetailView):
    model = PreUser
    template_name = 'bee_django_crm/preuser/preuser_detail.html'
    context_object_name = 'preuser'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PreuserDetail, self).get_context_data(**kwargs)
        preuser_id = kwargs["object"].pk

        context['application'] = PreUserApplication.objects.filter(preuser_id=preuser_id)
        context['track_list'] = get_track_list(preuser_id)
        context['contract_list'] = get_contract_list(preuser_id)
        context['fee_list'] = get_fee_list(preuser_id)
        return context

        # def get_json(cls, self,request, *args, **kwargs):
        #     from django.core import serializers
        #     res=serializers.serialize("json", {'data': self.get_queryset()})
        #     return HttpResponse(res, content_type='application/json')


# class PreuserAPIDetail(PreuserDetail):
#     def get(self, request, *args, **kwargs):
#         from django.core import serializers
#         res=serializers.serialize("json", {'data': self.get_queryset()})
#         return HttpResponse(res, content_type='application/json')


# def get_context_data(self, **kwargs):
#     print(kwargs)
#     # Call the base implementation first to get a context
#     context = super(PreuserDetail, self).get_context_data(**kwargs)
#     # Add in a QuerySet of all the books
#     context['preuser'] = get_object_or_404(PreUser,pk=kwargs['pk'])
#     return context



@method_decorator(cls_decorator(cls_name='PreuserCreate'), name='dispatch')
@method_decorator(permission_required('bee_django_crm.add_preuser'), name='dispatch')
class PreuserCreate(CreateView):
    model = PreUser
    form_class = PreuserCreateForm
    template_name = 'bee_django_crm/preuser/preuser_form.html'
    success_url = reverse_lazy('bee_django_crm:preuser_list')

    def form_valid(self, form):
        self.success_url += '?level=1'
        return super(PreuserCreate, self).form_valid(form)

        # def get(self, request, *args, **kwargs):
        #     # 权限
        #     if not self.request.user.has_perm("bee_django_crm.can_add_preuser"):
        #         return []
        #     return super(PreuserCreate, self).get(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='PreuserReg'), name='dispatch')
class PreuserReg(CreateView):
    model = PreUser
    form_class = PreuserCreateForm
    template_name = 'bee_django_crm/preuser/preuser_reg_form.html'
    success_url = reverse_lazy('bee_django_crm:preuser_reg_done')

    def get_context_data(self, **kwargs):
        context = super(PreuserReg, self).get_context_data(**kwargs)
        try:
            source = Source.objects.get(id=self.request.GET.get("source_id"))
            source_reg_name = source.reg_name
        except:
            source_reg_name = ''
        context["source_reg_name"] = source_reg_name
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        source_id = self.request.GET.get("source_id")
        try:
            source = Source.objects.get(pk=source_id)
        except:
            source = None
        referral_user_id1 = self.request.GET.get("referral_user_id1")
        referral_user_id2 = self.request.GET.get("referral_user_id2")
        preuser = form.save(commit=False)
        preuser.source = source
        preuser.referral_user1_id = referral_user_id1
        preuser.referral_user2_id = referral_user_id2
        preuser.save()
        messages.success(self.request, '报名已成功')
        return super(PreuserReg, self).form_valid(form)


class PreuserRegCode(CreateView):
    model = PreUser
    form_class = PreuserCouponCreateForm
    template_name = 'bee_django_crm/preuser/preuser_reg_coupon_form.html'
    success_url = reverse_lazy('bee_django_crm:preuser_reg_done')
    #
    # def get_context_data(self, **kwargs):
    #     context = super(PreuserRegCode, self).get_context_data(**kwargs)
    #
    #     return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        code = form.cleaned_data['code']
        password = form.cleaned_data['password']
        try:
            code = RegCode.objects.get(reg_name__exact=code, reg_code__exact=password)
            if code.used_at or code.used_preuser:
                messages.error(self.request, '该卡密已经被使用过，请重新填写卡密')
                return redirect(reverse_lazy("bee_django_crm:preuser_reg_done"))
            else:
                preuser = form.save(commit=False)
                preuser.level = 4
                preuser.save()
                code.used_preuser = preuser
                code.used_at = timezone.now()
                code.save()
                messages.success(self.request, '报名已成功')
        except:
            messages.error(self.request, '卡号或密码不正确，请重新填写卡密')
            return redirect(reverse_lazy("bee_django_crm:preuser_reg_done"))

        return super(PreuserRegCode, self).form_valid(form)


# 注册成功页
@func_decorator('preuser_reg_done')
def preuser_reg_done(request):
    return render(request, 'bee_django_crm/preuser/preuser_reg_done.html')


@func_decorator('update_preuser')
def update_preuser(request, pk):
    preuser = get_object_or_404(PreUser, pk=pk)

    if request.POST:
        form = PreuserUpdateAdminForm(data=request.POST, preuser=preuser, instance=preuser)
        if form.is_valid():
            preuser = form.save(commit=False)
            referral_user_id1 = form.cleaned_data['referral_user_id1']
            referral_user_id2 = form.cleaned_data['referral_user_id2']
            try:
                referral_user1 = User.objects.get(id=referral_user_id1)
            except:
                referral_user1 = None
            try:
                referral_user2 = User.objects.get(id=referral_user_id2)
            except:
                referral_user2 = None
            preuser.referral_user1 = referral_user1
            preuser.referral_user2 = referral_user2
            preuser.save()
            return redirect(reverse('bee_django_crm:preuser_detail', kwargs={'pk': preuser.id}))
        else:
            pass
    else:
        form = PreuserUpdateAdminForm(instance=preuser, preuser=preuser)

    return render(request, template_name='bee_django_crm/preuser/preuser_form.html', context={
        'form': form,
    })


@method_decorator(cls_decorator(cls_name='PreuserUpdate'), name='dispatch')
# class PreuserUpdate(UpdateView):
#     model = PreUser
#     # form_class = PreuserUpdateAdminForm
#     template_name = 'bee_django_crm/preuser/preuser_form.html'
#     fields = ['name', "mobile", "gender", "grade", "wx", "birthday", "province", "city", "address", 'source',
#               # fields = ['name', "mobile", "gender", "grade", "wx", "birthday", "province", "city", "address",
#               "email", "job", "hobby", "married", "children", "job_info", "family"]
#
#     def get_context_data(self, **kwargs):
#         context = super(PreuserUpdate, self).get_context_data(**kwargs)
#         # source = get_preuser_source(self.kwargs["pk"])
#         # context["source"] = get_preuser_source(self.kwargs["pk"])
#         # preuser = PreUser.objects.get(id=self.kwargs["pk"])
#         # print(preuser)
#         # self.form_class=PreuserUpdateAdminForm(preuser)
#         # context["preuser_form"] = PreuserUpdateAdminForm(preuser)
#         context["form"] = PreuserUpdateAdminForm(instance=self.object, preuser=None)
#         # print("context")
#         # print(source)
#
#         return context
#
#     def form_valid(self, form):
#         # This method is called when valid form data has been POSTed.
#         # It should return an HttpResponse.
#         preuser = form.save(commit=False)
#         referral_user_id = form.cleaned_data['referral_user_id']
#         preuser.referral_user_id = referral_user_id
#         # if form.cleaned_data["source"] in ["",None]:
#         #     source =
#         #     form.cleaned_data
#         preuser.save()
#         return super(PreuserUpdate, self).form_valid(form)
#
#         # def get(self, request, *args, **kwargs):
#         #     form_class = self.get_form_class()
#         #     form = self.get_form(form_class)
#         #     print(form_class,form)
#         #     return super(PreuserUpdate, self).get(request, *args, **kwargs)
#
#         # self.fields['Unit'].queryset = Units.objects.filter(status = 200, parent__id = 2)
@method_decorator(permission_required('bee_django_crm.delete_preuser'), name='dispatch')
class PreuserDelete(DeleteView):
    model = PreUser
    success_url = reverse_lazy('bee_django_crm:preuser_list')
    # permission_required = 'archives.delete_link'

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)
        #
        #
        # template_name = 'preuser_confirm_delete.html'


# api
def get_name_with_user(request):
    id = request.GET.get("id")
    name = get_referral_user_name_with_user(id)
    return JSONResponse(json.dumps({"name": name}, ensure_ascii=False))


# =======preuser end=======

# ======reg code=======
class RegCodeCheck(TemplateView):
    template_name = 'bee_django_crm/regcode/check_form.html'

    def get_regcode(self):
        reg_name = self.request.GET.get("reg_name")
        reg_code = self.request.GET.get("reg_code")
        # 验证卡密
        if reg_name and reg_code:
            if self.request.user.has_perm("bee_django_crm.can_ckeck_code"):
                try:
                    code = RegCode.objects.get(reg_name__exact=reg_name, reg_code__exact=reg_code)
                    return code
                except:
                    messages.error(self.request, '卡号或密码不正确')
                    return None
            else:
                messages.error(self.request, '没有权限')
                return None
        # 获取密码
        elif reg_name:
            if self.request.user.has_perm("bee_django_crm.can_get_code"):
                try:
                    code = RegCode.objects.get(reg_name__exact=reg_name)
                    return code
                except:
                    messages.error(self.request, '卡号不正确')
                    return None
            else:
                messages.error(self.request, '没有权限')
                return None
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super(RegCodeCheck, self).get_context_data(**kwargs)
        reg_name = self.request.GET.get("reg_name")
        reg_code = self.request.GET.get("reg_code")
        context["form"] = RegCodeCheckForm({"reg_name":reg_name,"reg_code":reg_code})
        context["regcode"] = self.get_regcode()
        return context


    # def get(self, request, *args, **kwargs):




# ========source===========
@method_decorator(permission_required('bee_django_crm.view_crm_source'), name='dispatch')
class SourceList(ListView):
    model = Source
    template_name = 'bee_django_crm/source/source_list.html'
    context_object_name = 'source_list'
    paginate_by = 20
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(SourceList, self).get_context_data(**kwargs)
        name = self.request.GET.get("name")
        context["poster_source"] = Source.objects.filter(is_poster=True)
        context["show_poster_count"] = len(get_poster_show_list())
        context["search_form"] = SourceSearchForm({"name": name})
        return context

    def search(self):
        name = self.request.GET.get("name")
        queryset = Source.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        self.queryset = queryset
        return queryset

    def get(self, request, *args, **kwargs):
        self.queryset = self.search()
        return super(SourceList, self).get(request)


@method_decorator(cls_decorator(cls_name='SourceDetail'), name='dispatch')
class SourceDetail(DetailView):
    model = Source
    template_name = 'bee_django_crm/source/source_detail.html'
    context_object_name = 'source'

    def get_context_data(self, **kwargs):
        context = super(SourceDetail, self).get_context_data(**kwargs)
        url_list = get_landing_url_list()
        landing_url_arg_list = []
        args = "?source_id=" + self.kwargs['pk'].__str__()
        if url_list:
            for url in url_list:
                landing_url_arg_list.append(url + args)

        reg_url = "http://" + self.request.META['HTTP_HOST'] + reverse(
            'bee_django_crm:preuser_reg') + args
        context["landing_url_arg_list"] = landing_url_arg_list
        context["reg_url"] = reg_url
        return context


# 获取二维码图片
# qrcode_type landing/reg
def source_qrcode(request, qrcode_type, source_id, landing_id=None):
    landing_url_list = get_landing_url_list()
    args = "?source_id=" + source_id.__str__()
    # print(landing_id, type(landing_id))
    if landing_id:
        landing_id = int(landing_id)
    url = None
    if qrcode_type == 'landing':
        url = landing_url_list[landing_id] + args
    elif qrcode_type == 'reg':
        url = "http://" + request.META['HTTP_HOST'] + reverse(
            'bee_django_crm:preuser_reg') + args
    if url:
        qrcode_image = qrcode.make(url)
        buf = BytesIO()
        qrcode_image.save(buf)
        image_stream = buf.getvalue()
        response = HttpResponse(image_stream, content_type="image/png")
        return response


def qrcode_img(request, url):
    # print(url)
    if url:
        url = urllib.urlencode(url)
        # print(url)
        qrcode_image = qrcode.make(url)
        buf = BytesIO()
        qrcode_image.save(buf)
        image_stream = buf.getvalue()
        response = HttpResponse(image_stream, content_type="image/png")
        return response


@method_decorator(cls_decorator(cls_name='SourceCreate'), name='dispatch')
class SourceCreate(CreateView):
    model = Source
    form_class = SourceForm
    template_name = 'bee_django_crm/source/source_form.html'


@method_decorator(cls_decorator(cls_name='SourceUpdate'), name='dispatch')
class SourceUpdate(UpdateView):
    model = Source
    form_class = SourceUpdateForm
    template_name = 'bee_django_crm/source/source_form.html'

    def get_context_data(self, **kwargs):
        context = super(SourceUpdate, self).get_context_data(**kwargs)
        context["source"] = Source.objects.get(id=self.kwargs["pk"])
        return context


@method_decorator(cls_decorator(cls_name='SourceDelete'), name='dispatch')
class SourceDelete(DeleteView):
    model = Source
    success_url = reverse_lazy('bee_django_crm:source_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# =======source end=======

# =======preuser tract=======
@method_decorator(cls_decorator(cls_name='PreuserTrackCreate'), name='dispatch')
class PreuserTrackCreate(CreateView):
    model = PreUserTrack
    form_class = PreuserTrackForm
    template_name = 'bee_django_crm/preuser/preuser_track_form.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        preuser_id = self.kwargs['preuser_id']
        track = form.save(commit=False)
        track.user_id = preuser_id
        try:
            track.created_by = form.request.user
        except:
            track.created_by = None
        track.save()
        # self.success_url = reverse_lazy("bee_django_crm:application_question_detail", kwargs={'pk': question_id})
        return super(PreuserTrackCreate, self).form_valid(form)


# =======preuser tract end=======

# =======application question=======
@method_decorator(permission_required('bee_django_crm.view_crm_application'), name='dispatch')
class ApplicationQuestionList(ListView):
    template_name = 'bee_django_crm/application/application_question_list.html'
    context_object_name = 'question_list'
    paginate_by = 20
    queryset = ApplicationQuestion.objects.all()


@method_decorator(cls_decorator(cls_name='ApplicationQuestionDetail'), name='dispatch')
class ApplicationQuestionDetail(DetailView):
    model = ApplicationQuestion
    template_name = 'bee_django_crm/application/application_question_detail.html'
    context_object_name = 'question'


@method_decorator(cls_decorator(cls_name='ApplicationQuestionCreate'), name='dispatch')
class ApplicationQuestionCreate(CreateView):
    model = ApplicationQuestion
    form_class = ApplicationQuestionCreateForm
    template_name = 'bee_django_crm/application/application_question_form.html'
    success_url = reverse_lazy("bee_django_crm:application_question_list")


@method_decorator(cls_decorator(cls_name='ApplicationQuestionUpdate'), name='dispatch')
class ApplicationQuestionUpdate(UpdateView):
    model = ApplicationQuestion
    form_class = ApplicationQuestionCreateForm
    template_name = 'bee_django_crm/application/application_question_form.html'


@method_decorator(cls_decorator(cls_name='ApplicationQuestionDelete'), name='dispatch')
class ApplicationQuestionDelete(DeleteView):
    model = ApplicationQuestion
    success_url = reverse_lazy('bee_django_crm:application_question_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# =====application option =========
@method_decorator(cls_decorator(cls_name='ApplicationOptionCreate'), name='dispatch')
class ApplicationOptionCreate(CreateView):
    model = ApplicationOption
    form_class = ApplicationOptionCreateForm
    template_name = 'bee_django_crm/application/application_option_form.html'
    success_url = ""

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        question_id = self.kwargs['pk']
        option = form.save(commit=False)
        option.question_id = question_id
        option.save()
        self.success_url = reverse_lazy("bee_django_crm:application_question_detail", kwargs={'pk': question_id})
        return super(ApplicationOptionCreate, self).form_valid(form)


# ========preuser application =======


@method_decorator(cls_decorator(cls_name='PreuserApplicationView'), name='dispatch')
class PreuserApplicationView(TemplateView):
    template_name = "bee_django_crm/preuser/preuser_application_form.html"

    def get_context_data(self, **kwargs):
        context = super(PreuserApplicationView, self).get_context_data(**kwargs)
        questions = ApplicationQuestion.objects.all()
        application_list = []
        for question in questions:
            question_dict = {"question": question}
            options = question.applicationoption_set.all()
            question_dict["options"] = options
            application_list.append(question_dict)
        context["application_list"] = application_list
        return context

    def post(self, request, *args, **kwargs):
        preuser_id = request.POST.get("preuser_id")
        questions = ApplicationQuestion.objects.all()
        post_dict = MultiValueDict(request.POST)
        preuser = get_object_or_404(PreUser, pk=preuser_id)
        for i, question in enumerate(questions):
            id = i + 1
            value_list = post_dict.getlist("input_" + id.__str__())
            # if len(value_list) == 0:
            #     return JSONResponse(json.dumps({"error": "error"}, ensure_ascii=False))
            value_str = ','.join(value_list)
            try:
                a = PreUserApplication.objects.get(preuser=preuser, question=question)
            except:
                a = PreUserApplication()
                a.preuser = preuser
                a.question = question
            a.answer = value_str
            a.save()
        if preuser.level < 3:
            preuser.level = 2
        preuser.applied_at = get_now()
        preuser.save()
        return redirect(reverse_lazy('bee_django_crm:preuser_application_update_preuser', kwargs={'pk': preuser.id}))


# 填申请表第二步：更新个人信息
@method_decorator(cls_decorator(cls_name='PreuserApplicationUpdate'), name='dispatch')
class PreuserApplicationUpdate(UpdateView):
    model = PreUser
    form_class = PreuserUpdateUserForm
    template_name = 'bee_django_crm/preuser/preuser_update_form.html'
    success_url = reverse_lazy('bee_django_crm:preuser_application_done')


# 填申请表完成页面
@func_decorator("preuser_application_done")
def preuser_application_done(request):
    return render(request, 'bee_django_crm/preuser/preuser_application_done.html')


# ========preuser application end===========


# ========countract============
@method_decorator(permission_required('bee_django_crm.view_crm_contract'), name='dispatch')
class ContractList(ListView):
    model = Contract
    template_name = 'bee_django_crm/contract/contract_list.html'
    context_object_name = 'contract_list'
    paginate_by = 20


class ContractDetail(DetailView):
    model = Contract
    template_name = 'bee_django_crm/contract/contract_detail.html'
    context_object_name = 'contract'


@method_decorator(cls_decorator(cls_name='ContractCreate'), name='dispatch')
class ContractCreate(CreateView):
    model = Contract
    form_class = ContractForm
    template_name = 'bee_django_crm/contract/contract_form.html'


@method_decorator(cls_decorator(cls_name='ContractUpdate'), name='dispatch')
class ContractUpdate(UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = 'bee_django_crm/contract/contract_form.html'


class ContractUpdateAgreement(UpdateView):
    model = Contract
    form_class = ContractUpdateAgreementForm
    template_name = 'bee_django_crm/contract/contract_agreement_form.html'


@method_decorator(cls_decorator(cls_name='ContractDelete'), name='dispatch')
class ContractDelete(DeleteView):
    model = Contract
    success_url = reverse_lazy('bee_django_crm:contract_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# =======contract end=======



# ========preuser countract===========
@method_decorator(permission_required('bee_django_crm.view_crm_preuser_contract'), name='dispatch')
class PreuserContractList(ListView):
    template_name = 'bee_django_crm/preuser/preuser_contract_list.html'
    context_object_name = 'preuser_contract_list'
    paginate_by = 20
    queryset = None
    preuser_id = None

    def search(self):
        self.preuser_id = self.kwargs["preuser_id"]
        if not self.preuser_id in [0, None, "0"]:
            queryset = PreUserContract.objects.filter(preuser_id=self.preuser_id)
        else:
            queryset = PreUserContract.objects.all()

        name = self.request.GET.get("name")
        contract_id = self.request.GET.get("contract")
        if name:
            queryset = queryset.filter(preuser__name__icontains=name)
        if contract_id:
            queryset = queryset.filter(contract_id=contract_id)
        self.queryset = queryset
        return queryset

    def get(self, request, *args, **kwargs):
        self.queryset = self.search()
        return super(PreuserContractList, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(PreuserContractList, self).get_context_data(**kwargs)
        try:
            preuser = PreUser.objects.get(id=self.preuser_id)
            context["preuser"] = preuser
        except:
            context["preuser"] = None
        name = self.request.GET.get("name")
        contract_id = self.request.GET.get("contract")
        context['search_form'] = PreuserContractSearchForm(
            {"name": name, "contract": contract_id})
        return context


@method_decorator(cls_decorator(cls_name='PreuserContractDetail'), name='dispatch')
class PreuserContractDetail(DetailView):
    model = PreUserContract
    template_name = 'bee_django_crm/preuser/preuser_contract_detail.html'
    context_object_name = 'preuser_contract'

    # def get_context_data(self, **kwargs):
    #     context = super(PreuserContractDetail, self).get_context_data(**kwargs)
    #     after_check_url = get_after_check_url(self.request.user,)
    #     if not settings.CRM_AFTER_CHECK_URL in ["", None]:
    #         after_check_url = settings.CRM_AFTER_CHECK_URL
    #     context["after_check_url"] = after_check_url
    #     return context


class PreuserContractAgreement(TemplateView):
    model = PreUserContract
    template_name = 'bee_django_crm/preuser/preuser_contract_agree.html'
    context_object_name = 'preuser_contract'

    def get_context_data(self, **kwargs):
        context = super(PreuserContractAgreement, self).get_context_data(**kwargs)
        preuser_contract_id = self.kwargs["preuser_contract_id"]
        preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        if preuser_contract.is_user_agree:
            context['is_user_agree'] = True
        else:
            context["form"] = PreuserContractAgreementForm()
            context["preuser_contract"] = preuser_contract
            context['is_user_agree'] = False
        return context

    def post(self, request, *args, **kwargs):
        form = PreuserContractAgreementForm(request.POST)
        if form.is_valid():
            preuser_contract_id = self.kwargs["preuser_contract_id"]
            preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
            preuser_contract.is_user_agree = True
            preuser_contract.save()
            return redirect(reverse('bee_django_crm:preuser_contract_agreement', kwargs=self.kwargs))


# @method_decorator(cls_decorator(cls_name='PreuserAllContractList'), name='dispatch')
# class PreuserAllContractList(ListView):
#     template_name = 'bee_django_crm/preuser/preuser_all_contract_list.html'
#     context_object_name = 'preuser_all_contract_list'
#     paginate_by = 20
#     queryset = PreUserContract.objects.all()
#
#     def get_context_data(self, **kwargs):
#         context = super(PreuserAllContractList, self).get_context_data(**kwargs)
#         _dict = self.queryset.aggregate(total_price=Sum('price'))
#         total_price = 0
#         if _dict.has_key("total_price"):
#             if _dict["total_price"] > 0:
#                 total_price = _dict["total_price"]
#         context["total_price"] = total_price
#         after_check_url = None
#         if not settings.CRM_AFTER_CHECK_URL in ["", None]:
#             after_check_url = settings.CRM_AFTER_CHECK_URL
#         context["after_check_url"] = after_check_url
#         return context


@method_decorator(cls_decorator(cls_name='PreuserContractCreate'), name='dispatch')
class PreuserContractCreate(CreateView):
    model = PreUserContract
    form_class = PreuserContractForm
    template_name = 'bee_django_crm/preuser/preuser_contract_form.html'
    success_url = ""

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        preuser_id = self.kwargs['preuser_id']
        u_contract = form.save(commit=False)
        u_contract.preuser_id = preuser_id
        u_contract.is_migrate = True
        u_contract.save()
        self.success_url = reverse_lazy("bee_django_crm:preuser_contract_list", kwargs={'preuser_id': preuser_id})
        return super(PreuserContractCreate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='PreuserContractUpdate'), name='dispatch')
class PreuserContractUpdate(UpdateView):
    model = PreUserContract
    form_class = PreuserContractForm
    template_name = 'bee_django_crm/preuser/preuser_contract_form.html'
    preuser_id = None
    success_url = None

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        preuser_contract_id = self.kwargs['pk']
        preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        self.preuser_id = preuser_contract.preuser.pk
        self.success_url = reverse_lazy('bee_django_crm:preuser_contract_list', kwargs={'preuser_id': self.preuser_id})
        return super(PreuserContractUpdate, self).form_valid(form)


# @method_decorator(cls_decorator(cls_name='ContractCheckCallBack'), name='dispatch')
# class ContractCheckCallBack(TemplateView):
#     def get(self, request, *args, **kwargs):
#         try:
#             preuser_contract_id = request.GET.get("preuser_contract_id")
#             preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
#             preuser_contract.is_checked = True
#             preuser_contract.checked_at = get_now()
#             preuser_contract.checked_by_id = request.user.pk
#             preuser_contract.save()
#             error = 0
#             msg = ""
#         except Exception as e:
#             error = 1
#             msg = e.__str__()
#         return JSONResponse(json.dumps({"error": error, "msg": msg}, ensure_ascii=False))


@method_decorator(cls_decorator(cls_name='PreuserContractDelete'), name='dispatch')
class PreuserContractDelete(DeleteView):
    model = PreUserContract
    success_url = None
    preuser_id = None

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        preuser_contract_id = self.kwargs['pk']
        preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        self.preuser_id = preuser_contract.preuser.pk
        self.success_url = reverse_lazy('bee_django_crm:preuser_contract_list', kwargs={'preuser_id': self.preuser_id})
        return super(PreuserContractDelete, self).post(request)

        # @decorator("PreuserContractDelete")
        # def form_valid(self, form):
        #     # This method is called when valid form data has been POSTed.
        #     # It should return an HttpResponse.
        #     preuser_contract_id = self.kwargs['pk']
        #     preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        #     self.preuser_id = preuser_contract.preuser.pk
        #     self.success_url = reverse_lazy('bee_django_crm:preuser_contract_list', kwargs={'preuser_id': self.preuser_id})
        #     return super(PreuserContractDelete, self).form_valid(form)


# =======contract end=======
# =======poster======


# def photo_upload(request):
#     if request.method == 'POST':
#         form = PhotoCreateForm(request.POST, request.FILES)
#         if form.is_valid():
#             # file is saved
#             form.save()
#             return HttpResponseRedirect('/success/url/')
#     else:
#         form = PhotoCreateForm()
#     return render_to_response('poster/photo_form.html', {'form': form})
#
#
# def handle_uploaded_file(f):
#     with open(os.path.join(settings.POSTER_PHOTO_PATH, 'temp_photo.jpg'), 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)

@method_decorator(cls_decorator(cls_name='PosterCreate'), name='dispatch')
class PosterCreate(CreateView):
    model = Poster
    form_class = PosterCreateForm
    template_name = 'bee_django_crm/poster/poster_create_form.html'
    success_url = None


    # def get(self, request, *args, **kwargs):
    #     print(args, kwargs)
    #     source_id = kwargs["source_id"]
    #     return super(PosterCreate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PosterCreate, self).get_context_data(**kwargs)
        source_id = self.kwargs["source_id"]
        source = Source.objects.get(id=source_id)
        context["poster_name"] = source.name
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        poster = form.save(commit=False)
        source_id = self.kwargs["source_id"]
        poster.source_id = source_id
        poster.save()
        self.success_url = reverse_lazy('bee_django_crm:poster_update', kwargs={'pk': poster.pk})
        return super(PosterCreate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='PosterUpdate'), name='dispatch')
class PosterUpdate(UpdateView):
    model = Poster
    form_class = PosterUpdateForm
    template_name = 'bee_django_crm/poster/poster_update_form.html'
    success_url = None

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        poster = form.save(commit=True)
        self.success_url = reverse_lazy('bee_django_crm:poster_update',
                                        kwargs={'pk': poster.pk})
        return super(PosterUpdate, self).form_valid(form)


# @func_decorator("poster_generate")
# def poster_generate(request, poster_id):
#     if settings.CRM_USER_TABLE in ["", None]:
#         user_model = User
#     else:
#         app_name = settings.CRM_USER_TABLE.split(".")[0]
#         model_name = settings.CRM_USER_TABLE.split(".")[1]
#         app = apps.get_app_config(app_name)
#         user_model = app.get_model(model_name)
#     users = user_model.objects.all()
#     if not settings.CRM_LANDING_URL in ["", None]:
#         url = settings.CRM_LANDING_URL
#     else:
#         url = "http://" + request.META['HTTP_HOST'] + reverse(
#             'bee_django_crm:preuser_reg')
#     poster = Poster.objects.get(id=poster_id)
#     for user in users:
#         qrcode_img = create_qrcode(url=url + "?source_id=" + poster_id + "&id=" + user.id.__str__(),
#                                    color=poster.qrcode_color)
#         error, msg, img = merge_img(referral_base_path=poster.photo,
#                                     qrcode_img=qrcode_img, qrcode_pos=(poster.qrcode_pos_x, poster.qrcode_pos_y),
#                                     qrcode_size=(poster.qrcode_width, poster.qrcode_height))
#         path = os.path.join(settings.CRM_POSTER_PHOTO_PATH, poster.id.__str__())
#         if not os.path.exists(path):
#             os.mkdir(path)
#         output_referral_path = os.path.join(path, user.id.__str__() + '_poster.jpg')
#         if img:
#             img.save(output_referral_path, quality=70)
#     return JSONResponse(json.dumps({"error": 0, 'count': users.count().__str__()}, ensure_ascii=False))


@method_decorator(cls_decorator(cls_name='PosterList'), name='dispatch')
class PosterList(ListView):
    model = Poster
    template_name = 'bee_django_crm/poster/poster_list.html'
    context_object_name = 'poster_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(PosterList, self).get_context_data(**kwargs)

        return context


@method_decorator(cls_decorator(cls_name='PosterDetail'), name='dispatch')
class PosterDetail(DetailView):
    model = Poster
    template_name = 'bee_django_crm/poster/poster_detail.html'
    context_object_name = 'poster'


@method_decorator(cls_decorator(cls_name='PosterDelete'), name='dispatch')
class PosterDelete(DeleteView):
    model = Poster
    success_url = reverse_lazy('bee_django_crm:poster_list')
    # success_url = reverse_lazy('bee_django_crm:poster_list',kwargs={'pk': question_id})

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# 显示用户的海报
# user_id 用户id
# poster_id 海报id
def user_poster_image(request, user_id, poster_id):
    try:
        poster = Poster.objects.get(id=poster_id)
        source_id = poster.source.id
    except:
        return
    landing_url_list = get_landing_url_list()
    if landing_url_list:
        url = landing_url_list[0]
    else:
        url = "http://" + request.META['HTTP_HOST'] + reverse(
            'bee_django_crm:preuser_reg')
    url += "?source_id=" + source_id.__str__() + "&id=" + user_id.__str__()
    qrcode_img = create_qrcode(url=url,
                               color=poster.qrcode_color)
    error, msg, img = merge_img(referral_base_path=poster.photo,
                                qrcode_img=qrcode_img, qrcode_pos=(poster.qrcode_pos_x, poster.qrcode_pos_y),
                                qrcode_size=(poster.qrcode_width, poster.qrcode_height))
    if img:
        response = HttpResponse(content_type='image/jpg')
        img.save(response, "JPEG")
        return response


# =======poster end =========

# ===========preuser_fee============
@method_decorator(permission_required('bee_django_crm.view_crm_preuser_fee'), name='dispatch')
class PreuserFeeList(ListView):
    model = PreUserFee
    template_name = 'bee_django_crm/preuser/preuser_fee_list.html'
    context_object_name = 'fee_list'
    paginate_by = 20
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(PreuserFeeList, self).get_context_data(**kwargs)
        pay_start = self.request.GET.get("pay_start")
        pay_end = self.request.GET.get("pay_end")
        preuser_pay_status = self.request.GET.get("preuser_pay_status")
        is_checked = self.request.GET.get("is_checked")
        context['search_form'] = PreuserFeeSearchForm(
            {"preuser_pay_status": preuser_pay_status, "pay_start": pay_start, "pay_end": pay_end,
             "is_checked": is_checked})
        _dict = self.search().aggregate(total_price=Sum('price'))
        total_price = 0
        if _dict.has_key("total_price"):
            if _dict["total_price"] > 0:
                total_price = _dict["total_price"]
        context["total_price"] = total_price
        context["preuser_id"] = self.kwargs["preuser_id"]
        return context

    def search(self):
        self.qureyset = PreUserFee.objects.all()
        preuser_id = self.kwargs["preuser_id"]
        if not preuser_id in [0, None, "", "0"]:
            self.qureyset = self.qureyset.filter(preuser_id=preuser_id)
        pay_start = self.request.GET.get("pay_start")
        pay_end = self.request.GET.get("pay_end")
        preuser_pay_status = self.request.GET.get("preuser_pay_status")
        is_checked = self.request.GET.get("is_checked")

        if pay_start:
            self.qureyset = self.qureyset.filter(paid_at__gte=pay_start)
        if pay_end:
            self.qureyset = self.qureyset.filter(paid_at__lte=pay_end)
        if not preuser_pay_status in ["-1", -1, None]:
            self.qureyset = self.qureyset.filter(preuser__pay_status=preuser_pay_status)
        if not is_checked in ["-1", -1, None]:
            self.qureyset = self.qureyset.filter(is_checked=is_checked)
        return self.qureyset

    def get_csv_info(self, fee):
        return [
            fee.preuser.name,
            fee.preuser_contract.contract.name,
            fee.get_pay_status(),
            fee.preuser_contract.price,
            fee.price,
            change_tz(fee.paid_at, tz=LOCAL_TIMEZONE).strftime("%Y-%m-%d"),
            fee.preuser_contract.info,
            fee.info,
        ]

    def get_csv_headers(self):
        return [
            '序号'.encode('utf-8'),
            '姓名'.encode('utf-8'),
            '合同名称'.encode('utf-8'),
            '付款类型'.encode('utf-8'),
            '应缴金额'.encode('utf-8'),
            '实际缴费金额'.encode('utf-8'),
            '缴费日期'.encode('utf-8'),
            '合同备注'.encode('utf-8'),
            '缴费备注'.encode('utf-8'),

        ]

    def get(self, request, *args, **kwargs):
        self.queryset = self.search()
        if request.GET.get("export"):
            rows = ([(i + 1).__str__()] + self.get_csv_info(fee) for i, fee in enumerate(self.queryset))
            return export_csv('缴费信息'.encode('utf-8'), self.get_csv_headers(), rows)
        else:
            return super(PreuserFeeList, self).get(request, *args, **kwargs)


class PreuserFeeDetail(DetailView):
    model = PreUserFee
    template_name = 'bee_django_crm/preuser/preuser_fee_detail.html'
    context_object_name = 'preuser_fee'


@method_decorator(permission_required('bee_django_crm.add_preuserfee'), name='dispatch')
class PreuserFeeCreate(CreateView):
    model = PreUserFee
    form_class = PreuserFeeForm
    template_name = 'bee_django_crm/preuser/preuser_fee_form.html'
    success_url = ""

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        preuser_contract_id = self.kwargs['preuser_contract_id']
        preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        preuser = preuser_contract.preuser

        preuser_fee = form.save(commit=False)
        preuser_fee.preuser_id = preuser.id
        preuser_fee.preuser_contract = preuser_contract
        preuser_fee.save()

        preuser.level = 3
        preuser.save()
        self.success_url = reverse_lazy("bee_django_crm:preuser_contract_detail", kwargs={"pk": preuser_contract_id})
        return super(PreuserFeeCreate, self).form_valid(form)


class PreuserFeeUpdate(UpdateView):
    model = PreUserFee
    form_class = PreuserFeeForm
    template_name = 'bee_django_crm/preuser/preuser_fee_form.html'
    preuser_id = None
    success_url = None

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        preuser_fee_id = self.kwargs['pk']
        preuser_fee = PreUserFee.objects.get(id=preuser_fee_id)
        self.preuser_id = preuser_fee.preuser.pk
        self.success_url = reverse_lazy('bee_django_crm:preuser_fee_list', kwargs={'preuser_id': self.preuser_id})
        return super(PreuserFeeUpdate, self).form_valid(form)


class PreuserFeeDelete(DeleteView):
    model = PreUserFee
    success_url = None

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        preuser_fee_id = self.kwargs['pk']
        preuser_fee = PreUserFee.objects.get(id=preuser_fee_id)
        preuser_contract = preuser_fee.preuser_contract
        self.success_url = reverse_lazy('bee_django_crm:preuser_contract_detail', kwargs={'pk': preuser_contract.id})
        return super(PreuserFeeDelete, self).post(request)


@method_decorator(permission_required('bee_django_crm.can_check_crm_preuser_fee'), name='dispatch')
class PreuserFeeUpdateCheck(TemplateView):
    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        preuser_fee_id = self.kwargs['pk']
        preuser_fee = PreUserFee.objects.get(id=preuser_fee_id)
        preuser_fee.is_checked = True
        preuser_fee.checked_at = get_now()
        preuser_fee.checked_by_id = request.user.pk
        preuser_fee.save()

        preuser = preuser_fee.preuser
        if preuser_fee.pay_status in [1, 4]:
            preuser.pay_status = 1
        elif preuser_fee.pay_status in [2, 3]:
            preuser.pay_status = 2
        preuser.save()

        url = get_after_check_url(request.user, preuser_fee)
        if not url:
            url = reverse('bee_django_crm:preuser_fee_list', kwargs={'preuser_id': 0})
        return JSONResponse(json.dumps({"url": url}, ensure_ascii=False))
