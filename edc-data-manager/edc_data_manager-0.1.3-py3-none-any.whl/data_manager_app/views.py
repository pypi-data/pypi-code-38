from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin
from edc_review_dashboard.views import (
    SubjectReviewListboardView as BaseSubjectReviewListboardView,
)
from edc_subject_dashboard.views import SubjectDashboardView as BaseSubjectDashboardView


class SubjectReviewListboardView(BaseSubjectReviewListboardView):

    listboard_model = "data_manager_app.subjectvisit"
    navbar_name = "edc_review_dashboard"
    navbar_selected = "review"

    def get_navbar_context_data(self, context):
        return context

    @property
    def has_view_listboard_perms(self):
        return True

    @property
    def has_view_only_my_listboard_perms(self):
        return False


class SubjectDashboardView(BaseSubjectDashboardView):

    consent_model = "data_manager_app.subjectconsent"
    navbar_name = "data_manager_app"
    visit_model = "data_manager_app.subjectvisit"

    def get_navbar_context_data(self, context):
        return context


class SubjectListboardView(ListboardView):

    listboard_model = "data_manager_app.subjectvisit"
    listboard_template = "subject_listboard_template"
    listboard_url = "subject_listboard_url"
    navbar_name = "data_manager_app"

    def get_navbar_context_data(self, context):
        return context


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):

    template_name = f"data_manager_app/home.html"
    navbar_name = "data_manager_app"
    navbar_selected_item = "data_manager_app"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            edc_packages=["not available"],
            third_party_packages=["not available"],
            installed_apps=settings.INSTALLED_APPS,
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
