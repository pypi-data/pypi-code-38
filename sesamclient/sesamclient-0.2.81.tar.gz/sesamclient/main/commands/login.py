# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import getpass
import os

from .config import get_configfilename, get_configparser, save_configparser_to_file
from ..utils import print_message

_jwt_configfile_section = "server"
_jwt_configfile_option = "jwt"


def logout_cmd(connection, args):
    myconfigparser = get_configparser()
    current_jwt = myconfigparser.get(_jwt_configfile_section, _jwt_configfile_option, fallback=None)
    if current_jwt is None:
        print_message("The sesam commandline client is not currently logged in.")
    else:
        myconfigparser.remove_option(_jwt_configfile_section, _jwt_configfile_option)
        save_configparser_to_file(myconfigparser)
        print_message("The sesam commandline client is now logged out.")


def login_cmd(connection, args):
    print_message("Login with the email address and password you used to register an account in the Sesam Portal. Warning: this will store the resulting authorization token in the file '%s'." % (
        get_configfilename()
    ))
    myconfigparser = get_configparser()

    email = input("Email: ")
    password = getpass.getpass(prompt="Password:")

    jwt_auth_token = connection.login(email, password)

    if not myconfigparser.has_section(_jwt_configfile_section):
        myconfigparser.add_section(_jwt_configfile_section)

    myconfigparser.set(_jwt_configfile_section, _jwt_configfile_option, jwt_auth_token)
    save_configparser_to_file(myconfigparser)

    print_message(
        "Logged in successfully and stored the new authorization token in the file '%s'." % (
            get_configfilename()
        ))