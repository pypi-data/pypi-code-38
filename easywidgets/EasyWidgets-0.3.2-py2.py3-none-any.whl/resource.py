from __future__ import with_statement
from __future__ import absolute_import
from __future__ import unicode_literals
import logging
import os.path
from itertools import groupby
from collections import defaultdict
from six.moves.urllib.parse import urlencode
from io import open

import pkg_resources
from markupsafe import Markup as literal

from .widget import Widget
from .utils import LazyProperty
from .core import widget_context
import six

log = logging.getLogger(__name__)

class ResourceManager(object):
    location = [ 'head_css', 'head_js',
                 'body_top_js', 'body_js', 'body_js_tail' ]
    block_size = 4096
    paths = []
    kwargs = {}
    resource_cache = {}

    def __init__(
        self,
        script_name='/_ew_resources/',
        compress=False,
        url_base=None,
        cache_max_age=60*60*24*365,
        use_cache=True,
        use_jsmin=False,
        use_cssmin=False):
        self.resources = defaultdict(list)
        self.script_name = script_name
        self.compress = compress
        if url_base is None:
            url_base = self.script_name
        self._url_base = url_base
        self.cache_max_age=cache_max_age
        self.use_cache = use_cache
        self.use_jsmin=use_jsmin
        self.use_cssmin=use_cssmin

    @classmethod
    def configure(cls, **kw):
        cls.kwargs = kw

    @classmethod
    def register_directory(cls, url_path, directory):
        for up,dir in cls.paths:
            if up == url_path:
                assert dir == directory, 'Attempt to reregister %s: %s=>%s' % (
                    url_path, dir, directory)
                return
        cls.paths.append((url_path, directory))

    @classmethod
    def register_all_resources(cls):
        for ep in pkg_resources.iter_entry_points('easy_widgets.resources'):
            log.info('Loading ep %s', ep)
            ep.load()(cls)

    @property
    def url_base(self):
        base = self._url_base
        if base.startswith(':'):
            base = widget_context.scheme + base
        return base

    def absurl(self, href):
        if '://' not in href and not href.startswith('/'):
            return self.url_base + href
        return href

    def emit(self, location):
        def squash_dupes(it):
            seen = set()
            for r in it:
                if r.squash and r in seen: continue
                yield r
                seen.add(r)
        def compress(it):
            for (cls, compress), rs in groupby(it, key=lambda r:(type(r), r.compress)):
                if not compress:
                    for r in rs: yield r
                else:
                    for cr in cls.compressed(self, rs):
                        yield cr
        resources = self.resources[location]
        resources = squash_dupes(resources)
        if self.compress:
            resources = compress(resources)
        yield literal('<!-- ew:%s -->\n' % location)
        for r in resources:
            yield r.display()
        yield literal('\n<!-- /ew:%s -->\n' % location)

    def register_widgets(self, context):
        '''Registers all the widget/resource-type objects that exist as attrs on
        context'''
        for name in dir(context):
            w = getattr(context, name)
            if isinstance(w, (Widget, Resource)):
                log.disabled = 0
                self.register(w)

    def register(self, resource):
        '''Registers the required resources for the given resource/widget'''
        if isinstance(resource, Resource):
            assert resource.location in self.location, \
                'Resource.location must be one of %r' % self.location
            self.resources[resource.location].append(resource)
            # print 'Register %s as %dth resource in %s' % (
            #     resource, len(self.resources[resource.location]), resource.location)
            resource.manager = self
        elif isinstance(resource, Widget):
            for r in resource.resources():
                self.register(r)
        else: # pragma no cover
            raise AssertionError('Unknown resource type %r' % resource)

    def get_filename(self, res_path):
        '''Translate a resource path to a filename'''
        for url_path, directory in self.paths:
            if res_path.startswith(url_path):
                fs_path = os.path.abspath(os.path.join(
                    directory,
                    res_path[len(url_path)+1:]))
                # Do not allow 'breaking out' of the subdirectory using ../../.., etc
                if not fs_path.startswith(os.path.abspath(directory)):
                    return None
                return fs_path
        return None

    def serve_slim(self, file_type, href):
        '''Serve a 'slim' version of a file (concat+minify, if possible)'''
        try:
            return self.resource_cache[href]
        except KeyError:
            pass
        def get_plain(h):
            fn = self.get_filename(h)
            return open(fn, encoding='utf-8').read()
        def get_min_js(h):
            if '.min.' in h:
                result = get_plain(h)
            else:
                try:
                    min_fn = h.rsplit('.', 1)[0] + '.min.js'
                    return get_plain(min_fn)
                except IOError:
                    text = get_plain(h)
                    result = jsmin.jsmin(text)
            prelude = '\n/* %s */\n' % h
            return prelude + result
        def get_min_css(h):
            if '.min.' in h:
                result = get_plain(h)
            else:
                try:
                    min_fn = h.rsplit('.', 1)[0] + '.min.css'
                    return get_plain(min_fn)
                except IOError:
                    text = get_plain(h)
                    result = cssmin.cssmin(text)
            prelude = '\n/* %s */\n' % h
            return prelude + result
        getter = get_plain
        if file_type == 'js' and self.use_jsmin:
            try:
                import jsmin
                getter = get_min_js
            except ImportError: # pragma no cover
                pass
        if file_type == 'css' and self.use_cssmin:
            try:
                import cssmin
                getter = get_min_css
            except ImportError: # pragma no cover
                pass
        joiner = ';\n' if file_type == 'js' else '\n'
        content = joiner.join(getter(h) for h in href.split(';') )
        if self.use_cache:
            self.resource_cache[href] = content
        return content
    
    def __repr__(self):  # pragma no cover
        l = ['<ResourceManager>']
        for name, res in six.iteritems(self.resources):
            l.append('  <Location %s>' % name)
            for r in res: l.append('    %r' % r)
        for u,d in self.paths:
            l.append('  <Path url="%s" directory="%s">' % (u, d))
        return '\n'.join(l)

