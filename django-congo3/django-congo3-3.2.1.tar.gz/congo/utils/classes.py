# -*- coding: utf-8 -*-

from collections import namedtuple

from django.conf import settings
from django.core.paginator import Page, Paginator as DefaultPaginator, EmptyPage, PageNotAnInteger
from django.db import connections
from django.db.models.query import prefetch_related_objects, RawQuerySet
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.translation import get_language_info, get_language

from congo.utils.i18n import get_url_for_language


class Message(object):
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    QUESTION = 26
    WARNING = 30
    ERROR = 40

    DEFAULT_TAGS = {
        DEBUG: 'debug',
        INFO: 'info',
        SUCCESS: 'success',
        QUESTION: 'question',
        WARNING: 'warning',
        ERROR: 'error',
    }

    CSS_CLASS_MAP = settings.CONGO_MESSAGE_CSS_CLASS_MAP
    CSS_ICON_CLASS_MAP = settings.CONGO_MESSAGE_CSS_ICON_CLASS_MAP

    def __init__(self, level, message, extra_tags = ''):
        self.level = level
        self.message = message
        self.tags = self.DEFAULT_TAGS[level]

        if len(extra_tags):
            self.tags += " " + extra_tags

    def __str__(self):
        return force_text(self.message)

    @classmethod
    def get_level_name(cls, level):
        return cls.DEFAULT_TAGS[level]

    @classmethod
    def get_level_by_name(cls, name):
        default_tags = {v:k for k, v in cls.DEFAULT_TAGS.items()}
        try:
            return default_tags[name]
        except KeyError:
            return None

    @classmethod
    def get_level_css_class(cls, level):
        return cls.CSS_CLASS_MAP[cls.get_level_name(level)]

    @classmethod
    def get_level_by_css_class(cls, css_class):
        css_class_map = {v:k for k, v in cls.CSS_CLASS_MAP.items()}
        try:
            return cls.get_level_by_name(css_class_map[css_class])
        except KeyError:
            return None

    @classmethod
    def render(cls, obj, **kwargs):
        close = kwargs.get('close', False)
        extra_tags = kwargs.get('extra_tags', '')

        level_name = cls.get_level_name(obj.level)
        css_class = cls.CSS_CLASS_MAP[level_name]
        css_icon_class = cls.CSS_ICON_CLASS_MAP[level_name]

        alert_class = settings.CONGO_MESSAGE_ALERT_CLASS % css_class
        dismiss_class = settings.CONGO_MESSAGE_DISMISS_CLASS if close else ""
        text_class = settings.CONGO_MESSAGE_TEXT_CLASS % css_class
        icon_class = settings.CONGO_MESSAGE_ICON_CLASS % css_icon_class

        _extra_tags = obj.tags
        if len(_extra_tags) > len(css_class) and _extra_tags[-(len(css_class) + 1):] == " %s" % css_class:
            _extra_tags = _extra_tags[:-(len(css_class) + 1)]
        elif _extra_tags == css_class:
            _extra_tags = ''

        alert_class_set = "%s %s %s %s" % (alert_class, dismiss_class, extra_tags, _extra_tags)
        alert_class_set = " ".join(alert_class_set.split())

        context = {
            'alert_class_set': alert_class_set,
            'close': close,
            'text_class': text_class,
            'icon_class': icon_class,
            'message': obj.message,
        }

        return render_to_string('congo/includes/message.html', context)

    @classmethod
    def debug(cls, message, extra_tags = ''):
        return cls(cls.DEBUG, message, extra_tags)

    @classmethod
    def info(cls, message, extra_tags = ''):
        return cls(cls.INFO, message, extra_tags)

    @classmethod
    def success(cls, message, extra_tags = ''):
        return cls(cls.SUCCESS, message, extra_tags)

    @classmethod
    def question(cls, message, extra_tags = ''):
        return cls(cls.QUESTION, message, extra_tags)

    @classmethod
    def warning(cls, message, extra_tags = ''):
        return cls(cls.WARNING, message, extra_tags)

    @classmethod
    def error(cls, message, extra_tags = ''):
        return cls(cls.ERROR, message, extra_tags)


