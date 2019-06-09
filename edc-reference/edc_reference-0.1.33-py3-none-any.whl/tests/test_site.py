from django.test import TestCase, tag
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..reference_model_config import ReferenceModelConfig
from ..reference_model_config import (
    ReferenceFieldValidationError,
    ReferenceDuplicateField,
)
from ..reference_model_config import ReferenceModelValidationError
from ..site_reference import site_reference_configs
from ..site_reference import AlreadyRegistered
from ..site_reference import SiteReferenceConfigError, ReferenceConfigNotRegistered
from .visit_schedule import visit_schedule


class TestSite(TestCase):
    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

    def test_site_register(self):
        name = "edc_reference.crfone"
        fields = ["field_date", "field_datetime", "field_int", "field_str"]
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.register(reference=reference)
        self.assertEqual(fields, site_reference_configs.get_fields(name=name))

    def test_site_reregister(self):
        name = "edc_reference.crfone"
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(
            name=name, fields=["field_date", "field_datetime", "field_int", "field_str"]
        )
        site_reference_configs.register(reference=reference)
        self.assertRaises(
            AlreadyRegistered, site_reference_configs.register, reference=reference
        )

    def test_autodiscover(self):
        site_reference_configs.registry = {}
        site_reference_configs.loaded = False
        site_reference_configs.autodiscover("tests.reference_model_configs")
        self.assertTrue(site_reference_configs.loaded)
        self.assertIn("edc_reference.erik", list(site_reference_configs.registry))

        self.assertEqual(
            ["f1", "f2", "f3", "f4"],
            site_reference_configs.get_fields("edc_reference.erik"),
        )

    def test_autodiscover_bad(self):
        self.assertRaises(
            TypeError,
            site_reference_configs.autodiscover,
            module_name="tests.reference_model_configs_bad",
        )

    def test_check_ok(self):
        name = "edc_reference.crfone"
        fields = ["field_str", "field_date", "field_datetime", "field_int"]
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(fields=fields, name=name)
        try:
            reference.check()
        except (ReferenceFieldValidationError, ReferenceModelValidationError) as e:
            self.fail(f"Reference validation error unexpectedly raised. Got{e}")

    def test_check_ok2(self):
        name = "edc_reference.crfone"
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(
            fields=["field_str", "field_date", "field_datetime", "field_int"], name=name
        )
        site_reference_configs.register(reference=reference)
        site_reference_configs.check()

    def test_check_bad_model(self):
        name = "edc_reference.erik"
        fields = ["f1"]
        reference = ReferenceModelConfig(fields=fields, name=name)
        self.assertRaises(ReferenceModelValidationError, reference.check)

    def test_check_bad_fields(self):
        name = "edc_reference.crfone"
        fields = ["f1"]
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(fields=fields, name=name)
        self.assertRaises(ReferenceFieldValidationError, reference.check)

    def test_raises_on_duplicate_field_name(self):
        name = "edc_reference.crfone"
        fields = ["f1", "f1"]
        self.assertRaises(
            ReferenceDuplicateField, ReferenceModelConfig, fields=fields, name=name
        )

    def test_not_registered_for_fields(self):
        name = "edc_reference.crfone"
        site_reference_configs.registry = {}
        self.assertRaises(
            SiteReferenceConfigError, site_reference_configs.get_fields, name=name
        )

    def test_not_registered_for_reference_model(self):
        name = "edc_reference.crfone"
        site_reference_configs.registry = {}
        self.assertRaises(
            SiteReferenceConfigError,
            site_reference_configs.get_reference_model,
            name=name,
        )

    def test_not_registered_for_reregister(self):
        name = "edc_reference.crfone"
        fields = ["f1"]
        reference = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.registry = {}
        self.assertRaises(
            ReferenceConfigNotRegistered, site_reference_configs.reregister, reference
        )

    def test_get_config(self):
        site_reference_configs.registry = {}
        name = "edc_reference.crfone"
        fields = ["f1"]
        reference = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.register(reference)
        self.assertEqual(
            reference, site_reference_configs.get_config(name="edc_reference.crfone")
        )
        self.assertRaises(
            SiteReferenceConfigError, site_reference_configs.get_config, name=None
        )

    def test_register_reference_models_from_visit_schedule(self):
        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_reference.subjectvisit"}
        )
        self.assertTrue(site_reference_configs.get_config(name="edc_reference.crfone"))

    def test_reregister_reference_models_from_visit_schedule(self):
        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_reference.subjectvisit"}
        )
        # do again
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_reference.subjectvisit"}
        )
        self.assertTrue(site_reference_configs.get_config(name="edc_reference.crfone"))

    def test_add_fields_to_reference_config(self):
        name = "edc_reference.crfone"
        fields = ["f1"]
        site_reference_configs.registry = {}
        reference_config = ReferenceModelConfig(fields=fields, name=name)
        site_reference_configs.register(reference_config)
        self.assertEqual(reference_config.field_names, ["f1"])
        site_reference_configs.add_fields_to_config(name=name, fields=["f2", "f3"])
        self.assertEqual(reference_config.field_names, ["f1", "f2", "f3"])
