# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class SimpleEmailMessageForm(forms.Form):
    subject = forms.CharField(max_length = 100, label = _(u"Temat"))
    sender_email = forms.EmailField(label = _(u"E-mail nadawcy"))
    sender_name = forms.CharField(max_length = 100, required = False, label = _(u"Nazwa nadawcy"))
    recipient_email = forms.EmailField(label = _(u"E-mail odbiorcy"))
    recipient_name = forms.CharField(max_length = 100, required = False, label = _(u"Nazwa odbiorcy"))
    message = forms.CharField(widget = forms.Textarea, label = _(u"Wiadomość"))
    html_mimetype = forms.BooleanField(required = False, label = _(u"HTML MIME type"))
