from ldap3 import Server, Connection, SIMPLE, SYNC, ASYNC, SUBTREE, ALL
from ldap3.core.exceptions import LDAPBindError
from tornado.options import options
from ...utils import json_utils
from .authentication import LoginHandler
import logging

AUTH_LDAP_ATTRS = [
    "cn",
    "cn",
    "department",
    "description",
    "displayname",
    "distinguishedname",
    "givenname",  # firstname
    "mail",
    "memberof",
    "name",  # full name
    "objectclass",
    "samaccountname",
    "sn",  # last name or surname
    "telephonenumber",
    "title",
    "useraccountcontrol",
    "userprincipalname",
    "whencreated",
]
AUTH_LDAP_SUPERUSERS = [
    "pshingavi@directbuy.com",
    "sashford@directbuy.com",
    "patrick.lowe@directbuy.com",
    "fleng@directbuy.com",
    "peter.bunyan@directbuy.com",
]


def _login_(username, password):
    try:
        s = Server(options.LDAP_HOST, get_info=ALL)
        c = Connection(
            s,
            auto_bind=True,
            client_strategy=SYNC,
            user=username.strip(),
            password=password.strip(),
            authentication=SIMPLE,
            check_names=True,
        )
        filter_str = f"(&(!(useraccountcontrol=514))(userprincipalname={c.user}))"
        logging.info(filter_str)
        r = c.search(
            search_base="dc=ucctops,dc=com",
            search_filter=filter_str,
            search_scope=SUBTREE,
            attributes=AUTH_LDAP_ATTRS,
        )
        if r is True:
            user = json_utils.loads(c.entries[0].entry_to_json())
            result = {"username": username, "user": user}
            logging.info("logged in %r", result)
            return result
        result = {"username": username}
        logging.info("logged in %r", result)
        return result
    except LDAPBindError as ex:
        logging.info("login failed: %s", ex)


class LDAP3LoginHandler(LoginHandler):
    def login(self, username, password):
        if username in AUTH_LDAP_SUPERUSERS:
            return _login_(username, password)
