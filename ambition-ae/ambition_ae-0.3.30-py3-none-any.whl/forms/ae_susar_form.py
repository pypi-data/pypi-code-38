from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin

from ..form_validators import AeSusarFormValidator
from ..models import AeSusar


class AeSusarForm(
    FormValidatorMixin,
    ModelFormSubjectIdentifierMixin,
    ActionItemFormMixin,
    forms.ModelForm,
):

    form_validator_cls = AeSusarFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = AeSusar
        fields = "__all__"
