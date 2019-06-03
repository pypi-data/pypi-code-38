import json
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.utils.text import slugify
from molo.core.models import (Languages, Main, SiteLanguageRelation,
                              SiteSettings)
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import (
    MoloSurveyFormField,
    MoloSurveyPage,
    SurveysIndexPage,
    PersonalisableSurvey,
    PersonalisableSurveyFormField
)

from .utils import skip_logic_data
from .base import (
    create_personalisable_survey_page,
    create_molo_dropddown_field,
    create_personalisable_dropddown_field,
    create_molo_survey_formfield,
    create_molo_survey_page
)

from .constants import SEGMENT_FORM_DATA

User = get_user_model()


class TestSurveyViews(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.client = Client()
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

        self.section = self.mk_section(self.section_index, title='section')
        self.article = self.mk_article(self.section, title='article')

        # Create surveys index pages
        self.surveys_index = SurveysIndexPage.objects.child_of(
            self.main).first()

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.french2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='fr',
            is_active=True)

        self.mk_main2(title='main3', slug='main3', path="00010003")
        self.client2 = Client(HTTP_HOST=self.main2.get_site().hostname)

    def create_molo_survey_page_with_field(
            self, parent, display_survey_directly=False,
            allow_anonymous_submissions=False, **kwargs):
        molo_survey_page = create_molo_survey_page(
            parent,
            display_survey_directly=display_survey_directly,
            allow_anonymous_submissions=allow_anonymous_submissions, **kwargs)
        molo_survey_page.save_revision().publish()
        molo_survey_form_field = create_molo_survey_formfield(
            survey=molo_survey_page,
            field_type='singleline',
            label="Your favourite animal",
            required=True)
        return (molo_survey_page, molo_survey_form_field)

    def test_homepage_button_text_customisable(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.surveys_index,
                homepage_button_text='share your story yo')
        self.client.login(username='tester', password='tester')
        response = self.client.get('/')
        self.assertContains(response, 'share your story yo')
        self.assertNotContains(response, 'Take the Survey')

    def test_correct_intro_shows_on_homepage(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.surveys_index,
                homepage_button_text='share your story yo')
        self.client.login(username='tester', password='tester')
        response = self.client.get('/')
        self.assertContains(response, 'Shorter homepage introduction')
        self.assertNotContains(response, 'Take the Survey')

    def test_anonymous_submissions_not_allowed_by_default(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.section_index)

        response = self.client.get(molo_survey_page.url)

        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, 'Please log in to take this survey')

    def test_submit_survey_as_logged_in_user(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.section_index)

        self.client.login(username='tester', password='tester')

        response = self.client.get(molo_survey_page.url)
        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, molo_survey_page.introduction)
        self.assertContains(response, molo_survey_form_field.label)
        self.assertContains(response, molo_survey_page.submit_text)

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)

        self.assertContains(response, molo_survey_page.thank_you_text)

        # for test_multiple_submissions_not_allowed_by_default
        return molo_survey_page.url

    def test_anonymous_submissions_option(self):
        molo_survey_page = create_molo_survey_page(
            parent=self.surveys_index,
            allow_anonymous_submissions=True)
        molo_survey_form_field = create_molo_survey_formfield(
            survey=molo_survey_page,
            field_type='singleline',
            label="test label")

        response = self.client.get(molo_survey_page.url)
        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, molo_survey_page.introduction)
        self.assertContains(response, molo_survey_form_field.label)
        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)
        self.assertContains(response, molo_survey_page.thank_you_text)

        # for test_multiple_submissions_not_allowed_by_default_anonymous
        return molo_survey_page.url

    def test_multiple_submissions_not_allowed_by_default(self):
        molo_survey_page_url = self.test_submit_survey_as_logged_in_user()

        response = self.client.get(molo_survey_page_url)

        self.assertContains(response,
                            'You have already completed this survey.')

    def test_multiple_submissions_not_allowed_by_default_anonymous(self):
        molo_survey_page_url = self.test_anonymous_submissions_option()

        response = self.client.get(molo_survey_page_url)

        self.assertContains(response,
                            'You have already completed this survey.')

    def test_multiple_submissions_option(self, anonymous=False):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.section_index,
                allow_multiple_submissions_per_user=True,
                allow_anonymous_submissions=anonymous
            )

        if not anonymous:
            self.client.login(username='tester', password='tester')

        for _ in range(2):
            response = self.client.get(molo_survey_page.url)

            self.assertContains(response, molo_survey_page.title)
            self.assertContains(response, molo_survey_page.introduction)
            self.assertContains(response, molo_survey_form_field.label)

            response = self.client.post(molo_survey_page.url, {
                molo_survey_form_field.label.lower().replace(' ', '-'):
                    'python'
            }, follow=True)

            self.assertContains(response, molo_survey_page.thank_you_text)

    def test_multiple_submissions_option_anonymous(self):
        self.test_multiple_submissions_option(True)

    def test_show_results_option(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.section_index,
                allow_anonymous_submissions=True,
                show_results=True
            )

        response = self.client.get(molo_survey_page.url)
        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, molo_survey_page.introduction)
        self.assertContains(response, molo_survey_form_field.label)

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)
        self.assertContains(response, molo_survey_page.thank_you_text)
        self.assertContains(response, 'Results')
        self.assertContains(response, molo_survey_form_field.label)
        self.assertContains(response, 'python</span> 1')

    def test_show_results_as_percentage_option(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.section_index,
                allow_anonymous_submissions=True,
                allow_multiple_submissions_per_user=True,
                show_results=True,
                show_results_as_percentage=True
            )

        response = self.client.get(molo_survey_page.url)
        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, molo_survey_page.introduction)
        self.assertContains(response, molo_survey_form_field.label)

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)
        self.assertContains(response, molo_survey_page.thank_you_text)
        self.assertContains(response, 'Results')
        self.assertContains(response, molo_survey_form_field.label)
        self.assertContains(response, 'python</span> 100%')

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'java'
        }, follow=True)
        self.assertContains(response, molo_survey_page.thank_you_text)
        self.assertContains(response, 'Results')
        self.assertContains(response, molo_survey_form_field.label)
        self.assertContains(response, 'python</span> 50%')

    def test_get_result_percentages_as_json(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.section_index,
                allow_multiple_submissions_per_user=True
            )

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)
        response = self.client.get(
            '/surveys/%s/results_json/' % molo_survey_page.slug)
        self.assertEqual(
            response.json(), {'Your favourite animal': {'python': 100}})

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'java'
        }, follow=True)
        response = self.client.get(
            '/surveys/%s/results_json/' % molo_survey_page.slug)
        self.assertEqual(response.json(),
                         {'Your favourite animal': {'java': 50, 'python': 50}})
        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'java'
        }, follow=True)
        response = self.client.get(
            '/surveys/%s/results_json/' % molo_survey_page.slug)
        self.assertEqual(response.json(),
                         {'Your favourite animal': {'java': 67, 'python': 33}})
        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'java'
        }, follow=True)
        response = self.client.get(
            '/surveys/%s/results_json/' % molo_survey_page.slug)
        self.assertEqual(response.json(),
                         {'Your favourite animal': {'java': 75, 'python': 25}})

    def test_multi_step_option(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.section_index,
                allow_anonymous_submissions=True,
                multi_step=True
            )

        extra_molo_survey_form_field = MoloSurveyFormField.objects.create(
            page=molo_survey_page,
            sort_order=2,
            label='Your favourite actor',
            field_type='singleline',
            required=True
        )

        response = self.client.get(molo_survey_page.url)

        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, molo_survey_page.introduction)
        self.assertContains(response, molo_survey_form_field.label)
        self.assertNotContains(response, extra_molo_survey_form_field.label)
        self.assertContains(response, 'Next Question')

        response = self.client.post(molo_survey_page.url + '?p=2', {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        })

        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, molo_survey_page.introduction)
        self.assertNotContains(response, molo_survey_form_field.label)
        self.assertContains(response, extra_molo_survey_form_field.label)
        self.assertContains(response, molo_survey_page.submit_text)

        response = self.client.post(molo_survey_page.url + '?p=3', {
            extra_molo_survey_form_field.label.lower().replace(' ', '-'):
                'Steven Seagal ;)'
        }, follow=True)

        self.assertContains(response, molo_survey_page.thank_you_text)

        # for test_multi_step_multi_submissions_anonymous
        return molo_survey_page.url

    def test_can_submit_after_validation_error(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.section_index,
                allow_anonymous_submissions=True
            )

        response = self.client.get(molo_survey_page.url)

        self.assertContains(response, molo_survey_page.title)
        self.assertContains(response, molo_survey_page.introduction)
        self.assertContains(response, molo_survey_form_field.label)

        response = self.client.post(molo_survey_page.url, {})

        self.assertContains(response, 'This field is required.')

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)

        self.assertContains(response, molo_survey_page.thank_you_text)

    def test_multi_step_multi_submissions_anonymous(self):
        '''
        Tests that multiple anonymous submissions are not allowed for
        multi-step surveys by default
        '''
        molo_survey_page_url = self.test_multi_step_option()

        response = self.client.get(molo_survey_page_url)

        self.assertContains(response,
                            'You have already completed this survey.')

    def test_survey_template_tag_on_home_page_specific(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.surveys_index)
        response = self.client.get("/")
        self.assertContains(response, 'Take The Survey</a>')
        self.assertContains(response, molo_survey_page.homepage_introduction)
        user = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client2.login(user=user)
        response = self.client2.get(self.site2.root_url)
        self.assertNotContains(response, 'Take The Survey</a>')

    def test_can_only_see_sites_surveys_in_admin(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.surveys_index)
        response = self.client.get("/")
        self.assertContains(response, 'Take The Survey</a>')
        self.assertContains(response, molo_survey_page.homepage_introduction)
        user = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client2.login(user=user)
        response = self.client2.get(self.site2.root_url)
        self.assertNotContains(response, 'Take The Survey</a>')
        self.login()
        response = self.client.get('/admin/surveys/')
        self.assertContains(
            response,
            '<h2><a href="/admin/surveys/submissions/%s/">'
            'Test Survey</a></h2>' % molo_survey_page.pk)
        user = get_user_model().objects.create_superuser(
            username='superuser2',
            email='superuser2@email.com', password='pass2')
        self.client2.login(username='superuser2', password='pass2')

        response = self.client2.get(self.site2.root_url + '/admin/surveys/')
        self.assertNotContains(
            response,
            '<h2><a href="/admin/surveys/submissions/%s/">'
            'Test Survey</a></h2>' % molo_survey_page.pk)

    def test_changing_languages_changes_survey(self):
        # Create a survey
        self.user = self.login()
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.surveys_index)
        # Create a translated survey
        response = self.client.post(reverse(
            'add_translation', args=[molo_survey_page.id, 'fr']))
        translated_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-test-survey')
        translated_survey.save_revision().publish()
        create_molo_survey_formfield(
            survey=translated_survey, field_type='singleline',
            label="Your favourite animal in french", required=True)

        # when requesting the english survey with the french language code
        # it should return the french survey
        request = RequestFactory().get(molo_survey_page.url)
        request.LANGUAGE_CODE = 'fr'
        request.context = {'page': molo_survey_page}
        request.site = self.main.get_site()
        response = molo_survey_page.serve_questions(request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['location'], translated_survey.url)

    def test_changing_languages_when_no_translation_stays_on_survey(self):
        setting = SiteSettings.objects.create(site=self.main.get_site())
        setting.show_only_translated_pages = True
        setting.save()

        # Create a survey
        self.user = self.login()
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.surveys_index)

        # when requesting the english survey with the french language code
        # it should return the english survey
        request = RequestFactory().get(molo_survey_page.url)
        request.LANGUAGE_CODE = 'fr'
        request.context = {'page': molo_survey_page}
        request.site = self.main.get_site()
        request.session = {}
        request.user = self.user
        response = molo_survey_page.serve_questions(request)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Test Survey')

    def test_can_see_translated_survey_submissions_in_admin(self):
        """ Test that submissions to translated surveys can be seen in the
            admin
        """
        # Create a survey
        self.user = self.login()
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.surveys_index)
        # Create a translated survey
        response = self.client.post(reverse(
            'add_translation', args=[molo_survey_page.id, 'fr']))
        translated_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-test-survey')
        translated_survey.save_revision().publish()
        translated_survey_form_field = create_molo_survey_formfield(
            survey=translated_survey, field_type='singleline',
            label="Your favourite animal in french", required=True)

        # Check both surveys are listed in the admin
        response = self.client.get('/admin/surveys/')
        self.assertContains(response, 'Test Survey')
        self.assertContains(response, 'French translation of Test Survey')

        # Submit responses to both surveys
        self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'):
                'an english answer'
        })
        self.client.post(translated_survey.url, {
            translated_survey_form_field.label.lower().replace(' ', '-'):
                'a french answer'
        })

        # Check the responses are shown on the submission pages
        response = self.client.get('/admin/surveys/submissions/%s/' %
                                   molo_survey_page.pk)
        self.assertContains(response, 'an english answer')
        self.assertNotContains(response, 'a french answer')
        response = self.client.get('/admin/surveys/submissions/%s/' %
                                   translated_survey.pk)
        self.assertNotContains(response, 'an english answer')
        self.assertContains(response, 'a french answer')

    def test_no_duplicate_indexes(self):
        self.assertTrue(SurveysIndexPage.objects.child_of(self.main2).exists())
        self.assertEquals(
            SurveysIndexPage.objects.child_of(self.main2).count(), 1)
        self.client.post(reverse(
            'wagtailadmin_pages:copy',
            args=(self.surveys_index.pk,)),
            data={
                'new_title': 'blank',
                'new_slug': 'blank',
                'new_parent_page': self.main2,
                'copy_subpages': 'true',
                'publish_copies': 'true'})
        self.assertEquals(
            SurveysIndexPage.objects.child_of(self.main2).count(), 1)

    def test_translated_survey(self):
        self.user = self.login()
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.surveys_index)

        self.client.post(reverse(
            'add_translation', args=[molo_survey_page.id, 'fr']))
        translated_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-test-survey')
        translated_survey.save_revision().publish()

        response = self.client.get("/")
        self.assertContains(response,
                            '<h1 class="surveys__title">Test Survey</h1>')
        self.assertNotContains(
            response,
            '<h1 class="surveys__title">French translation of Test Survey</h1>'
        )

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertNotContains(
            response,
            '<h1 class="surveys__title">Test Survey</h1>')
        self.assertContains(
            response,
            '<h1 class="surveys__title">French translation of Test Survey</h1>'
        )

    def test_survey_template_tag_on_footer(self):
        self.user = self.login()
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.surveys_index)

        self.client.post(reverse(
            'add_translation', args=[molo_survey_page.id, 'fr']))
        translated_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-test-survey')
        translated_survey.save_revision().publish()

        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/surveys-main-1/test-survey/" class="footer-link"> '
            '<div class="footer-link__thumbnail-icon"> '
            '<img src="/static/img/clipboard.png" '
            'class="menu-list__item--icon" /></div> '
            '<span class="footer-link__title">Test Survey', html=True)

        self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/surveys-main-1/french-translation-of-test-survey/"'
            'class="footer-link"> <div class="footer-link__thumbnail-icon"> '
            '<img src="/static/img/clipboard.png" '
            'class="menu-list__item--icon" /></div> '
            '<span class="footer-link__title">'
            'French translation of Test Survey', html=True)

    def test_survey_template_tag_on_section_page(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.section)

        response = self.client.get(self.section.url)
        self.assertContains(response, 'Take The Survey</a>')
        self.assertContains(response, molo_survey_page.homepage_introduction)

    def test_translated_survey_on_section_page(self):
        self.user = self.login()
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.section)

        self.client.post(reverse(
            'add_translation', args=[molo_survey_page.id, 'fr']))
        translated_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-test-survey')
        translated_survey.save_revision().publish()

        response = self.client.get(self.section.url)
        self.assertContains(response,
                            '<h1 class="surveys__title">Test Survey</h1>')
        self.assertNotContains(
            response,
            '<h1 class="surveys__title">French translation of Test Survey</h1>'
        )

        response = self.client.get('/locale/fr/')
        response = self.client.get(self.section.url)
        self.assertNotContains(
            response,
            '<h1 class="surveys__title">Test Survey</h1>')
        self.assertContains(
            response,
            '<h1 class="surveys__title">French translation of Test Survey</h1>'
        )

    def test_survey_template_tag_on_article_page(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(parent=self.article)
        response = self.client.get(self.article.url)
        self.assertContains(response,
                            'Take The Survey</a>'.format(
                                molo_survey_page.url))
        self.assertContains(response, molo_survey_page.homepage_introduction)

    def test_survey_list_display_direct_logged_out(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.surveys_index,
                display_survey_directly=True)
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Please log in to take this survey')
        self.assertNotContains(response, molo_survey_form_field.label)

    def test_survey_list_display_direct_logged_in(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.surveys_index,
                display_survey_directly=True)

        self.user = self.login()
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Please log in to take this survey')
        self.assertContains(response, molo_survey_form_field.label)

        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)

        self.assertContains(response, molo_survey_page.thank_you_text)

        response = self.client.get('/')
        self.assertNotContains(response, molo_survey_form_field.label)
        self.assertContains(response,
                            'You have already completed this survey.')

    def test_anonymous_submissions_option_display_direct(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.surveys_index,
                display_survey_directly=True,
                allow_anonymous_submissions=True,
            )

        response = self.client.get('/')

        self.assertContains(response, molo_survey_form_field.label)
        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)
        self.assertContains(response, molo_survey_page.thank_you_text)

        response = self.client.get('/')
        self.assertNotContains(response, molo_survey_form_field.label)
        self.assertContains(response,
                            'You have already completed this survey.')

    def test_multiple_submissions_display_direct(self):
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page_with_field(
                parent=self.surveys_index,
                display_survey_directly=True,
                allow_multiple_submissions_per_user=True,
            )

        self.user = self.login()
        response = self.client.post(molo_survey_page.url, {
            molo_survey_form_field.label.lower().replace(' ', '-'): 'python'
        }, follow=True)
        self.assertContains(response, molo_survey_page.thank_you_text)

        response = self.client.get('/')
        self.assertContains(response, molo_survey_form_field.label)
        self.assertNotContains(response,
                               'You have already completed this survey.')


