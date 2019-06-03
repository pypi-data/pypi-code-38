""" Auto discovery of Exporters
"""

from core_exporters_app.components.exporter.models import Exporter
from mongoengine.errors import ValidationError
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.contrib.admindocs.views import simplify_regex
import core_exporters_app.components.exporter.api as exporters_api
import core_main_app.components.template.api as templates_api
import core_main_app.commons.exceptions as main_exception
from core_exporters_app.exporters import urls
import re


def __assemble_endpoint_data__(pattern, prefix='', filter_path=None):
    """
    Creates a dictionary for matched API urls
    pattern -- the pattern to parse
    prefix -- the API path prefix (used by recursion)
    """
    path = simplify_regex(prefix + pattern.regex.pattern)

    if filter_path is not None:
        if re.match('^/?%s(/.*)?$' % re.escape(filter_path), path) is None:
            return None

    path = path.replace('<', '{').replace('>', '}')

    return {
        'url': path,
        'view': pattern.lookup_str,
        'name': pattern.default_args['name'],
        'enable_by_default': pattern.default_args['enable_by_default'],
    }


def __flatten_patterns_tree__(patterns, prefix='', filter_path=None):
    """
    Uses recursion to flatten url tree.
    patterns -- urlpatterns list
    prefix -- (optional) Prefix for URL pattern
    """
    pattern_list = []

    for pattern in patterns:
        if isinstance(pattern, RegexURLPattern):
            endpoint_data = __assemble_endpoint_data__(pattern, prefix, filter_path=filter_path)

            if endpoint_data is None:
                continue

            pattern_list.append(endpoint_data)

        elif isinstance(pattern, RegexURLResolver):

            pref = prefix + pattern.regex.pattern
            pattern_list.extend(__flatten_patterns_tree__(
                pattern.url_patterns,
                pref,
                filter_path=filter_path
            ))

    return pattern_list


def discover_exporter():
    """ Exporters discover

    Returns:

    """
    patterns = __flatten_patterns_tree__(urls.urlpatterns)
    try:
        for pattern in patterns:
            try:
                try:
                    exporters_api.get_by_url(pattern['view'])
                except main_exception.DoesNotExist:
                    # if there is no exporter with the given url
                    # we add it
                    exporter_added = Exporter(name=pattern['name'],
                                              url=pattern['view'],
                                              enable_by_default=pattern['enable_by_default'])
                    # if we added an exporter and it is a default one, we have to add it in all template
                    if exporter_added.enable_by_default is True:
                        exporter_added.templates = templates_api.get_all()
                    exporters_api.upsert(exporter_added)
            except Exception, e:
                print('ERROR : Impossible to load the following exporter, class not found : ' + pattern['view'])
    except ValidationError as e:
        raise Exception('A validation error occured during the exporter discovery :' + e.message)
    except Exception, e:
        raise e
