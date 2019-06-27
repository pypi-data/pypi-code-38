from django.conf.urls import url, include

app_name='aparnik'

urlpatterns = [
    url(r'^users/', include('aparnik.contrib.users.api.urls', namespace='users')),
    url(r'^addresses/', include('aparnik.contrib.addresses.api.urls', namespace='addresses')),
    url(r'^bankaccounts/', include('aparnik.contrib.bankaccounts.api.urls', namespace='bankaccounts')),
    url(r'^aboutus/', include('aparnik.contrib.aboutus.api.urls', namespace='aboutus')),
    url(r'^contactus/', include('aparnik.contrib.contactus.api.urls', namespace='contactus')),
    url(r'^invitations/', include('aparnik.contrib.invitation.api.urls', namespace='invitations')),
    url(r'^filefields/', include('aparnik.contrib.filefields.api.urls', namespace='files')),
    url(r'^provinces/', include('aparnik.contrib.province.api.urls', namespace='provinces')),
    url(r'^models/', include('aparnik.contrib.basemodels.api.urls', namespace='models')),
    url(r'^bookmarks/', include('aparnik.contrib.bookmarks.api.urls', namespace='bookmarks')),
    url(r'^reviews/', include('aparnik.contrib.reviews.api.urls', namespace='reviews')),
    url(r'^qa/', include('aparnik.contrib.questionanswers.api.urls', namespace='qa')),
    url(r'^pages/', include('aparnik.contrib.pages.api.urls', namespace='pages')),
    url(r'^sliders/', include('aparnik.contrib.sliders.api.urls', namespace='sliders')),
    url(r'^notifications/', include('aparnik.contrib.notifications.api.urls', namespace='notifications')),
    url(r'^notifiesme/', include('aparnik.contrib.notifiesme.api.urls', namespace='notifiesme')),
    url(r'^supports/', include('aparnik.contrib.supports.api.urls', namespace='supports')),
    url(r'^faq/', include('aparnik.contrib.faq.api.urls', namespace='faq')),
    url(r'^termsandconditions/', include('aparnik.contrib.termsandconditions.api.urls', namespace='termsandconditions')),
    url(r'^categories/', include('aparnik.contrib.categories.api.urls', namespace='categories')),
    url(r'^segments/', include('aparnik.contrib.segments.api.urls', namespace='segments')),
    url(r'^shops/', include('aparnik.packages.shops.urls.api', namespace='shops')),
    url(r'^educations/', include('aparnik.packages.educations.urls.api', namespace='educations')),
    url(r'^news/', include('aparnik.packages.news.api.urls', namespace='news')),
]
