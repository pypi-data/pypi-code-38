import collections
import copy
import typing
from urllib.parse import urlparse

import django.core.exceptions
import django.http
import django.urls
from django import forms
from django.apps import apps
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse
from django.views.generic.list import BaseListView
from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from . import models, registry, explore


def add_description(text: str):
    def inner(func: typing.Callable) -> typing.Callable:
        func.short_description = text
        return func
    return inner


@add_description(_('Duplicate'))
def copy_chart(_admin, _request, queryset):
    for chart in queryset:
        new = models.Chart.objects.create(
            title=str(_('Copy of {}')).format(chart.title),
            chart_type=chart.chart_type,
            until_type=chart.until_type,
            until_date=chart.until_date,
            period_count=chart.period_count,
            period_step=chart.period_step,
        )
        for criteria in chart.criteria.all():
            models.Criteria.objects.create(
                chart=new,
                stats_key=criteria.stats_key,
                filter_query=criteria.filter_query,
                group_query=criteria.group_query,
                axis_query=criteria.axis_query,
            )


class QueryAutocompleteJsonView(BaseListView):
    """Handle Widget's AJAX requests for data."""
    paginate_by = 20
    stats_key = ''

    def get(self, request, *args, **kwargs):
        """
        Return a JsonResponse with search results of the form:
        {
            results: [{id: "123" text: "foo"}],
        }
        """
        if not self.has_perm(request):
            return django.http.JsonResponse(
                {'error': '403 Forbidden'}, status=403)

        try:
            reg = registry.REGISTRY[self.stats_key]
        except KeyError:
            return django.http.HttpResponseBadRequest("Invalid stats key")
        term = self.request.GET.get('term', '')
        results = []
        for item in self.get_options(reg, term):
            results.append({'id': item, 'text': item})
        return django.http.JsonResponse({'results': results})

    def get_options(self, reg: registry.Registry, term: str) -> list:
        """Return queryset based on ModelAdmin.get_search_results()."""
        return reg.query_options(term)

    def has_perm(self, request, obj=None):
        """Check if user has permission to access the related model."""
        return request.user.has_perm('django_adminstats.view_chart')


class FilterAutocompleteJsonView(QueryAutocompleteJsonView):
    def get_options(self, reg: registry.Registry, term: str) -> list:
        return reg.query_options(term, is_filter=True)


class QueryAutocomplete(AutocompleteSelect):

    allow_multiple_selected = True
    is_required = False

    def __init__(self):
        super().__init__(None, None)
        self.choices = ()

    def get_url(self):
        return django.urls.reverse(
            'admin:django_adminstats_query_autocomplete', args=[''])

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        subgroup = []
        # just show the existing selected options, everything they can get
        # from select2
        for part in value:
            subgroup.append(self.create_option(
                name, part, part, True, 0,
                subindex=None, attrs=attrs,
            ))
        return [(None, subgroup, 0)]

    def value_omitted_from_data(self, data, files, name):
        # this is required otherwise django won't save blank values
        return False

    def format_value(self, value):
        """Return selected values as a list."""
        if value is None:
            return []
        return [s for s in value.split('&') if s != '']

    def value_from_datadict(self, data, _files, name):
        return '&'.join(data.getlist(name))

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-token-separator'] = '&'
        attrs['data-select-on-close'] = 'true'
        attrs['data-ajax--delay'] = '250'
        attrs['class'] = 'adminstats-autocomplete'
        return attrs


class FilterAutocomplete(QueryAutocomplete):

    def get_url(self):
        return django.urls.reverse(
            'admin:django_adminstats_filter_autocomplete', args=[''])


class CriteriaForm(forms.ModelForm):
    stats_key = forms.ChoiceField(choices=registry.REGISTRY.choices())

    class Meta:
        model = models.Criteria
        fields = ['stats_key', 'filter_query', 'group_query', 'axis_query']
        widgets = {
            'filter_query': FilterAutocomplete,
            'group_query': QueryAutocomplete,
            'axis_query': QueryAutocomplete,
        }


class CriteriaInline(admin.TabularInline):
    form = CriteriaForm
    model = models.Criteria
    min_num = 1
    extra = 0


