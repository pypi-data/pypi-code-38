# -*- coding: utf-8 -*-
from collections import namedtuple
import importlib
import json
import os
import urlparse
from warnings import warn

from PIL import Image
from congo.utils.i18n import get_url_for_language
from django.conf import settings
from django.core.paginator import Page, Paginator as DefaultPaginator
from django.db import connections
from django.db.models.query import RawQuerySet, prefetch_related_objects
from django.http.response import HttpResponse, JsonResponse
from django.utils._os import safe_join
from django.utils.encoding import filepath_to_uri, python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import get_language_info, get_language


class JSONResponse(HttpResponse):
    """
    HttpResponse rozszerzony o atrybut content_type = "application/json"
    """

    def __init__(self, content = {}, *args, **kwargs):
        warn(u"To be replaced with django.http.response.JsonResponse", DeprecationWarning)

        kwargs['content_type'] = "application/json"
        super(JSONResponse, self).__init__(json.dumps(content), *args, **kwargs)


class JsonResponseBadRequest(JsonResponse):
    status_code = 400


class JsonResponseForbidden(JsonResponse):
    status_code = 403


def get_class(class_path):
    warn(u"To be replaced with django.utils.module_loading.import_string", DeprecationWarning)

    module_name, class_name = class_path.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)

# Images


@python_2_unicode_compatible
class BlankImage(object):
    """
    Klasa reprezentująca puste zdjęcie. Pozwala na skalowanie, zwrot zarówno html jak i odnośnika do pliku.
    """

    def __init__(self):
        self.name = settings.CONGO_BLANK_IMAGE_FILENAME
        self.path = settings.CONGO_BLANK_IMAGE_PATH
        self.url = settings.CONGO_BLANK_IMAGE_URL

    def __str__(self):
        return self.get_path()

    def _get_size(self, max_width, max_height = None):
        if not max_height:
            max_height = max_width

        if not isinstance(max_width, int):
            max_width = settings.CONGO_DEFAULT_IMAGE_WIDTH

        if not isinstance(max_height, int):
            max_height = settings.CONGO_DEFAULT_IMAGE_HEIGHT

        return (max_width, max_height)

    def _resize(self, path, width, height):
        image = Image.open(self.get_path())
        image = image.resize((width, height), Image.ANTIALIAS)
        image.save(path)

        del image

    def render(self, max_width = None, max_height = None, **kwargs):
        url = self.get_url(max_width, max_height)

        width, height = self._get_size(max_width, max_height)
        css_class = kwargs.get('css_class', '')
        alt_text = kwargs.get('alt_text', '')

        html = """<img src="%s" width="%s" height="%s" class="%s" alt="%s" />""" % (url, width, height, css_class, alt_text)
        return mark_safe(html)

    def get_path(self, name = None):
        if not name:
            name = self.name
        return os.path.normpath(safe_join(self.path, name))

    def get_name(self, width, height):
        split = self.name.rsplit('.', 1)
        return '%s_%sx%s.%s' % (split[0], width, height, split[1])

    def get_url(self, max_width = None, max_height = None):
        width, height = self._get_size(max_width, max_height)
        name = self.get_name(width, height)
        path = self.get_path(name)

        if not os.path.isfile(path):
            try:
                self._resize(path, width, height)
            except IOError:
                self.get_path(name)

        return urlparse.urljoin(self.url, filepath_to_uri(name))

# Data structs


@python_2_unicode_compatible
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

    CSS_CLASS_DICT = {
        DEBUG: 'debug',
        INFO: 'info',
        SUCCESS: 'success',
        QUESTION: 'question',
        WARNING: 'warning',
        ERROR: 'danger',
    }

    def __init__(self, level, message, extra_tags = ''):
        self.level = level
        self.message = message
        self.tags = self.DEFAULT_TAGS[level]

        if len(extra_tags):
            self.tags += " " + extra_tags

    def __str__(self):
        return self.message

    @classmethod
    def get_level_name(cls, level):
        return cls.DEFAULT_TAGS[level]

    @classmethod
    def get_level_by_css_class(cls, css_class):
        for key, val in cls.CSS_CLASS_DICT.items():
            if  css_class == val:
                return key
        return None

    @classmethod
    def get_level_css_class(cls, level):
        return cls.CSS_CLASS_DICT[level]

    @classmethod
    def render(cls, obj, **kwargs):
        # close (bool)
        close = kwargs.get('close', False)
        extra_tags = kwargs.get('extra_tags', '')

        level_css_class = cls.CSS_CLASS_DICT[obj.level]
        alert_class = "alert-%s" % level_css_class
        dismiss_class = "alert-dismissible" if close else ""
        fade_class = "fade in" if close else ""
        close_html = """<button type="button" class="close" data-dismiss="alert">&times;</button>""" if close else ""
        text_class = "text-%s" % level_css_class
        icon_class = kwargs.get('icon_class', "icon-%s" % level_css_class)

        _extra_tags = obj.tags
        if len(_extra_tags) > len(level_css_class) and _extra_tags[-(len(level_css_class) + 1):] == " %s" % level_css_class:
            _extra_tags = _extra_tags[:-(len(level_css_class) + 1)]
        elif _extra_tags == level_css_class:
            _extra_tags = ''

        alert_class_set = "%s %s %s %s %s" % (alert_class, dismiss_class, fade_class, extra_tags, _extra_tags)
        alert_class_set = " ".join(alert_class_set.split())

        html = u"""
            <div class="alert %s">%s
              <div class="alert-icon %s"><i class="%s"></i></div>
              <div class="alert-body">%s</div>
            </div>
        """ % (alert_class_set, close_html, text_class, icon_class, obj.message)

        return mark_safe(html)

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


