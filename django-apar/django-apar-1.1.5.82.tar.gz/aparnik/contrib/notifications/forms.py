# -*- coding: utf-8 -*-


from django import forms
from django.contrib.auth import get_user_model

from .models import Notification, NotificationForSingleUser

User = get_user_model()

# class NotificationForm(forms.ModelForm):
#
#     class Meta:
#         model = Notification
#         fields = ('__all__')
#         widgets = {
#             'user': autocomplete.ModelSelect2(url='users:autocomplete')
#         }

class NotificationForAllUserForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = ('__all__')
        # widgets = {
        #     'temp': autocomplete.ModelSelect2(url='users:autocomplete')
        # }

# class NotificationForSingleUserForm(forms.ModelForm):
#
#     single_user = forms.ModelChoiceField(
#         queryset=User.objects.all(),
#         widget=autocomplete.ModelSelect2(url='users:autocomplete'),
#         required=True,
#         label="به یک کاربر"
#     )
#
#     class Meta:
#         model = NotificationForSingleUser
#         fields = ('__all__')
