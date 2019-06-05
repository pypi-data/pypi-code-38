from ambition_form_validators import FluconazoleMissedDosesFormValidator

from ..models import FluconazoleMissedDoses
from .form_mixins import SubjectModelFormMixin


class FluconazoleMissedDosesForm(SubjectModelFormMixin):

    form_validator_cls = FluconazoleMissedDosesFormValidator

    class Meta:
        model = FluconazoleMissedDoses
        fields = "__all__"
