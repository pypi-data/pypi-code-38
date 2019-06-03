from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from votebase.core.voting.views import VoteView, WelcomeView, FinishView, \
    InactiveView, AlreadyVotedView, OnlyForRegisteredView, PasswordView


urlpatterns = [
    url(_(r'welcome/(?P<pk>[-\d]+)/$'), WelcomeView.as_view(), name='voting_welcome'),
    url(_(r'finish/(?P<pk>[-\d]+)/$'), FinishView.as_view(), name='voting_finish'),
    url(_(r'inactive/(?P<pk>[-\d]+)/$'), InactiveView.as_view(), name='voting_inactive'),
    url(_(r'password/(?P<pk>[-\d]+)/$'), PasswordView.as_view(), name='voting_password'),
    url(_(r'already-voted/(?P<pk>[-\d]+)/$'), AlreadyVotedView.as_view(), name='voting_already_voted'),
    url(_(r'only-for-registered/(?P<pk>[-\d]+)/$'), OnlyForRegisteredView.as_view(), name='voting_for_registered'),
    url(r'(?P<pk>[-\d]+)/$', VoteView.as_view(), name='voting_vote'),
]