class TestDeleteButtonRemoved(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.login()

        self.surveys_index = SurveysIndexPage(
            title='Security Questions',
            slug='security-questions')
        self.main.add_child(instance=self.surveys_index)
        self.surveys_index.save_revision().publish()

    def test_delete_btn_removed_for_surveys_index_page_in_main(self):

        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        self.assertEquals(response.status_code, 200)

        surveys_index_page_title = (
            SurveysIndexPage.objects.first().title)

        soup = BeautifulSoup(response.content, 'html.parser')
        index_page_rows = soup.find_all('tbody')[0].find_all('tr')

        for row in index_page_rows:
            if row.h2.a.string == surveys_index_page_title:
                self.assertTrue(row.find('a', string='Edit'))
                self.assertFalse(row.find('a', string='Delete'))

    def test_delete_button_removed_from_dropdown_menu(self):
        surveys_index_page = SurveysIndexPage.objects.first()

        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(surveys_index_page.pk)))
        self.assertEquals(response.status_code, 200)

        delete_link = ('<a href="/admin/pages/{0}/delete/" '
                       'title="Delete this page" class="u-link '
                       'is-live ">Delete</a>'
                       .format(str(surveys_index_page.pk)))
        self.assertNotContains(response, delete_link, html=True)

    def test_delete_button_removed_in_edit_menu(self):
        surveys_index_page = SurveysIndexPage.objects.first()

        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(surveys_index_page.pk)))
        self.assertEquals(response.status_code, 200)

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(surveys_index_page.pk)))
        self.assertNotContains(response, delete_button, html=True)


