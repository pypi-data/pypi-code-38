#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Template generation"""

import os.path
from collections import namedtuple
from sat.core.constants import Const as C
from sat.core.i18n import _
from sat.core import exceptions
from sat.tools import config
from sat.tools.common import date_utils
from sat.core.log import getLogger
from xml.sax.saxutils import quoteattr
import time
import re
from babel import support
from babel import Locale
from babel.core import UnknownLocaleError
import pygments
from pygments import lexers
from pygments import formatters

try:
    import sat_templates
except ImportError:
    raise exceptions.MissingModule(
        u"sat_templates module is not available, please install it or check your path to "
        u"use template engine"
    )
else:
    sat_templates  # to avoid pyflakes warning

try:
    import jinja2
except:
    raise exceptions.MissingModule(
        u"Missing module jinja2, please install it from http://jinja.pocoo.org or with "
        u"pip install jinja2"
    )

from jinja2 import Markup as safe
from jinja2 import is_undefined
from jinja2 import utils
from jinja2 import TemplateNotFound
from jinja2 import contextfilter
from jinja2.loaders import split_template_path
from lxml import etree

log = getLogger(__name__)

HTML_EXT = ("html", "xhtml")
RE_ATTR_ESCAPE = re.compile(r"[^a-z_-]")
SITE_RESERVED_NAMES = (u"sat",)
TPL_RESERVED_CHARS = ur"()/."
RE_TPL_RESERVED_CHARS = re.compile(u"[" + TPL_RESERVED_CHARS + u"]")

TemplateData = namedtuple("TemplateData", ['site', 'theme', 'path'])


