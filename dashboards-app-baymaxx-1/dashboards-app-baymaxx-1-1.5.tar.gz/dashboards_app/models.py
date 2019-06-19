# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django.core.validators
from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_categories.fields import CategoryManyToManyField
from aldryn_categories.models import Category
from dashboards_app.utils.utilities import get_valid_languages_from_request
from aldryn_people.models import Person
from aldryn_translation_tools.models import TranslatedAutoSlugifyMixin, TranslationHelperMixin
from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language, get_redirect_on_fallback
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import connection, models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override, ugettext
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields
from sortedm2m.fields import SortedManyToManyField
# from taggit.managers import TaggableManager
from taggit.models import Tag

from .cms_appconfig import Dashboards_appConfig
from .managers import RelatedManager
from .utils import get_plugin_index_data, get_request, strip_tags

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode


if settings.LANGUAGES:
    LANGUAGE_CODES = [language[0] for language in settings.LANGUAGES]
elif settings.LANGUAGE:
    LANGUAGE_CODES = [settings.LANGUAGE]
else:
    raise ImproperlyConfigured(
        'Neither LANGUAGES nor LANGUAGE was found in settings.')


# At startup time, SQL_NOW_FUNC will contain the database-appropriate SQL to
# obtain the CURRENT_TIMESTAMP.
SQL_NOW_FUNC = {
    'mssql': 'GetDate()', 'mysql': 'NOW()', 'postgresql': 'now()',
    'sqlite': 'CURRENT_TIMESTAMP', 'oracle': 'CURRENT_TIMESTAMP'
}[connection.vendor]

SQL_IS_TRUE = {
    'mssql': '== TRUE', 'mysql': '= 1', 'postgresql': 'IS TRUE',
    'sqlite': '== 1', 'oracle': 'IS TRUE'
}[connection.vendor]


