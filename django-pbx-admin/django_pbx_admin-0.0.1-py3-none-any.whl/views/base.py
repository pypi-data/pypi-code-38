import csv
import json
import logging
import operator
import re
import urllib

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied, FieldDoesNotExist
from django.core.serializers import serialize
from django.db import IntegrityError
from django.db.models import ProtectedError, QuerySet
from django.db.models.manager import Manager
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, \
    DeleteView, \
    TemplateView
from django.views.generic.edit import FormMixin

from pbx_admin.conf import admin_settings
from pbx_admin.forms import SearchForm
from pbx_admin.utils import get_related_field

log = logging.getLogger(__name__)


class PermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('pbx_admin:login')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class FooterMixin:
    """Changes success_url to object's edit url if
    there is _continue in post request.
    Otherwise redirects to attribute default_success_url
    Also adds cancel_url.
    """
    success_url = None
    cancel_url = None
    no_cancel = False
    admin = None

    def get_success_url(self):
        if self.request.POST.get('_continue'):
            kwargs = self.kwargs.copy()
            if self.admin.url_kwarg not in kwargs:
                obj = self.object or self.get_object()
                if self.admin.pk_url_kwarg is not None:
                    kwargs[self.admin.url_kwarg] = obj.pk
                if self.admin.slug_field is not None:
                    kwargs[self.admin.url_kwarg] = \
                        getattr(obj, self.admin.slug_field)
            return self.admin.edit_url(**kwargs)
        admin_url = self.admin.get_success_url(self)
        if admin_url:
            return admin_url
        if self.success_url:
            return self.success_url
        return self.get_default_url()

    def get_cancel_url(self):
        admin_url = self.admin.get_cancel_url(self)
        if admin_url:
            return admin_url
        if self.cancel_url:
            return self.cancel_url
        return self.get_default_url()

    def get_default_url(self):
        kwargs = self.kwargs.copy()
        kwargs.pop(self.admin.pk_url_kwarg, '')
        kwargs.pop(self.admin.slug_url_kwarg, '')
        return self.admin.list_url(**kwargs)


class MessagesMixin:
    """
    Handle messages from django messages framework. Divide messages into
    two groups: to be display as bar or as modal.
    """

    def _update_messages(self, context):
        messages_storage = messages.get_messages(self.request)
        context['bar_messages'] = []
        context['modal_messages'] = []
        for msg in messages_storage:
            msg.tags_set = set(msg.tags.split())
            if {'bar', 'success'} & msg.tags_set:
                context['bar_messages'].append(msg)
            else:
                context['modal_messages'].append(msg)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self._update_messages(context)


class PbAdminViewMixin(PermissionMixin, MessagesMixin):
    admin = None

    success_message_template = '%s'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['admin'] = self.admin
        context['model'] = self.admin.model
        context['opts'] = self.admin.opts

        perms = self.admin.get_model_perms(self.request)
        context['model_perms'] = perms
        context['can_add'] = \
            perms['add'] and bool(self.admin.add_view_class)
        context['can_change'] = \
            perms['change'] and bool(self.admin.edit_view_class)
        context['can_delete'] = \
            perms['delete'] and bool(self.admin.delete_view_class)
        context['can_duplicate'] = \
            perms['duplicate'] and bool(self.admin.duplicate_view_class)

        context.update(self.admin.get_context_data(self.request,
                                                   **self.kwargs))

        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            self.admin.dispatch(self)
        except PermissionDenied:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        obj_name = self.admin.opts.verbose_name.capitalize()
        if 'name' in cleaned_data:
            obj_name += ' "{}" '.format(cleaned_data['name'])
        return self.success_message_template % obj_name


