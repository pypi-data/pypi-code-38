from django.urls import reverse
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser

import decimal
from math import log, floor

from aparnik.settings import aparnik_settings
from aparnik.contrib.settings.models import Setting


def document_directory_path(instance, filename, folder='file'):
    from django.utils.timezone import now
    import random
    return '{0}/{1}-{2}.{3}.{4}'.format(folder, filename.split(".")[0], now(), random.randint(0, 1000000),
                                        filename.split(".")[-1])


def convert_iran_phone_number_to_world_number(phone):
    if len(phone) == 10:

        phone = '+98' + phone
    elif len(phone) == 11:

        phone = '+98' + phone[1:]

    if phone[0:1] == '+':
        phone = '00' + phone[1:]

    if phone[0:4] == '0098' and phone[4] == 0:
        phone = phone[0:4] + phone[5:]

    return phone


def is_app_installed(app):
    from django.apps import apps
    return apps.is_installed(app)


def append_absolute_uri(request, urls):
    if request:
        urls_build = {}
        for key, ur in list(urls.items()):
            urls_build[key] = request.build_absolute_uri(ur)
    else:
        urls_build = urls

    return urls_build


def get_url_install(request=None):
    url = {
    }
    # User
    url['login'] = reverse('aparnik-api:users:login')
    url['user-register-with-password'] = reverse('aparnik-api:users:create')
    url['user-request-send-sms'] = reverse('aparnik-api:users:send-sms')
    url['user-verify-sms'] = reverse('aparnik-api:users:verify-sms')
    url['user-forget-password'] = reverse('aparnik-api:users:forget-password')
    url['logout'] = reverse('aparnik-api:users:logout')
    url['FCM-add-token'] = reverse('aparnik-api:users:FCM-add-token')
    url['verify'] = reverse('aparnik-api:users:verify')
    url['token'] = reverse('aparnik-api:users:token')
    url['user-list'] = reverse('aparnik-api:users:list')
    url['user-subset-list'] = reverse('aparnik-api:users:subset')

    # addresses
    url['user-addresses-list'] = reverse('aparnik-api:addresses:list')
    url['user-addresses-create'] = reverse('aparnik-api:addresses:create')

    # bank accounts
    url['user-bankaccounts-list'] = reverse('aparnik-api:bankaccounts:list')
    url['user-banknames-list'] = reverse('aparnik-api:bankaccounts:bankname-list')
    url['user-bankaccounts-create'] = reverse('aparnik-api:bankaccounts:create')

    url['invitations-list'] = reverse('aparnik-api:invitations:list')
    url['about-us'] = reverse('aparnik-api:aboutus:detail')

    # files
    url['s3-sign'] = reverse('aparnik-api:files:s3-sign')
    url['file-create'] = reverse('aparnik-api:files:create')

    # Province
    url['province-list'] = reverse('aparnik-api:provinces:list')

    # Notification
    url['notification-list'] = reverse('aparnik-api:notifications:list')
    url['notification-reads-all'] = reverse('aparnik-api:notifications:reads-all')

    # Notify me
    url['notifies-me-list'] = reverse('aparnik-api:notifiesme:list')

    # supports
    url['supports-list'] = reverse('aparnik-api:supports:list')

    # FAQ
    url['faq-detail'] = reverse('aparnik-api:faq:detail')

    # termsandconditions
    url['termsandconditions-detail'] = reverse('aparnik-api:termsandconditions:detail')

    # education degree
    url['educations-degree-list'] = reverse('aparnik-api:educations:educations:degree-list')
    url['educations-field-subject-list'] = reverse('aparnik-api:educations:educations:field-subject-list')
    url['educations-institude-list'] = reverse('aparnik-api:educations:educations:institude-list')

    # order
    url['order-charge-wallet'] = reverse('aparnik-api:shops:orders:charge-wallet')
    url['order-list'] = reverse('aparnik-api:shops:orders:list')
    url['order-add'] = reverse('aparnik-api:shops:orders:add')

    # Product
    url['products-sort'] = reverse('aparnik-api:shops:products:sort')
    url['products-list'] = reverse('aparnik-api:shops:products:list')

    # Products sharing
    url['productssharing-list'] = reverse('aparnik-api:shops:productssharing:list')

    # payments
    url['payments-list'] = reverse('aparnik-api:shops:payments:list')

    # subscriptions
    url['subscriptions-list'] = reverse('aparnik-api:shops:subscriptions:list')

    # vouchers
    url['vouchers-list'] = reverse('aparnik-api:shops:vouchers:list')

    # course
    url['course-list'] = reverse('aparnik-api:educations:courses:list')
    url['course-user-list'] = reverse('aparnik-api:educations:courses:user')
    url['course-create'] = reverse('aparnik-api:educations:courses:create')

    # book
    url['book-list'] = reverse('aparnik-api:educations:books:list')
    url['book-user-list'] = reverse('aparnik-api:educations:books:user')

    # Bookmark
    url['bookmark-user-list'] = reverse('aparnik-api:bookmarks:list')

    # Review
    url['review-user-list'] = reverse('aparnik-api:reviews:list')

    # QA
    url['qa-user-list'] = reverse('aparnik-api:qa:list')
    url['qa-sort'] = reverse('aparnik-api:qa:sort')

    # Contact us
    url['contact-us-list'] = reverse('aparnik-api:contactus:list')
    url['contact-us-create'] = reverse('aparnik-api:contactus:create')

    # news
    url['news-list'] = reverse('aparnik-api:news:list')

    # CoSale
    url['co-sale-users-list'] = reverse('aparnik-api:shops:cosales:user-list')
    url['co-sale-list'] = reverse('aparnik-api:shops:cosales:list')

    urls = append_absolute_uri(request, url)

    # admin area
    urls_admin = {

    }

    if request and request.user.is_authenticated and request.user.is_admin:

        urls_admin['filefields-list'] = reverse('aparnik-api:files:list')

        urls_admin['audits-sort'] = reverse('aparnik-api:audits:admin:sort')
        urls_admin['audits-list'] = reverse('aparnik-api:audits:admin:list')

        urls_admin['users-sort'] = reverse('aparnik-api:users:admin:sort')
        urls_admin['users-list'] = reverse('aparnik-api:users:admin:list')

        urls_admin['products-sort'] = reverse('aparnik-api:shops:products:admin:sort')
        urls_admin['products-list'] = reverse('aparnik-api:shops:products:admin:list')

        urls_admin['orders-sort'] = reverse('aparnik-api:shops:orders:admin:sort')
        urls_admin['orders-list'] = reverse('aparnik-api:shops:orders:admin:list')

        urls_admin['coupons-sort'] = reverse('aparnik-api:shops:coupons:admin:sort')
        urls_admin['coupons-list'] = reverse('aparnik-api:shops:coupons:admin:list')

        urls_admin['courses-sort'] = reverse('aparnik-api:educations:courses:admin:sort')
        urls_admin['courses-list'] = reverse('aparnik-api:educations:courses:admin:list')

        urls_admin['teachers-sort'] = reverse('aparnik-api:educations:teachers:admin:sort')
        urls_admin['teachers-list'] = reverse('aparnik-api:educations:teachers:admin:list')



    urls_admin = append_absolute_uri(request, urls_admin)

    properties = {}
    for setting in Setting.objects.home_properties():
        properties[setting.key] = setting.get_value()

    return urls, {
        'properties': properties,
        'AWS_ACTIVE': aparnik_settings.AWS_ACTIVE,
        'USER_LOGIN_WITH_PASSWORD': aparnik_settings.USER_LOGIN_WITH_PASSWORD
    }, urls_admin


