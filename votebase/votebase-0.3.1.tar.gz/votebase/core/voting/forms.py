from django.forms import forms, fields
from django.forms.widgets import PasswordInput
from django.utils.translation import ugettext_lazy as _


class PasswordForm(forms.Form):
    password = fields.CharField(label=_(u'Password'), required=True,
        widget=PasswordInput())

    def __init__(self, round, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.round = round

    def clean_password(self):
        data = self.cleaned_data
        if self.round.password != data.get('password', None):
            raise forms.ValidationError(_(u'Password is incorrect!'))
        return data.get('password')
