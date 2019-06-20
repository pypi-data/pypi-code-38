from hashlib import md5
from .caching import cache
from . import settings, utils
import os


if os.getenv('DJANGO_SETTINGS_MODULE'):
    from django.utils.html import escape
else:
    try:
        from markupsafe import escape
    except ImportError:  # pragma: no cover
        raise Exception(
            'Cannot find escape function in django.utils.html or markupsafe'
        )


class NotFoundError(Exception):
    pass


class CachedObject(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(
                    '__init__() got an unexpected keyword argument \'%s\'' % (
                        key
                    )
                )

            setattr(self, key, value)

    @property
    def _cachekey(self):
        return '%s%s' % (
            settings.CACHE_PREFIX,
            md5(str(self.id).encode('utf-8')).hexdigest()
        )

    @classmethod
    def load(cls, id):
        cachekey = '%s%s' % (
            settings.CACHE_PREFIX,
            md5(str(id).encode('utf-8')).hexdigest()
        )

        if cachekey in cache:
            obj = cache.get(cachekey)
            if 'id' in obj:
                del obj['id']

            return cls(**obj)

        raise NotFoundError(
            'Object not found with ID %s' % id
        )

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj

    def save(self):
        cache.set(
            self._cachekey,
            self.to_dict(),
            settings.CACHE_TIMEOUT
        )

    def to_dict(self):
        return {
            'id': self.id
        }


class Resource(CachedObject):
    url = ''
    width = 0
    html = ''
    title = ''
    thumbnail = ''

    def to_dict(self):
        d = super().to_dict()
        d.update(
            {
                'url': self.url,
                'width': self.width,
                'html': self.html,
                'title': self.title,
                'thumbnail': self.thumbnail
            }
        )

        return d

    def __str__(self):  # pragma: no cover
        return self.url

    @property
    def id(self):
        return str(self.url)

    @classmethod
    def load(cls, url):
        try:
            return super().load(url)
        except NotFoundError:
            return cls.create(url)

    @classmethod
    def create(cls, url, width=settings.WIDTH):
        endpoint, fmt = utils.get_oembed_endpoint(url)

        if endpoint and fmt:
            html, title, thumbnail = utils.get_oembed_content(
                url,
                endpoint,
                fmt,
                width
            )
        else:
            html, title, thumbnail = utils.guess_oembed_content(url, width)
            html = utils.sandbox_iframe(html)

        return super().create(
            url=url,
            width=width,
            html=html,
            title=title,
            thumbnail=thumbnail
        )

    def to_html(self, link=False, thumbnail=False):
        if thumbnail and self.thumbnail:
            body = '<img src="%s">' % escape(self.thumbnail)
        else:
            body = self.title and escape(self.title) or escape(self.url)

        prefix, suffix = '', ''

        if link:
            prefix = '<a href="%s" target="_blank" rel="noopener noreferrer" title="%s">' % (
                escape(self.url),
                self.title and escape(self.title) or '',
            )

            suffix = '</a>'

        if link or thumbnail:
            return prefix + body + suffix

        return self.html
