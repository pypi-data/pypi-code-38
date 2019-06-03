import roman

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_absolute_url(request):
#    if request.META['SERVER_PROTOCOL'] == 'HTTP/1.1':
#        protocol = 'http://'
#    else:
#        protocol = 'https://'
    protocol = 'https://' if request.is_secure() else 'http://'
    return protocol + request.get_host()


def error_email_confirmed(request):
    messages.error(request, _(u'You have not confirmed your email \
    address yet. If you did not receive confirmation, please click \
    <a href="%(url)s">here</a>.' % {
        'url': reverse('accounts_resend_confirmation'),
    }))


def redirect_back(request, path_name='home'):
    try:
        return redirect(request.META['HTTP_REFERER'])
    except KeyError:
        return redirect(path_name)


def decode(string):
    response = dict()
    for part in string.split('&'):
        parts = part.split('=')
        response[parts[0]] = parts[1]

    return response


def img(image, width=None, height=None):
    try:
        width = width or image.width
        height = height or image.height

        return '<a href="%(url)s" target="_blank"><img src="%(url)s" width="%(width)s" height="%(height)s"></a>' % {
            'url': image.url,
            'width': width,
            'height': height,
        }
    except IOError:
        return ''


def paginate(request, objects, paginate_by=10):
    paginator = Paginator(list(objects), paginate_by)
    page = request.GET.get('page')

    try:
        page_number = int(page)
    except TypeError:
        page_number = 1

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return {
        'is_paginated': paginator.page(page_number).has_other_pages(),
        'object_list': page.object_list,
        'page': page,
        'total_count': len(objects)
    }


def sorted_by_roman(roman_categories):
    try:
        # create list of categories with arabic numbers
        arabic_categories = []
        for roman_category in roman_categories:
            roman_number = roman_category.split('.')[0]
            arabic_number = roman.fromRoman(roman_number)
            arabic_category = roman_category.replace('%s.' % roman_number, '%d.' % arabic_number)
            arabic_categories.append(arabic_category)

        # sort arabic categories
        arabic_categories = sorted(arabic_categories)

        # rebuild roman categories list
        for index, arabic_category in enumerate(arabic_categories):
            arabic_number = int(arabic_category.split('.')[0])
            roman_number = roman.toRoman(arabic_number)
            roman_category = arabic_category.replace('%d.' % arabic_number, '%s.' % roman_number)
            roman_categories[index] = roman_category
    except roman.InvalidRomanNumeralError:
        pass

    return roman_categories
