# -*- coding: utf-8 -*-
from congo.admin.actions import make_active, make_inactive
from congo.maintenance import get_admin_model
from congo.maintenance.filters import LogLevelFilter, AuditLevelFilter, SiteLanguage
from congo.templatetags.common import or_blank
from django.contrib import messages
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import truncatechars
from django.utils.safestring import mark_safe

ModelAdmin = get_admin_model()

class SiteAdmin(ModelAdmin):
    list_display = ('domain', 'language', 'is_active')
    list_filter = (SiteLanguage, 'is_active',)
    search_fields = ('domain',)
    actions = (make_active, make_inactive)

class ConfigAdmin(ModelAdmin):
    list_display = ('name', 'value', 'use_cache', 'load_at_startup')
    list_filter = ('use_cache', 'load_at_startup',)
    search_fields = ('name', 'description',)

class LogAdmin(ModelAdmin):
    list_display = ('name', 'colored_level', 'render_message', 'user', 'date')
    list_filter = ('name', LogLevelFilter, 'user',)
    fields = ('name', 'colored_level', 'message', 'user', 'date', 'render_args')
    readonly_fields = fields
    search_fields = ('name', 'message', 'args')
    date_hierarchy = 'date'

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(LogAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if type(db_field) == models.TextField:
            field.widget.attrs['rows'] = 20
        return field

    def colored_level(self, obj):
        return obj.render_level(obj.level)
    colored_level.short_description = _("Poziom")
    colored_level.allow_tags = True
    colored_level.admin_order_field = 'level'

    def render_message(self, obj):
        html = """<span title="%s">%s</span>""" % (obj.message, truncatechars(obj.message, 50))
        return mark_safe(html)
    render_message.short_description = _("Opis")
    render_message.admin_order_field = 'date'

    def render_args(self, obj):
        return or_blank(obj.args)
    render_args.short_description = _("Szczegóły")
    render_args.admin_order_field = 'args'

class AuditAdmin(ModelAdmin):
    list_display = ('render_name', 'level', 'frequency', 'last_run_date', 'result', 'is_active')
    list_filter = (AuditLevelFilter, 'frequency', 'result', 'is_active', 'last_run_date')
    readonly_fields = ('render_description', 'last_run_date', 'result', 'render_details')
    search_fields = ('test', 'details')
    filter_horizontal = ('auditors',)
    actions = (make_active, make_inactive, 'run_test',)

    fieldsets = (
        (None, {
            'fields': ('test', 'render_description', 'level', 'frequency', 'is_active', 'auditors',)
        }),
        (_("Wyniki"), {
            'fields': ('last_run_date', 'result', 'render_details')
        }),
    )

    def render_name(self, obj):
        return or_blank(obj.name)
    render_name.short_description = _("Nazwa")
    render_name.admin_order_field = 'test'

    def render_description(self, obj):
        try:
            test = obj._get_test()
            if test:
                return or_blank(test.description)
        except ImportError:
            pass
        return or_blank(None)
    render_description.short_description = _("Opis")

    def render_details(self, obj):
        return or_blank(obj.details)
    render_details.short_description = _("Szczegóły")
    render_details.admin_order_field = 'details'
    render_details.allow_tags = True

    # actions
    def run_test(self, request, queryset):
        i = j = 0
        for audit in queryset:
            if audit.run_test(request.user):
                i += 1
            j += 1
        message = _("Testy audytów wykonane")
        level = messages.INFO if i == j else messages.ERROR
        self.message_user(request, "%s (%s / %s)" % (message, i, j), level = level)
    run_test.short_description = "Wykonaj testy audytów"

class CronAdmin(ModelAdmin):
    list_display = ('render_name', 'frequency', 'is_active', 'last_run_date', 'position',)
    list_filter = ('frequency', 'is_active', 'last_run_date')
    list_editable = ('position',)
    fields = ('job', 'render_description', 'frequency', 'is_active', 'last_run_date')
    readonly_fields = ('render_description', 'last_run_date')
    search_fields = ('job',)
    actions = (make_active, make_inactive, 'run_job',)

    def render_name(self, obj):
        return obj.name
    render_name.short_description = _("Nazwa")
    render_name.admin_order_field = 'job'

    def render_description(self, obj):
        try:
            job = obj._get_job()
            if job:
                return or_blank(job.description)
        except ImportError:
            pass
        return or_blank(None)
    render_description.short_description = _("Opis")

    # actions
    def run_job(self, request, queryset):
        i = j = 0
        for cron in queryset:
            if cron.run_job(request.user):
                i += 1
            j += 1
        message = _("Zadania CRON wykonane")
        level = messages.INFO if i == j else messages.ERROR
        self.message_user(request, "%s (%s / %s)" % (message, i, j), level = level)
    run_job.short_description = "Wykonaj zadania CRON"

class UrlRedirectAdmin(ModelAdmin):
    list_display = ('old_url', 'redirect_url', 'rewrite_tail', 'is_permanent_redirect')
    list_filter = ('rewrite_tail', 'is_permanent_redirect',)
    search_fields = ('old_url', 'redirect_url',)
