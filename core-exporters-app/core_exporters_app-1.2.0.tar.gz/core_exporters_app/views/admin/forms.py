""" Forms admin exporter
"""
from django import forms
from mongodbforms import DocumentForm

from core_exporters_app.components.exporter.models import Exporter
from core_main_app.components.template import api as template_api


class EditExporterForm(DocumentForm):
    name = forms.CharField(label='Name',
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Type the new name'}))

    class Meta:
        document = Exporter
        fields = ['name']


class AssociatedTemplatesForm(forms.Form):
    """ Associated Template form
    """
    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    templates_manager = forms.MultipleChoiceField(label='', widget=forms.SelectMultiple(), required=False)

    def __init__(self, *args, **kwargs):
        super(AssociatedTemplatesForm, self).__init__(*args, **kwargs)
        self.fields['templates_manager'].choices = _get_templates_versions()


def _get_templates_versions():
    """ Get templates versions.

    Returns:
        List of templates versions.

    """
    templates = []
    try:
        # display all template, global and from users
        template_list = template_api.get_all()
        for template in template_list:
            templates.append((template.id, template.display_name))
    except Exception:
        pass

    return templates
