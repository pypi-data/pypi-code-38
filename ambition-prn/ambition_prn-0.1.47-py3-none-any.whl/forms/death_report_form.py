from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ..form_validators import DeathReportFormValidator
from ..models import DeathReport


class DeathReportForm(
    SiteModelFormMixin, ActionItemFormMixin, FormValidatorMixin, forms.ModelForm
):

    form_validator_cls = DeathReportFormValidator

    subject_identifier = forms.CharField(
        label="Subject identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = DeathReport
        fields = "__all__"
