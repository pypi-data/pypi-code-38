from django.test import TestCase, Client

from molo.core.models import Main, SiteLanguageRelation, Languages
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.utils import generate_slug
from molo.surveys.models import (
    SurveysIndexPage,
    MoloSurveyPage,
    MoloSurveyFormField
)
from wagtail.core.models import Site


class TestSites(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.surveys_index = SurveysIndexPage.objects.child_of(
            self.main).first()

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

    def test_two_sites_point_to_one_root_page(self):
        # assert that there is only one site rooted at main
        self.assertEquals(self.main.sites_rooted_here.count(), 1)
        client_1 = Client()
        # add a site that points to the same root page
        site_2 = Site.objects.create(
            hostname=generate_slug('site2'), port=80, root_page=self.main)
        # create a link buetween the current langauges and the new site
        Languages.objects.create(
            site_id=site_2.pk)
        SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(site_2),
            locale='en',
            is_active=True)
        client_2 = Client(HTTP_HOST=site_2.hostname)

        # assert that there are now two sites rooted at main
        self.assertEquals(self.main.sites_rooted_here.count(), 2)

        # create molo survey page
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page(
                parent=self.surveys_index,
                homepage_button_text='share your story yo')

        # assert that both sites render the survey
        response = client_1.get('/surveys-main-1/test-survey/')
        self.assertEquals(response.status_code, 200)
        response = client_2.get(
            site_2.root_url + '/surveys-main-1/test-survey/')
        self.assertEquals(response.status_code, 200)
