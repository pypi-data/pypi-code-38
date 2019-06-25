# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import inspect
import os.path

from . import exceptions


def validate_in(key, mapping):
    if key not in mapping:
        raise AssertionError("The key '%s' was not found in the mapping %s!" % (key, mapping))


def validate_response_is_ok(response, allowable_response_status_codes=frozenset([200])):
    if isinstance(allowable_response_status_codes, int):
        allowable_response_status_codes = {allowable_response_status_codes}
    if response.status_code not in allowable_response_status_codes:
        if 400 <= response.status_code <= 499:
            exception_class_to_use = exceptions.BadRequestException
        else:
            exception_class_to_use = exceptions.InternalServerError

        raise exception_class_to_use(
            """response.status_code(%s) not in allowable_response_status_codes(%s) for the url\
             '%s' (request method:'%s'). response.content:\n%s""" % (
                response.status_code, allowable_response_status_codes,
                response.url,
                response.request.method,
                response.text[:1000]),
            response=response
        )

    if is_called_by_nose():
        # The sesamclient is being used by a ci-test, so do some additional checks.
        # check for headers with duplicate values

        # We must skip a couple of special case nodes that runs an old version of the code.
        url = response.request.url
        if not ("_msgpack-version-1" in url or "_msgpack-version-2" in url):
            for header_name, header_value in response.headers.items():
                if header_value:
                    header_values = header_value.split(",")
                    header_values_set = set()
                    for value in header_values:
                        value = value.strip()
                        if value in header_values_set:
                            raise AssertionError(
                                "Got a duplicate value '%s' in the '%s' response header for the url '%s'! "
                                "Header value: '%s'" % (
                                    value, header_name, response.request.url, header_value))
                        header_values_set.add(value)


def parse_json_response(response):
    """Utility-function for parsing a http response as json and reporting any parsing-errors in a human-readable
    way. The response.json() method doesn't give very helpful error-messages.

    :param response: The http response object
    :return: The response.content parsed as json
    """
    try:
        return response.json()
    except Exception as e:
        raise AssertionError(
            """Failed to parse the response as json for the url\
             '%s' (request method:'%s'): %s. response.content:\n%s""" % (
                response.url,
                response.request.method,
                e,
                response.text[:1000]))


def validate_equal_case_insensitive(expected, actual, msg=None):
    if isinstance(expected, str) and isinstance(actual, str):
        if expected.lower() == expected.lower():
            # the arguments are strings and they are the same when ignoring case.
            return
    if msg:
        raise AssertionError("""actual(%s) != expected(%s)! %s""" % (actual, expected, msg))
    else:
        raise AssertionError("""actual(%s) != expected(%s)""" % (actual, expected))


def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'VERSION.txt')) as version_file:
        return version_file.read().strip()


def is_called_by_nose():
    stack = inspect.stack()
    return any(x[0].f_globals['__name__'].startswith('nose.') for x in stack if x)
