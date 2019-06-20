# -*- coding: utf-8 -*-
# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>
# Written by Matt Prahl <mprahl@redhat.com>

"""Auth system based on the client certificate and FAS account"""
import json
import os
from socket import gethostname
import ssl

import requests
import kerberos
from flask import Response, g

# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack
from werkzeug.exceptions import Unauthorized as FlaskUnauthorized
from dogpile.cache import make_region

from module_build_service.errors import Unauthorized, Forbidden
from module_build_service import app, log, conf

try:
    import ldap3
except ImportError:
    log.warning("ldap3 import not found.  ldap/krb disabled.")


client_secrets = None
region = make_region().configure("dogpile.cache.memory")


def _json_loads(content):
    if not isinstance(content, str):
        content = content.decode("utf-8")
    return json.loads(content)


def _load_secrets():
    global client_secrets
    if client_secrets:
        return

    if "OIDC_CLIENT_SECRETS" not in app.config:
        raise Forbidden("OIDC_CLIENT_SECRETS must be set in server config.")

    secrets = _json_loads(open(app.config["OIDC_CLIENT_SECRETS"], "r").read())
    client_secrets = list(secrets.values())[0]


def _get_token_info(token):
    """
    Asks the token_introspection_uri for the validity of a token.
    """
    if not client_secrets:
        return None

    request = {
        "token": token,
        "token_type_hint": "Bearer",
        "client_id": client_secrets["client_id"],
        "client_secret": client_secrets["client_secret"],
    }
    headers = {"Content-type": "application/x-www-form-urlencoded"}

    resp = requests.post(client_secrets["token_introspection_uri"], data=request, headers=headers)
    return resp.json()


def _get_user_info(token):
    """
    Asks the userinfo_uri for more information on a user.
    """
    if not client_secrets:
        return None

    headers = {"authorization": "Bearer " + token}
    resp = requests.get(client_secrets["userinfo_uri"], headers=headers)
    return resp.json()


def get_user_oidc(request):
    """
    Returns the client's username and groups based on the OIDC token provided.
    """
    _load_secrets()

    if "authorization" not in request.headers:
        raise Unauthorized("No 'authorization' header found.")

    header = request.headers["authorization"].strip()
    prefix = "Bearer "
    if not header.startswith(prefix):
        raise Unauthorized("Authorization headers must start with %r" % prefix)

    token = header[len(prefix):].strip()
    try:
        data = _get_token_info(token)
    except Exception as e:
        error = "Cannot verify OIDC token: %s" % str(e)
        log.exception(error)
        raise Exception(error)

    if not data or "active" not in data or not data["active"]:
        raise Unauthorized("OIDC token invalid or expired.")

    if "OIDC_REQUIRED_SCOPE" not in app.config:
        raise Forbidden("OIDC_REQUIRED_SCOPE must be set in server config.")

    presented_scopes = data["scope"].split(" ")
    required_scopes = [
        "openid",
        "https://id.fedoraproject.org/scope/groups",
        app.config["OIDC_REQUIRED_SCOPE"],
    ]
    for scope in required_scopes:
        if scope not in presented_scopes:
            raise Unauthorized("Required OIDC scope %r not present: %r" % (scope, presented_scopes))

    try:
        extended_data = _get_user_info(token)
    except Exception as e:
        error = "Cannot verify determine user groups:  %s" % str(e)
        log.exception(error)
        raise Exception(error)

    username = data["username"]
    # If the user is part of the whitelist, then the group membership check is skipped
    if username in conf.allowed_users:
        groups = set()
    else:
        try:
            groups = set(extended_data["groups"])
        except Exception as e:
            error = "Could not find groups in UserInfo from OIDC %s" % str(e)
            log.exception(extended_data)
            raise Exception(error)

    return username, groups


