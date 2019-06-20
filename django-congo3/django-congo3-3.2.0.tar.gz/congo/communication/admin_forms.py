# -*- coding: utf-8 -*-
from django import forms

class SimpleEmailMessageForm(forms.Form):
    subject = forms.CharField(max_length = 100, label = "Temat")
    sender_email = forms.EmailField(label = "E-mail nadawcy")
    sender_name = forms.CharField(max_length = 100, required = False, label = "Nazwa nadawcy")
    recipient_email = forms.EmailField(label = "E-mail odbiorcy")
    recipient_name = forms.CharField(max_length = 100, required = False, label = "Nazwa odbiorcy")
    content = forms.CharField(widget = forms.Textarea, label = "Wiadomość")
    html_mimetype = forms.BooleanField(required = False, label = "Format HTML")
    attachments = forms.FileField(widget = forms.ClearableFileInput(attrs = {'multiple': True}), required = False, label = "Załączniki")
