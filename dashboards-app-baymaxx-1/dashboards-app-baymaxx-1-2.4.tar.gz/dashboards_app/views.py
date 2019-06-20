# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.http import (
    Http404,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    JsonResponse,

)
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin, ViewUrlMixin
from taggit.models import Tag

from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_categories.models import Category
from aldryn_people.models import Person

from dashboards_app.utils.utilities import get_valid_languages_from_request


from .models import Dashboard

from .utils import add_prefix_to_path

from dashboards_app.dash_docs_app.lib.DocsConstruction import BuildDoc
from .blero_utils.utils import set_up_dashboard_tree




import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)


class TemplatePrefixMixin(object):

    def prefix_template_names(self, template_names):
        if (hasattr(self.config, 'template_prefix') and
                self.config.template_prefix):
            prefix = self.config.template_prefix
            return [
                add_prefix_to_path(template, prefix)
                for template in template_names]
        return template_names

    def get_template_names(self):
        template_names = super(TemplatePrefixMixin, self).get_template_names()
        return self.prefix_template_names(template_names)


class EditModeMixin(object):
    """
    A mixin which sets the property 'edit_mode' with the truth value for
    whether a user is logged-into the CMS and is in edit-mode.
    """
    edit_mode = False

    def dispatch(self, request, *args, **kwargs):
        self.edit_mode = (
            self.request.toolbar and self.request.toolbar.edit_mode)
        return super(EditModeMixin, self).dispatch(request, *args, **kwargs)


class PreviewModeMixin(EditModeMixin):
    """
    If content editor is logged-in, show all dashboards. Otherwise, only the
    published dashboards should be returned.
    """
    def get_queryset(self):
        qs = super(PreviewModeMixin, self).get_queryset()
        # check if user can see unpublished items. this will allow to switch
        # to edit mode instead of 404 on dashboard detail page. CMS handles the
        # permissions.
        user = self.request.user
        user_can_edit = user.is_staff or user.is_superuser
        if not (self.edit_mode or user_can_edit):
            qs = qs.published()
        language = translation.get_language()
        qs = qs.active_translations(language).namespace(self.namespace)
        return qs


class AppHookCheckMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.valid_languages = get_valid_languages_from_request(
            self.namespace, request)
        return super(AppHookCheckMixin, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        # filter available objects to contain only resolvable for current
        # language. IMPORTANT: after .translated - we cannot use .filter
        # on translated fields (parler/django limitation).
        # if your mixin contains filtering after super call - please place it
        # after this mixin.
        qs = super(AppHookCheckMixin, self).get_queryset()
        return qs.translated(*self.valid_languages)


class DashboardDetail(AppConfigMixin, AppHookCheckMixin, PreviewModeMixin,
                    TranslatableSlugMixin, TemplatePrefixMixin, DetailView):
    model = Dashboard
    slug_field = 'slug'
    year_url_kwarg = 'year'
    month_url_kwarg = 'month'
    day_url_kwarg = 'day'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'






    def get(self, request, *args, **kwargs):
        """
        This handles non-permalinked URLs according to preferences as set in
        Dashboards_appConfig.
        """
        #TODO Review this code as there is an error while creating the log file
        # Creates a log file for each Dashboard ####
        active_dashboard = self.get_object()

        set_up_dashboard_tree(active_dashboard)

        # Build Documentation
        try:
            [one, two] = BuildDoc(self)
        except Exception as e:
            logger.exception("Doc not created")


        ###################################################

        if not hasattr(self, 'object'):
            self.object = self.get_object()
        set_language_changer(request, self.object.get_absolute_url)
        url = self.object.get_absolute_url()
        if (self.config.non_permalink_handling == 200 or request.path == url):
            # Continue as normal
            return super(DashboardDetail, self).get(request, *args, **kwargs)

        # Check to see if the URL path matches the correct absolute_url of
        # the found object
        if self.config.non_permalink_handling == 302:
            return HttpResponseRedirect(url)
        elif self.config.non_permalink_handling == 301:
            return HttpResponsePermanentRedirect(url)
        else:
            raise Http404('This is not the canonical uri of this object.')

    def get_object(self, queryset=None):
        """
        Supports ALL of the types of permalinks that we've defined in urls.py.
        However, it does require that either the id and the slug is available
        and unique.
        """

        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg, None)
        pk = self.kwargs.get(self.pk_url_kwarg, None)


        if pk is not None:
            # Let the DetailView itself handle this one
            return DetailView.get_object(self, queryset=queryset)
        elif slug is not None:
            # Let the TranslatedSlugMixin take over
            return super(DashboardDetail, self).get_object(queryset=queryset)

        raise AttributeError('DashboardDetail view must be called with either '
                             'an object pk or a slug')

    def get_context_data(self, **kwargs):




        context = super(DashboardDetail, self).get_context_data(**kwargs)



        context['prev_dashboard'] = self.get_prev_object(
            self.queryset, self.object)
        context['next_dashboard'] = self.get_next_object(
            self.queryset, self.object)
        return context

    def get_prev_object(self, queryset=None, object=None):
        if queryset is None:
            queryset = self.get_queryset()
        if object is None:
            object = self.get_object(self)
        prev_objs = queryset.filter(
            publishing_date__lt=object.publishing_date
        ).order_by(
            '-publishing_date'
        )[:1]
        if prev_objs:
            return prev_objs[0]
        else:
            return None

    def get_next_object(self, queryset=None, object=None):
        if queryset is None:
            queryset = self.get_queryset()
        if object is None:
            object = self.get_object(self)
        next_objs = queryset.filter(
            publishing_date__gt=object.publishing_date
        ).order_by(
            'publishing_date'
        )[:1]
        if next_objs:
            return next_objs[0]
        else:
            return None


