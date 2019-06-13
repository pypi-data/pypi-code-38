import ipaddress

from django.conf import settings


IP_NETWORKS = settings.IP_NETWORKS


def visitor_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def ip_networks_only(get_response):
    def middleware(request):
        ip = ipaddress.ip_address(visitor_ip_address(request))

        ipadd