class PbAdminListView(PbAdminViewMixin, FormMixin, FooterMixin, ListView):
    template_name = None
    allow_empty = True

    form_class = SearchForm
    list_display = ('id',)

    def get_paginate_by(self, queryset):
        return admin_settings.ITEMS_PER_PAGE

    def get_form_class(self):
        return self.admin.search_form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.GET:
            kwargs['data'] = self.request.GET
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = self.admin.get_search_form(self, form)
        return form

    def get_template_names(self):
        return ['pbx_admin/{}_list.html'.format(self.model._meta.model_name),
                self.template_name]

    def get_queryset(self, **kwargs):
        queryset = self.admin.get_queryset(self.request, **self.kwargs)

        form = self.get_form()
        if form and form.is_valid():
            queryset = queryset.filter(**form.get_filters())

        ordering = tuple()
        for field_name in self.get_ordering():
            try:
                get_related_field(self.model, field_name.lstrip('-'))
            except FieldDoesNotExist:
                if field_name.lstrip('-') in queryset.query.annotations:
                    ordering += (field_name,)
            else:
                ordering += (field_name,)
        return queryset.order_by(*ordering)

    def get_ordering(self):
        ordering = self.request.GET.get('o') or self.ordering
        if isinstance(ordering, str):
            ordering = (ordering,)

        # add default ordering if not in query params
        for field in self.ordering:
            if field.lstrip('-') not in ordering:
                ordering += (field,)

        return ordering

    def get_context_data(self, **kwargs):
        handler = admin_settings.DUPLICATE_MESSAGES_HANDLER
        if handler and self.model:
            handler(self.request, self.model)

        context = super().get_context_data(**kwargs)

        if self.admin.parent:
            context['menu_items'] = \
                self.admin.parent.get_menu_items(self.request, **self.kwargs)
        if self.form_class:
            context['form'] = self.get_form()

        context['add_form'] = self.admin.get_add_modal_form(self)
        context['duplicate_form'] = self.admin.get_duplicate_modal_form(self)

        context['breadcrumbs'] = self.admin.get_breadcrumbs(self.request,
                                                            **self.kwargs)
        context['total'] = context['paginator'].count
        context['params_for_page'] = self._get_context_params_for_page()
        context['header'] = self._get_context_header()

        # Pagination
        if context['is_paginated']:
            paginator = context['paginator']
            page = context['page_obj'].number
            # fixme: wtf
            context['pages_nums'] = [
                num for num in paginator.page_range
                if num < 3 or (page - 4 < num < page + 4) or
                num > paginator.num_pages - 2]
            context['pages_gaps'] = [
                i for idx, i in enumerate(context['pages_nums'][:-1])
                if context['pages_nums'][idx + 1] - i > 1]

        return context

    def _get_context_params_for_page(self, with_sorting=True):
        params = self.request.GET.copy()
        params.pop('page', None)
        if not with_sorting:
            params.pop('o', None)
        if params:
            return '{}&page='.format(params.urlencode())
        else:
            return 'page='

    def _get_context_header(self):
        header = []
        form = self.get_form()

        for field in self.admin.list_display:
            admin_field = getattr(self.admin, field, None)
            try:
                model_field = self.model._meta.get_field(field)
            except FieldDoesNotExist:
                model_field = None
            form_field = form.fields.get(field) if form else None

            if admin_field and hasattr(admin_field, 'label'):
                label = getattr(admin_field, 'label')
            elif model_field:
                label = model_field.verbose_name
            elif form_field:
                label = form_field.label
            else:
                label = field

            if admin_field and hasattr(admin_field, 'order_field'):
                order_field = getattr(admin_field, 'order_field')
            elif model_field:
                order_field = model_field.name
            else:
                order_field = ''

            order_param = self.request.GET.get('o', '')
            header.append({
                'name': field,
                'label': label,
                'is_ordered': order_param.lstrip('-') == order_field,
                'order_field': order_field,
                'order_desc': order_param == '-' + order_field,
            })

        return header


class FormsetsMixin:
    def get_formset_kwargs(self):
        kwargs = {}
        if hasattr(self, 'object'):
            kwargs['instance'] = self.object
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_formsets(self):
        formsets = self.admin.get_formsets(getattr(self, 'object', None))
        return [formset(prefix=prefix, **self.get_formset_kwargs())
                for prefix, formset in formsets.items()]

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except AttributeError:
            pass

        form = self.get_form()
        formsets = self.get_formsets()

        if form.is_valid() and all(formset.is_valid() for formset in formsets):
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

    def form_valid(self, form, formsets=None):
        handler = super().form_valid(form)

        if formsets:
            for formset in formsets:
                if hasattr(self, 'object'):
                    formset.instance = self.object
                formset.save()

        return handler

    def form_invalid(self, form, formsets=None):
        context = self.get_context_data(form=form, formsets=formsets)
        return self.render_to_response(context)


