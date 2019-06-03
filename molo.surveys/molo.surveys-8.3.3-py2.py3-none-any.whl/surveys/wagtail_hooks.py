from django.conf import settings
from django.conf.urls import include, url
from django.utils.html import format_html_join

from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.core import hooks

from molo.surveys.models import MoloSurveyPage, SurveyTermsConditions
from molo.surveys import admin_urls
from molo.core.models import ArticlePage

from .admin import SegmentUserGroupAdmin


modeladmin_register(SegmentUserGroupAdmin)


@hooks.register('insert_global_admin_js')
def global_admin_js():
    js_files = [
        'js/survey-admin.js',
    ]

    js_includes = format_html_join(
        '\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes


@hooks.register('after_copy_page')
def create_new_page_relations(request, page, new_page):
    if page and new_page:
        if new_page.get_descendants().count() >= \
                page.get_descendants().count():
            for survey in MoloSurveyPage.objects.descendant_of(
                    new_page.get_site().root_page):
                # replace old terms and conditions with new one, if it exists
                relations = SurveyTermsConditions.objects.filter(page=survey)
                for relation in relations:
                    if relation.terms_and_conditions:
                        new_article = ArticlePage.objects.descendant_of(
                            new_page.get_site().root_page).filter(
                                slug=relation.terms_and_conditions.slug)\
                            .first()
                        relation.terms_and_conditions = new_article
                        relation.save()


# This overrwrites the wagtailsuveys admin urls in order to use custom
# survey index view
@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^surveys/', include(admin_urls)),
    ]
