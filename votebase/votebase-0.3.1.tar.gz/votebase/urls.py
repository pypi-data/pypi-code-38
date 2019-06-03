from django.conf import settings
from django.conf.urls import include, url
from django.utils.translation import ugettext_lazy as _

from votebase.views import HomeView


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(_(r'^users/(?P<pk>[-\d]+)'), HomeView.as_view(), name='users_pk'),
    url(_(r'^users/(?P<slug>[-\w]+)'), HomeView.as_view(), name='users_slug'),
    url(_(r'^accounts/'), include('votebase.core.accounts.urls')),
    url(_(r'^surveys/'), include('votebase.core.surveys.urls')),
    url(_(r'^questions/'), include('votebase.core.questions.urls')),
    url(_(r'^voting/'), include('votebase.core.voting.urls')),
    url(_(r'^statistics/'), include('votebase.core.statistics.urls')),
#    url(_(r'^payments/'), include('votebase.core.payments.urls')),
    url(_(r'^impersonate/'), include('impersonate.urls')),
]