class TestSkipLogicSurveyView(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.molo_survey_page = self.new_survey('Test Survey')
        self.another_molo_survey_page = self.new_survey('Another Test Survey')

        self.last_molo_survey_form_field = MoloSurveyFormField.objects.create(
            page=self.molo_survey_page,
            sort_order=3,
            label='Your favourite actor',
            field_type='singleline',
            required=True
        )

        self.choices = ['next', 'end', 'survey', 'question']
        self.skip_logic_form_field = MoloSurveyFormField.objects.create(
            page=self.molo_survey_page,
            sort_order=1,
            label='Where should we go',
            field_type='dropdown',
            skip_logic=skip_logic_data(
                self.choices,
                self.choices,
                survey=self.another_molo_survey_page,
                question=self.last_molo_survey_form_field,
            ),
            required=True
        )

        self.molo_survey_form_field = MoloSurveyFormField.objects.create(
            page=self.molo_survey_page,
            sort_order=2,
            label='Your favourite animal',
            field_type='singleline',
            required=True
        )

        self.another_molo_survey_form_field = (
            MoloSurveyFormField.objects.create(
                page=self.another_molo_survey_page,
                sort_order=1,
                label='Your favourite actress',
                field_type='singleline',
                required=True
            )
        )

    def new_survey(self, name):
        survey = MoloSurveyPage(
            title=name, slug=slugify(name),
            introduction='Introduction to {}...'.format(name),
            thank_you_text='Thank you for taking the {}'.format(name),
            submit_text='survey submission text for {}'.format(name),
            allow_anonymous_submissions=True,
        )
        self.section_index.add_child(instance=survey)
        survey.save_revision().publish()
        return survey

    def assertSurveyAndQuestions(self, response, survey, questions):
        self.assertContains(response, survey.title)
        self.assertContains(response, survey.introduction)
        for question in questions:
            self.assertContains(response, question.label)
            self.assertContains(response, question.label)

    def test_skip_logic_next_question(self):
        response = self.client.get(self.molo_survey_page.url)

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.skip_logic_form_field]
        )
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label
        )
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, 'Next Question')

        response = self.client.post(self.molo_survey_page.url + '?p=2', {
            self.skip_logic_form_field.clean_name: self.choices[0],
        })

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.molo_survey_form_field, self.last_molo_survey_form_field]
        )
        self.assertNotContains(response, self.skip_logic_form_field.label)
        self.assertContains(response, self.molo_survey_page.submit_text)

        response = self.client.post(self.molo_survey_page.url + '?p=3', {
            self.molo_survey_form_field.clean_name: 'python',
            self.last_molo_survey_form_field.clean_name: 'Steven Seagal ;)',
        }, follow=True)

        self.assertContains(response, self.molo_survey_page.thank_you_text)

    def test_skip_logic_to_end(self):
        response = self.client.get(self.molo_survey_page.url)
        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.skip_logic_form_field]
        )
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label,
        )
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, 'Next Question')

        response = self.client.post(self.molo_survey_page.url + '?p=2', {
            self.skip_logic_form_field.clean_name: self.choices[1],
        }, follow=True)

        # Should end the survey and not complain about required
        # field for the last field

        self.assertContains(response, self.molo_survey_page.title)
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label
        )
        self.assertNotContains(response, self.molo_survey_page.submit_text)
        self.assertContains(response, self.molo_survey_page.thank_you_text)

    def test_skip_logic_to_another_survey(self):
        response = self.client.get(self.molo_survey_page.url)

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.skip_logic_form_field]
        )
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label
        )
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, 'Next Question')

        response = self.client.post(self.molo_survey_page.url + '?p=2', {
            self.skip_logic_form_field.clean_name: self.choices[2],
        }, follow=True)

        # Should end the survey and progress to the new survey
        self.assertSurveyAndQuestions(
            response,
            self.another_molo_survey_page,
            [self.another_molo_survey_form_field],
        )

    def test_skip_logic_to_another_question(self):
        response = self.client.get(self.molo_survey_page.url)

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.skip_logic_form_field]
        )
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label,
        )
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, 'Next Question')

        response = self.client.post(self.molo_survey_page.url + '?p=2', {
            self.skip_logic_form_field.clean_name: self.choices[3],
        }, follow=True)

        # Should end the survey and progress to the new survey
        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.last_molo_survey_form_field],
        )

    def test_skip_logic_checkbox_with_data(self):
        self.skip_logic_form_field.field_type = 'checkbox'
        self.skip_logic_form_field.skip_logic = skip_logic_data(
            ['', ''],
            self.choices[:2],
        )
        self.skip_logic_form_field.save()

        response = self.client.get(self.molo_survey_page.url)

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.skip_logic_form_field]
        )
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label,
        )
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, 'Next Question')

        response = self.client.post(self.molo_survey_page.url + '?p=2', {
            self.skip_logic_form_field.clean_name: 'on',
        }, follow=True)

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.molo_survey_form_field, self.last_molo_survey_form_field]
        )
        self.assertNotContains(response, self.skip_logic_form_field.label)
        self.assertContains(response, self.molo_survey_page.submit_text)

        response = self.client.post(self.molo_survey_page.url + '?p=3', {
            self.molo_survey_form_field.clean_name: 'python',
            self.last_molo_survey_form_field.clean_name: 'Steven Seagal ;)',
        }, follow=True)

        self.assertContains(response, self.molo_survey_page.thank_you_text)

    def test_skip_logic_checkbox_no_data(self):
        self.skip_logic_form_field.field_type = 'checkbox'
        self.skip_logic_form_field.skip_logic = skip_logic_data(
            ['', ''],
            self.choices[:2],
        )
        self.skip_logic_form_field.save()

        response = self.client.get(self.molo_survey_page.url)

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.skip_logic_form_field]
        )
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label,
        )
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, 'Next Question')

        # Unchecked textboxes have no data sent to the backend
        # Data cannot be empty as we will be submitting the csrf token
        response = self.client.post(
            self.molo_survey_page.url + '?p=2',
            {'csrf': 'dummy'},
            follow=True,
        )

        self.assertContains(response, self.molo_survey_page.title)
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertNotContains(
            response,
            self.last_molo_survey_form_field.label
        )
        self.assertNotContains(response, self.molo_survey_page.submit_text)
        self.assertContains(response, self.molo_survey_page.thank_you_text)

    def test_skip_logic_missed_required_with_checkbox(self):
        self.skip_logic_form_field.field_type = 'checkbox'
        self.skip_logic_form_field.skip_logic = skip_logic_data(
            ['', ''],
            [self.choices[3], self.choices[2]],  # question, survey
            survey=self.another_molo_survey_page,
            question=self.last_molo_survey_form_field,
        )
        self.skip_logic_form_field.save()

        # Skip a required question
        response = self.client.post(
            self.molo_survey_page.url + '?p=2',
            {self.skip_logic_form_field.clean_name: 'on'},
            follow=True,
        )

        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.last_molo_survey_form_field]
        )
        self.assertNotContains(response, self.skip_logic_form_field.label)
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, self.molo_survey_page.submit_text)

        # Dont answer last required question: trigger error messages
        response = self.client.post(
            self.molo_survey_page.url + '?p=3',
            {self.last_molo_survey_form_field.clean_name: ''},
            follow=True,
        )

        # Go back to the same page with validation errors showing
        self.assertSurveyAndQuestions(
            response,
            self.molo_survey_page,
            [self.last_molo_survey_form_field]
        )
        self.assertContains(response, 'required')
        self.assertNotContains(response, self.skip_logic_form_field.label)
        self.assertNotContains(response, self.molo_survey_form_field.label)
        self.assertContains(response, self.molo_survey_page.submit_text)

    def test_skip_logic_required_with_radio_button_field(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client.login(username='tester', password='tester')
        survey = MoloSurveyPage(
            title='Test Survey With Redio Button',
            slug='testw-survey-with-redio-button',
        )

        another_survey = MoloSurveyPage(
            title='Anotherw Test Survey',
            slug='anotherw-test-survey',
        )
        self.section_index.add_child(instance=survey)
        survey.save_revision().publish()
        self.section_index.add_child(instance=another_survey)
        another_survey.save_revision().publish()

        field_choices = ['next', 'end']

        third_field = MoloSurveyFormField.objects.create(
            page=survey,
            sort_order=4,
            label='A random animal',
            field_type='dropdown',
            skip_logic=skip_logic_data(
                field_choices,
                field_choices,
            ),
            required=True
        )
        first_field = MoloSurveyFormField.objects.create(
            page=survey,
            sort_order=1,
            label='Your other favourite animal',
            field_type='radio',
            skip_logic=skip_logic_data(
                field_choices + ['question', 'survey'],
                field_choices + ['question', 'survey'],
                question=third_field,
                survey=another_survey,
            ),
            required=True
        )
        second_field = MoloSurveyFormField.objects.create(
            page=survey,
            sort_order=2,
            label='Your favourite animal',
            field_type='dropdown',
            skip_logic=skip_logic_data(
                field_choices,
                field_choices,
            ),
            required=True
        )

        response = self.client.post(
            survey.url + '?p=2',
            {another_survey: ''},
            follow=True,
        )
        self.assertContains(response, 'required')
        self.assertNotContains(response, second_field.label)
        self.assertContains(response, first_field.label)


class TestPositiveNumberView(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.surveys_index = SurveysIndexPage(
            title='Surveys',
            slug='surveys')
        self.main.add_child(instance=self.surveys_index)
        self.surveys_index.save_revision().publish()

    def test_positive_number_field_validation(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client.login(username='tester', password='tester')
        survey = MoloSurveyPage(
            title='Test Survey With Positive Number',
            slug='testw-survey-with-positive-number',
            thank_you_text='Thank you for taking the survey',
        )
        self.surveys_index.add_child(instance=survey)
        survey.save_revision().publish()

        positive_number_field = MoloSurveyFormField.objects.create(
            page=survey,
            sort_order=1,
            label='Your lucky number?',
            field_type='positive_number',
            required=True
        )

        response = self.client.post(
            survey.url + '?p=2',
            {positive_number_field.clean_name: '-1'},
            follow=True,
        )

        self.assertContains(response, positive_number_field.label)
        self.assertContains(
            response, 'Ensure this value is greater than or equal to 0')

        response = self.client.post(
            survey.url + '?p=2',
            {positive_number_field.clean_name: '1'},
            follow=True,
        )

        self.assertContains(
            response, survey.thank_you_text)


class SegmentCountView(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester', email='tester@example.com', password='tester')
        # Create survey
        self.personalisable_survey = PersonalisableSurvey(title='Test Survey')
        SurveysIndexPage.objects.first().add_child(
            instance=self.personalisable_survey
        )
        self.personalisable_survey.save_revision()
        PersonalisableSurveyFormField.objects.create(
            field_type='singleline', label='Singleline Text',
            page=self.personalisable_survey
        )

    def submit_survey(self, survey, user):
        submission = survey.get_submission_class()
        data = {field.clean_name: 'super random text'
                for field in survey.get_form_fields()}
        submission.objects.create(user=user, page=self.personalisable_survey,
                                  form_data=json.dumps(data))

    def test_segment_user_count(self):
        self.submit_survey(self.personalisable_survey, self.user)
        response = self.client.post('/surveys/count/', SEGMENT_FORM_DATA)

        self.assertDictEqual(response.json(), {"segmentusercount": 1})

    def test_segment_user_count_returns_errors(self):
        self.submit_survey(self.personalisable_survey, self.user)
        data = SEGMENT_FORM_DATA
        data['name'] = [""]
        data['surveys_surveyresponserule_related-0-survey'] = ['20']
        response = self.client.post('/surveys/count/', data)

        self.assertDictEqual(response.json(), {"errors": {
            "surveys_surveyresponserule_related-0-survey": [
                "Select a valid choice. That choice is not one of the "
                "available choices."],
            "name": ["This field is required."]}})


class TestPollsViaSurveysView(TestCase, MoloTestCaseMixin):

    """
    Tests to check if polls are not
    being paginated when they include fields with skip_logic_data.
    Also test that page_break is not causing any pagination on the surveys
    """
    def setUp(self):
        self.mk_main()
        self.choices = ['next', 'end', 'survey']
        self.surveys_index = SurveysIndexPage.objects.first()

    def test_molo_poll(self):
        survey = create_molo_survey_page(
            self.surveys_index, display_survey_directly=True)
        drop_down_field = create_molo_dropddown_field(
            self.surveys_index, survey, self.choices)
        response = self.client.post(
            survey.url + '?p=1',
            {drop_down_field.clean_name: 'next'},
            follow=True,
        )
        self.assertContains(response, survey.thank_you_text)
        self.assertNotContains(response, 'That page number is less than 1')

    def test_molo_poll_with_page_break(self):
        survey = create_molo_survey_page(
            self.surveys_index, display_survey_directly=True)
        drop_down_field = create_molo_dropddown_field(
            self.surveys_index, survey, self.choices, page_break=True)
        response = self.client.post(
            survey.url + '?p=1',
            {drop_down_field.clean_name: 'next'},
            follow=True,
        )
        self.assertContains(response, survey.thank_you_text)
        self.assertNotContains(response, 'That page number is less than 1')

    def test_personalisable_survey_poll(self):
        survey = create_personalisable_survey_page(
            self.surveys_index,
            display_survey_directly=True)
        drop_down_field = create_personalisable_dropddown_field(
            self.surveys_index, survey, self.choices)
        response = self.client.post(
            survey.url + '?p=1',
            {drop_down_field.clean_name: 'next'},
            follow=True,
        )
        self.assertContains(response, survey.thank_you_text)
        self.assertNotContains(response, 'That page number is less than 1')

    def test_personalisable_survey_poll_with_page_break(self):
        survey = create_personalisable_survey_page(
            self.surveys_index, display_survey_directly=True)
        drop_down_field = create_personalisable_dropddown_field(
            self.surveys_index, survey, self.choices, page_break=True)
        response = self.client.post(
            survey.url + '?p=1',
            {drop_down_field.clean_name: 'next'},
            follow=True,
        )
        self.assertContains(response, survey.thank_you_text)
        self.assertNotContains(response, 'That page number is less than 1')
