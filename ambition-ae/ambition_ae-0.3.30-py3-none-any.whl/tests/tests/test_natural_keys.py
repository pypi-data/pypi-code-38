from ambition_rando.tests import AmbitionTestCaseMixin
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_metadata.tests import CrfTestHelper
from edc_registration.models import RegisteredSubject
from django_collect_offline.models import OutgoingTransaction
from django_collect_offline.tests import OfflineTestHelper
from model_mommy import mommy


@override_settings(SITE_ID="10")
class TestNaturalKey(AmbitionTestCaseMixin, TestCase):

    offline_test_helper = OfflineTestHelper()
    crf_test_helper = CrfTestHelper()

    def setUp(self):
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

    def test_natural_key_attrs(self):
        self.offline_test_helper.offline_test_natural_key_attr("ambition_ae")

    def test_get_by_natural_key_attr(self):
        self.offline_test_helper.offline_test_get_by_natural_key_attr("ambition_ae")

    def test_deserialize_ae_initial(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=ae_initial._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                ae_initial, outgoing_transaction
            )

    def test_deserialize_ae_tmg(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_tmg = mommy.make_recipe(
            "ambition_ae.aetmg",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=ae_tmg._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                ae_tmg, outgoing_transaction
            )

    def test_deserialize_ae_followup(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_followup = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=ae_followup._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                ae_followup, outgoing_transaction
            )

    def test_deserialize_recurrence_symptom(self):
        recurrence_symptoms = mommy.make_recipe(
            "ambition_ae.recurrencesymptom", subject_identifier=self.subject_identifier
        )
        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=recurrence_symptoms._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                recurrence_symptoms, outgoing_transaction
            )
