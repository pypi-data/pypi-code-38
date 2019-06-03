import urllib

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def qrcode(value, alt=None):
    """
    Generate QR Code image from a string with the Google charts API

    http://code.google.com/intl/fr-FR/apis/chart/types.html#qrcodes

    Exemple usage --
    {{ my_string|qrcode:"my alt" }}

    <img src="http://chart.apis.google.com/chart?chs=150x150&amp;cht=qr&amp;chl=my_string&amp;choe=UTF-8" alt="my alt" />
    """

    url = conditional_escape("http://chart.apis.google.com/chart?%s" %\
                             urllib.urlencode({'chs':'250x250', 'cht':'qr', 'chl':value, 'choe':'UTF-8'}))
    alt = conditional_escape(alt or value)

    return mark_safe(u"""<img class="qrcode" src="%s" width="250" height="250" alt="%s" />""" % (url, alt))


@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__


@register.inclusion_tag('votebase/helpers/pagination.html', takes_context=True)
def paginator(context, objects, page_ident='page', anchor=None, adjacent=2):
    page_range = objects.paginator.page_range
    number = objects.number

    page_numbers = [n for n in range(number - adjacent, number + adjacent + 1)
                    if n > 0 and n <= len(page_range)]

    show_left_dots = True
    if number - adjacent - 1 == 1:
        show_left_dots = False

    show_right_dots = True
    if number + adjacent + 1 == len(page_range):
        show_right_dots = False

    return {
        'anchor': anchor,
        'request': context.get('request', None),
        'page_ident': page_ident,
        'results_per_page': objects.paginator.per_page,
        'page': objects.number,
        'pages': page_range,
        'count': len(page_range),
        'page_numbers': page_numbers,
        'next': objects.next_page_number,
        'previous': objects.previous_page_number,
        'has_next': objects.has_next,
        'has_previous': objects.has_previous,
        'show_first': 1 not in page_numbers,
        'show_last': False if len(page_range) - number <= adjacent else True,
        'show_left_dots': show_left_dots,
        'show_right_dots': show_right_dots,
    }