class MetaData(object):

    def __init__(self, request, title = "", **kwargs):
        self.request = request

        self.title = title
        self.full_title = kwargs.get('full_title', None)
        self.subtitle = kwargs.get('subtitle', None)

        self.active = kwargs.get('active', None)
        self.breadcrumbs = kwargs.get('breadcrumbs', [])

        self.meta_title = kwargs.get('meta_title', None)
        self.meta_description = kwargs.get('meta_description', None)
        self.meta_image = kwargs.get('meta_image', None)

        self.append_default_title = kwargs.get('append_default_title', settings.CONGO_APPEND_DEFAULT_TITLE)

        self.canonical_url = kwargs.get('canonical_url', None)
        self.prev_url = kwargs.get('prev_url', None)
        self.next_url = kwargs.get('next_url', None)

        self.lang_obj = kwargs.get('lang_obj', None)
        self.lang_urls = kwargs.get('lang_urls', [])

        if self.active is None and request.resolver_match:
            self.active = request.resolver_match.url_name;

    def __str__(self):
        return self.get_meta_title()

    def get_full_title(self):
        return self.full_title or self.title

    def get_meta_title(self):
        meta_title = self.meta_title or self.title
        if self.append_default_title:
            if meta_title:
                return "%s %s %s" % (meta_title, settings.CONGO_DEFAULT_META_TITLE_DIVIDER, settings.CONGO_DEFAULT_META_TITLE)
            else:
                return settings.CONGO_DEFAULT_META_TITLE
        return meta_title

    def get_meta_description(self):
        if self.meta_description is None:
            return settings.CONGO_DEFAULT_META_DESCRIPTION
        return self.meta_description

    def get_meta_image(self):
        if self.meta_image is None:
            return settings.CONGO_DEFAULT_META_IMAGE
        return self.meta_image

    def add_breadcrumb(self, title = None, url = None):
        if title is None:
            title = self.title
        if url is None:
            url = self.request.path
        self.breadcrumbs.append([title, url])

    def get_parent_url(self):
        if len(self.breadcrumbs) > 1:
            return self.breadcrumbs[-2]
        return False

    def is_active(self, active):
        return self.active == active

    def get_lang_urls(self):
        if not hasattr(self, '_lang_urls'):
            if self.lang_urls is None:
                self._lang_urls = []
            elif self.lang_urls:
                self._lang_urls = self.lang_urls
            else:
                language = get_language()
                LangUrl = namedtuple('LangUrl', ['language', 'url', 'name', 'name_local'])
                self._lang_urls = []
                for code, name in settings.LANGUAGES:
                    if language == code:
                        continue
                    url = get_url_for_language(code, self.lang_obj or self.request.get_full_path())
                    if url:
                        info = get_language_info(code)
                        self._lang_urls.append(LangUrl(code, url, name, info.get('name_local')))

        return self._lang_urls


class DatabaseNotSupportedException(Exception):
    pass


class SearchQuerySetPaginator(DefaultPaginator):
    """
    Wydajny paginator dla SearchQuerySetów.
    """

    def __init__(self, object_list, per_page, result_model = None, orphans = 0, allow_empty_first_page = True, fields_to_prefetch = []):
        super(SearchQuerySetPaginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.search_query_set = self.object_list
        self._count = None
        self.fields_to_prefetch = fields_to_prefetch
        self.result_model = result_model

    def _get_count(self):
        if self._count is None:
            self._count = self.search_query_set.count()
        return self._count

    @property
    def count(self):
        return self._get_count()

    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_('That page number is not an integer'))
        if number < 1:
            raise EmptyPage(_('That page number is less than 1'))
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage(_('That page contains no results'))
        return number

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count

        # id_list = self.search_query_set.values_list('product_id', flat = True)[bottom:top]
        id_score_list = self.search_query_set.values_list('product_id', 'score')[bottom:top]
        id_list = [int(x[0]) for x in id_score_list]
        score_dict = {int(x):y for x, y in id_score_list}

        count = top - bottom
        enum_dict = dict(zip(id_list, range(0, count)))
        item_dict = {}

        for item in self.result_model.objects.filter(id__in = id_list).prefetch_related('translations'):
            item.score = score_dict[item.id]
            item_dict[item] = enum_dict[item.id]

        page_objects = sorted(item_dict, key = item_dict.__getitem__)
        return Page(page_objects, number, self)


