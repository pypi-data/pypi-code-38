import django.apps
import django.contrib.admin.apps


class AdminSite(django.contrib.admin.AdminSite):
    index_template = 'django_adminstats/admin/index.html'
    app_index_template = 'django_adminstats/admin/app_index.html'


class AdminConfig(django.contrib.admin.apps.AdminConfig):
    default_site = 'django_adminstats.apps.AdminSite'


class Config(django.apps.AppConfig):
    name = 'django_adminstats'
    verbose_name = 'Statistics Charting'