@python_2_unicode_compatible
class MetaData(object):

    def __init__(self, request, title = u"", **kwargs):
        self.request = request

        self.title = title
        self.full_title = kwargs.get('full_title', None)
        self.subtitle = kwargs.get('subtitle', None)
        self.meta_title = kwargs.get('meta_title', None)
        self.meta_description = kwargs.get('meta_description', None)
        self.meta_image = kwargs.get('meta_image', None)
        self.canonical_url = kwargs.get('canonical_url', None)
        self.prev_url = kwargs.get('prev_url', None)
        self.next_url = kwargs.get('next_url', None)
        self.active = kwargs.get('active', None)
        self.breadcrumbs = kwargs.get('breadcrumbs', [])
        self.view = kwargs.get('view', None) # @fg potrzebne?
        self.append_default_title = kwargs.get('append_default_title', settings.CONGO_APPEND_DEFAULT_TITLE)
        self.is_popup = kwargs.get('is_popup', None) # @fg potrzebne?
        self.ng_app = kwargs.get('ng_app', None)

        self.lang_obj = kwargs.get('lang_obj', None)
        self.lang_urls = kwargs.get('lang_urls', [])

        try:
            self.request_method = request.META.get('REQUEST_METHOD', None)
        except AttributeError:
            self.request_method = None

    def __str__(self):
        return self.get_meta_title()

    def get_full_title(self):
        return self.full_title or self.title

    def get_meta_title(self):
        meta_title = self.meta_title or self.title
        if self.append_default_title:
            if meta_title:
                return u"%s %s %s" % (meta_title, settings.CONGO_DEFAULT_META_TITLE_DIVIDER, settings.CONGO_DEFAULT_META_TITLE)
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

    def add_breadcrumb(self, label = None, url = None):
        if label is None:
            label = self.title
        if url is None:
            url = self.request.path
        self.breadcrumbs.append([label, url])

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


class UserDevice(object):
    # device screen
    XS = 'xs'
    SM = 'sm'
    MD = 'md'
    LG = 'lg'

    # device type
    MOBILE = 'mobile'
    TABLET = 'tablet'
    PC = 'pc'

    # break_points
    BREAK_XS = 768
    BREAK_SM = 992
    BREAK_MD = 1200

    device_screen = LG
    device_type = None
    device_family = None

    os_family = None
    os_version = None

    browser_family = None
    browser_version = None

    is_mobile = False
    is_tablet = False
    is_pc = True

    is_touch_capable = False

    def __init__(self, request):
        # django_user_agents.middleware.UserAgentMiddleware required
        if hasattr(request, 'user_agent'):
            user_agent = request.user_agent

            # device_screen
            if user_agent.is_mobile:
                self.device_screen = self.XS
            elif user_agent.is_tablet:
                self.device_screen = self.SM

            # device_type
            if user_agent.is_mobile:
                self.device_type = self.MOBILE
            elif user_agent.is_tablet:
                self.device_type = self.TABLET
            elif user_agent.is_pc:
                self.device_type = self.PC

            self.device_family = user_agent.device.family

            self.os_family = user_agent.os.family
            self.os_version = user_agent.os.version_string

            self.browser_family = user_agent.browser.family
            self.browser_version = user_agent.browser.version_string

            self.is_mobile = user_agent.is_mobile
            self.is_tablet = user_agent.is_tablet
            self.is_pc = user_agent.is_pc

            self.is_touch_capable = user_agent.is_touch_capable

        device_screen = self.get_device_screen(request)
        if device_screen:
            self.device_screen = device_screen

    @property
    def is_xs(self):
        return self.device_screen == self.XS

    @property
    def is_sm(self):
        return self.device_screen == self.SM

    @property
    def is_md(self):
        return self.device_screen == self.MD

    @property
    def is_lg(self):
        return self.device_screen == self.LG

    @classmethod
    def set_device_screen(cls, request, screen_size):
        screen_size = int(screen_size)

        if screen_size <= cls.BREAK_XS:
            device_screen = cls.XS
        elif screen_size <= cls.BREAK_SM:
            device_screen = cls.SM
        elif screen_size <= cls.BREAK_MD:
            device_screen = cls.MD
        else:
            device_screen = cls.LG

        cached = cls.get_device_screen(request)

        if device_screen == cached:
            change = False
        else:
            request.session['device_screen'] = device_screen
            change = True

        return change

    @classmethod
    def get_device_screen(cls, request, dafault = None):
        return request.session.get('device_screen', dafault)


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
