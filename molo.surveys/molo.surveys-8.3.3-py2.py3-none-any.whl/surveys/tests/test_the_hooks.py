from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from molo.core.models import SiteLanguageRelation, Main, Languages
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import (MoloSurveyPage, MoloSurveyFormField,
                                 SurveysIndexPage, SurveyTermsConditions,
                                 TermsAndConditionsIndexPage)

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

        # Create surveys index pages
        self.surveys_index = SurveysIndexPage.objects.child_of(
            self.main).first()

        # create terms and conditions index_page
        terms_conditions_index = TermsAndConditionsIndexPage(
            title='terms and conditions pages', slug='terms-1')
        self.surveys_index.add_child(instance=terms_conditions_index)
        terms_conditions_index.save_revision().publish()

        # create terms and conditions page
        self.article = self.mk_article(
            terms_conditions_index, title='ts and cs')

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
        self.mk_main2(title='main3', slug='main3', path="00010003")
        self.client2 = Client(HTTP_HOST=self.main2.get_site().hostname)

    def create_molo_survey_page(self, parent, **kwargs):
        molo_survey_page = MoloSurveyPage(
            title='Test Survey', slug='test-survey',
            introduction='Introduction to Test Survey ...',
            thank_you_text='Thank you for taking the Test Survey',
            submit_text='survey submission text',
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

    def test_copying_main_copies_surveys_relations_correctly(self):
        self.user = self.login()
        # create survey page
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page(
                parent=self.surveys_index,
                homepage_button_text='share your story yo')

        # create the terms and conditions relation with survey page
        SurveyTermsConditions.objects.create(
            page=molo_survey_page, terms_and_conditions=self.article)
        # copy one main to create another
        response = self.client.post(reverse(
            'wagtailadmin_pages:copy',
            args=(self.main.id,)),
            data={
                'new_title': 'blank',
                'new_slug': 'blank',
                'new_parent_page': self.root.id,
                'copy_subpages': 'true',
                'publish_copies': 'true'})
        self.assertEquals(response.status_code, 302)
        main3 = Main.objects.get(slug='blank')
        self.assertEquals(
            main3.get_children().count(), self.main.get_children().count())

        # it should replace the terms and conditions page with the new one
        relation = MoloSurveyPage.objects.descendant_of(
            main3).first().terms_and_conditions.first()
        self.assertTrue(relation.terms_and_conditions.is_descendant_of(main3))
