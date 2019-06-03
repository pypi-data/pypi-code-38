from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import MoloSurveyPageView


class TestDeduplicatePageviewData(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.section = self.mk_section(parent=self.section_index)
        self.page = self.mk_article(parent=self.section)
        self.user = self.login()

    def create_pageview(self, page=None, user=None):
        if page is None:
            page = self.page
        if user is None:
            user = self.user
        return MoloSurveyPageView.objects.create(
            page=page,
            user=user,
        )

    def test_deletes_pageviews_from_same_user_page_within_a_minute(self):
        self.create_pageview()
        self.create_pageview()
        call_command('deduplicate_pageview_data')
        self.assertEqual(MoloSurveyPageView.objects.count(), 1)

    def test_does_not_delete_pageviews_from_same_user_page_after_minutes(self):
        pageview_one = self.create_pageview()
        self.create_pageview()
        pageview_one.visited_at = timezone.now() - timedelta(minutes=2)
        pageview_one.save()
        call_command('deduplicate_pageview_data')
        self.assertEqual(MoloSurveyPageView.objects.count(), 2)

    def test_does_not_delete_pageviews_from_different_user(self):
        new_user = get_user_model().objects.create_user('testuser')
        self.create_pageview()
        self.create_pageview(user=new_user)
        call_command('deduplicate_pageview_data')
        self.assertEqual(MoloSurveyPageView.objects.count(), 2)

    def test_does_not_delete_pageviews_for_different_page(self):
        new_page = self.mk_article(parent=self.section)
        self.create_pageview()
        self.create_pageview(page=new_page)
        call_command('deduplicate_pageview_data')
        self.assertEqual(MoloSurveyPageView.objects.count(), 2)
