# -*- coding: utf-8 -*-
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from django.utils.translation import ugettext_lazy as _
from congo.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps as django_apps
from collections import OrderedDict

class OrderedIndexDashboard(Dashboard):
    def init_with_context(self, context):

        # append an app list module for "Applications"
        self.children.append(OrderedAppList(
            _(u'Aplikacje'),
            deletable = False,
            exclude = ('django.contrib.*', 'accounts.*', 'maintenance.*'),
        ))

        # append an app list module for "Administration"
        self.children.append(OrderedAppList(
            _(u'Administracja'),
            deletable = False,
            models = ('django.contrib.*', 'accounts.*', 'maintenance.*'),
        ))

        model_name = settings.CONGO_SITE_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Site model, configure settings.CONGO_SITE_MODEL first.")
        model = django_apps.get_model(*model_name.split('.', 1))

        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _(u"Strony"),
            deletable = False,
            children = [[u"Wróć do strony", '/']] + [[site.domain, "http://%s" % site.domain, True] for site in model.objects.all()]
        ))

class OrderedAppIndexDashboard(AppIndexDashboard):
    # we disable title because its redundant with the model list module
    title = ''

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        super(OrderedAppIndexDashboard, self).init_with_context(context)

        # append a model list module and a recent actions module
        self.children += [
            OrderedModelList(self.app_title, self.models),
            modules.RecentActions(
                _(u'Najnowsze Akcje'),
                include_list = self.get_app_content_types(),
                limit = 5
            )
        ]

class OrderedAppList(modules.AppList):
    def init_with_context(self, context):
        if self._initialized:
            return

        items = self._visible_models(context['request'])
        apps = {}

        app_order_dict = OrderedDict(settings.ADMIN_TOOLS_APP_ORDER)
        added_app_list = []
        added_model_list = []

        for model, perms in items:
            app_label = model._meta.app_label
            if app_label not in apps:
                apps[app_label] = {
                    'title': django_apps.get_app_config(app_label).verbose_name,
                    'url': self._get_admin_app_list_url(model, context),
                    'models_dict': {},
                    'models': [],
                }

            model_dict = {}
            model_dict['title'] = model._meta.verbose_name_plural
            if perms['change']:
                model_dict['change_url'] = self._get_admin_change_url(model, context)
            if perms['add']:
                model_dict['add_url'] = self._get_admin_add_url(model, context)
            apps[app_label]['models_dict'][model._meta.object_name] = model_dict

        for app_label in app_order_dict.keys():
            if app_label in apps:
                for model_name in app_order_dict[app_label]:
                    if model_name in apps[app_label]['models_dict']:
                        model_dict = apps[app_label]['models_dict'][model_name]
                        model_path = '%s.%s' % (app_label, model_name)
                        added_model_list.append(model_path)
                        apps[app_label]['models'].append(model_dict)

                for model_name in sorted(apps[app_label]['models_dict'].keys()):
                    model_dict = apps[app_label]['models_dict'][model_name]
                    model_path = '%s.%s' % (app_label, model_name)
                    if not model_path in added_model_list:
                        apps[app_label]['models'].append(model_dict)

                added_app_list.append(app_label)
                self.children.append(apps[app_label])

        for app_label in sorted(apps.keys()):
            if not app_label in added_app_list:
                apps[app_label]['models'] = apps[app_label]['models_dict'].values()
                apps[app_label]['models'].sort(key = lambda x: x['title'])
                self.children.append(apps[app_label])

        self._initialized = True

class OrderedModelList(modules.ModelList):
    def init_with_context(self, context):
        if self._initialized:
            return

        # hack for not working model list
        _app_label = context['app_list'][0]['app_label']

        items = self._visible_models(context['request'])
        if not items:
            return

        apps = {}

        for model, perms in items:
            app_label = model._meta.app_label

            # hack for not working model list
            if app_label != _app_label:
                continue

            if app_label not in apps:
                apps[app_label] = {}

            model_dict = {}
            model_dict['title'] = model._meta.verbose_name_plural
            if perms['change']:
                model_dict['change_url'] = self._get_admin_change_url(model, context)
            if perms['add']:
                model_dict['add_url'] = self._get_admin_add_url(model, context)

            apps[app_label][model._meta.object_name] = model_dict

        app_order_dict = OrderedDict(settings.ADMIN_TOOLS_APP_ORDER)
        added_app_list = []
        added_model_list = []

        for app_label in app_order_dict.keys():
            if app_label in apps:
                for model_name in app_order_dict[app_label]:
                    if model_name in apps[app_label]:
                        model_dict = apps[app_label][model_name]
                        model_path = '%s.%s' % (app_label, model_name)
                        added_model_list.append(model_path)
                        self.children.append(model_dict)

                for model_name in sorted(apps[app_label].keys()):
                    model_dict = apps[app_label][model_name]
                    model_path = '%s.%s' % (app_label, model_name)
                    if not model_path in added_model_list:
                        self.children.append(model_dict)

                added_app_list.append(app_label)

        for app_label in sorted(apps.keys()):
            if not app_label in added_app_list:
                for model_name in sorted(apps[app_label].keys()):
                    model_dict = apps[app_label][model_name]
                    self.children.append(model_dict)

        if self.extra:
            # TODO - permissions support
            for extra_url in self.extra:
                model_dict = {}
                model_dict['title'] = extra_url['title']
                model_dict['change_url'] = extra_url['change_url']
                model_dict['add_url'] = extra_url.get('add_url', None)
                self.children.append(model_dict)

        self._initialized = True