@admin.register(models.Chart)
class ChartAdmin(admin.ModelAdmin):
    change_form_template = 'django_adminstats/chart/change_form.html'
    inlines = [CriteriaInline]
    list_display = ('title', 'chart_type', 'show_action_links')
    list_filter = ('chart_type',)
    chart_template = 'django_adminstats/chart/chart.html'
    explore_template = 'django_adminstats/chart/explore.html'
    actions = [copy_chart]

    class Media:
        js = ('django_adminstats/chart_form.js',)
        css = {'all': ('django_adminstats/chart_form.css',)}

    def get_urls(self):
        return [
            url(
                r'^explore/(?P<app>\w+)/(?P<model>\w+)$',
                # self.admin_site.admin_view(self.explore),
                self.explore,
                name='django_adminstats_explore'),
            url(
                r'^(?P<chart_id>\w+)/chart$',
                self.admin_site.admin_view(self.view_chart),
                name='django_adminstats_chart'),
            url(
               r'^filter_autocomplete/(?P<stats_key>.*)$',
               self.filter_autocomplete_view,
               name='django_adminstats_filter_autocomplete'),
            url(
               r'^query_autocomplete/(?P<stats_key>.*)$',
               self.query_autocomplete_view,
               name='django_adminstats_query_autocomplete'),
            ] + super().get_urls()

    @add_description(_('Actions'))
    def show_action_links(self, obj):
        return format_html(
            '<a href="{url}">{text}</a>',
            text=_('Show Chart'), url='{}/chart'.format(obj.pk))

    @staticmethod
    def query_autocomplete_view(request, stats_key):
        return QueryAutocompleteJsonView.as_view(stats_key=stats_key)(request)

    @staticmethod
    def filter_autocomplete_view(request, stats_key):
        return FilterAutocompleteJsonView.as_view(stats_key=stats_key)(request)

    def explore(self, request, app, model):
        # first, we want to find the admin thingy
        if request.method != 'GET':
            return django.http.HttpResponseNotAllowed(('GET',))
        try:
            app_config = apps.get_app_config(app)
        except LookupError:
            return django.http.HttpResponseNotFound()
        try:
            model_cls = app_config.get_model(model)
        except LookupError:
            return django.http.HttpResponseNotFound()
        model_admin = self.admin_site._registry.get(model_cls, None)
        if model_admin is None:
            return django.http.HttpResponseNotFound()
        if not model_admin.has_view_permission(request):
            path = request.build_absolute_uri()
            resolved_login_url = reverse('admin:login')
            current_scheme, current_netloc = urlparse(path)[:2]
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            return redirect_to_login(path, resolved_login_url)

        un_grouped_query_dict = copy.copy(request.GET)
        group_filters = un_grouped_query_dict.pop('_group', [])
        x_field = un_grouped_query_dict.get('_x', None)
        entry_query_dict = copy.copy(un_grouped_query_dict)
        entry_query_dict.pop('_x', None)
        mock_request = explore.mock_request(
            request, ('_group', '_x'))
        changelist = model_admin.get_changelist_instance(mock_request)

        # set up groups, filters, & axes
        filters = [explore.Filter(
            spec, changelist, un_grouped_query_dict, group_filters, x_field)
            for spec in changelist.filter_specs if spec.has_output()]
        filters = collections.OrderedDict(((f.id, f) for f in filters))

        # generate data
        qs = explore.get_queryset(changelist, mock_request)

        group_annotations, columns = explore.get_group_annotations(
            group_filters, filters, model_admin, qs)

        xqd = explore.get_x_annotations(x_field, filters, request.GET, qs)

        if group_annotations:
            qs = qs.annotate(**group_annotations).values(*columns.keys())
            qs = qs.annotate(**xqd.annotations)
        else:
            qs = [qs.aggregate(**xqd.annotations)]

        chart_table = explore.build_table(
            qs, columns, xqd, un_grouped_query_dict, request.GET)

        entry_url = reverse('admin:{}_{}_changelist'.format(app, model))
        entry_url = '{}?{}'.format(entry_url, entry_query_dict.urlencode())

        context = {
            'title': _('Explore: %s') % model_cls._meta.verbose_name_plural,
            'media': self.media,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': getattr(model_cls, '_meta'),
            'groupings': [f for f in filters.values() if not f.is_filtered],
            'filters': [f for f in filters.values() if f.is_filtered],
            'axes': [f for f in filters.values() if f.is_scalar],
            'table': chart_table,
            'entry_url': entry_url,
            'save_as': False,
            'show_save': True,
        }
        context.update(self.admin_site.each_context(mock_request))
        request.current_app = self.admin_site.name
        return TemplateResponse(request, self.explore_template, context)

    def view_chart(self, request, chart_id):
        if not self.has_view_permission(request):
            return django.http.HttpResponseForbidden()
        chart = self.get_object(request, chart_id)  # type: models.Chart
        if chart is None:
            return django.http.HttpResponseNotFound()
        if request.method != 'GET':
            return django.http.HttpResponseNotAllowed(('GET',))

        exceptions = []
        chart_header = list(chart.dates())
        chart_rows = collections.OrderedDict()
        for criteria in chart.criteria.all():
            try:
                group_data = registry.REGISTRY.query(criteria)
            except (ValueError, django.core.exceptions.FieldError) as ex:
                exceptions.append(ex)
            else:
                for group, data in group_data.items():
                    row = [0] * len(chart_header)
                    for date, value in data.items():
                        try:
                            date_idx = chart_header.index(date)
                            row[date_idx] = value
                        except ValueError:
                            pass
                    label = registry.REGISTRY[criteria.stats_key].label
                    if group:
                        label = '{}—{}'.format(label, group)
                    idx = 1
                    if criteria.filter_query:
                        label = '{} ({})'.format(label, criteria.filter_query)
                    while idx < 10 and label in chart_rows:
                        if criteria.filter_query:
                            label = '{} ({}, {})'.format(
                                label, criteria.filter_query, idx)
                        else:
                            label = '{} ({})'.format(label, idx)
                    chart_rows[label] = row

        context = {
            'title': _('View Chart: %s') % chart.title,
            'media': self.media,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': getattr(self.model, '_meta'),
            'chart': chart,
            'header': chart_header,
            'rows': chart_rows,
            'exceptions': exceptions,
            'save_as': False,
            'show_save': True,
        }
        context.update(self.admin_site.each_context(request))
        request.current_app = self.admin_site.name
        return TemplateResponse(request, self.chart_template, context)
