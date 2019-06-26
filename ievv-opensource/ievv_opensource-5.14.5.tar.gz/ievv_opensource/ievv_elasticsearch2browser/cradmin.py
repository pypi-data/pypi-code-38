from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django_cradmin import crinstance, crmenu

from ievv_opensource.ievv_elasticsearch2browser.views import indexbrowse


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add_menuitem(
            label=_('ElasticSearch'), url=self.appindex_url('indexbrowse'),
            active=self.request.cradmin_app.appname == 'indexbrowse')


class ElasticSearchBrowserCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = 'ievv_elasticsearchbrowser'
    menuclass = Menu
    rolefrontpage_appname = 'indexbrowse'
    flatten_rolefrontpage_url = True

    apps = [
        ('indexbrowse', indexbrowse.App),
    ]

    def has_access(self):
        return self.request.user.is_superuser

    @classmethod
    def matches_urlpath(cls, urlpath):
        """
        We only need this because we have multiple cradmin UIs
        in the same project.
        """
        return urlpath.startswith('/ievv_elasticsearch2browser')
