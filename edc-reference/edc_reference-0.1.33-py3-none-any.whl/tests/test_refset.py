from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_utils import get_utcnow

from ..models import Reference
from ..reference_model_config import ReferenceModelConfig
from ..refsets import Refset, RefsetError, RefsetOverlappingField
from ..site_reference import site_reference_configs
from .models import SubjectVisit, CrfOne
from pprint import pprint
from edc_constants.constants import NEG


class TestRefset(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"
        site_reference_configs.registry = {}
        site_reference_configs.loaded = False
        reference = ReferenceModelConfig(
            name="edc_reference.subjectvisit", fields=["report_datetime", "visit_code"]
        )
        site_reference_configs.register(reference=reference)
        reference = ReferenceModelConfig(
            name="edc_reference.crfone",
            fields=["field_date", "field_datetime", "field_int", "field_str"],
        )
        site_reference_configs.register(reference=reference)

        values = [
            ("NEG", get_utcnow() - relativedelta(years=3)),
            ("POS", get_utcnow() - relativedelta(years=2)),
            ("POS", get_utcnow() - relativedelta(years=1)),
        ]
        self.subject_visits = []
        for index in [0, 1, 2]:
            self.subject_visits.append(
                SubjectVisit.objects.create(
                    subject_identifier=self.subject_identifier,
                    report_datetime=get_utcnow() - relativedelta(months=3 - index),
                    visit_code=str(index),
                )
            )
        for index, subject_visit in enumerate(
            SubjectVisit.objects.filter(
                subject_identifier=self.subject_identifier
            ).order_by("report_datetime")
        ):
            CrfOne.objects.create(
                subject_visit=subject_visit,
                field_int=index,
                field_str=values[index][0],
                field_datetime=values[index][1],
                field_date=values[index][1].date(),
            )

    def test_raises_model_not_in_site(self):
        site_reference_configs.registry = {}
        self.assertRaises(
            RefsetError,
            Refset,
            name="edc_reference.blah",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )

    def test_raises_unknown_reference_model(self):
        self.assertRaises(
            RefsetError,
            Refset,
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=None,
        )

    def test_raises_missing_report_datetime(self):
        self.assertRaises(
            RefsetError,
            Refset,
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=None,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )

    def test_raises_missing_subject_identifier(self):
        self.assertRaises(
            RefsetError,
            Refset,
            name="edc_reference.crfone",
            subject_identifier=None,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )

    def test_raises_missing_timepoint(self):
        self.assertRaises(
            RefsetError,
            Refset,
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=None,
            reference_model_cls=Reference,
        )

    def test_no_reference_instance(self):
        Reference.objects.all().delete()
        refset = Refset(
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )
        for value in refset._fields.values():
            self.assertIsNone(value)

    def test_missing_reference_instance_for_one_field(self):
        Reference.objects.filter(field_name="field_str").delete()
        refset = Refset(
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )
        self.assertIsNone(refset._fields.get("field_str"))

    def test_multiple_reference_instance_for_one_field(self):
        refset = Refset(
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )
        self.assertEqual(NEG, refset._fields.get("field_str"))

    def test_if_reference_exists_updates_report_datetime_in_fields(self):
        refset = Refset(
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )
        for field, value in refset._fields.items():
            if field == "report_datetime":
                self.assertEqual(value, self.subject_visits[0].report_datetime)
            elif field == "visit_code":
                self.assertEqual(value, self.subject_visits[0].visit_code, msg=field)

    def test_if_reference_updates_fields(self):
        for index, subject_visit in enumerate(self.subject_visits):
            with self.subTest(index=index, subject_visit=subject_visit):
                refset = Refset(
                    name="edc_reference.crfone",
                    subject_identifier=subject_visit.subject_identifier,
                    report_datetime=subject_visit.report_datetime,
                    timepoint=subject_visit.visit_code,
                    reference_model_cls=Reference,
                )
                crf_one = CrfOne.objects.get(subject_visit=subject_visit)
                for field, value in refset._fields.items():
                    if field == "report_datetime":
                        self.assertEqual(
                            value, subject_visit.report_datetime, msg=field
                        )
                    elif field == "visit_code":
                        self.assertEqual(value, subject_visit.visit_code, msg=field)
                    else:
                        self.assertEqual(value, getattr(crf_one, field), msg=field)

    def test_raises_on_overlapping_field(self):
        site_reference_configs.add_fields_to_config(
            "edc_reference.crfone", ["subject_identifier"]
        )
        Reference.objects.create(
            model="edc_reference.crfone",
            identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            field_name="subject_identifier",
        )
        self.assertRaises(
            RefsetOverlappingField,
            Refset,
            name="edc_reference.crfone",
            subject_identifier=self.subject_identifier,
            report_datetime=self.subject_visits[0].report_datetime,
            timepoint=self.subject_visits[0].visit_code,
            reference_model_cls=Reference,
        )
