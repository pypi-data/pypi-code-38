from hashlib import md5
from logging import getLogger
from opengraph import OpenGraph
from requests.exceptions import RequestException
from urllib.parse import urljoin, urlparse, parse_qs
from xml.etree import ElementTree as ET
from . import settings, get_version
import json
import os
import random
import re
import requests
import string


if os.getenv('DJANGO_SETTINGS_MODULE'):
    from django.utils.html import escape
else:
    try:
        from markupsafe import escape
    except ImportError:  # pragma: no cover
        raise Exception(
            'Cannot find escape function in django.utils.html or markupsafe'
        )


def get_user_agent(human=False):
    if not human:
        return 'podiant-oembed/%s' % get_version()

    return (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/39.0.2171.95 Safari/537.36'
    )


def get_oembed_endpoint(url):
    logger = getLogger('oembed')

    for (patterns, endpoint, fmt) in settings.URL_PATTERNS:
        if not isinstance(patterns, (list, tuple)):
            patterns = [patterns]

        for pattern in [
            re.compile(
                p.replace(
                    '.', '\\.'
                ).replace(
                    '*', '.*'
                ).replace(
                    '?', '\\?'
                ),
                re.IGNORECASE
            ) for p in patterns
        ]:
            if pattern.match(url) is not None:
                logger.debug('Found %s endpoint for resource' % fmt.upper())
                return endpoint, fmt

    return None, None


def get_oembed_response(url, endpoint, fmt, width=settings.WIDTH):
    logger = getLogger('oembed')

    if fmt == 'json':
        mimetype = 'application/json'
    elif fmt == 'xml':
        mimetype = 'text/xml'
    elif fmt != 'html':  # pragma: no cover
        raise Exception(
            'Handler configured incorrectly (unrecognised format %s)' % fmt
        )

    params = {
        'url': url
    }

    if int(width) > 0:
        params['width'] = width
        params['maxwidth'] = width

    logger.debug(
        'Getting %s resource from %s' % (
            fmt.upper(),
            urlparse(endpoint).netloc
        )
    )

    oembed_response = requests.get(
        endpoint,
        params=params,
        headers={
            'Accept': mimetype,
            'User-Agent': get_user_agent()
        }
    )

    if oembed_response.status_code == 204:
        raise Exception('Content has gone')

    if oembed_response.status_code >= 200:
        if oembed_response.status_code < 400:
            return oembed_response.content.decode('utf-8')

    oembed_response.raise_for_status()  # pragma: no cover


def parse_oembed_response(response, fmt):
    if fmt == 'html':
        return response, None, None

    if fmt == 'json':
        data = json.loads(response)

        if 'html' in data:
            return (
                data.get('html'),
                data.get('title'),
                data.get('thumbnail_url')
            )

        raise Exception(
            'Response not understood',
            data
        )  # pragma: no cover

    xml = ET.fromstring(response)
    return (
        xml.find('html').text or '',
        xml.find('title').text or '',
        xml.find('thumbnail_url').text or ''
    )


def get_oembed_content(url, endpoint, fmt, width=None):
    logger = getLogger('oembed')

    try:
        response = get_oembed_response(url, endpoint, fmt, width)
    except Exception:
        logger.warning('Error getting content', exc_info=True)
        return None, None, None

    return parse_oembed_response(response, fmt)


