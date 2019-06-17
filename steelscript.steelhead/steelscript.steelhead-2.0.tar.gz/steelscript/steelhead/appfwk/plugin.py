# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import pkg_resources

from django.apps import AppConfig

from steelscript.appfwk.apps.plugins import Plugin as AppsPlugin


class SteelHeadPlugin(AppsPlugin):
    title = 'SteelHead Datasource Plugin'
    description = 'A Portal datasource plugin with example report'
    version = pkg_resources.get_distribution('steelscript.steelhead').version
    author = 'Riverbed Technology'

    enabled = True
    can_disable = True

    devices = ['devices']
    datasources = ['datasources']
    reports = ['reports']


class SteelScriptAppConfig(AppConfig):
    name = 'steelscript.steelhead.appfwk'
    # label cannot have '.' in it
    label = 'steelscript_steelhead'
    verbose_name = 'SteelScript SteelHead'
