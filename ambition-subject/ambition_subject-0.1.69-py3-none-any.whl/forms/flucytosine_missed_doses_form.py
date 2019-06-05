from ambition_form_validators import FlucytosineMissedDosesFormValidator

from ..models import FlucytosineMissedDoses
from .form_mixins import SubjectModelFormMixin


class FlucytosineMissedDosesForm(SubjectModelFormMixin):

    form_validator_cls = FlucytosineMissedDosesFormValidator

    class Meta:
        model = FlucytosineMissedDoses
        fields = "__all__"