def guess_oembed_content(url, width, inline_images=True):
    logger = getLogger('oembed')

    try:
        headers = requests.head(url).headers
    except RequestException:
        logger.warning('Connection error discovering resource', exc_info=True)
        return None, None, None

    if headers.get('Content-Type'):
        if headers['Content-Type'].startswith('image/'):
            return (
                '<a href="%s" class="thumbnail" target="_blank" rel="noopener noreferrer">%s</a>' % (
                    escape(url),
                    (
                        '<img class="embedded-image" src="%s" '
                        'style="max-width: 100%%;">'
                    ) % escape(url)
                ),
                '',
                url
            )

    accept = (
        'text/html,'
        'application/xhtml+xml,'
        'application/xml;'
        'q=0.9,*/*;q=0.8'
    )

    headers = {
        'Accept': accept,
        'User-Agent': get_user_agent(human=True),
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate'
    }

    logger.debug('Discovering resource from %s' % urlparse(url).netloc)

    try:
        html_response = requests.get(
            url,
            headers=headers
        )
    except RequestException:
        logger.warning('Connection error discovering resource', exc_info=True)
        return None, None, None

    if html_response.status_code == 404:
        return None, None, None

    try:
        html_response.raise_for_status()
    except Exception:
        logger.warning(
            'HTTP error discovering resource',
            exc_info=True,
            extra={
                'url': url
            }
        )

        return None, None, None

    try:
        html = html_response.content.decode('utf-8')
    except Exception:
        logger.warning(
            'Parsing error discovering resource',
            exc_info=True,
            extra={
                'url': url
            }
        )

        return None, None, None

    matches = settings.LINK_REGEX.findall(html)

    for match in matches:
        attrs = {}
        for attr in settings.ATTR_REGEX.findall(match):
            key, value1, value2 = attr
            attrs[key] = value1 or value2

        if attrs.get('rel') == 'alternate':
            fmt = settings.LINK_TYPE_REGEX.match(attrs.get('type', ''))
            if fmt is not None:
                fmt = fmt.groups()[0]
                discovery_url = urljoin(url, attrs.get('href'))
                urlparts = urlparse(discovery_url)
                params = parse_qs(urlparts.query or urlparts.params)
                q = discovery_url.find('?')

                if q > -1:
                    discovery_url = discovery_url[:q]

                params['width'] = width
                params['maxwidth'] = width

                logger.debug('Successfully discovered endpoint')

                try:
                    oembed_response = requests.get(
                        discovery_url,
                        params=params,
                        headers={
                            'Accept': {
                                'json': 'application/json',
                                'xml': 'text/aml'
                            }[fmt],
                            'User-Agent': get_user_agent()
                        }
                    )
                except RequestException:
                    logger.warning('Error calling discovered endpoint')
                    return None, None, None

                if oembed_response.status_code >= 200:
                    if oembed_response.status_code < 400:
                        return parse_oembed_response(
                            oembed_response.content.decode('utf-8'),
                            fmt
                        )

    try:
        graph = OpenGraph(
            html=html,
            scrape=True
        )
    except Exception:
        logger.error('Error reading Open Graph data', exc_info=True)
        return None, None, None  # pragma: no cover

    title = graph.get('title')
    image = graph.get('image')

    link = '<p><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></p>' % (
        escape(url),
        escape(url)
    )

    if title:
        link = '<p><a href="%s" target="_blank" rel="noopener noreferrer">%s</a></p>' % (
            escape(url),
            escape(title)
        )

        if image:
            link = (
                '<p><a href="%s" target="_blank" rel="noopener noreferrer">'
                '<img src="%s" max-width="100%%"><br>%s</a></p>'
            ) % (
                escape(url),
                escape(image),
                escape(title)
            )

        return link, title, url

    return None, None, None  # pragma: no cover


def sandbox_iframe(html):
    if html:
        return html.replace(
            '<iframe ',
            '<iframe sandbox="allow-pointer-lock allow-scripts" '
        )

    return html  # pragma: no cover


def make_printable(s):
    printable = set(string.printable)
    return ''.join(
        filter(lambda x: x in printable, s)
    )


def wrap_ajax(url, origin):
    from django.template.loader import render_to_string

    try:
        from django.core.urlresolvers import reverse
    except ImportError:
        from django.urls import reverse

    return render_to_string(
        'oembed/placeholder.inc.html',
        {
            'url': url,
            'origin': origin,
            'id': 'oembed_%s' % md5(
                ''.join(
                    url + random.choice(string.ascii_uppercase + string.digits)
                    for i in range(24)
                ).encode('ascii')
            ).hexdigest(),
            'OBJECT_URL': (
                settings.AJAX_OBJECT_URL or reverse('oembed_object')
            )
        }
    )