def get_pages(request):
    from aparnik.contrib.pages.models import Page
    from aparnik.contrib.pages.api.serializers import PageListPolymorphicSerializer
    pages = PageListPolymorphicSerializer(Page.objects.home(), many=True, read_only=True,
                                          context={'request': request}).data

    return pages


def get_request():
    request = HttpRequest()
    server_url = 'aparnik.com'
    server_port = '80'
    try:
        setting = Setting.objects.get(key='SERVER_NAME')
        server_url = setting.get_value()
    except:
        pass

    try:
        setting = Setting.objects.get(key='SERVER_PORT')
        server_port = setting.get_value()
    except:
        pass

    if server_port == '443':
        HttpRequest.scheme = 'https'

    request.META['SERVER_NAME'] = server_url
    request.META['SERVER_PORT'] = server_port
    request.user = AnonymousUser()
    return request


def round(value):
    value = decimal.Decimal(value)
    return value.quantize(decimal.Decimal('1.'), rounding=decimal.ROUND_UP)


def human_format(number):
    if number == 0:
        return "0"
    format_string = '%.1f %s'
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    result = number / k ** magnitude
    if magnitude == 0:
        format_string = '%.0f %s'
    return format_string % (result, units[magnitude])


def field_with_prefix(field, prefix=''):
    if prefix:
        field = prefix + '__' + field
    return field