class DashboardListBase(AppConfigMixin, AppHookCheckMixin, TemplatePrefixMixin,
                      PreviewModeMixin, ViewUrlMixin, ListView):
    model = Dashboard
    show_header = False

    def get_paginate_by(self, queryset):
        if self.paginate_by is not None:
            return self.paginate_by
        else:
            try:
                return self.config.paginate_by
            except AttributeError:
                return 10  # sensible failsafe

    def get_pagination_options(self):
        # Django does not handle negative numbers well
        # when using variables.
        # So we perform the conversion here.
        if self.config:
            options = {
                'pages_start': self.config.pagination_pages_start,
                'pages_visible': self.config.pagination_pages_visible,
            }
        else:
            options = {
                'pages_start': 10,
                'pages_visible': 4,
            }

        pages_visible_negative = -options['pages_visible']
        options['pages_visible_negative'] = pages_visible_negative
        options['pages_visible_total'] = options['pages_visible'] + 1
        options['pages_visible_total_negative'] = pages_visible_negative - 1
        return options

    def get_context_data(self, **kwargs):
        context = super(DashboardListBase, self).get_context_data(**kwargs)
        context['pagination'] = self.get_pagination_options()
        return context


class DashboardList(DashboardListBase):
    """A complete list of dashboards."""
    show_header = True



    def get_queryset(self):
        qs = super(DashboardList, self).get_queryset()
        # exclude featured dashboards from queryset, to allow featured dashboard
        # plugin on the list view page without duplicate entries in page qs.
        # exclude_count = self.config.exclude_featured
        # if exclude_count:
        #     featured_qs = Dashboard.objects.all().filter(is_featured=True)
        #     if not self.edit_mode:
        #         featured_qs = featured_qs.published()
        #     exclude_featured = featured_qs[:exclude_count].values_list('pk')
        #     qs = qs.exclude(pk__in=exclude_featured)
        return qs


class DashboardSearchResultsList(DashboardListBase):
    model = Dashboard
    http_method_names = ['get', 'post', ]
    partial_name = 'dashboards_app/includes/search_results.html'
    template_name = 'dashboards_app/dashboard_list.html'

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get('q')
        self.max_dashboards = request.GET.get('max_dashboards', 0)
        self.edit_mode = (request.toolbar and request.toolbar.edit_mode)
        return super(DashboardSearchResultsList, self).get(request)

    def get_paginate_by(self, queryset):
        """
        If a max_dashboards was set (by a plugin), use that figure, else,
        paginate by the app_config's settings.
        """
        return self.max_dashboards or super(
            DashboardSearchResultsList, self).get_paginate_by(self.get_queryset())

    def get_queryset(self):
        qs = super(DashboardSearchResultsList, self).get_queryset()
        if not self.edit_mode:
            qs = qs.published()
        if self.query:
            return qs.filter(
                Q(translations__title__icontains=self.query) |
                Q(translations__lead_in__icontains=self.query) |
                Q(translations__search_data__icontains=self.query)
            ).distinct()
        else:
            return qs.none()

    def get_context_data(self, **kwargs):
        cxt = super(DashboardSearchResultsList, self).get_context_data(**kwargs)
        cxt['query'] = self.query
        return cxt

    def get_template_names(self):
        if self.request.is_ajax:
            template_names = [self.partial_name]
        else:
            template_names = [self.template_name]
        return self.prefix_template_names(template_names)


