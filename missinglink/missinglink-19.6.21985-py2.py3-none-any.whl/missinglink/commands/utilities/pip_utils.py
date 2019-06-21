# -*- coding: utf-8 -*-
import json
import logging
import subprocess
import sys

import pkg_resources
from six.moves import urllib_request
from six import string_types

logger = logging.getLogger()


def get_keywords(package):
    try:
        dist = pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        return None

    parsed_pkg_info = getattr(dist, '_parsed_pkg_info', None)

    if parsed_pkg_info is None:
        return None

    logger.debug('get_keywords for: %s are %s ', package, parsed_pkg_info.get('Keywords'))
    return parsed_pkg_info.get('Keywords')


def installed_version(package):
    try:
        dist = pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        return None

    logger.debug('installed_version for: %s is %s ', package, dist.version)
    return str(dist.version)


def get_pip_server(keywords=None):
    keywords = keywords or ''
    pypi_server_hostname = 'testpypi' if 'test' in keywords else 'pypi'
    server = 'https://{hostname}.python.org/pypi'.format(hostname=pypi_server_hostname)

    logger.debug('get_pip_server for: %s is %s', keywords, server)
    return server


def _has_pip(hint_package=None):
    try:
        import pip
    except ImportError:
        hint = ''
        if hint_package:
            hint = ", can't install %s" % hint_package

        logging.warning("pip not found %s", hint)
        return False

    return True


def pip_install(pip_server, require_package, user_path):
    # use current interpreter for update
    args = [sys.executable, '-m', 'pip', 'install', '--upgrade', '-i']

    if not _has_pip():
        return None, None

    if user_path:
        args.append('--user')

    args.extend([pip_server, require_package])

    logger.debug('pip_install for: %s is %s', require_package, args)
    return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE), tuple(args)


def latest_version(keywords, throw_exception=False, package=None):
    try:
        pypi_server = get_pip_server(keywords)
        package = package or 'missinglink-kernel'
        url = '{server}/{package}/json'.format(server=pypi_server, package=package)

        html = urllib_request.urlopen(url).read()

        # in python3 it will be returned as bytes
        if not isinstance(html, string_types):
            html = html.decode('utf-8')

        package_info = json.loads(html)

        return package_info['info']['version']
    except Exception as e:
        if throw_exception:
            raise

        logger.exception('could not check for new missinglink-sdk version:\n%s', e)
        return None
