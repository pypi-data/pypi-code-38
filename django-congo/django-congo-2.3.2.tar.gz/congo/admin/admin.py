# -*- coding: utf-8 -*-
from congo.templatetags.admin_utils import admin_change_url
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.contrib.auth import get_permission_codename
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 50

    def get_actions(self, request):
        # moves delete_selected to the end of list
        actions = super(BaseModelAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            delete_selected = actions['delete_selected']
            del actions['delete_selected']
            actions['delete_selected'] = delete_selected
        return actions

    def has_change_permission(self, request, obj = None):
        # http://stackoverflow.com/questions/1336382/how-can-i-modify-django-to-create-view-permission
        codename = get_permission_codename('view', self.opts)
        if not request.POST and request.user.has_perm("%s.%s" % (self.opts.app_label, codename)):
            return True
        return super(BaseModelAdmin, self).has_change_permission(request, obj)

    def change_view(self, request, object_id, form_url = '', extra_context = {}):
        obj = self.get_object(request, unquote(object_id))

        try:
            title = unicode(obj)
        except TypeError:
            title = _(u"(Brak)")

        context = {
            'title': title,
        }
        context.update(extra_context or {})

        codename = get_permission_codename('change', self.opts)
        if request.POST and not request.user.has_perm("%s.%s" % (self.opts.app_label, codename)):
            request.POST._mutable = True
            request.POST.clear()
            request.POST._mutable = False
            messages.error(request, _(u"Nie masz uprawnień do edytowania! Zmiany nie były zastosowane."))
            return HttpResponseRedirect('.')

        return super(BaseModelAdmin, self).change_view(request, object_id, extra_context = context)

    def changelist_view(self, request, extra_context = None):

        context = {
            'title': self.opts.verbose_name_plural,
        }
        context.update(extra_context or {})

        return super(BaseModelAdmin, self).changelist_view(request, context)

    def history_view(self, request, object_id, extra_context = None):
        obj = self.get_object(request, unquote(object_id))

        context = {
            'title': u"%s - %s" % (obj, _(u"Historia")),
        }
        context.update(extra_context or {})

        return super(BaseModelAdmin, self).history_view(request, object_id, context)

    def action_view(self, request, action):
        function_name = "%s_action" % action

        if hasattr(self, function_name):
            getattr(self, function_name)(request)

        return HttpResponseRedirect("..")

    # fields
    def user_anchor(self, obj):
        if obj.user:
            url = admin_change_url(obj.user)
            return """<a href="%s">%s</a>""" % (url, obj.user)
        return None
    user_anchor.short_description = _(u"Użytkownik")
    user_anchor.admin_order_field = 'user__email'
    user_anchor.allow_tags = True

    def user_email_anchor(self, obj):
        if obj.user:
            url = admin_change_url(obj.user)
            return """<a href="%s">%s</a>""" % (url, obj.user.email)
        return None
    user_email_anchor.short_description = _(u"E-mail użytkownika")
    user_email_anchor.admin_order_field = 'user__email'
    user_email_anchor.allow_tags = True

    def render_language(self, obj):
        return '<i class="flag-icon" style="background-image: url(/media/img/flags/%s.svg");"></i> %s' % (obj.language, obj.get_language_display())
    render_language.short_description = _(u"Język")
    render_language.admin_order_field = 'language'
    render_language.allow_tags = True
