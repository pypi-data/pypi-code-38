from django import forms

from modelformhistory.forms import HistoryModelFormMixin
from .models import Foo


class FooModelFormRequest(HistoryModelFormMixin, forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(FooModelFormRequest, self).__init__(*args, **kwargs)

    class Meta:
        model = Foo
        fields = "__all__"


class FooModelForm(HistoryModelFormMixin, forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FooModelForm, self).__init__(*args, **kwargs)

    def get_history_user(self):
        return self.user

    class Meta:
        model = Foo
        fields = "__all__"
