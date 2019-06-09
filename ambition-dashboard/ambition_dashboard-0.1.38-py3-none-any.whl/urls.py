from django.apps import apps as django_apps
from django.urls.conf import path

from .patterns import screening_identifier
from .views import (
    AeHomeView,
    AeListboardView,
    ClosedTmgAeListboardView,
    DataManagerHomeView,
    DeathReportListboardView,
    NewTmgAeListboardView,
    OpenTmgAeListboardView,
    ScreeningListboardView,
    SubjectDashboardView,
    SubjectListboardView,
    SubjectReviewListboardView,
    TmgDeathListboardView,
    TmgHomeView,
    TmgSummaryListboardView,
)

app_name = "ambition_dashboard"

subject_identifier_pattern = django_apps.get_app_config(
    "edc_identifier"
).subject_identifier_pattern  # "092\-[0-9\-]+"


urlpatterns = [
    path("tmg/", TmgHomeView.as_view(), name="tmg_home_url"),
    path("ae/", AeHomeView.as_view(), name="ae_home_url"),
    path("dm/", DataManagerHomeView.as_view(), name="dm_home_url"),
]

urlpatterns += SubjectListboardView.urls(
    namespace=app_name,
    label="subject_listboard",
    identifier_pattern=subject_identifier_pattern,
)
urlpatterns += ScreeningListboardView.urls(
    namespace=app_name,
    label="screening_listboard",
    identifier_label="screening_identifier",
    identifier_pattern=screening_identifier,
)
urlpatterns += SubjectDashboardView.urls(
    namespace=app_name,
    label="subject_dashboard",
    identifier_pattern=subject_identifier_pattern,
)


urlpatterns += NewTmgAeListboardView.urls(
    namespace=app_name,
    label="new_tmg_ae_listboard",
    identifier_pattern=subject_identifier_pattern,
)
urlpatterns += OpenTmgAeListboardView.urls(
    namespace=app_name,
    label="open_tmg_ae_listboard",
    identifier_pattern=subject_identifier_pattern,
)
urlpatterns += ClosedTmgAeListboardView.urls(
    namespace=app_name,
    label="closed_tmg_ae_listboard",
    identifier_pattern=subject_identifier_pattern,
)


urlpatterns += TmgDeathListboardView.urls(
    namespace=app_name,
    label="tmg_death_listboard",
    identifier_pattern=subject_identifier_pattern,
)
urlpatterns += TmgSummaryListboardView.urls(
    namespace=app_name,
    label="tmg_summary_listboard",
    identifier_pattern=subject_identifier_pattern,
)
urlpatterns += SubjectReviewListboardView.urls(
    namespace=app_name,
    label="subject_review_listboard",
    identifier_pattern=subject_identifier_pattern,
)
urlpatterns += AeListboardView.urls(
    namespace=app_name,
    label="ae_listboard",
    identifier_pattern=subject_identifier_pattern,
)
urlpatterns += DeathReportListboardView.urls(
    namespace=app_name,
    label="death_report_listboard",
    identifier_pattern=subject_identifier_pattern,
)
