import hashlib
import json
import logging
import requests
import os
import re

from math import radians, cos, sin, asin, sqrt
from timezonefinder import TimezoneFinder
from ipaddress import ip_address

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.contrib.gis.geoip2 import GeoIP2
from django.core.handlers.wsgi import WSGIRequest

from . import models

logger = logging.getLogger('django_tasker_geobase')


def geo(query: str) -> models.Geobase:
    """
    Calculates geolocation by IP address.

    :param query: string address
    :returns: models.GeoTree
    """
    cache_key = hashlib.sha256()
    cache_key.update(query.encode('utf-8'))

    cache_geocoder = cache.get("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__))
    if cache_geocoder:
        return get_object_or_404(models.Geobase, id=cache_geocoder)

    data = _search(query=query)
    if not data:
        return

    geobase = None
    country = None
    for i in data.get('components'):
        geobase, created = models.Geobase.objects.get_or_create(
            en=i.get('en'),
            ru=i.get('ru'),
            parent=geobase,
            type=i.get('type_model'),
        )
        if i.get('type') == 'country':
            country = i.get('ru')

        if i.get('type') == 'house' or i.get('type') == 'apartment':
            geobase.timezone = data.get('timezone')
            geobase.zipcode = data.get('zipcode')
            geobase.latitude = data.get('latitude')
            geobase.longitude = data.get('longitude')
            geobase.save()
        elif i.get('type') == 'locality':

            if data.get('formatted') and created:
                locality_data = _search_yandex(
                    query="{country}, {city}".format(
                        country=country,
                        city=i.get('ru'),
                    ),
                    language='ru'
                )
                geobase.latitude = locality_data.get('latitude')
                geobase.longitude = locality_data.get('longitude')

            geobase.timezone = data.get('timezone')
            geobase.save()
        elif i.get('type') == 'street':
            geobase.timezone = data.get('timezone')
            geobase.save()

    cache.set("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__), geobase.id, 60 * 60 * 24 * 30)
    return geobase


def wifi(mac) -> models.Geobase:
    """
    Detect geolocation by MAC address.

    :param mac: MAC address
    :returns: models.GeoTree
    """

    mac = mac.strip().replace(":", "")

    cache_key = hashlib.sha256()
    cache_key.update(mac.encode('utf-8'))

    cache_geocoder = cache.get("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__))
    if cache_geocoder:
        return get_object_or_404(models.Geobase, id=cache_geocoder)

    proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    if proxies:
        proxies = {'http': proxies, 'https': proxies}

    yandex_locator_key = getattr(settings, 'GEOBASE_YANDEX_LOCATOR_KEY', os.environ.get('GEOBASE_YANDEX_LOCATOR_KEY'))
    if not yandex_locator_key:
        raise Exception("Invalid yandex locator key")

    json_params = json.dumps({
        "common": {
            "version": "1.0",
            "api_key": yandex_locator_key
        },
        "wifi_networks": [{
            "mac": str(mac)
        }],
    })

    response = requests.post(
        url='https://api.lbs.yandex.net/geolocation',
        data={'json': json_params},
        timeout=5,
        proxies=proxies
    )
    locator_result = response.json()
    if locator_result.get('position'):
        if locator_result.get('position').get('latitude') and locator_result.get('position').get('longitude'):
            latitude = locator_result.get('position').get('latitude')
            longitude = locator_result.get('position').get('longitude')
            geobase = geo(query="{longitude}, {latitude}".format(latitude=latitude, longitude=longitude))
            cache.set("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__), geobase.id, 60 * 60 * 24 * 30)
            return geobase

    return


def ip(request: WSGIRequest = None, ip: str = None) -> models.Geobase:
    """
    Calculates geolocation by IP address.

    :param request: WSGIRequest object
    :param ip: ip address IPv4 or IPv6.
    :returns: models.GeoTree
    """

    if request and isinstance(request, WSGIRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

    proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    if proxies:
        proxies = {'http': proxies, 'https': proxies}

    yandex_locator_key = getattr(settings, 'GEOBASE_YANDEX_LOCATOR_KEY', os.environ.get('GEOBASE_YANDEX_LOCATOR_KEY'))

    cache_key = hashlib.sha256()
    cache_key.update(ip.encode('utf-8'))

    cache_geocoder = cache.get("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__))
    if cache_geocoder:
        return get_object_or_404(models.Geobase, id=cache_geocoder)

    ip = ip_address(ip)
    if ip.version == 4 and ip.is_global and yandex_locator_key:
        json_params = json.dumps({
            "common": {
                "version": "1.0",
                "api_key": yandex_locator_key
            },
            "ip": {
                "address_v4": str(ip)
            }
        })
        response = requests.post(
            url='https://api.lbs.yandex.net/geolocation',
            data={'json': json_params},
            timeout=5,
            proxies=proxies
        )
        locator_result = response.json()
        if response.status_code == 200:
            if locator_result.get('position').get('latitude') and locator_result.get('position').get('longitude'):
                latitude = locator_result.get('position').get('latitude')
                longitude = locator_result.get('position').get('longitude')

    elif ip.version == 4 and ip.is_global:
        g = GeoIP2()
        geoip = g.city(str(ip))
        latitude = geoip.get('latitude')
        longitude = geoip.get('longitude')
    elif ip.version == 6 and ip.is_global:
        g = GeoIP2()
        geoip = g.city(str(ip))
        latitude = geoip.get('latitude')
        longitude = geoip.get('longitude')
    else:
        latitude = 51.478186
        longitude = -0.015424

    geobase = geo(query="{longitude}, {latitude}".format(latitude=latitude, longitude=longitude))
    cache.set("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__), geobase.id, 60 * 60 * 24 * 30)
    return geobase


def haversine(latitude1: float, longitude1: float, latitude2: float, longitude2: float) -> float:
    """
    Calculates the distance in kilometers between two points, given the circumference of the Earth.
    https://en.wikipedia.org/wiki/Haversine_formula

    :param latitude1: latitude1
    :param latitude2: latitude2
    :param longitude1: longitude1
    :param longitude2: longitude2
    :returns: models.GeoTree
    """

    # convert decimal degrees to radians
    longitude1, latitude1, longitude2, latitude2 = map(radians, (longitude1, latitude1, longitude2, latitude2))

    # haversine formula
    dlon = longitude2 - longitude1
    dlat = latitude2 - latitude1
    a = sin(dlat / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6367 * c * 1000


def _search(query: str) -> dict:

    ru = _search_yandex(query=query, language='ru')
    en = _search_yandex(query=query, language='en')

    d = []
    count = 0
    for item in ru.get('components'):
        en_match = en.get('components')[count]
        d.append({
            'type': item.get('type'),
            'type_model': item.get('type_model'),
            'ru': item.get('value'),
            'en': en_match.get('value')
        })
        count = count+1

    ru['components'] = d
    ru['formatted'] = ru.get('formatted')

    if ru.get('latitude') and ru.get('longitude'):
        tf = TimezoneFinder()
        ru['timezone'] = tf.timezone_at(lng=ru.get('longitude'), lat=ru.get('latitude'))

    return ru


def _search_yandex(query: str, language='en') -> dict:

    # Get proxy
    proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    if proxies:
        proxies = {'http': proxies, 'https': proxies}

    params = {
        "apikey": getattr(settings, 'GEOBASE_YANDEX_MAP_KEY', os.environ.get('GEOBASE_YANDEX_MAP_KEY')),
        "format": "json",
        "geocode": query,
    }

    if language == 'ru':
        params['lang'] = 'ru_RU'
    else:
        params['lang'] = 'en_RU'

    try:
        response = requests.get('https://geocode-maps.yandex.ru/1.x/', params=params, timeout=5, proxies=proxies)
        logger.debug("get url: {url}".format(url=response.url))

    except requests.exceptions.RequestException as error:
        logger.error(error)
        return {}

    data = {'components': []}
    json_yandex_map = response.json()
    geoobject = json_yandex_map.get('response').get('GeoObjectCollection').get('featureMember')
    for item in geoobject:
        item = item.get('GeoObject')

        if 'Point' in item:
            pos = item.get('Point').get('pos')
            pos = pos.split(" ")
            data['longitude'] = float(pos[0])
            data['latitude'] = float(pos[1])

        if 'postal_code' in item.get('metaDataProperty').get('GeocoderMetaData').get('Address'):
            data['zipcode'] = item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('postal_code')

        if 'country_code' in item.get('metaDataProperty').get('GeocoderMetaData').get('Address'):
            country_code = item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('country_code')
            data['country_code'] = country_code

        if 'formatted' in item.get('metaDataProperty').get('GeocoderMetaData').get('Address'):
            data['formatted'] = item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('formatted')

        for component in item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('Components'):

            if component.get('kind') == 'country':
                type_model = 1
            elif component.get('kind') == 'province':
                type_model = 2
            elif component.get('kind') == 'area':
                # type_model = 3
                continue
            elif component.get('kind') == 'locality':
                type_model = 4
            elif component.get('kind') == 'district':
                type_model = 5
            elif component.get('kind') == 'street':
                type_model = 6
            elif component.get('kind') == 'house':
                type_model = 7
            elif component.get('kind') == 'hydro':
                type_model = 8
            elif component.get('kind') == 'railway':
                type_model = 9
            elif component.get('kind') == 'route':
                type_model = 10
            elif component.get('kind') == 'vegetation':
                type_model = 11
            elif component.get('kind') == 'airport':
                type_model = 12
            elif component.get('kind') == 'metro':
                type_model = 13
            else:
                type_model = 14

            data['components'].append({
                'type_model': type_model,
                'type': component.get('kind'),
                'value': component.get('name'),
            })
        break

    # We calculate the apartment or office
    apartment = re.search(r'(кв|квартира|офис|оф|а/я|app|apartment)\.*\s*(\w+)$', query)
    if apartment:
        for i in data['components']:
            if i.get('type') == 'house':
                data['components'].append({'type_model': 15, 'type': 'apartment', 'value': apartment.group(2)})
                break

    # We receive postal codes of Kazakhstan
    if data.get('country_code') == 'KZ':
        for i in data['components']:
            if i.get('type') == 'house':
                try:
                    url = 'https://api.post.kz/api/byAddress/{formatted}'.format(formatted=data['formatted'])
                    response = requests.get(url, timeout=5, proxies=proxies)
                except requests.exceptions.RequestException as error:
                    logger.error(error)
                else:
                    post_kz = response.json()
                    for item_post_kz in post_kz.get('data'):
                        data['zipcode'] = item_post_kz.get('postcode')
                        break
                break

    return data