@python_2_unicode_compatible
class Dashboard(TranslatedAutoSlugifyMixin,
              TranslationHelperMixin,
              TranslatableModel):

    # TranslatedAutoSlugifyMixin options
    slug_source_field_name = 'title'
    slug_default = _('untitled-dashboard')
    # when True, updates the dashboard's search_data field
    # whenever the dashboard is saved or a plugin is saved
    # on the dashboard's content placeholder.
    update_search_on_save = getattr(
        settings,
        'dashboards_app_UPDATE_SEARCH_DATA_ON_SAVE',
        False
    )

    translations = TranslatedFields(
        title=models.CharField(_('title'), max_length=234),
        slug=models.SlugField(
            verbose_name=_('slug'),
            max_length=255,
            db_index=True,
            blank=True,
            help_text=_(
                'Used in the URL. If changed, the URL will change. '
                'Clear it to have it re-created automatically.'),
        ),
        lead_in=HTMLField(
            verbose_name=_('lead'), default='',
            help_text=_(
                'The lead gives the reader the main idea of the story, this '
                'is useful in overviews, lists or as an introduction to your '
                'dashboard.'
            ),
            blank=True,
        ),
        meta_title=models.CharField(
            max_length=255, verbose_name=_('meta title'),
            blank=True, default=''),
        meta_description=models.TextField(
            verbose_name=_('meta description'), blank=True, default=''),
        meta_keywords=models.TextField(
            verbose_name=_('meta keywords'), blank=True, default=''),
        meta={'unique_together': (('language_code', 'slug', ), )},

        search_data=models.TextField(blank=True, editable=False)
    )

    #for api


    #for api
    content = PlaceholderField('dashboard_content',
                               related_name='dashboard_content')
    sidebar_content=PlaceholderField('dashboard_sidebar_content',
                                     related_name='dashboard_sidebar_content')

    author = models.ForeignKey(Person, null=True, blank=True,
                               verbose_name=_('author'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'))
    app_config = AppHookConfigField(
        Dashboards_appConfig,
        verbose_name=_('Section'),
        help_text='',
    )
    categories = CategoryManyToManyField('aldryn_categories.Category',
                                         verbose_name=_('categories'),
                                         blank=True)
    publishing_date = models.DateTimeField(_('publishing date'),
                                           default=now)
    is_published = models.BooleanField(_('is published'), default=False,
                                       db_index=True)
    is_featured = models.BooleanField(_('is featured'), default=False,
                                      db_index=True)
    featured_image = FilerImageField(
        verbose_name=_('featured image'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    # tags = TaggableManager(blank=True)

    # Setting "symmetrical" to False since it's a bit unexpected that if you
    # set "B relates to A" you immediately have also "A relates to B". It have
    # to be forced to False because by default it's True if rel.to is "self":
    #
    # https://github.com/django/django/blob/1.8.4/django/db/models/fields/related.py#L2144
    #
    # which in the end causes to add reversed releted-to entry as well:
    #
    # https://github.com/django/django/blob/1.8.4/django/db/models/fields/related.py#L977
    related = SortedManyToManyField('self', verbose_name=_('related dashboards'),
                                    blank=True, symmetrical=False)

    objects = RelatedManager()

    class Meta:
        ordering = ['-publishing_date']

    def getId(self):
        return self.id

    @property
    def published(self):
        """
        Returns True only if the dashboard (is_published == True) AND has a
        published_date that has passed.
        """
        return (self.is_published and self.publishing_date <= now())

    @property
    def future(self):
        """
        Returns True if the dashboard is published but is scheduled for a
        future date/time.
        """
        return (self.is_published and self.publishing_date > now())

    def get_absolute_url(self, language=None):
        """Returns the url for this Dashboard in the selected permalink format."""
        if not language:
            language = get_current_language()
        kwargs = {}
        permalink_type = self.app_config.permalink_type
        if 'y' in permalink_type:
            kwargs.update(year=self.publishing_date.year)
        if 'm' in permalink_type:
            kwargs.update(month="%02d" % self.publishing_date.month)
        if 'd' in permalink_type:
            kwargs.update(day="%02d" % self.publishing_date.day)
        if 'i' in permalink_type:
            kwargs.update(pk=self.pk)
        if 's' in permalink_type:
            slug, lang = self.known_translation_getter(
                'slug', default=None, language_code=language)
            if slug and lang:
                site_id = getattr(settings, 'SITE_ID', None)
                if get_redirect_on_fallback(language, site_id):
                    language = lang
                kwargs.update(slug=slug)

        if self.app_config and self.app_config.namespace:
            namespace = '{0}:'.format(self.app_config.namespace)
        else:
            namespace = ''

        with override(language):
            return reverse('{0}dashboard-detail'.format(namespace), kwargs=kwargs)

    def get_search_data(self, language=None, request=None):
        """
        Provides an index for use with Haystack, or, for populating
        Dashboard.translations.search_data.
        """
        if not self.pk:
            return ''
        if language is None:
            language = get_current_language()
        if request is None:
            request = get_request(language=language)
        description = self.safe_translation_getter('lead_in', '')
        text_bits = [strip_tags(description)]
        for category in self.categories.all():
            text_bits.append(
                force_unicode(category.safe_translation_getter('name')))
        for tag in self.tags.all():
            text_bits.append(force_unicode(tag.name))
        if self.content:
            plugins = self.content.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                plugin_text_content = ' '.join(
                    get_plugin_index_data(base_plugin, request))
                text_bits.append(plugin_text_content)
        return ' '.join(text_bits)

    def save(self, *args, **kwargs):
        # Update the search index
        if self.update_search_on_save:
            self.search_data = self.get_search_data()

        # Ensure there is an owner.
        if self.app_config.create_authors and self.author is None:
            self.author = Person.objects.get_or_create(
                user=self.owner,
                defaults={
                    'name': ' '.join((
                        self.owner.first_name,
                        self.owner.last_name,
                    )),
                })[0]
        # slug would be generated by TranslatedAutoSlugifyMixin
        super(Dashboard, self).save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True)



class PluginEditModeMixin(object):
    def get_edit_mode(self, request):
        """
        Returns True only if an operator is logged-into the CMS and is in
        edit mode.
        """
        return (
            hasattr(request, 'toolbar') and request.toolbar and
            request.toolbar.edit_mode)


class AdjustableCacheModelMixin(models.Model):
    # NOTE: This field shouldn't even be displayed in the plugin's change form
    # if using django CMS < 3.3.0
    cache_duration = models.PositiveSmallIntegerField(
        default=0,  # not the most sensible, but consistent with older versions
        blank=False,
        help_text=_(
            "The maximum duration (in seconds) that this plugin's content "
            "should be cached.")
    )

    class Meta:
        abstract = True


class Dashboards_appCMSPlugin(CMSPlugin):
    """AppHookConfig aware abstract CMSPlugin class for Aldryn Newsblog"""
    # avoid reverse relation name clashes by not adding a related_name
    # to the parent plugin
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name='+', parent_link=True)

    app_config = models.ForeignKey(Dashboards_appConfig, verbose_name=_('Apphook configuration'))

    class Meta:
        abstract = True

    def copy_relations(self, old_instance):
        self.app_config = old_instance.app_config


@python_2_unicode_compatible
class Dashboards_appArchivePlugin(PluginEditModeMixin, AdjustableCacheModelMixin,
                            Dashboards_appCMSPlugin):
    # NOTE: the PluginEditModeMixin is eventually used in the cmsplugin, not
    # here in the model.
    def __str__(self):
        return ugettext('%s archive') % (self.app_config.get_app_title(), )


class Dashboards_appDashboardSearchPlugin(Dashboards_appCMSPlugin):
    max_dashboards = models.PositiveIntegerField(
        _('max dashboards'), default=10,
        validators=[django.core.validators.MinValueValidator(1)],
        help_text=_('The maximum number of found dashboards display.')
    )

    def __str__(self):
        return ugettext('%s archive') % (self.app_config.get_app_title(), )


@python_2_unicode_compatible
class Dashboards_appAuthorsPlugin(PluginEditModeMixin, Dashboards_appCMSPlugin):
    def get_authors(self, request):
        """
        Returns a queryset of authors (people who have published an dashboard),
        annotated by the number of dashboards (dashboard_count) that are visible to
        the current user. If this user is anonymous, then this will be all
        dashboards that are published and whose publishing_date has passed. If the
        user is a logged-in cms operator, then it will be all dashboards.
        """

        # The basic subquery (for logged-in content managers in edit mode)
        subquery = """
            SELECT COUNT(*)
            FROM dashboards_app_dashboard
            WHERE
                dashboards_app_dashboard.author_id =
                    aldryn_people_person.id AND
                dashboards_app_dashboard.app_config_id = %d"""

        # For other users, limit subquery to published dashboards
        if not self.get_edit_mode(request):
            subquery += """ AND
                dashboards_app_dashboard.is_published %s AND
                dashboards_app_dashboard.publishing_date <= %s
            """ % (SQL_IS_TRUE, SQL_NOW_FUNC, )

        # Now, use this subquery in the construction of the main query.
        query = """
            SELECT (%s) as dashboard_count, aldryn_people_person.*
            FROM aldryn_people_person
        """ % (subquery % (self.app_config.pk, ), )

        raw_authors = list(Person.objects.raw(query))
        authors = [author for author in raw_authors if author.dashboard_count]
        return sorted(authors, key=lambda x: x.dashboard_count, reverse=True)

    def __str__(self):
        return ugettext('%s authors') % (self.app_config.get_app_title(), )


@python_2_unicode_compatible
class Dashboards_appCategoriesPlugin(PluginEditModeMixin, Dashboards_appCMSPlugin):
    def __str__(self):
        return ugettext('%s categories') % (self.app_config.get_app_title(), )

    def get_categories(self, request):
        """
        Returns a list of categories, annotated by the number of dashboards
        (dashboard_count) that are visible to the current user. If this user is
        anonymous, then this will be all dashboards that are published and whose
        publishing_date has passed. If the user is a logged-in cms operator,
        then it will be all dashboards.
        """

        subquery = """
            SELECT COUNT(*)
            FROM dashboards_app_dashboard, dashboards_app_dashboard_categories
            WHERE
                dashboards_app_dashboard_categories.category_id =
                    aldryn_categories_category.id AND
                dashboards_app_dashboard_categories.dashboard_id =
                    dashboards_app_dashboard.id AND
                dashboards_app_dashboard.app_config_id = %d
        """ % (self.app_config.pk, )

        if not self.get_edit_mode(request):
            subquery += """ AND
                dashboards_app_dashboard.is_published %s AND
                dashboards_app_dashboard.publishing_date <= %s
            """ % (SQL_IS_TRUE, SQL_NOW_FUNC, )

        query = """
            SELECT (%s) as dashboard_count, aldryn_categories_category.*
            FROM aldryn_categories_category
        """ % (subquery, )

        raw_categories = list(Category.objects.raw(query))
        categories = [
            category for category in raw_categories if category.dashboard_count]
        return sorted(categories, key=lambda x: x.dashboard_count, reverse=True)


@python_2_unicode_compatible
class Dashboards_appFeaturedDashboardsPlugin(PluginEditModeMixin, Dashboards_appCMSPlugin):
    dashboard_count = models.PositiveIntegerField(
        default=1,
        validators=[django.core.validators.MinValueValidator(1)],
        help_text=_('The maximum number of featured dashboards display.')
    )

    def get_dashboards(self, request):
        if not self.dashboard_count:
            return Dashboard.objects.none()
        queryset = Dashboard.objects
        if not self.get_edit_mode(request):
            queryset = queryset.published()
        languages = get_valid_languages_from_request(
            self.app_config.namespace, request)
        if self.language not in languages:
            return queryset.none()
        queryset = queryset.translated(*languages).filter(
            app_config=self.app_config,
            is_featured=True)
        return queryset[:self.dashboard_count]

    def __str__(self):
        if not self.pk:
            return 'featured dashboards'
        prefix = self.app_config.get_app_title()
        if self.dashboard_count == 1:
            title = ugettext('featured dashboard')
        else:
            title = ugettext('featured dashboards: %(count)s') % {
                'count': self.dashboard_count,
            }
        return '{0} {1}'.format(prefix, title)


@python_2_unicode_compatible
class Dashboards_appLatestDashboardsPlugin(PluginEditModeMixin,
                                   AdjustableCacheModelMixin,
                                   Dashboards_appCMSPlugin):
    latest_dashboards = models.IntegerField(
        default=5,
        help_text=_('The maximum number of latest dashboards to display.')
    )
    exclude_featured = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        help_text=_(
            'The maximum number of featured dashboards to exclude from display. '
            'E.g. for uses in combination with featured dashboards plugin.')
    )

    def get_dashboards(self, request):
        """
        Returns a queryset of the latest N dashboards. N is the plugin setting:
        latest_dashboards.
        """
        queryset = Dashboard.objects
        featured_qs = Dashboard.objects.all().filter(is_featured=True)
        if not self.get_edit_mode(request):
            queryset = queryset.published()
            featured_qs = featured_qs.published()
        languages = get_valid_languages_from_request(
            self.app_config.namespace, request)
        if self.language not in languages:
            return queryset.none()
        queryset = queryset.translated(*languages).filter(
            app_config=self.app_config)
        featured_qs = featured_qs.translated(*languages).filter(
            app_config=self.app_config)
        exclude_featured = featured_qs.values_list(
            'pk', flat=True)[:self.exclude_featured]
        queryset = queryset.exclude(pk__in=list(exclude_featured))
        return queryset[:self.latest_dashboards]

    def __str__(self):
        return ugettext('%(app_title)s latest dashboards: %(latest_dashboards)s') % {
            'app_title': self.app_config.get_app_title(),
            'latest_dashboards': self.latest_dashboards,
        }


@python_2_unicode_compatible
class Dashboards_appRelatedPlugin(PluginEditModeMixin, AdjustableCacheModelMixin,
                            CMSPlugin):
    # NOTE: This one does NOT subclass Dashboards_appCMSPlugin. This is because this
    # plugin can really only be placed on the dashboard detail view in an apphook.
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name='+', parent_link=True)

    def get_dashboards(self, dashboard, request):
        """
        Returns a queryset of dashboards that are related to the given dashboard.
        """
        languages = get_valid_languages_from_request(
            dashboard.app_config.namespace, request)
        if self.language not in languages:
            return Dashboard.objects.none()
        qs = dashboard.related.translated(*languages)
        if not self.get_edit_mode(request):
            qs = qs.published()
        return qs

    def __str__(self):
        return ugettext('Related dashboards')


