import re
from collections import namedtuple
import math


class BaseAction(object):

    def __init__(self, name=None, fields=None, filter=None, breaker=None, parser=None, static=False, refresh=False, referer=None):
        self.name = name
        self.fields = fields
        self.filter = filter
        self.breaker = breaker
        self.parser = parser
        self.static = static
        self.refresh = refresh
        self.referer = referer


class Root(BaseAction):
    def __init__(self, url, payloader=None, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name or url
        self.url = url
        self.payloader = payloader


class Url(BaseAction):
    def __init__(self, url, generator=None, previewer=None, payloader=None, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.name = self.name or url
        self.previewer = previewer
        self.generator = generator
        self.payloader = payloader


class RegexUrl(BaseAction):
    def __init__(self, regex, recursive=False, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name or regex
        self.regex = re.compile(regex)
        self.recursive = recursive


def root(url, fields=None, name=None, filter=None, breaker=None, parser=None, refresh=False, relay=True, referer=None, payloader=None):
    return Root(
        url,
        name=name,
        fields=fields,
        filter=filter,
        breaker=None,
        parser=parser,
        refresh=refresh,
        static=not relay,
        referer=referer,
        payloader=payloader
    )


def url(url, generator=None, previewer=None, fields=None, name=None, filter=None, breaker=None, parser=None, refresh=False, relay=True, referer=None, payloader=None):
    return Url(
        url,
        generator=generator,
        previewer=previewer,
        name=name,
        fields=fields,
        filter=filter,
        breaker=breaker,
        parser=parser,
        refresh=refresh,
        static=not relay,
        referer=referer,
        payloader=payloader,
    )


def urlpattern(regx, fields=None, name=None, filter=None, breaker=None, parser=None, recursive=False, refresh=False, relay=True, referer=None):
    return RegexUrl(
        regx,
        name=name,
        fields=fields,
        filter=filter,
        breaker=breaker,
        parser=parser,
        recursive=recursive,
        refresh=refresh,
        static=not relay,
        referer=referer,
    )
