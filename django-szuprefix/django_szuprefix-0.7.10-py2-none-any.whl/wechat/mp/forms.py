# -*- coding:utf-8 -*-
from django import forms


class PayInfoForm(forms.Form):
    orderId = forms.CharField(label=u'编号')
    title = forms.CharField(label=u'标题')
    detail = forms.CharField(label=u'详情')
    totalFee = forms.DecimalField(decimal_places=2, label=u'金额')
    notifyUrl = forms.CharField(label=u'通知接口url')