class TemplateLoader(jinja2.BaseLoader):
    """A template loader which handle site, theme and absolute paths"""
    # TODO: list_templates should be implemented

    def __init__(self, sites_paths, trusted=False):
        """
        @param trusted(bool): if True, absolue template paths will be allowed
            be careful when using this option and sure that you can trust the template,
            as this allow the template to open any file on the system that the
            launching user can access.
        """
        if not sites_paths or not u"" in sites_paths:
            raise exceptions.InternalError(u"Invalid sites_paths")
        super(jinja2.BaseLoader, self).__init__()
        self.sites_paths = sites_paths
        self.trusted = trusted

    @staticmethod
    def parse_template(template):
        """Parse template path and return site, theme and path

        @param template_path(unicode): path to template with parenthesis syntax
            The site and/or theme can be specified in parenthesis just before the path
            e.g.: (some_theme)path/to/template.html
                  (/some_theme)path/to/template.html (equivalent to previous one)
                  (other_site/other_theme)path/to/template.html
                  (other_site/)path/to/template.html (defaut theme for other_site)
                  /absolute/path/to/template.html (in trusted environment only)
        @return (TemplateData):
            site, theme and template_path.
            if site is empty, SàT Templates are used
            site and theme can be both None if absolute path is used
            Relative path is the path from theme root dir e.g. blog/articles.html
        """
        if template.startswith(u"("):
            # site and/or theme are specified
            try:
                theme_end = template.index(u")")
            except IndexError:
                raise ValueError(u"incorrect site/theme in template")
            theme_data = template[1:theme_end]
            theme_splitted = theme_data.split(u'/')
            if len(theme_splitted) == 1:
                site, theme = u"", theme_splitted[0]
            elif len(theme_splitted) == 2:
                site, theme = theme_splitted
            else:
                raise ValueError(u"incorrect site/theme in template")
            template_path = template[theme_end+1:]
            if not template_path or template_path.startswith(u"/"):
                raise ValueError(u"incorrect template path")
        elif template.startswith(u"/"):
            # this is an absolute path, so we have no site and no theme
            site = None
            theme = None
            template_path = template
        else:
            # a default template
            site = u""
            theme = C.TEMPLATE_THEME_DEFAULT
            template_path = template

        if site is not None:
            site = site.strip()
            if not site:
                site = u""
            elif site in SITE_RESERVED_NAMES:
                raise ValueError(_(u"{site} can't be used as site name, "
                                   u"it's reserved.").format(site=site))

        if theme is not None:
            theme = theme.strip()
            if not theme:
                theme = C.TEMPLATE_THEME_DEFAULT
            if RE_TPL_RESERVED_CHARS.search(theme):
                raise ValueError(_(u"{theme} contain forbidden char. Following chars "
                                   u"are forbidden: {reserved}").format(
                                   theme=theme, reserved=TPL_RESERVED_CHARS))

        return TemplateData(site, theme, template_path)

    @staticmethod
    def getSitesAndThemes(site, theme):
        """Get sites and themes to check for template/file

        Will add default theme and default site in search list when suitable
        @param site(unicode): site requested
        @param theme(unicode): theme requested
        @return (list[tuple[unicode, unicode]]): site and theme couples to check
        """
        sites_and_themes = [[site, theme]]
        if theme != C.TEMPLATE_THEME_DEFAULT:
            sites_and_themes.append([site, C.TEMPLATE_THEME_DEFAULT])
        if site:
            # the site is not the default one, so we add default at the end
            sites_and_themes.append([u'', C.TEMPLATE_THEME_DEFAULT])
        return sites_and_themes

    def _get_template_f(self, site, theme, path_elts):
        """Look for template and return opened file if found

        @param site(unicode): names of site to check
            (default site will also checked)
        @param theme(unicode): theme to check (default theme will also be checked)
        @param path_elts(iterable[str]): elements of template path
        @return (tuple[(File, None), (str, None)]): a tuple with:
            - opened template, or None if not found
            - absolute file path, or None if not found
        """
        if site is None:
            raise exceptions.InternalError(
                u"_get_template_f must not be used with absolute path")
        for site, theme in self.getSitesAndThemes(site, theme):
            try:
                base_path = self.sites_paths[site]
            except KeyError:
                log.warning(_(u"Unregistered site requested: {site}").format(
                    site=site))
            filepath = os.path.join(base_path, C.TEMPLATE_TPL_DIR, theme, *path_elts)
            f = utils.open_if_exists(filepath)
            if f is not None:
                return f, filepath
        return None, None

    def get_source(self, environment, template):
        """Retrieve source handling site and themes

        If the path is absolute it is used directly if in trusted environment
        else and exception is raised.
        if the path is just relative, "default" theme is used.
        @raise PermissionError: absolute path used in untrusted environment
        """
        site, theme, template_path = self.parse_template(template)

        if site is None:
            # we have an abolute template
            if theme is not None:
                raise exceptions.InternalError(u"We can't have a theme with absolute "
                                               u"template.")
            if not self.trusted:
                log.error(_(u"Absolute template used while unsecure is disabled, hack "
                            u"attempt? Template: {template}").format(template=template))
                raise exceptions.PermissionError(u"absolute template is not allowed")
            filepath = template_path
            f = utils.open_if_exists(filepath)
        else:
            # relative path, we have to deal with site and theme
            assert theme and template_path
            path_elts = split_template_path(template_path)
            # if we have non default site, we check it first, else we only check default
            f, filepath = self._get_template_f(site, theme, path_elts)

        if f is None:
            if (site is not None and path_elts[0] == u"error"
                and os.path.splitext(template_path)[1][1:] in HTML_EXT):
                # if an HTML error is requested but doesn't exist, we try again
                # with base error.
                f, filepath = self._get_template_f(
                    site, theme, ("error", "base.html"))
                if f is None:
                    raise exceptions.InternalError(u"error/base.html should exist")
            else:
                raise TemplateNotFound(template)

        try:
            contents = f.read().decode('utf-8')
        finally:
            f.close()

        mtime = os.path.getmtime(filepath)

        def uptodate():
            try:
                return os.path.getmtime(filepath) == mtime
            except OSError:
                return False

        return contents, filepath, uptodate


