# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.maintenance import get_domain, get_protocol
from congo.utils.classes import Message
from congo.utils.i18n import get_url_for_language
from django.contrib.messages.storage.base import Message as DjangoMessage
from django.core.cache import caches, cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.serializers.json import json, DjangoJSONEncoder
from django.template import Library, TemplateSyntaxError, Node
from django.template.base import VariableDoesNotExist
from django.template.defaultfilters import iriencode, stringfilter
from django.utils.http import urlunquote
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, get_language
from random import random


register = Library()

# utils

@register.simple_tag(takes_context = True)
def domain(context, **kwargs):
    """
    Tag zwraca adres domeny zależnie od podanego kontekstu.
    
    {% domain %} zwraca: http://www.example.com/
    {% domain ssl=True %} zwraca: https://www.example.com/
    {% domain prepend_protocol=False append_slash=False %} zwraca: www.example.com 
    """

    # request
    request = context.get('request')

    # ssl: False, True
    ssl = bool(kwargs.get('ssl', None))

    # prepend_protocol: False, True
    prepend_protocol = bool(kwargs.get('prepend_protocol', True))

    # append_slash: False, True
    append_slash = bool(kwargs.get('append_slash', True))

    parts = []

    if prepend_protocol:
        if ssl is None:
            parts.append(get_protocol(request, "http://"))
        else:
            parts.append("https://" if ssl else "http://")

    d = get_domain(request)
    if not d:
        d = settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) else 'www.example.com'
    parts.append(d)

    if append_slash:
        parts.append('/')

    return ''.join(parts)

@register.simple_tag(takes_context = True)
def lang_url(context, language, url_or_obj = None, *args, **kwargs):
    """
    Tag zwraca adres aktualnego adresu w innym języku.
    
    {% lang_url "en" %} zwraca adres do wersji angielskiej,
    {% lang_url "en" "home" %} zwraca url "home" w wersji angielskiej,
    {% lang_url "en" "user_details" request.user.id %} zwraca url "user_details" z argumentem request.user.id w wersji angielskiej,
    {% lang_url "en" obj %} zwraca obj.get_absolute_url() w wersji angielskiej,
    
    \*args i \*\*kwargs są przekazywane do funkcji reverse gdy podano nazwę url'a. 
    """

    request = context.get('request')

    if url_or_obj is None:
        url_or_obj = request.get_full_path()

    return get_url_for_language(language, url_or_obj, url_args = args, url_kwargs = kwargs)

# utils

@register.simple_tag
def iff(a, b, c = None):
    """
    .. code-block:: python
    
        if c:
            return b if a else c
            
        return a if a else b
    """
    if c:
        return b if a else c
    return a if a else b

@register.filter(is_safe = True)
def or_blank(value, use_html = True):
    if value:
        return value
    else:
        text = _("(Brak)")
        html = """<span class="text-muted">%s</span>""" % text
        blank = html if bool(use_html) else text
        return mark_safe(blank)

# string

@register.filter
@stringfilter
def urldecode(url):
    return urlunquote(url)

@register.filter
@stringfilter
def url_protocole(url, protocole = None):
    """
    Tag zmienia protokuł url'a lub go usuwa.
    """

    if protocole or protocole == False:
        url = url.replace('http://', '').replace('https://', '')
    if protocole:
        return "%s%s" % (protocole, url)
    return url

@register.filter
@stringfilter
def form_iriencode(url):
    return iriencode(url).replace("%20", "+")

@register.filter
@stringfilter
def remove(value, arg):
    """
    Tag usuwa podaną frazę ze stringa.
    {% remove "To jest test" "es" %} zwróci "To jt tt"
    """

    try:
        return value.replace(arg, "")
    except AttributeError:
        return value

@register.filter
@stringfilter
def reverse(value):
    """
    Tag odwraca podaną uporządkowaną strukturę (np. tablicę lub string).
    """

    return value[::-1]

