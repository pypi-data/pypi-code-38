

class AdminSite(object):

    def __init__(self, name='admin', app_name='admin'):
        self.name = name
        self.app_name = app_name

    def get_urls(self):
        from django.conf.urls import patterns, url, include

        from bigtiger.contrib.admin.views.main import MainView
        from bigtiger.contrib.admin.views.login import LoginView, PwdModifyView, logout
        from bigtiger.contrib.admin.views.iframe import IframeView, IframeScrollView
        from bigtiger.contrib.weather.views import baidu_weather

        import bigtiger.contrib.admin.sae.urls
        import bigtiger.contrib.admin.apis.urls
        import bigtiger.contrib.admin.urls

        urlpatterns = patterns(
            '',
            url(r'^$', LoginView.as_view(), name='index'),
            url(r'^login/$', LoginView.as_view(), name='login'),
            url(r'^logout/$', logout, name='logout'),
            url(r'^password_change/$', PwdModifyView.as_view(),
                name='password_change'),

            url(r'^main/$', MainView.as_view(), name='main'),
            url(r'^iframe/$', IframeView.as_view(), name='iframe'),
            url(r'^iframe_scroll/$', IframeScrollView.as_view(),
                name='iframe_scroll'),
            url(r'^baidu_weather/$', baidu_weather, name='weather'),

            url(r'^pages/', include(bigtiger.contrib.admin.urls)),
            url(r'^api/', include(bigtiger.contrib.admin.apis.urls)),
            url(r'^sae/', include(bigtiger.contrib.admin.sae.urls)),
        )
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name


# This global object represents the default admin site, for the common case.
# You can instantiate AdminSite in your own code to create a custom admin site.
site = AdminSite()