class AuthorDashboardList(DashboardListBase):
    """A list of dashboards written by a specific author."""
    def get_queryset(self):
        # Note: each Dashboard.author is Person instance with guaranteed
        # presence of unique slug field, which allows to use it in URLs
        return super(AuthorDashboardList, self).get_queryset().filter(
            author=self.author
        )

    def get(self, request, author):
        language = translation.get_language_from_request(
            request, check_path=True)
        self.author = Person.objects.language(language).active_translations(
            language, slug=author).first()
        if not self.author:
            raise Http404('Author not found')
        return super(AuthorDashboardList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['dashboards_app_author'] = self.author
        return super(AuthorDashboardList, self).get_context_data(**kwargs)


class CategoryDashboardList(DashboardListBase):
    """A list of dashboards filtered by categories."""
    def get_queryset(self):
        return super(CategoryDashboardList, self).get_queryset().filter(
            categories=self.category
        )

    def get(self, request, category):
        self.category = get_object_or_404(
            Category, translations__slug=category)
        return super(CategoryDashboardList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['dashboards_app_category'] = self.category
        ctx = super(CategoryDashboardList, self).get_context_data(**kwargs)
        ctx['dashboards_app_category'] = self.category
        return ctx


class TagDashboardList(DashboardListBase):
    """A list of dashboards filtered by tags."""
    def get_queryset(self):
        return super(TagDashboardList, self).get_queryset().filter(
            tags=self.tag
        )

    def get(self, request, tag):
        self.tag = get_object_or_404(Tag, slug=tag)
        return super(TagDashboardList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['dashboards_app_tag'] = self.tag
        return super(TagDashboardList, self).get_context_data(**kwargs)


class DateRangeDashboardList(DashboardListBase):
    """A list of dashboards for a specific date range"""
    def get_queryset(self):
        return super(DateRangeDashboardList, self).get_queryset().filter(
            publishing_date__gte=self.date_from,
            publishing_date__lt=self.date_to
        )

    def _daterange_from_kwargs(self, kwargs):
        raise NotImplemented('Subclasses of DateRangeDashboardList need to'
                             'implement `_daterange_from_kwargs`.')

    def get(self, request, **kwargs):
        self.date_from, self.date_to = self._daterange_from_kwargs(kwargs)
        return super(DateRangeDashboardList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['dashboards_app_day'] = (
            int(self.kwargs.get('day')) if 'day' in self.kwargs else None)
        kwargs['dashboards_app_month'] = (
            int(self.kwargs.get('month')) if 'month' in self.kwargs else None)
        kwargs['dashboards_app_year'] = (
            int(self.kwargs.get('year')) if 'year' in self.kwargs else None)
        if kwargs['dashboards_app_year']:
            kwargs['dashboards_app_archive_date'] = date(
                kwargs['dashboards_app_year'],
                kwargs['dashboards_app_month'] or 1,
                kwargs['dashboards_app_day'] or 1)
        return super(DateRangeDashboardList, self).get_context_data(**kwargs)


class YearDashboardList(DateRangeDashboardList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), 1, 1)
        date_to = date_from + relativedelta(years=1)
        return date_from, date_to


class MonthDashboardList(DateRangeDashboardList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), int(kwargs['month']), 1)
        date_to = date_from + relativedelta(months=1)
        return date_from, date_to


class DayDashboardList(DateRangeDashboardList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(
            int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        date_to = date_from + relativedelta(days=1)
        return date_from, date_to


@csrf_exempt
def plugin_position(request, plugin_type):
    from django.apps import apps


    try:

        app_label = request.POST['app_label']
        position_model = request.POST['position_model']

        RenderingModel = apps.get_model(app_label, plugin_type)
        PositionModel = apps.get_model(app_label, position_model)

        logger.debug("Saving Plugin Position of " + plugin_type)
        logger.debug("......" + position_model + ' pk: ' + request.POST['pk'])
        # logger.debug( request.POST)


        if request.method == 'POST':
            width = request.POST['width']
            height = request.POST['height']
            top = request.POST['top']
            left = request.POST['left']
            pk = request.POST['pk']




            obj, created = PositionModel.objects.update_or_create(
                model=RenderingModel.objects.get(pk=pk),
                defaults={
                    'is_resized': True,
                    'width': width,
                    'height': height,
                    'top': top,
                    'left': left
                }
            )




            if created:
                status = 'plugin saved succesfully - '+plugin_type


            else:
                status = 'plugin updated succesfully - '+ plugin_type


            logger.debug('......'+ status +pk)




            obj.refresh_from_db()

        else:
            pk = request.GET['pk']

            position = PositionModel.objects.filter(model=RenderingModel.objects.get(pk=pk))


            if position.exists():
                g = position.first()
                g.is_resized = False
                g.save()
                g.refresh_from_db()
            status = 'Plugin reset'+plugin_type
    except Exception as e:
        logger.exception('...... Error on '+plugin_type)
        # transaction.commit()

    return JsonResponse({'status': status})
