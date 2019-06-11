# Copyright (c) 2017 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.ldap as ldap

def add_schema_argument_group(parser):
    schema_group = parser.add_argument_group(
        title="LDAP schema arguments",
        description="Set the schema attributes used for LDAP queries.")
    schema_group.add_argument(
        "--rfc2307",
        action="store_true",
        help="Use the standard schema defined in RFC2307. "
            "Cannot be combined with any custom schema arguments.")
    schema_group.add_argument(
        "--custom-group-member-attribute",
        type=str,
        default=None,
        help="The attribute on a group object which contains references to"
            " the members in that group.")
    schema_group.add_argument(
        "--custom-user-group-identifier-attribute",
        type=str,
        default=None,
        help="The attribute on a user that the value of the"
            " group_member_attribute on a group refers to.")
    schema_group.add_argument(
        "--custom-login-name-attribute",
        type=str,
        default=None,
        help="The attribute on a user that identifies their login name.")
    schema_group.add_argument(
        "--custom-group-name-attribute",
        type=str,
        default=None,
        help="The attribute on a group that identifies their name.")
    schema_group.add_argument(
        "--custom-user-object-class",
        type=str,
        default=None,
        help="The class of user objects.")
    schema_group.add_argument(
        "--custom-group-object-class",
        type=str,
        default=None,
        help="The class of group objects.")
    schema_group.add_argument(
        "--custom-uid-number-attribute",
        type=str,
        default=None,
        help="The attribute on a user that identifies their uid number.")
    schema_group.add_argument(
        "--custom-gid-number-attribute",
        type=str,
        default=None,
        help="The attribute on an object that identifies their gid number.")

def parse_schema_arguments(args):
    schema_description = {
        "group_member_attribute": args.custom_group_member_attribute,
        "user_group_identifier_attribute":
            args.custom_user_group_identifier_attribute,
        "login_name_attribute": args.custom_login_name_attribute,
        "group_name_attribute": args.custom_group_name_attribute,
        "user_object_class": args.custom_user_object_class,
        "group_object_class": args.custom_group_object_class,
        "uid_number_attribute": args.custom_uid_number_attribute,
        "gid_number_attribute": args.custom_gid_number_attribute,
    }
    has_custom = any([v is not None for v in schema_description.values()])
    unspecified_custom_args = [
        arg for arg, val in schema_description.items() if val is None
    ]

    if args.rfc2307:
        # Error handling for specifying rfc2307 and custom attributes
        if has_custom:
            raise ValueError(
                "Cannot specify both RFC2307 Schema and custom "
                "attributes. To specify a custom schema, please specify only "
                "--custom_* arguments")
        # Shorthand for easily specifying default RFC2307-mode
        return ("RFC2307", None)

    # rfc2307 and custom attributes were both unspecified
    if set(unspecified_custom_args) == set(schema_description.keys()):
        return (None, None)

    # Error handling for specifying partial custom attribute arguments
    if unspecified_custom_args:
        raise ValueError(
            "Error: All attributes must be specified for custom schemas. "
            "Unspecified arguments: {}".format(unspecified_custom_args))

    return ("CUSTOM", schema_description)

class LdapPostCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_set_settings"
    DESCRIPTION = "Set settings for LDAP interaction"

    @staticmethod
    def options(parser):
        parser.add_argument("--use-ldap", type=str, required=True,
            choices={"true", "false"},
            help="Whether or not to enable the use of the LDAP server on "
            "the cluster.")
        parser.add_argument("--bind-uri", type=str, required=True,
            help="LDAP URI used to bind. Example: "
                "ldap://ldap-server.example.com")
        parser.add_argument("--base-dn", type=str, required=True,
            help="Base DNs (Distinguished Names). Separate multiple DNs using "
            "semicolons. Example: dc=account,dc=example,dc=com")

        # Optional arguments.
        parser.add_argument("--bind-username", type=str, required=False,
            default='', help="Binding users's DN. Default is empty.")
        parser.add_argument("--bind-password", type=str, required=False,
            default=None, help="Password for simple authentication against "
            "LDAP server. If not specified, will use password that is "
            "currently stored on disk.")
        parser.add_argument("--encrypt-connection", type=str,
            default="true", choices={"true", "false"},
            help="If true, LDAP connection must be encrypted using TLS. "
            "Default is true.")

        add_schema_argument_group(parser)

    @staticmethod
    def main(conninfo, credentials, args):
        schema_args = parse_schema_arguments(args)
        if schema_args == (None, None):
            raise ValueError(
                "Please specify --rfc2307 or a custom LDAP schema.")
        print ldap.settings_set_v2(conninfo, credentials,
            args.bind_uri,
            args.base_dn,
            ldap_schema=schema_args[0],
            ldap_schema_description=schema_args[1],
            user=args.bind_username,
            password=args.bind_password,
            use_ldap=qumulo.lib.util.bool_from_string(args.use_ldap),
            encrypt_connection=qumulo.lib.util.bool_from_string(
                args.encrypt_connection))

class LdapGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_get_settings"
    DESCRIPTION = "Get settings for LDAP interaction"

    @staticmethod
    def main(conninfo, credentials, _args):
        print ldap.settings_get_v2(conninfo, credentials)

class LdapPatchCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_update_settings"
    DESCRIPTION = "Update settings for LDAP interaction"

    @staticmethod
    def options(parser):
        parser.add_argument("--use-ldap", type=str, default=None,
            choices={"true", "false"},
            help="Enable or disable the use of standalone LDAP.")
        parser.add_argument("--bind-uri", type=str, default=None,
            help="LDAP URI used to bind. Example: "
                "ldap://ldap-server.example.com")
        parser.add_argument("--base-dn", type=str, default=None,
            help="Base DNs (Distinguished Names). Example: "
            "dc=account,dc=example,dc=com")
        parser.add_argument("--bind-username", type=str, default=None,
            help="Binding users's DN.")
        parser.add_argument("--bind-password", type=str, default=None,
            help="Password for simple authentication against "
            "LDAP server.")
        parser.add_argument("--encrypt-connection", type=str,
            default=None, choices={"true", "false"},
            help="If true, LDAP conenction must be encrypted using TLS.")

        add_schema_argument_group(parser)

    @staticmethod
    def main(conninfo, credentials, args):
        schema_args = parse_schema_arguments(args)
        print ldap.settings_update_v2(conninfo, credentials,
            bind_uri=args.bind_uri,
            base_distinguished_names=args.base_dn,
            ldap_schema=schema_args[0],
            ldap_schema_description=schema_args[1],
            user=args.bind_username,
            password=args.bind_password,
            use_ldap= \
                qumulo.lib.util.bool_from_string(args.use_ldap) \
                if args.use_ldap is not None else None,
            encrypt_connection=qumulo.lib.util.bool_from_string(
                args.encrypt_connection) \
                if args.encrypt_connection is not None else None)

class LdapStatusGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_get_status"
    DESCRIPTION = "Get LDAP client connection states"

    @staticmethod
    def main(conninfo, credentials, _args):
        print ldap.status_get(conninfo, credentials)

class UidNumberToLoginNameGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_uid_number_to_login_name"
    DESCRIPTION = "Get login name from uidNumber using LDAP server"

    @staticmethod
    def options(parser):
        parser.add_argument("--uid-number", type=str, required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.uid_number_to_login_name_get(conninfo, credentials,
            args.uid_number)

class LoginNameToGidNumbersGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_login_name_to_gid_numbers"
    DESCRIPTION = "Query the LDAP server for the gid numbers for all the " \
        "groups of which the given login name is a member. This returns a " \
        "vector of results in the case that the given login name maps to " \
        "multiple uid numbers."

    @staticmethod
    def options(parser):
        parser.add_argument("--login-name", type=str, required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.login_name_to_gid_numbers_get(
            conninfo, credentials, args.login_name)

class LoginNameToUidNumbersGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_login_name_to_uid_numbers"
    DESCRIPTION = "Get the uidNumbers from a login name using the LDAP server"

    @staticmethod
    def options(parser):
        parser.add_argument("--login-name", type=str, required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.login_name_to_uid_numbers_get(
            conninfo, credentials, args.login_name)