class RawQuerySetPaginator(DefaultPaginator):
    """
    Wydajny paginator dla RawQuerySetów.
    """

    def __init__(self, object_list, per_page, orphans = 0, allow_empty_first_page = True, fields_to_prefetch = []):
        super(RawQuerySetPaginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.raw_query_set = self.object_list
        self.connection = connections[self.raw_query_set.db]
        self._count = None
        self.fields_to_prefetch = fields_to_prefetch

    def _get_count(self):
        if self._count is None:
            cursor = self.connection.cursor()
            count_query = 'SELECT COUNT(1) FROM (%s) AS sub_query_for_count' % self.raw_query_set.raw_query
            cursor.execute(count_query, self.raw_query_set.params)
            self._count = cursor.fetchone()[0]
        return self._count

    count = property(_get_count)

    # # mysql, postgresql, and sqlite can all use this syntax
    def __get_limit_offset_query(self, limit, offset):
        return '''SELECT * FROM (%s) as sub_query_for_pagination
                LIMIT %s OFFSET %s''' % (self.raw_query_set.raw_query, limit, offset)

    mysql_getquery = __get_limit_offset_query
    postgresql_getquery = __get_limit_offset_query
    sqlite_getquery = __get_limit_offset_query

    # # Get the oracle query, but check the version first
    # # Query is only supported in oracle version >= 12.1
    # # I have no access to oracle and have no idea if this code works
    # # TODO:TESTING
    def oracle_getquery(self, limit, offset):
        (major_version, minor_version) = self.connection.oracle_version[0:2]
        if major_version < 12 or (major_version == 12 and minor_version < 1):
            raise DatabaseNotSupportedException('Oracle version must be 12.1 or higher')
        return '''SELECT * FROM (%s) as sub_query_for_pagination
                  OFFSET %s ROWS FETCH NEXT %s ROWS ONLY''' % (self.raw_query_set.raw_query, offset, limit)

    def firebird_getquery(self, limit, offset): # # TODO:TESTING
        return '''SELECT FIRST %s SKIP %s *
                FROM (%s) as sub_query_for_pagination''' % (limit, offset, self.raw_query_set.raw_query)

    def page(self, number):
        number = self.validate_number(number)
        offset = (number - 1) * self.per_page
        limit = self.per_page
        if offset + limit + self.orphans >= self.count:
            limit = self.count - offset
        database_vendor = self.connection.vendor
        try:
            query_with_limit = getattr(self, '%s_getquery' % database_vendor)(limit, offset)
        except AttributeError:
            raise DatabaseNotSupportedException('%s is not supported by RawQuerySetPaginator' % database_vendor)

        if self.fields_to_prefetch:
            page_objects = list(self.raw_query_set.model.objects.raw(query_with_limit, self.raw_query_set.params))

            for field in self.fields_to_prefetch:
                prefetch_related_objects(page_objects, field)

            return Page(page_objects, number, self)
        else:
            return Page(list(self.raw_query_set.model.objects.raw(query_with_limit, self.raw_query_set.params)), number, self)


def Paginator(object_list, per_page, result_model = None, orphans = 0, allow_empty_first_page = True, fields_to_prefetch = []):
    """
    Wrapper dla customowych Paginatorów. Obsługuje RawQuerySet, SearchQuerySet (haystack) oraz zwykłe QuerySety.
    """
    try:
        from haystack.query import SearchQuerySet
        if isinstance(object_list, RawQuerySet):
            return RawQuerySetPaginator(object_list, per_page, orphans, allow_empty_first_page, fields_to_prefetch)

        elif isinstance(object_list, SearchQuerySet):
            return SearchQuerySetPaginator(object_list, per_page, result_model, orphans, allow_empty_first_page)

        else:
            return DefaultPaginator(object_list, per_page, orphans, allow_empty_first_page)

    except ImportError:
        if isinstance(object_list, RawQuerySet):
            return RawQuerySetPaginator(object_list, per_page, orphans, allow_empty_first_page, fields_to_prefetch)
        else:
            return DefaultPaginator(object_list, per_page, orphans, allow_empty_first_page)
