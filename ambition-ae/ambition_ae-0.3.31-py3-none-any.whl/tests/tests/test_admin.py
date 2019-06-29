from ambition_ae.admin_site import ambition_ae_admin
from ambition_ae.models import AeFollowup, AeInitial
from ambition_rando.tests import AmbitionTestCaseMixin
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, DEAD
from edc_list_data.site_list_data import site_list_data
from edc_registration.models import RegisteredSubject
from model_mommy import mommy


class TestAdmin(AmbitionTestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        site_list_data.autodiscover()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

    def test_ae_followup_status(self):
        modeladmin = ambition_ae_admin._registry.get(AeFollowup)
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_followup = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            followup=YES,
            subject_identifier=self.subject_identifier,
        )
        self.assertEqual(
            modeladmin.status(ae_followup),
            f"{ae_followup.get_outcome_display()}. See AE Followup.",
        )

        ae_followup.followup = NO
        ae_followup.save()
        self.assertEqual(
            modeladmin.status(ae_followup), ae_followup.get_outcome_display()
        )

    def test_ae_followup_ae_follow_up(self):
        modeladmin = ambition_ae_admin._registry.get(AeFollowup)
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )

        ae_followup = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            followup=YES,
            subject_identifier=self.subject_identifier,
        )

        self.assertIn(ae_followup.identifier, modeladmin.ae_followup(ae_followup))

    @tag("4")
    def test_ae_initial_follow_up_reports(self):
        modeladmin = ambition_ae_admin._registry.get(AeInitial)
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        self.assertIsNone(modeladmin.follow_up_reports(ae_initial))

        ae_followup1 = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            followup=YES,
            subject_identifier=self.subject_identifier,
        )

        ae_followup2 = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            followup=NO,
            subject_identifier=self.subject_identifier,
        )

        self.assertIn(ae_followup1.identifier, modeladmin.follow_up_reports(ae_initial))
        self.assertIn(ae_followup2.identifier, modeladmin.follow_up_reports(ae_initial))

    @tag("4")
    def test_ae_initial_if_sae_reason(self):
        modeladmin = ambition_ae_admin._registry.get(AeInitial)
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        self.assertIsNone(modeladmin.follow_up_reports(ae_initial))

        mommy.make_recipe(
            "ambition_ae.aeinitial",
            sae_reason=DEAD,
            subject_identifier=self.subject_identifier,
        )
        self.assertTrue(modeladmin.description(ae_initial))

    @tag("4")
    def test_ae_initial_description(self):
        modeladmin = ambition_ae_admin._registry.get(AeInitial)
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        self.assertTrue(modeladmin.description(ae_initial))

    @tag("4")
    def test_ae_initial_user(self):
        modeladmin = ambition_ae_admin._registry.get(AeInitial)
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        self.assertTrue(modeladmin.user(ae_initial))
