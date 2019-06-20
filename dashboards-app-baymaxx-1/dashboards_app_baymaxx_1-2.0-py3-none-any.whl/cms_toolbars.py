# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.translation import (
    ugettext as _, get_language_from_request, override)

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool

from aldryn_apphooks_config.utils import get_app_instance
from aldryn_translation_tools.utils import (
    get_object_from_request,
    get_admin_url,
)

from .models import Dashboard
from .cms_appconfig import Dashboards_appConfig


@toolbar_pool.register
class Dashboards_appToolbar(CMSToolbar):
    # watch_models must be a list, not a tuple
    # see https://github.com/divio/django-cms/issues/4135
    watch_models = [Dashboard, ]
    supported_apps = ('dashboards_app',)

    def get_on_delete_redirect_url(self, dashboard, language):
        with override(language):
            url = reverse(
                '{0}:dashboard-list'.format(dashboard.app_config.namespace))
        return url

    def __get_dashboards_app_config(self):
        try:
            __, config = get_app_instance(self.request)
            if not isinstance(config, Dashboards_appConfig):
                # This is not the app_hook you are looking for.
                return None
        except ImproperlyConfigured:
            # There is no app_hook at all.
            return None

        return config

    def populate(self):
        config = self.__get_dashboards_app_config()
        if not config:
            # Do nothing if there is no Dashboards_app app_config to work with
            return

        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if user and view_name:
            language = get_language_from_request(self.request, check_path=True)

            # If we're on an Dashboard detail page, then get the dashboard
            if view_name == '{0}:dashboard-detail'.format(config.namespace):
                dashboard = get_object_from_request(Dashboard, self.request)
            else:
                dashboard = None

            menu = self.toolbar.get_or_create_menu('dashboards_app-app',
                                                   config.get_app_title())

            change_config_perm = user.has_perm(
                'dashboards_app.change_dashboards_appconfig')
            add_config_perm = user.has_perm(
                'dashboards_app.add_dashboards_appconfig')
            config_perms = [change_config_perm, add_config_perm]

            change_dashboard_perm = user.has_perm(
                'dashboards_app.change_dashboard')
            delete_dashboard_perm = user.has_perm(
                'dashboards_app.delete_dashboard')
            add_dashboard_perm = user.has_perm('dashboards_app.add_dashboard')
            dashboard_perms = [change_dashboard_perm, add_dashboard_perm,
                             delete_dashboard_perm, ]

            if change_config_perm:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('dashboards_app_dashboards_appconfig_change',
                                    [config.pk, ], **url_args)
                menu.add_modal_item(_('Configure addon'), url=url)

            if any(config_perms) and any(dashboard_perms):
                menu.add_break()

            if change_dashboard_perm:
                url_args = {}
                if config:
                    url_args = {'app_config__id__exact': config.pk}
                url = get_admin_url('dashboards_app_dashboard_changelist',
                                    **url_args)
                menu.add_sideframe_item(_('Dashboard list'), url=url)

            if add_dashboard_perm:
                url_args = {'app_config': config.pk, 'owner': user.pk, }
                if language:
                    url_args.update({'language': language, })
                url = get_admin_url('dashboards_app_dashboard_add', **url_args)
                menu.add_modal_item(_('Add new dashboard'), url=url)

            if change_dashboard_perm and dashboard:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('dashboards_app_dashboard_change',
                                    [dashboard.pk, ], **url_args)
                menu.add_modal_item(_('Edit this dashboard'), url=url,
                                    active=True)

            if delete_dashboard_perm and dashboard:
                redirect_url = self.get_on_delete_redirect_url(
                    dashboard, language=language)
                url = get_admin_url('dashboards_app_dashboard_delete',
                                    [dashboard.pk, ])
                menu.add_modal_item(_('Delete this dashboard'), url=url,
                                    on_close=redirect_url)
