import time
import json
from http.cookiejar import Cookie, LWPCookieJar
from http.cookies import Morsel, SimpleCookie

from aninja.utils import format_expires, filter_attrs, expires_to_number, expires_to_str
from requests.cookies import RequestsCookieJar


# Typing
_Page = 'Page'
_Cookie = 'Cookie'
_Path = str
_CookieJar = 'CookieJar'


class NinjaCookieJar(LWPCookieJar, RequestsCookieJar):
    """:class:`requests.cookies.RequestsCookieJar` compatible
    :class:`cookielib.LWPCookieJar`"""
    pass


class CookiesManager:
    """Extended storage and manager for cookies.

    Synchronize information between different types of cookies. Also
    save and load cookies with files.
    """

    def __init__(self) -> None:
        self._jar = NinjaCookieJar()

    def load(self, filename, ):
        """Load cookies from the file :attr:`.API.cookies_filename`"""
        self._jar.load(filename, ignore_discard=True, ignore_expires=True)

    def save(self, filename, ):
        """Save cookies to the file"""
        self._jar.save(filename, ignore_discard=True, ignore_expires=True)

    def update(self, other):
        """updates with cookies from another CookieJar or dict-like, same as RequestsCookieJar"""
        self._jar.update(other)

    def update_from_aiohttp_session(self, session) -> None:
        for morsel in session.cookie_jar:
            self._jar.set_cookie(morsel_to_cookie(morsel))

    async def update_from_pyppeteer(self, page: _Page) -> None:
        cookies_list = await page.cookies()
        for cookie_dict in cookies_list:
            f = filter_attrs(time_format='number', **cookie_dict)
            name = f.pop('name')
            value = f.pop('value')
            cookie = create_cookie(name, value, **f)
            self._jar.set_cookie(cookie)

    def update_from_simplecookie(self, simplecookie):
        for morsel in simplecookie.values():
            self._jar.set_cookie(morsel_to_cookie(morsel))

    def sync_to_aiohttp_session(self, session) -> None:
        session.cookie_jar.update_cookies(self.output_simplecookie())

    def sync_to_cookiejar(self, cookiejar: _CookieJar) -> None:
        cookiejar.update(self._jar)

    async def sync_to_pyppeteer(self, page: _Page) -> None:
        if len(self):
            for cookie_dict in self.output_detailed():
                await page.setCookie(cookie_dict)

    def output_header_string(self, domain=None, path=None) -> str:
        return '; '.join(
            [k+'='+v
             for k, v in self.output_dict(domain, path).items()]
        )

    def output_js(self, domain=None, path=None) -> str:
        return self.output_simplecookie(domain, path).js_output()

    def output_dict(self, domain=None, path=None) -> dict:
        """returns a plain old Python dict of name-value pairs of cookies.
        """
        return self._jar.get_dict(domain, path)

    def output_json(self, domain=None, path=None) -> str:
        return json.dumps(self.output_detailed(domain, path))

    def output_detailed(self, domain=None, path=None) -> list:
        """returnes a list of dictionaries which contain name, value and other
        attributes for cookie.
        """
        rlist = []
        for cookie in iter(self._jar):
            if ((domain is None or cookie.domain == domain) and
                    (path is None or cookie.path == path)):
                dictionary = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                }
                if cookie.expires:
                    dictionary['expires'] = cookie.expires
                rlist.append(dictionary)
        return rlist

    def output_simplecookie(self, domain=None, path=None):
        C = SimpleCookie()
        for cookie in iter(self._jar):
            if ((domain is None or cookie.domain == domain) and
                    (path is None or cookie.path == path)):
                C[cookie.name] = cookie_to_morsel(cookie)
        return C

    def output_cookiejar(self):
        return self._jar

    def set(self, name, value, **kwargs):
        return self._jar.set(name, value, **kwargs)

    def set_cookie(self, cookie, *args, **kwargs):
        return self._jar.set_cookie(cookie, *args, **kwargs)

    def copy(self) -> 'CookiesManager':
        m = CookiesManager()
        m.update(self._jar)
        return m

    def __len__(self):
        return len(self._jar.values())

    def __str__(self):
        return str(self._jar)

    __repr__ = __str__


def morsel_to_cookie(morsel):
    """Convert a Morsel object into a Cookie containing the one k/v pair.
    Original from `requests.cookies.morsel_to_cookie`
    """

    expires = None
    if morsel['max-age']:
        try:
            expires = int(time.time() + int(morsel['max-age']))
        except ValueError:
            raise TypeError('max-age: %s must be integer' % morsel['max-age'])
    elif morsel['expires']:
        expires = expires_to_number(morsel['expires'])
    return create_cookie(
        comment=morsel['comment'],
        comment_url=bool(morsel['comment']),
        discard=False,
        domain=morsel['domain'],
        expires=expires,
        name=morsel.key,
        path=morsel['path'],
        port=None,
        rest={'HttpOnly': morsel['httponly']},
        rfc2109=False,
        secure=bool(morsel['secure']),
        value=morsel.value,
        version=morsel['version'] or 0,
    )


def cookie_to_morsel(cookie):
    """Convert a Cookie object into a Morsel"""
    info = {}
    attrs = ('version', 'domain', 'path', 'expires',
             'secure', 'comment')

    for attr in attrs:
        if attr == 'expires':
            expires = getattr(cookie, attr)
            if expires:
                info[attr] = expires_to_str(expires)
            else:
                pass
        else:
            value = getattr(cookie, attr)
            if value:
                info[attr] = value
    return create_morsel(cookie.name, cookie.value, **info)


def create_morsel(key, value, **kwargs):
    """Make a Morsel from underspecified parameters.
    """
    morsel = Morsel()
    morsel.set(key, value, str(value))
    result = {
        'version': '',
        'domain': '',
        'path': '/',
        'secure': '',
        'expires': '',
        'comment': '',
        'httponly': ''
    }

    badargs = set(kwargs) - set(result)
    if badargs:
        err = 'create_cookie() got unexpected keyword arguments: %s'
        raise TypeError(err % list(badargs))

    morsel.update(kwargs)

    return morsel


def create_cookie(name, value, **kwargs):
    """Make a cookie from underspecified parameters.

    """
    result = {
        'version': 0,
        'name': name,
        'value': value,
        'port': None,
        'domain': '',
        'path': '/',
        'secure': False,
        'expires': None,
        'discard': False,
        'comment': None,
        'comment_url': None,
        'rest': {'HttpOnly': None},
        'rfc2109': False,
    }

    badargs = set(kwargs) - set(result)
    if badargs:
        err = 'create_cookie() got unexpected keyword arguments: %s'
        raise TypeError(err % list(badargs))

    result.update(kwargs)
    result['port_specified'] = bool(result['port'])
    result['domain_specified'] = bool(result['domain'])
    result['domain_initial_dot'] = result['domain'].startswith('.')
    result['path_specified'] = bool(result['path'])

    return Cookie(**result)
