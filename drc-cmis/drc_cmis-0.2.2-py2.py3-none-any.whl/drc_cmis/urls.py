from django.urls import path

from .views import CmisDownloadView

app_name = "drc_cmis"
urlpatterns = [path("<uuid>.bin", CmisDownloadView.as_view(), name="cmis_download")]
