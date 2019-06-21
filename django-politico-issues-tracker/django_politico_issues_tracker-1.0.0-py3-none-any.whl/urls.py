from django.urls import path, include
from rest_framework import routers
from .viewsets import CategoryViewset, IssueViewset, CandidateViewset
from .views import (
    Home,
    Category,
    Issue,
    BakeryHome,
    BakeryCategory,
    BakeryIssue,
    BakeryCandidate,
    BakerySitemap,
)

# Django REST
router = routers.DefaultRouter()
router.register(r"category", CategoryViewset, base_name="category")
router.register(r"issue", IssueViewset, base_name="issue")
router.register(r"candidate", CandidateViewset, base_name="candidate")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/bakery/sitemap/", BakerySitemap.as_view(), name="bakery-sitemap"
    ),
    path("api/bakery/home/", BakeryHome.as_view(), name="bakery-home"),
    path(
        "api/bakery/category/<slug:category>/",
        BakeryCategory.as_view(),
        name="bakery-category",
    ),
    path(
        "api/bakery/issue/<slug:issue>/",
        BakeryIssue.as_view(),
        name="bakery-issue",
    ),
    path(
        "api/bakery/candidate/<slug:candidate>/",
        BakeryCandidate.as_view(),
        name="bakery-candidate",
    ),
    path("", Home.as_view(), name="home"),
    path("category/<slug:category>/", Category.as_view(), name="category"),
    path("issue/<slug:issue>/", Issue.as_view(), name="issue"),
]