@register.filter
@stringfilter
def strip(value):
    """
    Tag usuwa z początku oraz końca stringa białe znaki.
    """
    return value.strip()

@register.filter
@stringfilter
def endswith(value, arg):
    """
    Tag zwraca true lub false zależnie od tego, czy value kończy się na podanym arg.
    """

    return value.endswith(arg)

@register.filter
@stringfilter
def startswith(value, arg):
    """
    Tag zwraca true lub false zależnie od tego, czy value zaczyna się na podanym arg.
    """
    return value.startswith(arg)

@register.filter
@stringfilter
def str_to_list(value, arg, delimiter = ","):
    # @BZ -> @OG słaba nazwa co nie?
    """
    Tak splituje podany string (arg) po delimiterze i zwraca obiekt o indeksie value.
    """

    return arg.split(delimiter)[value]

@register.filter
def to_json(value):
    """
    Tag zwraca podaną strukturę jako json.
    """
    return json.dumps(value, cls = DjangoJSONEncoder)

# numeric

@register.filter
def occurrences(value, arg):
    """
    Tag zwraca ilość wystąpień podanego arg'a w value.
    """

    try:
        return value.count(arg)
    except AttributeError:
        return 0

@register.filter
def add(value, arg):
    return value + arg

@register.filter
def times(value, arg):
    return value * arg

@register.filter
def mod(value, arg):
    return value % arg

# range

@register.filter('range')
def make_range(value, start_from_0 = True):
    """
    Tag zwraca range o długości value.
    """

    try:
        i = int(value)

        if start_from_0:
            return range(i)
        else:
            return range(1, i + 1)
    except ValueError:
        return value

# Messages

@register.simple_tag
def message(msg, **kwargs):
    # dismiss (bool, False)
    # close (bool, False)

    if not msg:
        return ""
    elif isinstance(msg, Message) or isinstance(msg, DjangoMessage):
        obj = msg
    else:
        level = kwargs.get('level', None)
        if level not in list(Message.DEFAULT_TAGS.values()):
            level = 'info'
        obj = getattr(Message, level)(msg)
    return Message.render(obj, **kwargs)

@register.tag
def blockmessage(parser, token):
    node_list = parser.parse(('endblockmessage',))
    parser.delete_first_token()
    tokens = token.split_contents()

    if len(tokens) == 1:
        level = "info"
        extra_tags = ''
    elif len(tokens) == 2:
        level = tokens[1]
        extra_tags = ''
    elif len(tokens) == 3:
        level, extra_tags = tokens[1:]
    else:
        raise TemplateSyntaxError("'blockmessage' tag accepts max 2 arguments.")

    return BlockMessageNode(node_list, level[1:-1], extra_tags[1:-1])

class BlockMessageNode(Node):
    def __init__(self, node_list, level, extra_tags = ''):
        self.node_list = node_list
        self.level = level
        self.extra_tags = extra_tags

    def render(self, context):
        level = self.level
        if level not in list(Message.DEFAULT_TAGS.values()):
            level = 'info'
        extra_tags = self.extra_tags
        obj = getattr(Message, level)(self.node_list.render(context))
        return Message.render(obj, extra_tags = extra_tags)

# var & blockvar

@register.simple_tag
def var(obj):
    """
    Tag zwraca obj, pozwalająć go zaliasować
    {% var 123 as x %}
    """
    return obj

@register.tag
def blockvar(parser, token):
    """
    Tag przechowuje swoją zawartość którą można potem zwrócić jak zwykłą zmienną.
    
    {% blockvar "var_name" %}...jakaś zawartość...{% endblockvar %}
    a potem: {{ var_name }}
    """
    # https://djangosnippets.org/snippets/545/
    try:
        tag_name, var_name = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError("'var' node requires a variable name.")
    node_list = parser.parse(('endblockvar',))
    parser.delete_first_token()
    return VarNode(node_list, var_name[1:-1])

