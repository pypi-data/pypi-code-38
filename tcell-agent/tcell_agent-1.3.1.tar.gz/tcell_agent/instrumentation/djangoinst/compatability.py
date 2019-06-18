from __future__ import unicode_literals

import django

from tcell_agent.tcell_logger import get_module_logger

isDjango20 = False
isDjango15 = False
django15or16 = False
try:
    isDjango15 = django.get_version().startswith("1.5")
    django15or16 = isDjango15 or django.get_version().startswith("1.6")
    isDjango20 = django.get_version().startswith("2")
except Exception:
    get_module_logger(__name__).warn("Could not determine Django version for compatibility tests")


def midVersionGreaterThanOrEqualTo(version_string):
    try:
        django_midv = django.get_version().split(".")[:2]
        comparison_midv = version_string.split(".")[:2]
        if int(django_midv[0]) >= int(comparison_midv[0]) and int(django_midv[1]) >= int(comparison_midv[1]):
            return True
    except Exception:
        get_module_logger(__name__).warn("Could not determine Django midversion for compatibility tests")
    return False


if isDjango20:
    from django.urls import Resolver404, get_resolver  # pylint: disable=no-name-in-module
elif midVersionGreaterThanOrEqualTo("1.10"):
    from django.urls.resolvers import Resolver404, get_resolver  # pylint: disable=no-name-in-module
else:
    from django.core.urlresolvers import Resolver404, get_resolver


def is_django_20():
    return isDjango20


def get_route_handler(path_info):
    try:
        resolver = get_resolver(None)
        return resolver.resolve(path_info)
    except Resolver404:
        pass
    except Exception as route_ex:
        LOGGER = get_module_logger(__name__)
        LOGGER.error("Unknown resolver error {e}".format(e=route_ex))
        LOGGER.exception(route_ex)

    return None


def get_url_patterns():
    resolver = get_resolver(None)
    return resolver.url_patterns
