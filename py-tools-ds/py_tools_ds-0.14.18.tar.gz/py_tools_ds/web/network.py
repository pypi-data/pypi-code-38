# -*- coding: utf-8 -*-

from six import PY3
import json
import socket

if PY3:
    # noinspection PyCompatibility
    from urllib.request import urlopen
else:
    from urllib import urlopen


def get_geoinfo():
    """Returns a dictionary containing country, city, longitude, latitude and IP of the executing host."""

    url = 'http://ipinfo.io/json'
    info = json.loads(urlopen(url).read())
    ip = info['ip']

    urlFoLaction = "http://www.freegeoip.net/json/{0}".format(ip)
    locationInfo = json.loads(urlopen(urlFoLaction).read())

    return dict(
        Country=locationInfo['country_name'],
        City=locationInfo['city'],
        Latitude=str(locationInfo['latitude']),
        Longitude=str(locationInfo['longitude']),
        IP=str(locationInfo['ip'])
    )


def is_connected(REMOTE_SERVER="www.google.com"):
    """Checks if an internet connection is present."""

    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 80), 2)
        return True
    except Exception:
        pass
    return False
