
from django.conf.urls import url
from molo.surveys.views import (
    SurveySuccess, ResultsPercentagesJson, submission_article,
    get_segment_user_count
)


urlpatterns = [
    url(
        r"^(?P<slug>[\w-]+)/success/$",
        SurveySuccess.as_view(),
        name="success"
    ),
    url(
        r"^(?P<slug>[\w-]+)/results_json/$",
        ResultsPercentagesJson.as_view(),
        name="results_json"
    ),
    url(
        r'^submissions/(\d+)/article/(\d+)/$',
        submission_article, name='article'
    ),
    url(
        r"^count/$",
        get_segment_user_count,
        name="segmentusercount"
    ),
]
