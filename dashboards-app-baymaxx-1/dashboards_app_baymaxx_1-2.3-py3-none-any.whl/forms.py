# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms

from . import models


class AutoAppConfigFormMixin(object):
    """
    If there is only a single AppConfig to choose, automatically select it.
    """
    def __init__(self, *args, **kwargs):
        super(AutoAppConfigFormMixin, self).__init__(*args, **kwargs)
        if 'app_config' in self.fields:
            # if has only one choice, select it by default
            if self.fields['app_config'].queryset.count() == 1:
                self.fields['app_config'].empty_label = None


class Dashboards_appArchivePluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.Dashboards_appArchivePlugin
        fields = ['app_config', 'cache_duration']


class Dashboards_appDashboardSearchPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.Dashboards_appDashboardSearchPlugin
        fields = ['app_config', 'max_dashboards']


class Dashboards_appAuthorsPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.Dashboards_appAuthorsPlugin
        fields = ['app_config']


class Dashboards_appCategoriesPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.Dashboards_appCategoriesPlugin
        fields = ['app_config']


class Dashboards_appFeaturedDashboardsPluginForm(AutoAppConfigFormMixin,
                                         forms.ModelForm):
    class Meta:
        model = models.Dashboards_appFeaturedDashboardsPlugin
        fields = ['app_config', 'dashboard_count']


class Dashboards_appLatestDashboardsPluginForm(AutoAppConfigFormMixin,
                                       forms.ModelForm):
    class Meta:
        model = models.Dashboards_appLatestDashboardsPlugin
        fields = [
            'app_config', 'latest_dashboards', 'exclude_featured',
            'cache_duration'
        ]


# class Dashboards_appTagsPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
#     class Meta:
#         fields = ['app_config']


class Dashboards_appRelatedPluginForm(forms.ModelForm):
    class Meta:
        fields = ['cache_duration']