class Indexer(object):
    """Index global to a page"""

    def __init__(self):
        self._indexes = {}

    def next(self, value):
        if value not in self._indexes:
            self._indexes[value] = 0
            return 0
        self._indexes[value] += 1
        return self._indexes[value]

    def current(self, value):
        return self._indexes.get(value)


class ScriptsHandler(object):
    def __init__(self, renderer, template_data):
        self.renderer = renderer
        self.template_data = template_data
        self.scripts = []  #  we don't use a set because order may be important

    def include(self, library_name, attribute="defer"):
        """Mark that a script need to be imported.

        Must be used before base.html is extended, as <script> are generated there.
        If called several time with the same library, it will be imported once.
        @param library_name(unicode): name of the library to import
        @param loading:
        """
        if attribute not in (u"defer", u"async", u""):
            raise exceptions.DataError(
                _(u'Invalid attribute, please use one of "defer", "async" or ""')
            )
        if not library_name.endswith(u".js"):
            library_name = library_name + u".js"
        if (library_name, attribute) not in self.scripts:
            self.scripts.append((library_name, attribute))
        return u""

    def generate_scripts(self):
        """Generate the <script> elements

        @return (unicode): <scripts> HTML tags
        """
        scripts = []
        tpl = u"<script src={src} {attribute}></script>"
        for library, attribute in self.scripts:
            library_path = self.renderer.getStaticPath(self.template_data, library)
            if library_path is None:
                log.warning(_(u"Can't find {libary} javascript library").format(
                    library=library))
                continue
            path = self.renderer.getFrontURL(library_path)
            scripts.append(tpl.format(src=quoteattr(path), attribute=attribute))
        return safe(u"\n".join(scripts))


class Environment(jinja2.Environment):

    def get_template(self, name, parent=None, globals=None):
        if name[0] not in (u'/', u'('):
            # if name is not an absolute path or a full template name (this happen on
            # extend or import during rendering), we convert it to a full template name.
            # This is needed to handle cache correctly when a base template is overriden.
            # Without that, we could not distinguish something like base/base.html if
            # it's launched from some_site/some_theme or from [default]/default
            name = u"({site}/{theme}){template}".format(
                site=self._template_data.site,
                theme=self._template_data.theme,
                template=name)

        return super(Environment, self).get_template(name, parent, globals)


