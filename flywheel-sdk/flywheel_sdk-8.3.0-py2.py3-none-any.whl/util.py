"""Provides utility functions"""
import collections
import os


def seconds_to_years(seconds):
    """Convert seconds to years"""
    return seconds / 31557600.0

def years_to_seconds(years):
    """Convert years to seconds"""
    return int(years * 31557600.0)

def seconds_to_months(seconds):
    """Convert seconds to months"""
    return seconds / 2592000.0

def months_to_seconds(months):
    """Convert months to seconds"""
    return int(months * 2592000.0)

def seconds_to_weeks(seconds):
    """Convert seconds to weeks"""
    return seconds / 604800.0

def weeks_to_seconds(weeks):
    """Convert weeks to seconds"""
    return int(weeks * 604800.0)

def seconds_to_days(seconds):
    """Convert seconds to days"""
    return seconds / 86400.0

def days_to_seconds(days):
    """Convert days to seconds"""
    return int(days * 86400.0)

def params_to_dict(method_name, args, kwargs):
    """Given args and kwargs, return a dictionary object"""
    if len(args) > 1:
        raise TypeError(method_name + '() takes at most 1 positional argument')
    if args:
        if kwargs:
            raise ValueError(method_name + '() expects either a dictionary or kwargs')
        elif not isinstance(args[0], collections.MutableMapping) and not hasattr(args[0], 'to_dict'):
            raise ValueError(method_name + '() expects first argument to be a dictionary')
        return args[0]
    elif not kwargs:
        raise ValueError(method_name + '() expects either a dictionary or kwargs')
    return kwargs

def params_to_list(args):
    """Convert a list of arguments (some of which may be lists) to a flat list"""
    result = []
    for arg in args:
        if isinstance(arg, list):
            result += arg
        else:
            result.append(arg)
    return result

def to_ref(obj):
    """Convert a file or container to a reference"""
    ref_fn = getattr(obj, 'ref')
    if ref_fn:
        return ref_fn()
    return obj

def set_verify_ssl(session):
    """Create a session that verifies against correct certs"""
    if 'FW_SSL_CERT_FILE' in os.environ:
        session.verify = os.environ['FW_SSL_CERT_FILE']
