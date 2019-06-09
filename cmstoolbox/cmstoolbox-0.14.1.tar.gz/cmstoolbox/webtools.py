# pylint: disable=protected-access, unexpected-keyword-arg, bad-option-value, redefined-variable-type, too-many-locals

"""
A high-level module for getting JSON information from web services.
The HTTP vs HTTPS and certificate handling is done here.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


import os
import time
import re
import stat
import json
import logging
import ssl
import urllib
import subprocess
try:
    import httplib
except ImportError:
    import http.client as httplib # pylint: disable=import-error


def get_json(host, request, params='', body='', headers=None,
             port=None, retries=3, **kwargs):
    """
    Function for getting JSON from a URL that handles the connection
    and certificates with just a couple of bools.

    :param str host: The name of the host to connect to
    :param str request: The request to make to the host
    :param dict params: The parameters to pass to the request
    :param str body: The body to send in a POST request
    :param dict headers: Headers to pass to request. If ``None``,
                         ``{'Accept': 'application/json'}`` will be passed.
    :param int port: The port to access, if a not default value
    :param int retries: The number of times to try to get the JSON response before giving up
    :param kwargs: Additional aruments that can be used to change
                   the connection behavior.
                   These are listed below:

                   - use_https (bool) - Uses HTTP connection by default
                   - use_cert (bool) - Does not pass a certificate by default
                   - cert_file (str) - Default is ``$X509_USER_PROXY``.
                   - use_post (bool) - Determines whether to use POST or GET.
                   - cookie_file (str) - Location of a Shibboleth cookie to pass in header
                   - cookie_pem (str) - Location of ``.pem`` file to generate cookie
                   - cookie_key (str) - Location of ``.rsa`` key to generate cookie
                   - cookie_time (float) - Time, in seconds, until generating a new cookie

    :returns: The JSON from the query
    :rtype: dict
    """

    check_for_port = host.split(':')
    if len(check_for_port) == 2:
        host = check_for_port[0]
        port = int(check_for_port[1])

    use_cert = kwargs.get('use_cert', False)
    use_https = kwargs.get('use_https', use_cert or bool(kwargs.get('cookie_file')))

    if use_https:
        use_port = port or 443
        cert_file = kwargs.get(
            'cert_file',
            os.environ.get('X509_USER_PROXY',
                           '/tmp/x509up_u%i' % os.geteuid())
            ) if use_cert else None

        # Python 2.7.something verifies HTTPS connections,
        # but earlier version of Python do not
        try:
            conn = httplib.HTTPSConnection(
                host, use_port, cert_file=cert_file, key_file=cert_file,
                context=ssl._create_unverified_context())

        except AttributeError:
            conn = httplib.HTTPSConnection(
                host, use_port, cert_file=cert_file, key_file=cert_file)

    else:
        use_port = port or 80
        conn = httplib.HTTPConnection(host, use_port)

    method = "POST" if kwargs.get('use_post', bool(body)) else "GET"
    full_request = '%s?%s' % (request, urllib.urlencode(params)) if params else request

    header = headers or {'Accept': 'application/json'}

    if kwargs.get('cookie_file'):
        sso_request_url = 'https://%s:%i%s' % (host, use_port, full_request)

        header['Cookie'] = get_cookie_header(sso_request_url, kwargs['cookie_file'],
                                             kwargs.get('cookie_pem'), kwargs.get('cookie_key'),
                                             kwargs.get('cookie_time'))[host]

    tries = 0

    while tries <= retries:
        conn.request(
            method, full_request, json.dumps(body), header)

        res = conn.getresponse()

        if res.status == 200:
            result = json.loads(res.read())
            conn.close()
            return result

        logging.warning('STATUS: %s, REASON: %s', res.status, res.reason)
        tries += 1
        conn.close()

    return {}


def get_cookie_header(url, cookie_file, pem=None, key=None, refresh_time=None):
    """
    Get the header infomation that meeds to be passed to the server.
    This function by default requires a .rsa key inside your ``~/.globus`` directory.
    To generate this run the following commands from ``~/.globus``::

        openssl rsa -in userkey.pem -out userkey.rsa
        chmod 400 userkey.rsa

    This function also requires ``cern-get-sso-cookie`` to be installed on your machine.

    :param str url: The location to get the cookie from
    :param str cookie_file: The location where to store the cookie
    :param str pem: The location of the ``.pem`` file (default ``~/.globus/usercert.pem``)
    :param str key: The location of the ``.rsa`` key (default ``~/.globus/userkey.rsa``)
    :param float refresh_time: The number of seconds until the next time the cookie is generated
                     (default to three hours)
    :returns: The cookie string for each host to be set as the
              ``'Cookie'`` element of the request header
    :rtype: dict
    """

    old_time = refresh_time or float(3 * 60 * 60)

    output = {}

    # If cookie not existing or is old, generate a new cookie
    if not os.path.exists(cookie_file) or (time.time() - os.stat(cookie_file).st_mtime) > old_time:

        pem_file = pem or os.path.join(os.environ['HOME'], '.globus', 'usercert.pem')
        rsa_file = key or os.path.join(os.environ['HOME'], '.globus', 'userkey.rsa')

        # Make the cookie file
        subprocess.call(['cern-get-sso-cookie', '--nocertverify', '-u', url,
                         '--cert', pem_file, '--key', rsa_file, '-o', cookie_file])
        # Modify permissions
        os.chmod(cookie_file, stat.S_IRUSR | stat.S_IWUSR)

    with open(cookie_file, 'r') as cookie_fd:
        # Skip the header
        contents = list(cookie_fd)[4:]

        for line in contents:
            domain, _, _, _, _, key, val = re.sub(r'^#*(HttpOnly_)*', '', line.strip()).split()

            if output.get(domain):
                output[domain] += '; '
            else:
                output[domain] = ''

            output[domain] += '%s=%s' % (key, val)

    return output