class Renderer(object):

    def __init__(self, host, front_url_filter=None, trusted=False, private=False):
        """
        @param front_url_filter(callable): filter to retrieve real url of a directory/file
            The callable will get a two arguments:
                - a dict with a "template_data" key containing TemplateData instance of
                  current template. Only site and theme should be necessary.
                - the relative URL of the file to retrieve, relative from theme root
            None to use default filter which return real path on file
            Need to be specified for web rendering, to reflect URL seen by end user
        @param trusted(bool): if True, allow to access absolute path
            Only set to True if environment is safe (e.g. command line tool)
        @param private(bool): if True, also load sites from sites_path_private_dict
        """
        self.host = host
        self.trusted = trusted
        self.sites_paths = {
            u"": os.path.dirname(sat_templates.__file__),
        }
        conf = config.parseMainConf()
        public_sites = config.getConfig(conf, None, u"sites_path_public_dict", {})
        sites_data = [public_sites]
        if private:
            private_sites = config.getConfig(conf, None, u"sites_path_private_dict", {})
            sites_data.append(private_sites)
        for sites in sites_data:
            normalised = {}
            for name, path in sites.iteritems():
                if RE_TPL_RESERVED_CHARS.search(name):
                    log.warning(_(u"Can't add \"{name}\" site, it contains forbidden "
                                  u"characters. Forbidden characters are {forbidden}.")
                                .format(name=name, forbidden=TPL_RESERVED_CHARS))
                    continue
                path = os.path.expanduser(os.path.normpath(path))
                if not path or not path.startswith(u"/"):
                    log.warning(_(u"Can't add \"{name}\" site, it should map to an "
                                  u"absolute path").format(name=name))
                    continue
                normalised[name] = path
            self.sites_paths.update(normalised)

        self.env = Environment(
            loader=TemplateLoader(sites_paths=self.sites_paths, trusted=trusted),
            autoescape=jinja2.select_autoescape(["html", "xhtml", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=["jinja2.ext.i18n"],
        )
        self.env._template_data = None
        self._locale_str = C.DEFAULT_LOCALE
        self._locale = Locale.parse(self._locale_str)
        self.installTranslations()

        # we want to have access to SàT constants in templates
        self.env.globals[u"C"] = C

        # custom filters
        self.env.filters[u"next_gidx"] = self._next_gidx
        self.env.filters[u"cur_gidx"] = self._cur_gidx
        self.env.filters[u"date_fmt"] = self._date_fmt
        self.env.filters[u"xmlui_class"] = self._xmlui_class
        self.env.filters[u"attr_escape"] = self.attr_escape
        self.env.filters[u"item_filter"] = self._item_filter
        self.env.filters[u"adv_format"] = self._adv_format
        self.env.filters[u"dict_ext"] = self._dict_ext
        self.env.filters[u"highlight"] = self.highlight
        self.env.filters[u"front_url"] = (self._front_url if front_url_filter is None
                                         else front_url_filter)
        # custom tests
        self.env.tests[u"in_the_past"] = self._in_the_past
        self.icons_path = os.path.join(host.media_dir, u"fonts/fontello/svg")

        # policies
        self.env.policies[u"ext.i18n.trimmed"] = True

    def getFrontURL(self, template_data, path=None):
        """Give front URL (i.e. URL seen by end-user) of a path

        @param template_data[TemplateData]: data of current template
        @param path(unicode, None): relative path of file to get,
            if set, will remplate template_data.path
        """
        return self.env.filters[u"front_url"]({u"template_data": template_data},
                                path or template_data.path)

    def installTranslations(self):
        # TODO: support multi translation
        #       for now, only translations in sat_templates are handled
        self.translations = {}
        for site_key, site_path in self.sites_paths.iteritems():
            site_prefix = u"[{}] ".format(site_key) if site_key else u''
            i18n_dir = os.path.join(site_path, "i18n")
            for lang_dir in os.listdir(i18n_dir):
                lang_path = os.path.join(i18n_dir, lang_dir)
                if not os.path.isdir(lang_path):
                    continue
                po_path = os.path.join(lang_path, "LC_MESSAGES/sat.mo")
                try:
                    locale = Locale.parse(lang_dir)
                    with open(po_path, "rb") as f:
                        try:
                            translations = self.translations[locale]
                        except KeyError:
                            self.translations[locale] = support.Translations(f, "sat")
                        else:
                            translations.merge(support.Translations(f, "sat"))
                except EnvironmentError:
                    log.error(
                        _(u"Can't find template translation at {path}").format(
                            path=po_path))
                except UnknownLocaleError as e:
                    log.error(_(u"{site}Invalid locale name: {msg}").format(
                        site=site_prefix, msg=e))
                else:
                    log.info(_(u"{site}loaded {lang} templates translations").format(
                        site = site_prefix,
                        lang=lang_dir))

        default_locale = Locale.parse(self._locale_str)
        if default_locale not in self.translations:
            # default locale disable gettext,
            # so we can use None instead of a Translations instance
            self.translations[default_locale] = None

        self.env.install_null_translations(True)
        # we generate a tuple of locales ordered by display name that templates can access
        # through the "locales" variable
        self.locales = tuple(sorted(self.translations.keys(),
                                    key=lambda l: l.language_name.lower()))


    def setLocale(self, locale_str):
        """set current locale

        change current translation locale and self self._locale and self._locale_str
        """
        if locale_str == self._locale_str:
            return
        if locale_str == "en":
            # we default to GB English when it's not specified
            # one of the main reason is to avoid the nonsense U.S. short date format
            locale_str = "en_GB"
        try:
            locale = Locale.parse(locale_str)
        except ValueError as e:
            log.warning(_(u"invalid locale value: {msg}").format(msg=e))
            locale_str = self._locale_str = C.DEFAULT_LOCALE
            locale = Locale.parse(locale_str)

        locale_str = unicode(locale)
        if locale_str != C.DEFAULT_LOCALE:
            try:
                translations = self.translations[locale]
            except KeyError:
                log.warning(_(u"Can't find locale {locale}".format(locale=locale)))
                locale_str = C.DEFAULT_LOCALE
                locale = Locale.parse(self._locale_str)
            else:
                self.env.install_gettext_translations(translations, True)
                log.debug(_(u"Switched to {lang}").format(lang=locale.english_name))

        if locale_str == C.DEFAULT_LOCALE:
            self.env.install_null_translations(True)

        self._locale = locale
        self._locale_str = locale_str

    def getThemeAndRoot(self, template):
        """retrieve theme and root dir of a given tempalte

        @param template(unicode): template to parse
        @return (tuple[unicode, unicode]): theme and absolute path to theme's root dir
        @raise NotFound: requested site has not been found
        """
        # FIXME: check use in jp, and include site
        site, theme, __ = self.env.loader.parse_template(template)
        if site is None:
            # absolute template
            return  u"", os.path.dirname(template)
        try:
            site_root_dir = self.sites_paths[site]
        except KeyError:
            raise exceptions.NotFound
        return theme, os.path.join(site_root_dir, C.TEMPLATE_TPL_DIR, theme)

    def getStaticPath(self, template_data, filename):
        """Retrieve path of a static file if it exists with current theme or default

        File will be looked at <site_root_dir>/<theme_dir>/<static_dir>/filename,
        then <site_root_dir>/<default_theme_dir>/<static_dir>/filename anf finally
        <default_site>/<default_theme_dir>/<static_dir> (i.e. sat_templates).
        In case of absolue URL, base dir of template is used as base. For instance if
        template is an absolute template to "/some/path/template.html", file will be
        checked at "/some/path/<filename>"
        @param template_data(TemplateData): data of current template
        @return (TemplateData, None): built template data instance where .path is
            the relative path to the file, from theme root dir.
            None if not found.
        """
        if template_data.site is None:
            # we have and absolue path
            if (not template_data.theme is None
                or not template_data.path.startswith(u'/')):
                raise exceptions.InternalError(
                    u"invalid template data, was expecting absolute URL")
            static_dir = os.path.dirname(template_data.path)
            file_path = os.path.join(static_dir, filename)
            if os.path.exists(file_path):
                return TemplateData(site=None, theme=None, path=file_path)
            else:
                return None

        sites_and_themes = TemplateLoader.getSitesAndThemes(template_data.site,
                                                            template_data.theme)
        for site, theme in sites_and_themes:
            site_root_dir = self.sites_paths[site]
            relative_path = os.path.join(C.TEMPLATE_STATIC_DIR, filename)
            absolute_path = os.path.join(site_root_dir, C.TEMPLATE_TPL_DIR,
                                         theme, relative_path)
            if os.path.exists(absolute_path):
                return TemplateData(site=site, theme=theme, path=relative_path)

        return None

    def _appendCSSPaths(self, template_data, css_files, css_files_noscript, name_root):
        """Append found css to css_files and css_files_noscript

        @param css_files(list): list to fill of relative path to found css file
        @param css_files_noscript(list): list to fill of relative path to found css file
            with "_noscript" suffix
        """
        name = name_root + u".css"
        css_path = self.getStaticPath(template_data, name)
        if css_path is not None:
            css_files.append(self.getFrontURL(css_path))
            noscript_name = name_root + u"_noscript.css"
            noscript_path = self.getStaticPath(template_data, noscript_name)
            if noscript_path is not None:
                css_files_noscript.append(self.getFrontURL(noscript_path))

    def getCSSFiles(self, template_data):
        """Retrieve CSS files to use according template_data

        For each element of the path, a .css file is looked for in /static, and returned
        if it exists.
        Previous element are kept by replacing '/' with '_'.
        styles_extra.css, styles.css, highlight.css and fonts.css are always used if they
            exist.
        For each found file, if a file with the same name and "_noscript" suffix exists,
        it will be return is second part of resulting tuple.
        For instance, if template_data is (some_site, some_theme, blog/articles.html),
        following files are returned, earch time trying [some_site root] first,
        then default site (i.e. sat_templates) root:
            - some_theme/static/styles.css is returned if it exists
              else default/static/styles.css
            - some_theme/static/blog.css is returned if it exists
              else default/static/blog.css (if it exists too)
            - some_theme/static/blog_articles.css is returned if it exists
              else default/static/blog_articles.css (if it exists too)
        and for each found files, if same file with _noscript suffix exists, it is put
        in noscript list (for instance (some_theme/static/styles_noscript.css)).
        @param template_data(TemplateData): data of the current template
        @return (tuple[list[unicode], list[unicode]]): a tuple with:
            - front URLs of CSS files to use
            - front URLs of CSS files to use when scripts are not enabled
        """
        # TODO: some caching would be nice
        css_files = []
        css_files_noscript = []
        path_elems = template_data.path.split(u'/')
        path_elems[-1] = os.path.splitext(path_elems[-1])[0]

        css_path = self.getStaticPath(template_data, u'fonts.css')
        if css_path is not None:
            css_files.append(self.getFrontURL(css_path))

        for name_root in (u'styles', u'styles_extra', u'highlight'):
            self._appendCSSPaths(template_data, css_files, css_files_noscript, name_root)

        for idx in xrange(len(path_elems)):
            name_root = u"_".join(path_elems[:idx+1])
            self._appendCSSPaths(template_data, css_files, css_files_noscript, name_root)

        return css_files, css_files_noscript

    ## custom filters ##

    @contextfilter
    def _front_url(self, ctx, relative_url):
        """Get front URL (URL seen by end-user) from a relative URL

        This default method return absolute full path
        """
        template_data = ctx[u'template_data']
        if template_data.site is None:
            assert template_data.theme is None
            assert template_data.path.startswith(u"/")
            return os.path.join(os.path.dirname(template_data.path, relative_url))

        site_root_dir = self.sites_paths[template_data.site]
        return os.path.join(site_root_dir, C.TEMPLATE_TPL_DIR, template_data.theme,
                            relative_url)

    @contextfilter
    def _next_gidx(self, ctx, value):
        """Use next current global index as suffix"""
        next_ = ctx["gidx"].next(value)
        return value if next_ == 0 else u"{}_{}".format(value, next_)

    @contextfilter
    def _cur_gidx(self, ctx, value):
        """Use current current global index as suffix"""
        current = ctx["gidx"].current(value)
        return value if not current else u"{}_{}".format(value, current)

    def _date_fmt(self, timestamp, fmt="short", date_only=False, auto_limit=None,
                  auto_old_fmt=None):
        if is_undefined(fmt):
            fmt = u"short"
        try:
            return date_utils.date_fmt(
                timestamp, fmt, date_only, auto_limit, auto_old_fmt,
                locale_str = self._locale_str
            )
        except Exception as e:
            log.warning(_(u"Can't parse date: {msg}").format(msg=e))
            return timestamp

    def attr_escape(self, text):
        """escape a text to a value usable as an attribute

        remove spaces, and put in lower case
        """
        return RE_ATTR_ESCAPE.sub(u"_", text.strip().lower())[:50]

    def _xmlui_class(self, xmlui_item, fields):
        """return classes computed from XMLUI fields name

        will return a string with a series of escaped {name}_{value} separated by spaces.
        @param xmlui_item(xmlui.XMLUIPanel): XMLUI containing the widgets to use
        @param fields(iterable(unicode)): names of the widgets to use
        @return (unicode, None): computer string to use as class attribute value
            None if no field was specified
        """
        classes = []
        for name in fields:
            escaped_name = self.attr_escape(name)
            try:
                for value in xmlui_item.widgets[name].values:
                    classes.append(escaped_name + "_" + self.attr_escape(value))
            except KeyError:
                log.debug(
                    _(u'ignoring field "{name}": it doesn\'t exists').format(name=name)
                )
                continue
        return u" ".join(classes) or None

    @contextfilter
    def _item_filter(self, ctx, item, filters):
        """return item's value, filtered if suitable

        @param item(object): item to filter
            value must have name and value attributes,
            mostly used for XMLUI items
        @param filters(dict[unicode, (callable, dict, None)]): map of name => filter
            if filter is None, return the value unchanged
            if filter is a callable, apply it
            if filter is a dict, it can have following keys:
                - filters: iterable of filters to apply
                - filters_args: kwargs of filters in the same order as filters (use empty
                                dict if needed)
                - template: template to format where {value} is the filtered value
        """
        value = item.value
        filter_ = filters.get(item.name, None)
        if filter_ is None:
            return value
        elif isinstance(filter_, dict):
            filters_args = filter_.get(u"filters_args")
            for idx, f_name in enumerate(filter_.get(u"filters", [])):
                kwargs = filters_args[idx] if filters_args is not None else {}
                filter_func = self.env.filters[f_name]
                try:
                    eval_context_filter = filter_func.evalcontextfilter
                except AttributeError:
                    eval_context_filter = False

                if eval_context_filter:
                    value = filter_func(ctx.eval_ctx, value, **kwargs)
                else:
                    value = filter_func(value, **kwargs)
            template = filter_.get(u"template")
            if template:
                # format will return a string, so we need to check first
                # if the value is safe or not, and re-mark it after formatting
                is_safe = isinstance(value, safe)
                value = template.format(value=value)
                if is_safe:
                    value = safe(value)
            return value

    def _adv_format(self, value, template, **kwargs):
        """Advancer formatter

        like format() method, but take care or special values like None
        @param value(unicode): value to format
        @param template(None, unicode): template to use with format() method.
            It will be formatted using value=value and **kwargs
            None to return value unchanged
        @return (unicode): formatted value
        """
        if template is None:
            return value
        #  jinja use string when no special char is used, so we have to convert to unicode
        return unicode(template).format(value=value, **kwargs)

    def _dict_ext(self, source_dict, extra_dict, key=None):
        """extend source_dict with extra dict and return the result

        @param source_dict(dict): dictionary to extend
        @param extra_dict(dict, None): dictionary to use to extend first one
            None to return source_dict unmodified
        @param key(unicode, None): if specified extra_dict[key] will be used
            if it doesn't exists, a copy of unmodified source_dict is returned
        @return (dict): resulting dictionary
        """
        if extra_dict is None:
            return source_dict
        if key is not None:
            extra_dict = extra_dict.get(key, {})
        ret = source_dict.copy()
        ret.update(extra_dict)
        return ret

    def highlight(self, code, lexer_name=None, lexer_opts=None, html_fmt_opts=None):
        """Do syntax highlighting on code

        Under the hood, pygments is used, check its documentation for options possible
        values.
        @param code(unicode): code or markup to highlight
        @param lexer_name(unicode, None): name of the lexer to use
            None to autodetect it
        @param html_fmt_opts(dict, None): kword arguments to use for HtmlFormatter
        @return (unicode): HTML markup with highlight classes
        """
        if lexer_opts is None:
            lexer_opts = {}
        if html_fmt_opts is None:
            html_fmt_opts = {}
        if lexer_name is None:
            lexer = lexers.guess_lexer(code, **lexer_opts)
        else:
            lexer = lexers.get_lexer_by_name(lexer_name, **lexer_opts)
        formatter = formatters.HtmlFormatter(**html_fmt_opts)
        return safe(pygments.highlight(code, lexer, formatter))

    ## custom tests ##

    def _in_the_past(self, timestamp):
        """check if a date is in the past

        @param timestamp(unicode, int): unix time
        @return (bool): True if date is in the past
        """
        return time.time() > int(timestamp)

    ## template methods ##

    def _icon_defs(self, *names):
        """Define svg icons which will be used in the template.

        Their name is used as id
        """
        svg_elt = etree.Element(
            "svg",
            nsmap={None: "http://www.w3.org/2000/svg"},
            width="0",
            height="0",
            style="display: block",
        )
        defs_elt = etree.SubElement(svg_elt, "defs")
        for name in names:
            path = os.path.join(self.icons_path, name + u".svg")
            icon_svg_elt = etree.parse(path).getroot()
            # we use icon name as id, so we can retrieve them easily
            icon_svg_elt.set("id", name)
            if not icon_svg_elt.tag == "{http://www.w3.org/2000/svg}svg":
                raise exceptions.DataError(u"invalid SVG element")
            defs_elt.append(icon_svg_elt)
        return safe(etree.tostring(svg_elt, encoding="unicode"))

    def _icon_use(self, name, cls=""):
        return safe(u'<svg class="svg-icon{cls}" xmlns="http://www.w3.org/2000/svg" '
                    u'viewBox="0 0 100 100">\n'
                    u'    <use href="#{name}"/>'
                    u'</svg>\n'.format(name=name, cls=(" " + cls) if cls else ""))

    def render(self, template, site=None, theme=None, locale=C.DEFAULT_LOCALE,
               media_path=u"", css_files=None, css_inline=False, **kwargs):
        """Render a template

        @param template(unicode): template to render (e.g. blog/articles.html)
        @param site(unicide): site name
            None or empty string for defaut site (i.e. SàT templates)
        @param theme(unicode): template theme
        @param media_path(unicode): prefix of the SàT media path/URL to use for
            template root. Must end with a u'/'
        @param css_files(list[unicode],None): CSS files to used
            CSS files must be in static dir of the template
            use None for automatic selection of CSS files based on template category
            None is recommended. General static/style.css and theme file name will be
            used.
        @param css_inline(bool): if True, CSS will be embedded in the HTML page
        @param **kwargs: variable to transmit to the template
        """
        if not template:
            raise ValueError(u"template can't be empty")
        if site is not None or theme is not None:
            # user wants to set site and/or theme, so we add it to the template path
            if site is None:
                site = u''
            if theme is None:
                theme = C.TEMPLATE_THEME_DEFAULT
            if template[0] == u"(":
                raise ValueError(
                    u"you can't specify site or theme in template path and in argument "
                    u"at the same time"
                )

            template_data = TemplateData(site, theme, template)
            template = u"({site}/{theme}){template}".format(
                site=site, theme=theme, template=template)
        else:
            template_data = self.env.loader.parse_template(template)

        # we need to save template_data in environment, to load right templates when they
        # are referenced from other templates (e.g. import)
        # FIXME: this trick will not work anymore if we use async templates (it works
        #        here because we know that the rendering will be blocking until we unset
        #        _template_data)
        self.env._template_data = template_data

        template_source = self.env.get_template(template)

        if css_files is None:
            css_files, css_files_noscript = self.getCSSFiles(template_data)

        kwargs["icon_defs"] = self._icon_defs
        kwargs["icon"] = self._icon_use

        if css_inline:
            css_contents = []
            for files, suffix in ((css_files, u""),
                                  (css_files_noscript, u"_noscript")):
                site_root_dir = self.sites_paths[template_data.site]
                for css_file in files:
                    css_file_path = os.path.join(site_root_dir, css_file)
                    with open(css_file_path) as f:
                        css_contents.append(f.read())
                if css_contents:
                    kwargs[u"css_content" + suffix] = u"\n".join(css_contents)

        scripts_handler = ScriptsHandler(self, template_data)
        self.setLocale(locale)

        # XXX: theme used in template arguments is the requested theme, which may differ
        #      from actual theme if the template doesn't exist in the requested theme.
        rendered = template_source.render(
            template_data=template_data,
            media_path=media_path,
            css_files=css_files,
            css_files_noscript=css_files_noscript,
            locale=self._locale,
            locales=self.locales,
            gidx=Indexer(),
            script=scripts_handler,
            **kwargs
        )
        self.env._template_data = None
        return rendered