# @python_2_unicode_compatible
# class Dashboards_appTagsPlugin(PluginEditModeMixin, Dashboards_appCMSPlugin):
#
#     def get_tags(self, request):
#         """
#         Returns a queryset of tags, annotated by the number of dashboards
#         (dashboard_count) that are visible to the current user. If this user is
#         anonymous, then this will be all dashboards that are published and whose
#         publishing_date has passed. If the user is a logged-in cms operator,
#         then it will be all dashboards.
#         """
#
#         dashboard_content_type = ContentType.objects.get_for_model(Dashboard)
#
#         subquery = """
#             SELECT COUNT(*)
#             FROM dashboards_app_dashboard, taggit_taggeditem
#             WHERE
#                 taggit_taggeditem.tag_id = taggit_tag.id AND
#                 taggit_taggeditem.content_type_id = %d AND
#                 taggit_taggeditem.object_id = dashboards_app_dashboard.id AND
#                 dashboards_app_dashboard.app_config_id = %d"""
#
#         if not self.get_edit_mode(request):
#             subquery += """ AND
#                 dashboards_app_dashboard.is_published %s AND
#                 dashboards_app_dashboard.publishing_date <= %s
#             """ % (SQL_IS_TRUE, SQL_NOW_FUNC, )
#
#         query = """
#             SELECT (%s) as dashboard_count, taggit_tag.*
#             FROM taggit_tag
#         """ % (subquery % (dashboard_content_type.id, self.app_config.pk), )
#
#         raw_tags = list(Tag.objects.raw(query))
#         tags = [tag for tag in raw_tags if tag.dashboard_count]
#         return sorted(tags, key=lambda x: x.dashboard_count, reverse=True)
#
#     def __str__(self):
#         return ugettext('%s tags') % (self.app_config.get_app_title(), )


@receiver(post_save, dispatch_uid='dashboard_update_search_data')
def update_search_data(sender, instance, **kwargs):
    """
    Upon detecting changes in a plugin used in an Dashboard's content
    (PlaceholderField), update the dashboard's search_index so that we can
    perform simple searches even without Haystack, etc.
    """
    is_cms_plugin = issubclass(instance.__class__, CMSPlugin)

    if Dashboard.update_search_on_save and is_cms_plugin:
        placeholder = (getattr(instance, '_placeholder_cache', None) or
                       instance.placeholder)
        if hasattr(placeholder, '_attached_model_cache'):
            if placeholder._attached_model_cache == Dashboard:
                dashboard = placeholder._attached_model_cache.objects.language(
                    instance.language).get(content=placeholder.pk)
                dashboard.search_data = dashboard.get_search_data(instance.language)
                dashboard.save()
