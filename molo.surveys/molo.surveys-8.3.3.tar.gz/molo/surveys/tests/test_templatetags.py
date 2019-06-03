from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.template import Context
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware

from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import (MoloSurveyPage, MoloSurveyFormField,
                                 SurveysIndexPage, PersonalisableSurvey,
                                 MoloSurveySubmission)

from molo.surveys.templatetags.molo_survey_tags import (
    get_survey_list, load_user_choice_poll_survey)
from .base import create_survey


def add_session_to_request(request):
    """Annotate a request object with a session"""
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()


class LoadUserChoicePollSurvey(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.surveys_index = SurveysIndexPage.objects.child_of(
            self.main).first()
        self.user = self.login()
        # create a requset object
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.site = self.site
        self.request.user = self.user
        add_session_to_request(self.request)

    def test_load_user_choice_poll_survey(self):
        create_survey([
            {
                "question": "I feel I can be myself around other people",
                "type": 'radio',
                "choices": ["agree", "disagree"],
                "required": True,
                "page_break": False,
            },
        ],
            language=self.english)
        survey = MoloSurveyPage.objects.last()
        self.client.post(survey.url, {
            'i-feel-i-can-be-myself-around-other-people':
                'agree',
            'ajax': 'True'
        })
        self.assertEquals(MoloSurveySubmission.objects.count(), 1)
        self.assertTrue(load_user_choice_poll_survey(
            {'request': self.request},
            survey, 'i-feel-i-can-be-myself-around-other-people',
            'agree'))
        self.assertFalse(load_user_choice_poll_survey(
            {'request': self.request},
            survey, 'i-feel-i-can-be-myself-around-other-people',
            'disagree'))
        self.client.post(survey.url, {
            'i-feel-i-can-be-myself-around-other-people':
                'disagree',
            'ajax': 'True'
        })
        self.assertEquals(MoloSurveySubmission.objects.count(), 1)
        self.assertFalse(load_user_choice_poll_survey(
            {'request': self.request},
            survey, 'i-feel-i-can-be-myself-around-other-people',
            'agree'))
        self.assertTrue(load_user_choice_poll_survey(
            {'request': self.request},
            survey, 'i-feel-i-can-be-myself-around-other-people',
            'disagree'))


class SurveyListTest(TestCase, MoloTestCaseMixin):

    def create_molo_survey_page(self,
                                parent,
                                title="Test Survey",
                                slug="test-survey",
                                **kwargs):
        molo_survey_page = MoloSurveyPage(
            title=title,
            slug=slug,
            introduction='Introduction to Test Survey ...',
            thank_you_text='Thank you for taking the Test Survey',
            **kwargs
        )

        parent.add_child(instance=molo_survey_page)
        molo_survey_page.save_revision().publish()
        molo_survey_form_field = MoloSurveyFormField.objects.create(
            page=molo_survey_page,
            sort_order=1,
            label='Your favourite animal',
            field_type='singleline',
            required=True
        )
        return molo_survey_page, molo_survey_form_field

    def create_personalisable_survey(
            self,
            parent,
            title="Test Survey",
            slug="test-survey",
            **kwargs):
        personalisable_survey = PersonalisableSurvey(
            title=title,
            slug=slug,
            introduction='Introduction to Test Survey ...',
            thank_you_text='Thank you for taking the Test Survey',
            **kwargs
        )

        parent.add_child(instance=personalisable_survey)
        personalisable_survey.save_revision().publish()
        survey_form_field = MoloSurveyFormField.objects.create(
            page=personalisable_survey,
            sort_order=1,
            label='Your favourite animal',
            field_type='singleline',
            required=True
        )
        return personalisable_survey, survey_form_field

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)
        self.surveys_index = SurveysIndexPage.objects.child_of(
            self.main).first()

        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')

        # create a requset object
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.site = self.site
        self.request.user = self.user
        add_session_to_request(self.request)
        self.user = self.login()

        # create direct questions
        self.direct_molo_survey_page, direct_molo_survey_form_field = (
            self.create_molo_survey_page(
                parent=self.surveys_index,
                title="direct survey title",
                slug="direct_survey_title",
                display_survey_directly=True,
            ))
        self.client.post(reverse(
            'add_translation', args=[self.direct_molo_survey_page.id, 'fr']))
        self.translated_direct_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-direct-survey-title')
        self.translated_direct_survey.save_revision().publish()

        self.linked_molo_survey_page, linked_molo_survey_form_field = (
            self.create_molo_survey_page(
                parent=self.surveys_index,
                title="linked survey title",
                slug="linked_survey_title",
                display_survey_directly=False,
            ))
        self.yourwords_molo_survey_page, yourwords_molo_survey_form_field = (
            self.create_molo_survey_page(
                parent=self.surveys_index,
                title="yourwords survey title",
                slug="yourwords_survey_title",
                your_words_competition=True,
            ))
        self.client.post(reverse(
            'add_translation', args=[self.linked_molo_survey_page.id, 'fr']))
        self.translated_linked_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-linked-survey-title')
        self.translated_linked_survey.save_revision().publish()

        self.personalisable_survey, personalisable_survey_form_field = (
            self.create_personalisable_survey(
                parent=self.surveys_index,
                title="personalisable survey title",
                slug="personalisable_survey_title",
            ))
        self.client.post(reverse(
            'add_translation', args=[self.personalisable_survey.id, 'fr']))
        self.trans_personalisable_survey = PersonalisableSurvey.objects.get(
            slug='french-translation-of-personalisable-survey-title')
        self.trans_personalisable_survey.save_revision().publish()

    def test_get_survey_list_default(self):
        context = Context({
            'locale_code': 'en',
            'request': self.request,
        })
        context = get_survey_list(context)
        self.assertEqual(len(context['surveys']), 3)
        self.assertTrue(self.direct_molo_survey_page in context['surveys'])
        self.assertTrue(self.linked_molo_survey_page in context['surveys'])

        context = Context({
            'locale_code': 'fr',
            'request': self.request,
        })
        context = get_survey_list(context)
        self.assertEqual(len(context['surveys']), 3)
        self.assertTrue(self.translated_direct_survey in context['surveys'])
        self.assertTrue(self.translated_linked_survey in context['surveys'])
        self.assertTrue(self.yourwords_molo_survey_page in context['surveys'])

    def test_get_survey_list_only_direct(self):
        context = Context({
            'locale_code': 'en',
            'request': self.request,
        })
        context = get_survey_list(context, only_direct_surveys=True)
        self.assertEqual(len(context['surveys']), 1)
        self.assertTrue(self.direct_molo_survey_page in context['surveys'])
        self.assertTrue(self.linked_molo_survey_page not in context['surveys'])
        context = Context({
            'locale_code': 'fr',
            'request': self.request,
        })
        context = get_survey_list(context, only_direct_surveys=True)
        self.assertEqual(len(context['surveys']), 1)
        self.assertTrue(self.translated_direct_survey in context['surveys'])
        self.assertTrue(
            self.translated_linked_survey not in context['surveys'])

    def test_get_survey_list_only_yourwords(self):
        context = Context({
            'locale_code': 'en',
            'request': self.request,
        })
        context = get_survey_list(context, only_yourwords=True)
        self.assertEqual(len(context['surveys']), 1)
        self.assertTrue(self.yourwords_molo_survey_page in context['surveys'])
        self.assertTrue(self.linked_molo_survey_page not in context['surveys'])

    def test_get_survey_list_only_linked(self):
        context = Context({
            'locale_code': 'en',
            'request': self.request,
        })
        context = get_survey_list(context, only_linked_surveys=True)
        self.assertEqual(len(context['surveys']), 1)
        self.assertTrue(self.direct_molo_survey_page not in context['surveys'])
        self.assertTrue(self.linked_molo_survey_page in context['surveys'])
        context = Context({
            'locale_code': 'fr',
            'request': self.request,
        })
        context = get_survey_list(context, only_linked_surveys=True)
        self.assertEqual(len(context['surveys']), 1)
        self.assertTrue(
            self.translated_direct_survey not in context['surveys'])
        self.assertTrue(self.translated_linked_survey in context['surveys'])

    def test_get_survey_list_arg_error(self):
        context = Context({
            'locale_code': 'en',
            'request': self.request,
        })
        with self.assertRaises(ValueError):
            context = get_survey_list(context,
                                      only_linked_surveys=True,
                                      only_direct_surveys=True,)

    def test_get_survey_list_personalisable_survey(self):
        context = Context({
            'locale_code': 'en',
            'request': self.request,
        })
        context = get_survey_list(context, personalisable_survey=True)
        self.assertEqual(len(context['surveys']), 1)
        self.assertTrue(
            self.direct_molo_survey_page not in context['surveys'])
        self.assertTrue(self.personalisable_survey in context['surveys'])
        context = Context({
            'locale_code': 'fr',
            'request': self.request,
        })
        context = get_survey_list(context, personalisable_survey=True)
        self.assertEqual(len(context['surveys']), 1)
        self.assertTrue(
            self.translated_direct_survey not in context['surveys'])
        self.assertTrue(
            self.trans_personalisable_survey in context['surveys'])