class ResourceHolder(Widget):
    '''Simple widget that does nothing but hold resources'''

    def __init__(self, *resources):
        self._resources = resources

    def resources(self):
        return self._resources

class Resource(object):

    def __init__(self, location, squash=True, compress=True):
        self.location = location
        self.squash = squash
        self.compress = compress
        self.manager = None
        self.widget = None

    def display(self):
        return self.widget.display()

    @classmethod
    def compressed(cls, manager, resources):
        return resources
    
class ResourceLink(Resource):
    file_type=None

    def __init__(self, url, location, squash, compress):
        self._url = url
        super(ResourceLink, self).__init__(location, squash, compress)

    def url(self):
        return self.manager.absurl(self._url)

    def __repr__(self): # pragma no cover
        return '<%s %s>' % (self.__class__.__name__, self._url)

    def __hash__(self):
        return hash(self.location) + hash(self._url) + hash(self.squash)

    def __eq__(self, o):
        return (self.__class__ == o.__class__
                and self._url == o._url
                and self.location == o.location
                and self.squash == o.squash)

    @classmethod
    def compressed(cls, manager, resources):
        rel_hrefs = [ r.url()[len(manager.url_base):]
                      for r in resources ]
        query = urlencode([('href', ';'.join(rel_hrefs))])
        result = cls('%s_slim/%s?%s' % (
                manager.url_base,
                cls.file_type,
                query))
        result.manager = manager
        yield result

class JSLink(ResourceLink):
    file_type='js'
    WidgetClass=None
    def __init__(self, url, location='body_js', squash=True, compress=True):
        super(JSLink, self).__init__(url, location, squash, compress)
        del self.widget

    @LazyProperty
    def widget(self):
        return self.WidgetClass(href=self.url())

class CSSLink(ResourceLink):
    file_type='css'
    WidgetClass=None

    def __init__(self, url, squash=True, compress=True, **attrs):
        super(CSSLink, self).__init__(url, 'head_css', squash, compress)
        self.attrs = attrs
        del self.widget

    @LazyProperty
    def widget(self):
        return self.WidgetClass(href=self.url(), attrs=self.attrs)

class ResourceScript(Resource):
    file_type=None

    def __init__(self, text, location, squash, compress):
        self.text = text
        super(ResourceScript, self).__init__(location, squash, compress)

    def __hash__(self):
        return (hash(self.text)
                + hash(self.location)
                + hash(self.squash)
                + hash(self.compress))

    def __eq__(self, o):
        return (self.__class__ == o.__class__
                and self.text == o.text
                and self.location == o.location
                and self.squash == o.squash
                and self.compress == o.compress)

    @classmethod
    def compressed(cls, manager, resources):
        text = '\n'.join(r.text for r in resources)
        yield cls(text)

class JSScript(ResourceScript):
    file_type='js'
    WidgetClass=None

    def __init__(self, text, location='body_js_tail', squash=True, compress=True):
        super(JSScript, self).__init__(text, location, squash, compress)
        del self.widget

    @LazyProperty
    def widget(self):
        return self.WidgetClass(text=self.text)

class CSSScript(ResourceScript):
    file_type='css'
    WidgetClass=None

    def __init__(self, text):
        super(CSSScript, self).__init__(text, 'head_css', True, True)
        del self.widget

    @LazyProperty
    def widget(self):
        return self.WidgetClass(text=self.text)

class GoogleAnalytics(Resource):
    WidgetClass=None
    
    def __init__(self, account):
        self.account = account
        super(GoogleAnalytics, self).__init__('head_js', True)
        del self.widget

    @LazyProperty
    def widget(self):
        return self.WidgetClass(account=self.account)
