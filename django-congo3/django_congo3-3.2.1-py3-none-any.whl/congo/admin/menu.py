# -*- coding: utf-8 -*-
from admin_tools.menu import items, Menu
from admin_tools.menu.items import AppList, MenuItem
from collections import OrderedDict
from congo.conf import settings
from django.apps import apps as django_apps
from django.urls import reverse

class OrderedAppList(AppList):
    def init_with_context(self, context):
        """
        Please refer to the :meth:`~admin_tools.menu.items.MenuItem.init_with_context`
        documentation from :class:`~admin_tools.menu.items.MenuItem` class.
        """
        items = self._visible_models(context['request'])
        apps = {}
        for model, perms in items:
            if not perms['change']:
                continue

            app_label = model._meta.app_label
            if app_label not in apps:
                apps[app_label] = {
                    'title': django_apps.get_app_config(app_label).verbose_name,
                    'url': self._get_admin_app_list_url(model, context),
                    'models_dict': {}
                }

            apps[app_label]['models_dict'][model._meta.object_name] = {
                'title': model._meta.verbose_name_plural,
                'url': self._get_admin_change_url(model, context)
            }

        app_order_dict = OrderedDict(settings.ADMIN_TOOLS_APP_ORDER)
        added_app_list = []
        added_model_list = []

        for app_label in list(app_order_dict.keys()):
            if app_label in apps:
                item = MenuItem(title = apps[app_label]['title'], url = apps[app_label]['url'])
                added_app_list.append(app_label)

                for model_name in app_order_dict[app_label]:
                    if model_name in apps[app_label]['models_dict']:
                        model_dict = apps[app_label]['models_dict'][model_name]
                        model_path = '%s.%s' % (app_label, model_name)
                        added_model_list.append(model_path)
                        item.children.append(MenuItem(**model_dict))

                for model_name in sorted(apps[app_label]['models_dict'].keys()):
                    model_dict = apps[app_label]['models_dict'][model_name]
                    model_path = '%s.%s' % (app_label, model_name)
                    if not model_path in added_model_list:
                        item.children.append(MenuItem(**model_dict))

                self.children.append(item)

        for app in sorted(apps.keys()):
            if app not in added_app_list:
                app_dict = apps[app]
                item = MenuItem(title = app_dict['title'], url = app_dict['url'])

                for model_name in sorted(apps[app]['models_dict'].keys()):
                    model_dict = apps[app]['models_dict'][model_name]
                    model_path = '%s.%s' % (app, model_name)
                    if not model_path in added_model_list:
                        item.children.append(MenuItem(**model_dict))

                self.children.append(item)

class OrderedMenu(Menu):
    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        super(OrderedMenu, self).init_with_context(context)

        self.children += [
            items.MenuItem("Panel", reverse('admin:index')),
            OrderedAppList("Aplikacje", exclude = ('django.contrib.*', 'accounts.*', 'maintenance.*')),
            OrderedAppList("Administracja", models = ('django.contrib.*', 'accounts.*', 'maintenance.*')),
        ]

        if context['request'].user.is_superuser:
            self.children += [
                items.MenuItem(
                    "Zaawansowane",
                    children = [
                        items.MenuItem("Wyczyść cache", reverse('congo:clear_cache')),
                        items.MenuItem("Mail testowy", reverse('congo:test_mail')),
                    ]
                ),
            ]

        self.children += [
            items.Bookmarks(),
        ]
