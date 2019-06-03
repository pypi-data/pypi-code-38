from django.conf.urls import url

from views.accounts import RegisterView, LoginView, ProfileView, LogoutView
from views.statistics import VotersView
from views.surveys import SurveysView, SurveyView, SegmentView, SegmentUpdateView
from views.voting import VotingView

urlpatterns = [
    url(r'^accounts/register/$', RegisterView.as_view(), name='api_v1_register'),  # POST
    url(r'^accounts/login/$', LoginView.as_view(), name='api_v1_login'),  # POST
    url(r'^accounts/profile/$', ProfileView.as_view(), name='api_v1_profile'),  # GET & POST
    url(r'^accounts/logout/$', LogoutView.as_view(), name='api_v1_logout'),  # GET

    url(r'^surveys/segment/(?P<pk>[-\d]+)/update/$', SegmentUpdateView.as_view(), name='api_v1_segment_update'),  # POST
    url(r'^surveys/segment/(?P<pk>[-\d]+)/$', SegmentView.as_view(), name='api_v1_segment'),  # GET
    url(r'^surveys/(?P<pk>[-\d]+)/$', SurveyView.as_view(), name='api_v1_survey'),  # GET
    url(r'^surveys/$', SurveysView.as_view(), name='api_v1_surveys'),  # GET

    url(r'^voters/(?P<segment_pk>[-\d]+)/$', VotersView.as_view(), name='api_v1_voters'),  # GET  # deprecated !!!

    url(r'^statistics/voters/(?P<segment_pk>[-\d]+)/$', VotersView.as_view(), name='api_v1_statistics_voters'),  # GET

    url(r'^voting/(?P<segment_pk>[-\d]+)/vote/$', VotingView.as_view(), name='api_v1_vote'),  # POST
]
