from django.conf.urls import url
from .views import RetrievePackagingHierarchyView

app_name = 'quartet_integrations'

urlpatterns = [
    url(
        r'^PackagingHierarchyServiceAMService/retrievePackagingHierarchyResponse/$',
        RetrievePackagingHierarchyView.as_view(), name="retrievePackagingHierarchyResponse"
    )
]
