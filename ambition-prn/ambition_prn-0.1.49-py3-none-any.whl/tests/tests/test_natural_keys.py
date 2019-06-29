from ambition_rando.tests import AmbitionTestCaseMixin
from django.test import TestCase, tag
from django.test.utils import override_settings
from django_collect_offline.models import OutgoingTransaction
from django_collect_offline.tests import OfflineTestHelper
from model_mommy import mommy


@override_settings(SITE_ID="10")
class TestNaturalKey(AmbitionTestCaseMixin, TestCase):

    offline_test_helper = OfflineTestHelper()

    def setUp(self):
        self.subject_identifier = self.create_subject()

    def test_natural_key_attrs(self):
        self.offline_test_helper.offline_test_natural_key_attr("ambition_prn")

    def test_get_by_natural_key_attr(self):
        self.offline_test_helper.offline_test_get_by_natural_key_attr("ambition_prn")

    def test_deserialize_death_report(self):
        death_report = mommy.make_recipe(
            "ambition_prn.deathreport", subject_identifier=self.subject_identifier
        )

        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=death_report._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                death_report, outgoing_transaction
            )

    def test_deserialize_death_report_tmg(self):
        death_report = mommy.make_recipe(
            "ambition_prn.deathreport", subject_identifier=self.subject_identifier
        )
        death_report_tmg = mommy.make_recipe(
            "ambition_prn.deathreporttmg",
            subject_identifier=self.subject_identifier,
            death_report=death_report,
        )
        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=death_report_tmg._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                death_report_tmg, outgoing_transaction
            )

    def test_deserialize_protocol_deviation(self):
        protocol_deviation = mommy.make_recipe(
            "ambition_prn.protocoldeviationviolation",
            subject_identifier=self.subject_identifier,
        )
        for outgoing_transaction in OutgoingTransaction.objects.filter(
            tx_name=protocol_deviation._meta.label_lower
        ):
            self.offline_test_helper.offline_test_deserialize(
                protocol_deviation, outgoing_transaction
            )
