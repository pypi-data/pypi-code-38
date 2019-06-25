from django.conf.urls import url, include

from ievv_opensource.ievv_elasticsearch2browser.cradmin import ElasticSearchBrowserCrAdminInstance

urlpatterns = [
    url(r'^', include(ElasticSearchBrowserCrAdminInstance.urls())),
]
