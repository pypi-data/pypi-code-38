# -*- coding: utf-8 -*-
from congo.accounts.forms import UserChangeForm, UserCreationForm
from congo.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http.response import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.module_loading import import_string
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

modeladmin_name = settings.CONGO_ADMIN_MODEL
# modeladmin = get_class(modeladmin_name)
modeladmin = import_string(modeladmin_name)

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class GroupAdmin(modeladmin):
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)

    def formfield_for_manytomany(self, db_field, request = None, **kwargs):
        if db_field.name == 'permissions':
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            queryset = kwargs.get('queryset', db_field.rel.to.objects)
            kwargs['queryset'] = queryset.select_related('content_type')
        return super(GroupAdmin, self).formfield_for_manytomany(db_field, request = request, **kwargs)


class UserAdmin(modeladmin):
    list_display = ('get_full_name', 'email', 'is_staff', 'is_active', 'last_login',)
    list_filter = ('is_active', 'is_staff', 'is_superuser',)
    list_display_links = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        (_(u"Dane osobiste"), {'fields': ('first_name', 'last_name', 'mobile_phone')}),
        (_(u"Uprawnienia"), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_(u"Inne informacje"), {'fields': ('date_joined', 'last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name',)
    filter_horizontal = ('groups', 'user_permissions',)

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None

    def get_fieldsets(self, request, obj = None):
        if not obj:
            return self.add_fieldsets
        return super(UserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj = None, **kwargs):
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.utils.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(UserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            url(r'^(.+)/password/$', self.admin_site.admin_view(self.user_change_password), name = 'auth_user_password_change'),
        ] + super(UserAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        if lookup.startswith('password'):
            return False
        return super(modeladmin, self).lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url = '', extra_context = None):
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(UserAdmin, self).add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url = ''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_(u'% (name)s obiekt o kluczu %(key)r nie istnieje.') % {
                'name': force_text(self.model._meta.verbose_name),
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = ugettext(u'Hasło zostało zmienione pomyślnie.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(reverse('%s:%s_%s_change' % (self.admin_site.name, user._meta.app_label, user._meta.model_name), args = (user.pk,)))
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _(u'Zmień hasło :%s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(admin.site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(request, self.change_user_password_template or 'admin/auth/user/change_password.html', context)

# @og nie pamietam po co to bylo, ale na Dj 11 wali bledem, wiec poki co wylaczam
#    def response_add(self, request, obj, post_url_continue = None):
#        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
#            request.POST['_continue'] = 1
#        return super(UserAdmin, self).response_add(request, obj, post_url_continue)


class UserConfigAdmin(modeladmin):
    list_display = ('user', 'name', 'value',)
    list_filter = ('user', 'name',)
    search_fields = ('name',)
