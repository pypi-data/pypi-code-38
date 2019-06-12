from django.conf import settings
from django.urls import include, path

from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()


router.register('categories', views.CategoryViewSet, 'api-category')
router.register('faqs', views.FAQViewSet, 'api-faq')


urlpatterns = [
    path('api/', include(router.urls))
]
