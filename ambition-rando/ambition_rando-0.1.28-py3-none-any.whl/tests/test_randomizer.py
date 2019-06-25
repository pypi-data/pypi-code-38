import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_registration.models import RegisteredSubject
from random import shuffle
from tempfile import mkdtemp

from ..models import RandomizationList
from ..randomization_list_importer import RandomizationListImporter
from ..randomizer import RandomizationError, AllocationError
from ..randomizer import Randomizer, RandomizationListError, AlreadyRandomized
from ..utils import InvalidDrugAssignment
from ..randomization_list_verifier import RandomizationListVerifier
from .ambition_test_case_mixin import AmbitionTestCaseMixin
from .make_test_list import make_test_list
from .models import SubjectConsent


class TestRandomizer(AmbitionTestCaseMixin, TestCase):

    import_randomization_list = False

    def populate_list(self, site_names=None, per_site=None):
        path = make_test_list(
            site_names=site_names or self.site_names, per_site=per_site
        )
        RandomizationListImporter(path=path, overwrite=True)

    @override_settings(SITE_ID=40)
    def test_with_consent_no_site(self):
        subject_consent = SubjectConsent.objects.create(subject_identifier="12345")
        self.assertRaises(
            RandomizationListError,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )

    @override_settings(SITE_ID=40)
    def test_with_consent(self):
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site
        )
        self.assertRaises(
            RandomizationListError,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )

    @override_settings(SITE_ID=40)
    def test_with_list_selects_first(self):
        self.populate_list()
        site = Site.objects.get_current()
        RandomizationList.objects.update(site_name=site.name)
        first_obj = RandomizationList.objects.all().first()
        subject_consent = SubjectConsent.objects.create(subject_identifier="12345")
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        self.assertEqual(rando.sid, first_obj.sid)

    @override_settings(SITE_ID=40)
    def test_updates_registered_subject(self):
        self.populate_list()
        site = Site.objects.get_current()
        RandomizationList.objects.update(site_name=site.name)
        subject_consent = SubjectConsent.objects.create(subject_identifier="12345")
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        first_obj = RandomizationList.objects.all().first()
        rs = RegisteredSubject.objects.get(subject_identifier="12345")
        self.assertEqual(rs.subject_identifier, first_obj.subject_identifier)
        self.assertEqual(rs.sid, str(first_obj.sid))
        self.assertEqual(rs.randomization_datetime, first_obj.allocated_datetime)

    @override_settings(SITE_ID=40)
    def test_updates_list_obj_as_allocated(self):
        self.populate_list()
        site = Site.objects.get_current()
        RandomizationList.objects.update(site_name=site.name)
        RandomizationList.objects.all().first()
        subject_consent = SubjectConsent.objects.create(subject_identifier="12345")
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        first_obj = RandomizationList.objects.all().first()
        self.assertEqual(first_obj.subject_identifier, "12345")
        self.assertTrue(first_obj.allocated)
        self.assertIsNotNone(first_obj.allocated_user)
        self.assertEqual(first_obj.allocated_user, subject_consent.user_modified)
        self.assertEqual(first_obj.allocated_datetime, subject_consent.consent_datetime)
        self.assertGreater(first_obj.modified, subject_consent.created)

    @override_settings(SITE_ID=40)
    def test_cannot_rerandomize(self):
        self.populate_list()
        site = Site.objects.get_current()
        RandomizationList.objects.update(site_name=site.name)
        first_obj = RandomizationList.objects.all().first()
        subject_consent = SubjectConsent.objects.create(subject_identifier="12345")
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        self.assertEqual(rando.sid, first_obj.sid)
        self.assertRaises(
            AlreadyRandomized,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )

    @override_settings(SITE_ID=40)
    def test_error_condition1(self):
        """Assert raises if RegisteredSubject not updated correctly.
        """
        self.populate_list()
        site = Site.objects.get_current()
        RandomizationList.objects.update(site_name=site.name)
        subject_consent = SubjectConsent.objects.create(subject_identifier="12345")
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        rando.registered_subject.sid = None
        rando.registered_subject.save()
        with self.assertRaises(AlreadyRandomized) as cm:
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_modified,
            )
        self.assertEqual(cm.exception.code, "ambition_rando.randomizationlist")

    @override_settings(SITE_ID=40)
    def test_error_condition2(self):
        """Assert raises if RandomizationList not updated correctly.
        """
        self.populate_list()
        site = Site.objects.get_current()
        RandomizationList.objects.update(site_name=site.name)
        subject_consent = SubjectConsent.objects.create(subject_identifier="12345")
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        rando.registered_subject.sid = None
        rando.registered_subject.save()
        with self.assertRaises(AlreadyRandomized) as cm:
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_modified,
            )
        self.assertEqual(cm.exception.code, "ambition_rando.randomizationlist")

    def test_error_condition3(self):
        """Assert raises if RandomizationList not updated correctly.
        """
        self.populate_list()
        site = Site.objects.get(name="gaborone")
        RandomizationList.objects.update(site_name=site.name)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site
        )
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        RandomizationList.objects.update(subject_identifier=None)
        with self.assertRaises(AlreadyRandomized) as cm:
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_modified,
            )
        self.assertEqual(cm.exception.code, "edc_registration.registeredsubject")

    def test_subject_does_not_exist(self):
        self.populate_list()
        site = Site.objects.get(name="gaborone")
        RandomizationList.objects.update(site_name=site.name)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site
        )
        RegisteredSubject.objects.all().delete()
        self.assertRaises(
            RandomizationError,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )

    def test_str(self):
        self.populate_list()
        site = Site.objects.get(name="gaborone")
        RandomizationList.objects.update(site_name=site.name)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site
        )
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )
        obj = RandomizationList.objects.all().first()
        self.assertTrue(str(obj))

    @override_settings(SITE_ID=40)
    def test_for_sites(self):
        """Assert that allocates by site correctly.
        """
        RandomizationList.objects.all().delete()
        self.populate_list(site_names=self.site_names, per_site=5)
        site_names = [obj.site_name for obj in RandomizationList.objects.all()]
        shuffle(site_names)
        assert len(site_names) == len(self.site_names * 5)
        # consent and randomize 5 for each site
        for index, site_name in enumerate(site_names):
            site = Site.objects.get(name=site_name)
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=f"12345{index}", site=site
            )
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_modified,
            )
        # assert consented subjects were allocated SIDs in the
        # correct order per site.
        for site_name in site_names:
            randomized_subjects = [
                (obj.subject_identifier, str(obj.sid))
                for obj in RandomizationList.objects.filter(
                    allocated_site__name=site_name, subject_identifier__isnull=False
                ).order_by("sid")
            ]
            for index, obj in enumerate(
                SubjectConsent.objects.filter(site__name=site_name).order_by(
                    "consent_datetime"
                )
            ):
                rs = RegisteredSubject.objects.get(
                    subject_identifier=obj.subject_identifier
                )
                self.assertEqual(obj.subject_identifier, randomized_subjects[index][0])
                self.assertEqual(rs.sid, randomized_subjects[index][1])

        # clear out any unallocated
        RandomizationList.objects.filter(subject_identifier__isnull=True).delete()

        # assert raises on next attempt to randomize
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=f"ABCDEF", site=site
        )
        self.assertRaises(
            AllocationError,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )

    @override_settings(SITE_ID=40, RANDOMIZTION_LIST_PATH="/tmp/erik.csv")
    def test_invalid_path(self):
        message = RandomizationListVerifier().message
        self.assertIn("Randomization list has not been loaded.", message)

    @override_settings(
        SITE_ID=40, RANDOMIZATION_LIST_PATH=os.path.join(mkdtemp(), "randolist.csv")
    )
    def test_invalid_assignment(self):
        # change to a different assignments
        drug_assignments = [100, 101]
        make_test_list(
            full_path=settings.RANDOMIZATION_LIST_PATH,
            site_names=self.site_names,
            drug_assignments=drug_assignments,
            count=5,
        )
        self.assertRaises(InvalidDrugAssignment, RandomizationListImporter)

    @override_settings(SITE_ID=40)
    def test_invalid_sid(self):
        # change to a different starting SID
        RandomizationListImporter()
        obj = RandomizationList.objects.all().order_by("sid").first()
        obj.sid = 100
        obj.save()
        message = RandomizationListVerifier().message
        self.assertIn("Randomization list is invalid", message or "")

    @override_settings(SITE_ID=40)
    def test_invalid_count(self):
        site = Site.objects.get_current()
        # change number of SIDs in DB
        RandomizationListImporter()
        RandomizationList.objects.create(
            sid=100, drug_assignment="single_dose", site_name=site.name
        )
        self.assertEqual(RandomizationList.objects.all().count(), 41)
        message = RandomizationListVerifier().message
        self.assertIn("Randomization list count is off", message)
