from django.contrib import admin
from django.urls import path

from .admin_site import data_manager_app_admin
from .views import (
    HomeView,
    SubjectDashboardView,
    SubjectListboardView,
    SubjectReviewListboardView,
)

app_name = "data_manager_app"

urlpatterns = SubjectReviewListboardView.urls(
    app_name, label="subject_review_listboard")
urlpatterns += SubjectDashboardView.urls(
    app_name, label="subject_dashboard")
urlpatterns += SubjectListboardView.urls(
    app_name, label="subject_dashboard")

urlpatterns += [
    path("admin/", admin.site.urls),
    path("admin/", data_manager_app_admin.urls),
    path("", HomeView.as_view(), name="home_url"),
    path("", HomeView.as_view(), name="administration_url"),
]
