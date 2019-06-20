from urllib.parse import urlparse
from .models import Resource
from . import settings, utils


def parse_html(value, ajax=False):
    if not value:
        return ''

    value = str(value)
    if '<p' not in value and '</p>' not in value:
        if not value.strip().startswith('<') and not value.strip().endswith('</p>'):
            value = '<p>%s</p>' % value

    match = settings.P_REGEX.search(value)
    while match is not None and match.end() <= len(value):
        start = match.start()
        end = match.end()
        groups = match.groups()

        url = groups[0]
        if not url.startswith('http:') and not url.startswith('https:'):
            match = settings.P_REGEX.search(value, start + len(url))
            continue

        if ajax:
            printable_url = utils.make_printable(url)
            domain = urlparse(printable_url).netloc
            origin = 'unknown'

            for d in settings.KNOWN_DOMAINS:
                if d.lower() in domain.lower():
                    origin = d.split('.')[0].lower()
                    break

            inner = utils.wrap_ajax(
                printable_url,
                origin
            )
        else:
            resource = Resource.load(url)
            inner = resource.to_html()

        if inner is None:
            inner = '<p><a href="%(url)s" rel="noopener noreferrer" target="_blank">%(url)s</a></p>' % {
                'url': url
            }

        value = value[:start] + inner + value[end:]
        match = settings.P_REGEX.search(value, start + len(inner))

    return value
