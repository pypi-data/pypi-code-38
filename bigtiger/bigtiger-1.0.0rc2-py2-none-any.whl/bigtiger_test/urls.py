from django.conf.urls import patterns, include, url
from django.shortcuts import HttpResponseRedirect

from bigtiger.contrib import admin

def login(request):
    return HttpResponseRedirect(settings.LOGIN_URL)


urlpatterns = patterns(
    '',
    url(r'^$', login, name='login'),
    url(r'^admin/', include(admin.site.urls)),
)


from django.conf import settings
if settings.DEBUG:

    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}),
        (r'^bower_components/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.BOWER_COMPONENTS_ROOT, 'show_indexes': True}),
        (r'^bigtiger/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.BIGTIGER_ROOT, 'show_indexes': True}),
    )
