from django.test import TestCase, tag
from edc_utils import get_utcnow

from ..models import Reference


class TestModel(TestCase):

    reference_model_cls = Reference
    subject_identifier = "11111"

    def test_model_update(self):
        reference = self.reference_model_cls.objects.create(
            model=f"edc_reference.testmodel",
            identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            field_name="field_name",
        )
        reference.update_value(value="5", internal_type="CharField")
        self.assertEqual(
            self.reference_model_cls.objects.get(id=reference.id).value, "5"
        )
        self.assertEqual(
            self.reference_model_cls.objects.get(id=reference.id).value_str, "5"
        )
