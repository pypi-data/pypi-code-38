# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from distutils.version import LooseVersion
from django.utils.translation import ugettext_lazy as _

from cms import __version__ as cms_version
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models, forms
from .utils import add_prefix_to_path, default_reverse

CMS_GTE_330 = LooseVersion(cms_version) >= LooseVersion('3.3.0')


class TemplatePrefixMixin(object):

    def get_render_template(self, context, instance, placeholder):
        if (hasattr(instance, 'app_config') and
                instance.app_config.template_prefix):
            return add_prefix_to_path(
                self.render_template,
                instance.app_config.template_prefix
            )
        return self.render_template


class Dashboards_appPlugin(TemplatePrefixMixin, CMSPluginBase):
    module = 'Dashboards App'


class AdjustableCacheMixin(object):
    """
    For django CMS < 3.3.0 installations, we have no choice but to disable the
    cache where there is time-sensitive information. However, in later CMS
    versions, we can configure it with `get_cache_expiration()`.
    """
    if not CMS_GTE_330:
        cache = False

    def get_cache_expiration(self, request, instance, placeholder):
        return getattr(instance, 'cache_duration', 0)

    def get_fieldsets(self, request, obj=None):
        """
        Removes the cache_duration field from the displayed form if we're not
        using django CMS v3.3.0 or later.
        """
        fieldsets = super(AdjustableCacheMixin, self).get_fieldsets(request, obj=None)
        if CMS_GTE_330:
            return fieldsets

        field = 'cache_duration'
        for fieldset in fieldsets:
            new_fieldset = [
                item for item in fieldset[1]['fields'] if item != field]
            fieldset[1]['fields'] = tuple(new_fieldset)
        return fieldsets


@plugin_pool.register_plugin
class Dashboards_appArchivePlugin(AdjustableCacheMixin, Dashboards_appPlugin):
    render_template = 'dashboards_app/plugins/archive.html'
    name = _('Archive')
    model = models.Dashboards_appArchivePlugin
    form = forms.Dashboards_appArchivePluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance

        queryset = models.Dashboard.objects

        context['dates'] = queryset.get_months(
            request,
            namespace=instance.app_config.namespace
        )
        return context


@plugin_pool.register_plugin
class Dashboards_appDashboardSearchPlugin(Dashboards_appPlugin):
    render_template = 'dashboards_app/plugins/dashboard_search.html'
    name = _('Dashboard Search')
    model = models.Dashboards_appDashboardSearchPlugin
    form = forms.Dashboards_appDashboardSearchPluginForm

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['query_url'] = default_reverse('{0}:dashboard-search'.format(
            instance.app_config.namespace), default=None)
        return context


@plugin_pool.register_plugin
class Dashboards_appAuthorsPlugin(Dashboards_appPlugin):
    render_template = 'dashboards_app/plugins/authors.html'
    name = _('Authors')
    model = models.Dashboards_appAuthorsPlugin
    form = forms.Dashboards_appAuthorsPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['authors_list'] = instance.get_authors(request)
        context['dashboard_list_url'] = default_reverse(
            '{0}:dashboard-list'.format(instance.app_config.namespace),
            default=None)

        return context


@plugin_pool.register_plugin
class Dashboards_appCategoriesPlugin(Dashboards_appPlugin):
    render_template = 'dashboards_app/plugins/categories.html'
    name = _('Categories')
    model = models.Dashboards_appCategoriesPlugin
    form = forms.Dashboards_appCategoriesPluginForm
    cache = False

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['categories'] = instance.get_categories(request)
        context['dashboard_list_url'] = default_reverse(
            '{0}:dashboard-list'.format(instance.app_config.namespace),
            default=None)
        return context


@plugin_pool.register_plugin
class Dashboards_appFeaturedDashboardsPlugin(Dashboards_appPlugin):
    render_template = 'dashboards_app/plugins/featured_dashboards.html'
    name = _('Featured Dashboards')
    model = models.Dashboards_appFeaturedDashboardsPlugin
    form = forms.Dashboards_appFeaturedDashboardsPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['dashboards_list'] = instance.get_dashboards(request)
        return context


@plugin_pool.register_plugin
class Dashboards_appLatestDashboardsPlugin(AdjustableCacheMixin, Dashboards_appPlugin):
    render_template = 'dashboards_app/plugins/latest_dashboards.html'
    name = _('Latest Dashboards')
    model = models.Dashboards_appLatestDashboardsPlugin
    form = forms.Dashboards_appLatestDashboardsPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['dashboard_list'] = instance.get_dashboards(request)
        return context


@plugin_pool.register_plugin
class Dashboards_appRelatedPlugin(AdjustableCacheMixin, Dashboards_appPlugin):
    render_template = 'dashboards_app/plugins/related_dashboards.html'
    name = _('Related Dashboards')
    model = models.Dashboards_appRelatedPlugin
    form = forms.Dashboards_appRelatedPluginForm

    def get_dashboard(self, request):
        if request and request.resolver_match:
            view_name = request.resolver_match.view_name
            namespace = request.resolver_match.namespace
            if view_name == '{0}:dashboard-detail'.format(namespace):
                dashboard = models.Dashboard.objects.active_translations(
                    slug=request.resolver_match.kwargs['slug'])
                if dashboard.count() == 1:
                    return dashboard[0]
        return None

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        dashboard = self.get_dashboard(request)
        if dashboard:
            context['dashboard'] = dashboard
            context['dashboard_list'] = instance.get_dashboards(dashboard, request)
        return context


# @plugin_pool.register_plugin
# class Dashboards_appTagsPlugin(Dashboards_appPlugin):
#     render_template = 'dashboards_app/plugins/tags.html'
#     name = _('Tags')
#     model = models.Dashboards_appTagsPlugin
#     form = forms.Dashboards_appTagsPluginForm
#
#     def render(self, context, instance, placeholder):
#         request = context.get('request')
#         context['instance'] = instance
#         context['tags'] = instance.get_tags(request)
#         context['dashboard_list_url'] = default_reverse(
#             '{0}:dashboard-list'.format(instance.app_config.namespace),
#             default=None)
#         return context