class PbAdminSingleObjectView(PbAdminViewMixin, FormsetsMixin,
                              SuccessMessageMixin, FooterMixin):
    template_name = 'pbx_admin/edit.html'

    def get_initial(self):
        initial = self.initial.copy()
        initial.update(self.admin.get_initial(self.request, **self.kwargs))
        return initial

    def get_form_class(self):
        return self.admin.get_form_class(self)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.admin.get_form_kwargs(self))
        return kwargs

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs.update(self.admin.get_formset_kwargs(self))
        return kwargs

    def get_fieldsets(self, form=None, formsets=None):
        if form is None:
            form = self.get_form()
        if formsets is None:
            formsets = self.get_formsets()

        formsets = {formset.prefix: formset for formset in formsets}
        fieldsets = []

        for title, fieldset in self.admin.get_fieldsets(form):
            fieldset = fieldset.copy()

            if 'formset' in fieldset and fieldset['prefix'] in formsets:
                fieldset['formset'] = formsets[fieldset['prefix']]

            elif 'fields' in fieldset:
                fieldset['form'] = form
                if isinstance(fieldset['fields'], str) and \
                        fieldset['fields'] == '__all__':
                    fieldset['fields'] = form.fields

            fieldsets.append((title, fieldset))
        return fieldsets

    def get_context_data(self, **kwargs):
        form = kwargs.pop('form', self.get_form())
        formsets = kwargs.pop('formsets', self.get_formsets())

        context = super().get_context_data(**kwargs)

        fieldsets = self.get_fieldsets(form, formsets)
        context['fieldsets'] = fieldsets
        context['menu_items'] = self.admin.get_menu_items(self.request,
                                                          **self.kwargs)

        # set extra parent field in context if not defined in any fieldset
        p_field = self.admin.parent_field
        if p_field and p_field.name in form.fields and \
                not any(p_field.name in fs['fields'] for name, fs in fieldsets
                        if 'fields' in fs):
            context['parent_field'] = form[p_field.name]

        # TODO: ustawiać enctype=multipart/form-data na podstawie poniższego
        # aktualnie sprawdzane jest jedynie form.is_multipart()
        # formularze overridują metodę is_multipart() jeśli jakiś formset
        # jest multipart
        # context['is_multipart'] = \
        #     form.is_multipart() or any(f.is_multipart() for f in formsets)

        return context


class PbAdminCreateView(PbAdminSingleObjectView, CreateView):
    success_message_template = _('%s was created successfully.')
    object = None

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        # TODO: get rid of get_initial_object, use initial data
        kwargs['instance'] = self.admin.get_initial_object(self.request,
                                                           **self.kwargs)
        return kwargs

    def form_valid(self, form, formsets=None):
        handler = super().form_valid(form, formsets)
        log.info("Created %s %s", self.model.__name__, self.object.id,
                 extra={'request': self.request, 'object': self.object})
        return handler

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.admin.get_initial_object(self.request, **self.kwargs)
        context['breadcrumbs'] = \
            self.admin.get_breadcrumbs(self.request, obj, **self.kwargs)
        return context

    def test_func(self):
        if not self.admin.has_add_permission(self.request):
            return False
        return super().test_func()


class PbAdminUpdateView(PbAdminSingleObjectView, UpdateView):
    success_message_template = _('%s was saved successfully.')
    formsets = {}

    def form_valid(self, form, formsets=None):
        old_object = json.loads(serialize('json', [self.get_object()]))[0]
        handler = super().form_valid(form, formsets)
        log.info("Updated %s %s", self.model.__name__, self.object.id,
                 extra={'request': self.request, 'object': self.object,
                        'old_object_fields': json.dumps(old_object['fields'])})
        return handler

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.admin.get_breadcrumbs(
            self.request, self.object, **self.kwargs)
        return context

    def test_func(self):
        if not self.admin.has_change_permission(self.request):
            return False
        return super().test_func()

    def handle_no_permission(self):
        if self.admin.has_show_permission(self.request):
            return redirect(self.admin.show_url(**self.kwargs))
        return super().handle_no_permission()


