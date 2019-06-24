# -*- coding:utf-8 -*-
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, RedirectView, TemplateView, View

from django_szuprefix.wechat.helper import get_wx_oauth_url

__author__ = 'denishuang'
from . import helper, forms


@csrf_exempt
def ports(request):
    echostr = request.GET.get("echostr")
    api = helper.api
    flag = api.check_tencent_signature(request)
    if flag:
        um = api.deal_post(request.body)
        if um:
            response = HttpResponse(api.response_user(um), "text/xml; charset=utf-8")
            response._charset = "utf-8"
            return response
    return HttpResponse(echostr)


@csrf_exempt
def notice(request):
    return HttpResponse(helper.api.pay_result_notify(request.body))


class LoginView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get("next")


class QRLoginView(TemplateView):
    template_name = "wechat/mp/qrlogin.html"

    def post(self, request, task_id):
        from celery.result import AsyncResult
        import json
        rs = AsyncResult(task_id)
        user = self.request.user
        from django.core.signing import TimestampSigner
        signer = TimestampSigner(salt=user.username)
        password = signer.sign(user.id)
        d = dict(username=user.username, password=password)
        rs.backend.store_result(rs.id, d, 'SUCCESS')
        return HttpResponse("success:%s" % rs)


class TestPayView(FormView):
    template_name = "wechat/mp/test_pay.html"
    form_class = forms.PayInfoForm

    def get_initial(self):
        import time
        return {"title": u"iphone 6手机", "orderId": int(time.time()), "detail": u"土豪金,128G内存", "totalFee": 0.01,
                "notifyUrl": helper.PAID_NOTIFY_URL}

    def form_valid(self, form):
        context = self.get_context_data()
        context['form'] = form
        wxuser = self.request.user.wxusers.first()
        data = helper.api.order(wxuser and wxuser.openId,
                                form.cleaned_data['orderId'],
                                form.cleaned_data['title'],
                                form.cleaned_data['totalFee'],
                                self.request.META['REMOTE_ADDR'],
                                detail=form.cleaned_data['detail'],
                                notifyUrl=form.cleaned_data['notifyUrl']
                                )
        context['JSPayParams'] = helper.api.get_jspay_params(data.get("prepay_id"))
        return self.render_to_response(context)


class LoginQRCodeView(View):
    def get(self, request):
        from django.shortcuts import reverse
        import uuid
        task_id = unicode(uuid.uuid1())
        url = reverse("wechat:mp:qr-login", kwargs=dict(task_id=task_id))
        url = request.build_absolute_uri(url)
        url = get_wx_oauth_url(helper.api.appid, url)
        return JsonResponse({'url': url, 'task': {'id': task_id, 'status': 'RUNNING'}})
