from django import forms
from django.apps import apps

from .models import Management, FieldList


class ManagementForm(forms.ModelForm):
    APPLICATION_CHOICES = [(app.label, app.label) for app in list(apps.app_configs.values())]

    application = forms.ChoiceField(choices=APPLICATION_CHOICES)

    class Meta:
        model = Management
        fields = []
        exclude = []
        search_fields = ['application']


def field_choices():
    models = [app for app in apps.get_models()]
    fields = []
    for model in models:
        for field in model._meta.get_fields(include_parents=True):
            fields.append((field.name, model._meta.object_name + '.' + field.name))
    return fields


class FieldListForm(forms.ModelForm):
    MODELS_CHOICES = [(app._meta.object_name, app._meta.label) for app in apps.get_models()]
    FIELD_CHOICES = field_choices()

    model = forms.ChoiceField(choices=MODELS_CHOICES)
    name = forms.ChoiceField(choices=FIELD_CHOICES)

    class Meta:
        model = FieldList
        fields = []
        exclude = []