class PbAdminDeleteView(PbAdminViewMixin, SuccessMessageMixin,
                        FooterMixin, DeleteView):
    success_message_template = _('%s was deleted successfully.')
    query_pk_and_slug = True

    def test_func(self):
        if not self.admin.has_delete_permission(self.request):
            return False
        return super().test_func()

    def get_queryset(self):
        return self.admin.get_queryset(self.request, **self.kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        # After delete obj does not have the id
        obj_id = obj.id
        serialized_object = serialize('json', [obj])

        try:
            self.admin.delete(obj)

        except ProtectedError as e:
            handler = admin_settings.PROTECTED_ERROR_HANDLER
            level, message = handler(e, obj)

        except IntegrityError as e:
            level = messages.ERROR
            message = str(e)

        else:
            log.info("Deleted %s %s", self.model.__name__, obj_id,
                     extra={'request': self.request,
                            'serialized_object': serialized_object})
            level = messages.SUCCESS
            message = self.success_message % {'name': obj}

        messages.add_message(request, level, message)
        return HttpResponseRedirect(self.get_success_url())


class PbAdminShowView(PbAdminUpdateView):
    http_method_names = ['get', 'head', 'trace']
    read_only = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        for field in form.fields.values():
            field.disabled = True
        return form

    def get_formsets(self):
        formsets = super().get_formsets()
        for formset in formsets:
            for form in formset.forms:
                for field in form.fields.values():
                    field.disabled = True
        return formsets

    def test_func(self):
        if self.admin.has_show_permission(self.request):
            return True


class ListSelectionMixin:
    def get_filtered_queryset(self, request):
        ids = request.POST.get('ids', '')
        queryset = self.admin.get_queryset(self.request, **self.kwargs)

        if ids == 'all':
            params = request.POST.get('search_params', '')
            form_class = self.admin.search_form_class
            form = form_class(data={
                k: v[0] for k, v in
                urllib.parse.parse_qs(params[1:]).items()
            })
            if form.is_valid():
                return queryset.filter(**form.get_filters())
        elif ids:
            return queryset.filter(pk__in=ids.split(','))

        return queryset.none()


class PbAdminDeleteMultipleView(PbAdminViewMixin, SuccessMessageMixin,
                                FooterMixin, ListSelectionMixin, TemplateView):
    success_message_template = _('%s were deleted successfully.')
    model = None

    def test_func(self):
        if not self.admin.has_delete_permission(self.request):
            return False
        return super().test_func()

    def post(self, request, *args, **kwargs):
        queryset = self.get_filtered_queryset(request)
        success = []
        errors = []

        for obj in queryset:
            serialized_object = serialize('json', [obj])
            try:
                self.admin.delete(obj)

            except ProtectedError as e:
                errors.append((
                    obj, f'it is used in {len(e.protected_objects)} '
                         f'other objects'
                ))

            except IntegrityError as e:
                errors.append((obj, str(e)))

            else:
                log.info("Deleted %s %s", self.model.__name__, obj.id,
                         extra={'request': request,
                                'serialized_object': serialized_object})
                success.append(obj)

        message = format_html(
            '<p>{} {} have been deleted.</p>',
            len(success), self.model._meta.verbose_name_plural
        )

        if errors:
            message += format_html(
                '<p>{}</p><ul>{}</ul>',
                format_html('There have been {} deletion problems:',
                            len(errors)),
                format_html_join(
                    '', '<li>{} "{}" could not be deleted because: {}</li>',
                    ((obj._meta.verbose_name, obj, exc) for obj, exc in errors)
                )
            )

        level = messages.ERROR if errors else messages.SUCCESS
        messages.add_message(request, level, message)
        return HttpResponseRedirect(self.get_success_url())


class CSVExportView(PermissionMixin, ListSelectionMixin, View):
    export_fields = None
    model = None
    admin = None

    def post(self, request, *args, **kwargs):
        queryset = self.get_filtered_queryset(request)
        if queryset.exists():
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = \
                'attachment; filename="{}.csv"'.format(
                    self.admin.opts.verbose_name_plural)
            cw = csv.writer(response)

            header = []
            for field in self.export_fields:
                try:
                    model_field = get_related_field(self.model, field)
                    title = model_field.verbose_name
                except FieldDoesNotExist:
                    title = None
                header.append(title or re.sub(r'_+', r' ', str(field)))
            cw.writerow(header)

            for obj in queryset:
                data = []
                for field in self.export_fields:
                    field = field.replace('shinar_', '').replace('__', '.')
                    try:
                        value = operator.attrgetter(field)(obj)
                    except AttributeError:
                        value = None

                    if isinstance(value, Manager):
                        value = value.all()
                    if isinstance(value, QuerySet):
                        value = ', '.join([str(o) for o in value])

                    data.append(value)
                cw.writerow(data)
            return response
        else:
            messages.info(request, _('No objects selected.'))
            return HttpResponseRedirect(self.admin.list_url(**kwargs))
