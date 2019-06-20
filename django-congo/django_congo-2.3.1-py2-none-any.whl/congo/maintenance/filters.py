# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps

class SiteLanguage(SimpleListFilter):
    title = _(u"Język")
    parameter_name = 'language'

    def lookups(self, request, model_admin):
        model_name = settings.CONGO_SITE_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Site model, configure settings.CONGO_SITE_MODEL first.")
        model = apps.get_model(*model_name.split('.', 1))

        languages = model.objects.order_by('language').values_list('language', flat = True).distinct()
        languages_dict = dict(settings.LANGUAGES)
        return [(language, languages_dict[language]) for language in languages]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(language__exact = self.value())
        else:
            return queryset

class LogLevelFilter(SimpleListFilter):
    title = _(u"Poziom")
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        model_name = settings.CONGO_LOG_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Log model, configure settings.CONGO_LOG_MODEL first.")
        model = apps.get_model(*model_name.split('.', 1))

#        levels = model.objects.order_by('level').values_list('level', flat = True).distinct()
#        return [(level, model.get_level_name(level)) for level in levels]

        return model.LEVEL_CHOICE

    def queryset(self, request, queryset):
        if self.value():
#            return queryset.filter(level__exact = self.value())
            return queryset.filter(level__gte = self.value())
        else:
            return queryset

class AuditLevelFilter(SimpleListFilter):
    title = _(u"Poziom")
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        model_name = settings.CONGO_AUDIT_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Audit model, configure settings.CONGO_AUDIT_MODEL first.")
        model = apps.get_model(*model_name.split('.', 1))

#        levels = model.objects.order_by('level').values_list('level', flat = True).distinct()
#        return [(level, model.get_level_name(level)) for level in levels]

        return model.LEVEL_CHOICE

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(level__gte = self.value())
        else:
            return queryset