# Insired by https://pagure.io/waiverdb/blob/master/f/waiverdb/auth.py which was
# inspired by https://github.com/mkomitee/flask-kerberos/blob/master/flask_kerberos.py
class KerberosAuthenticate(object):
    def __init__(self):
        if conf.kerberos_http_host:
            hostname = conf.kerberos_http_host
        else:
            hostname = gethostname()
        self.service_name = "HTTP@{0}".format(hostname)

        # If the config specifies a keytab to use, then override the KRB5_KTNAME
        # environment variable
        if conf.kerberos_keytab:
            os.environ["KRB5_KTNAME"] = conf.kerberos_keytab

        if "KRB5_KTNAME" in os.environ:
            try:
                principal = kerberos.getServerPrincipalDetails("HTTP", hostname)
            except kerberos.KrbError as error:
                raise Unauthorized('Kerberos: authentication failed with "{0}"'.format(str(error)))

            log.debug('Kerberos: server is identifying as "{0}"'.format(principal))
        else:
            raise Unauthorized(
                'Kerberos: set the config value of "KERBEROS_KEYTAB" or the '
                'environment variable "KRB5_KTNAME" to your keytab file'
            )

    def _gssapi_authenticate(self, token):
        """
        Performs GSSAPI Negotiate Authentication
        On success also stashes the server response token for mutual authentication
        at the top of request context with the name kerberos_token, along with the
        authenticated user principal with the name kerberos_user.
        """
        state = None
        ctx = stack.top
        try:
            rc, state = kerberos.authGSSServerInit(self.service_name)
            if rc != kerberos.AUTH_GSS_COMPLETE:
                log.error("Kerberos: unable to initialize server context")
                return None

            rc = kerberos.authGSSServerStep(state, token)
            if rc == kerberos.AUTH_GSS_COMPLETE:
                log.debug("Kerberos: completed GSSAPI negotiation")
                ctx.kerberos_token = kerberos.authGSSServerResponse(state)
                ctx.kerberos_user = kerberos.authGSSServerUserName(state)
                return rc
            elif rc == kerberos.AUTH_GSS_CONTINUE:
                log.debug("Kerberos: continuing GSSAPI negotiation")
                return kerberos.AUTH_GSS_CONTINUE
            else:
                log.debug("Kerberos: unable to step server context")
                return None
        except kerberos.GSSError as error:
            log.error("Kerberos: unable to authenticate: {0}".format(str(error)))
            return None
        finally:
            if state:
                kerberos.authGSSServerClean(state)

    def process_request(self, token):
        """
        Authenticates the current request using Kerberos.
        """
        kerberos_user = None
        kerberos_token = None
        ctx = stack.top
        rc = self._gssapi_authenticate(token)
        if rc == kerberos.AUTH_GSS_COMPLETE:
            kerberos_user = ctx.kerberos_user
            kerberos_token = ctx.kerberos_token
        elif rc != kerberos.AUTH_GSS_CONTINUE:
            raise Forbidden("Invalid Kerberos ticket")

        return kerberos_user, kerberos_token


def get_user_kerberos(request):
    user = None
    if "Authorization" not in request.headers:
        response = Response("Unauthorized", 401, {"WWW-Authenticate": "Negotiate"})
        exc = FlaskUnauthorized()
        # For some reason, certain versions of werkzeug raise an exception when passing `response`
        # in the constructor. This is a work-around.
        exc.response = response
        raise exc
    header = request.headers.get("Authorization")
    token = "".join(header.strip().split()[1:])
    user, kerberos_token = KerberosAuthenticate().process_request(token)
    # Remove the realm
    user = user.split("@")[0]
    # If the user is part of the whitelist, then the group membership check is skipped
    if user in conf.allowed_users:
        groups = []
    else:
        groups = get_ldap_group_membership(user)
    return user, set(groups)


@region.cache_on_arguments()
def get_ldap_group_membership(uid):
    """ Small wrapper on getting the group membership so that we can use caching
    :param uid: a string of the uid of the user
    :return: a list of groups the user is a member of
    """
    ldap_con = Ldap()
    return ldap_con.get_user_membership(uid)


class Ldap(object):
    """ A class that handles LDAP connections and queries
    """

    connection = None
    base_dn = None

    def __init__(self):
        if not conf.ldap_uri:
            raise Forbidden("LDAP_URI must be set in server config.")
        if conf.ldap_groups_dn:
            self.base_dn = conf.ldap_groups_dn
        else:
            raise Forbidden("LDAP_GROUPS_DN must be set in server config.")

        if conf.ldap_uri.startswith("ldaps://"):
            tls = ldap3.Tls(
                ca_certs_file="/etc/pki/tls/certs/ca-bundle.crt", validate=ssl.CERT_REQUIRED)
            server = ldap3.Server(conf.ldap_uri, use_ssl=True, tls=tls)
        else:
            server = ldap3.Server(conf.ldap_uri)
        self.connection = ldap3.Connection(server)
        try:
            self.connection.open()
        except ldap3.core.exceptions.LDAPSocketOpenError as error:
            log.error(
                'The connection to "{0}" failed. The following error was raised: {1}'.format(
                    conf.ldap_uri, str(error)))
            raise Forbidden(
                "The connection to the LDAP server failed. Group membership couldn't be obtained.")

    def get_user_membership(self, uid):
        """ Gets the group membership of a user
        :param uid: a string of the uid of the user
        :return: a list of common names of the posixGroups the user is a member of
        """
        ldap_filter = "(memberUid={0})".format(uid)
        # Only get the groups in the base container/OU
        self.connection.search(
            self.base_dn, ldap_filter, search_scope=ldap3.LEVEL, attributes=["cn"])
        groups = self.connection.response
        try:
            return [group["attributes"]["cn"][0] for group in groups]
        except KeyError:
            log.exception(
                "The LDAP groups could not be determined based on the search results "
                'of "{0}"'.format(str(groups)))
            return []


def get_user(request):
    """ Authenticates the user and returns the username and group name
    :param request: a Flask request
    :return: a tuple with a string representing the user name and a set with the user's group
    membership such as ('mprahl', {'factory2', 'devel'})
    """
    if conf.no_auth is True:
        log.debug("Authorization is disabled.")
        return "anonymous", {"packager"}

    if "user" not in g and "groups" not in g:
        get_user_func_name = "get_user_{0}".format(conf.auth_method)
        get_user_func = globals().get(get_user_func_name)
        if not get_user_func:
            raise RuntimeError('The function "{0}" is not implemented'.format(get_user_func_name))
        g.user, g.groups = get_user_func(request)
    return g.user, g.groups
