from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_utils import get_utcnow

from ..models import Reference
from ..populater import Populater
from ..reference_model_config import ReferenceModelConfig
from ..site_reference import site_reference_configs
from .models import SubjectVisit, CrfOne


class TestPopulater(TestCase):
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
        self.report_datetime = get_utcnow()
        self.report_date = get_utcnow().date()
        self.subject_visit1 = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
        )
        CrfOne.objects.create(
            subject_visit=self.subject_visit1,
            field_date=self.report_date,
            field_datetime=self.report_datetime,
            field_int=1,
            field_str="erik",
        )
        self.subject_visit2 = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime - relativedelta(years=1),
        )
        CrfOne.objects.create(
            subject_visit=self.subject_visit2,
            field_date=self.report_date,
            field_datetime=self.report_datetime,
            field_int=1,
            field_str="erik",
        )

    def test_populates_for_visit(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="edc_reference.subjectvisit",
                        report_datetime=visit.report_datetime,
                        field_name="report_datetime",
                        value_datetime=visit.report_datetime,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_date(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="edc_reference.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_date",
                        value_date=self.report_date,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_datetime(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="edc_reference.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_datetime",
                        value_datetime=self.report_datetime,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_str(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        report_datetime=visit.report_datetime,
                        model="edc_reference.crfone",
                        field_name="field_str",
                        value_str="erik",
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populates_for_crfone_field_int(self):
        Reference.objects.all().delete()
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="edc_reference.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_int",
                        value_int=1,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")

    def test_populater_updates(self):
        populater = Populater()
        populater.populate()
        for visit in SubjectVisit.objects.all():
            with self.subTest(report_datetime=visit.report_datetime):
                try:
                    Reference.objects.get(
                        identifier=self.subject_identifier,
                        model="edc_reference.crfone",
                        report_datetime=visit.report_datetime,
                        field_name="field_int",
                        value_int=1,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(f"Object unexpectedly DoesNotExist. Got {e}")