class VarNode(Node):
    def __init__(self, node_list, var_name):
        self.node_list = node_list
        self.var_name = var_name

    def render(self, context):
        output = self.node_list.render(context)
        context[self.var_name] = output
        return ""

# cache

@register.tag('cache')
def do_cache(parser, token):
    """
    Tag zcashuje zawartość templaty na pewien czas.

    Użycie::
    
        {% cache "cache_key" [expire_time] %}
            .. drogie przemyślenia ..
        {% endcache %}
    
    Tag wspiera również podawanie argumentów::

        {% cache "cache_key" [expire_time] [var1] [var2] .. %}
            .. drogie przymyślenia ..
        {% endcache %}

    Można również podać backend za którego pomocą chcemy scashować zawartość::

        {% cache ....  using="cache_backend" %}

    Każdy unikatowy zbiór argumentów stworzy oddzielny wpis do cashu.
    """

    node_list = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.split_contents()

    expire_time = ""
    vary_on = []
    cache_backend = None

    if len(tokens) == 2:
        cache_key = tokens[1]

    elif len(tokens) > 2:
        cache_key, expire_time = tokens[1:3]

        if len(tokens) > 3 and tokens[-1].startswith('using='):
            cache_backend = parser.compile_filter(tokens[-1][len('using='):])
            tokens = tokens[:-1]

        vary_on = tokens[3:]

    else:
        raise TemplateSyntaxError('"cache" tag requires at least 1 argument.')

    return CacheNode(
        node_list,
        parser.compile_filter(cache_key),
        parser.compile_filter(expire_time),
        [parser.compile_filter(var) for var in vary_on],
        cache_backend
    )

class CacheNode(Node):
    def __init__(self, node_list, cache_key, expire_time, vary_on, cache_backend):
        self.node_list = node_list
        self.cache_key = cache_key
        self.expire_time = expire_time
        self.vary_on = vary_on
        self.cache_backend = cache_backend

    def get_cache_key(self, context):
        cache_key_parts = ['tmpl', self.cache_key.resolve(context)]
        cache_key_parts += [var.resolve(context) for var in self.vary_on]

        if settings.CONGO_TEMPLATE_CACHE_KEY_APPEND_LANGUAGE:
            cache_key_parts.append(get_language())

        return ':'.join([str(part) for part in cache_key_parts])

    def render(self, context):
        # expire_time

        try:
            expire_time = self.expire_time.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.expire_time.var)

        try:
            expire_time = 0 if expire_time is None else int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError('"cache" tag got a non-integer timeout value: %r' % expire_time)

        # cache_backend & cache_backend

        if self.cache_backend:
            try:
                cache_backend = self.cache_backend.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.cache_backend.var)
        else:
            cache_backend = settings.CONGO_TEMPLATE_CACHE_BACKEND

        try:
            cache = caches[cache_backend]
        except InvalidCacheBackendError:
            raise TemplateSyntaxError('Invalid cache name specified for cache tag: %r' % cache_backend)

        # do cache

        # @og debug

#        print("")
#        print("cache_key", self.cache_key)
#        print("expire_time", expire_time)
#        print("vary_on", self.vary_on)
#        print("cache_backend", cache_backend)
#        print("cache", cache)
#        print("get_cache_key()", self.get_cache_key(context))
#        print("")

        value = cache.get(self.get_cache_key(context))
        if value is None:
            value = self.node_list.render(context)

            if expire_time is None:
                # jeśli nie podano czasu, ustawiamy cache na domyślny -15% / +15%
                expire_time = settings.CACHES[cache_backend].get('TIMEOUT', 0)
                expire_time = int(expire_time * (.85 + random() * .3))

            if expire_time:
                cache.set(self.get_cache_key(context), value, expire_time)
            else:
                cache.set(self.get_cache_key(context), value)

        return value
