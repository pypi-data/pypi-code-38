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
# Written by Ralph Bean <rbean@redhat.com>
# Written by Matt Prahl <mprahl@redhat.com>
from os import path, environ

import pytest
import mock
from mock import patch, PropertyMock, Mock
import kerberos
import ldap3
from werkzeug.exceptions import Unauthorized as FlaskUnauthorized

import module_build_service.auth
import module_build_service.errors
import module_build_service.config as mbs_config
from module_build_service import app


class TestAuthModule:
    def test_get_user_no_token(self):
        base_dir = path.abspath(path.dirname(__file__))
        client_secrets = path.join(base_dir, "client_secrets.json")
        with patch.dict(
            "module_build_service.app.config",
            {"OIDC_CLIENT_SECRETS": client_secrets, "OIDC_REQUIRED_SCOPE": "mbs-scope"},
        ):
            request = mock.MagicMock()
            request.cookies.return_value = {}

            with pytest.raises(module_build_service.errors.Unauthorized) as cm:
                with app.app_context():
                    module_build_service.auth.get_user(request)
                assert str(cm.value) == "No 'authorization' header found."

    @patch("module_build_service.auth._get_token_info")
    @patch("module_build_service.auth._get_user_info")
    def test_get_user_failure(self, get_user_info, get_token_info):
        base_dir = path.abspath(path.dirname(__file__))
        client_secrets = path.join(base_dir, "client_secrets.json")
        with patch.dict(
            "module_build_service.app.config",
            {"OIDC_CLIENT_SECRETS": client_secrets, "OIDC_REQUIRED_SCOPE": "mbs-scope"},
        ):
            # https://www.youtube.com/watch?v=G-LtddOgUCE
            name = "Joey Jo Jo Junior Shabadoo"
            mocked_get_token_info = {
                "active": False,
                "username": name,
                "scope": ("openid https://id.fedoraproject.org/scope/groups mbs-scope"),
            }
            get_token_info.return_value = mocked_get_token_info

            get_user_info.return_value = {"groups": ["group"]}

            headers = {"authorization": "Bearer foobar"}
            request = mock.MagicMock()
            request.headers.return_value = mock.MagicMock(spec_set=dict)
            request.headers.__getitem__.side_effect = headers.__getitem__
            request.headers.__setitem__.side_effect = headers.__setitem__
            request.headers.__contains__.side_effect = headers.__contains__

            with pytest.raises(module_build_service.errors.Unauthorized) as cm:
                with app.app_context():
                    module_build_service.auth.get_user(request)
                assert str(cm.value) == "OIDC token invalid or expired."

    @pytest.mark.parametrize("allowed_users", (set(), set(["Joey Jo Jo Junior Shabadoo"])))
    @patch.object(mbs_config.Config, "allowed_users", new_callable=PropertyMock)
    @patch("module_build_service.auth._get_token_info")
    @patch("module_build_service.auth._get_user_info")
    def test_get_user_good(self, get_user_info, get_token_info, m_allowed_users, allowed_users):
        m_allowed_users.return_value = allowed_users
        base_dir = path.abspath(path.dirname(__file__))
        client_secrets = path.join(base_dir, "client_secrets.json")
        with patch.dict(
            "module_build_service.app.config",
            {"OIDC_CLIENT_SECRETS": client_secrets, "OIDC_REQUIRED_SCOPE": "mbs-scope"},
        ):
            # https://www.youtube.com/watch?v=G-LtddOgUCE
            name = "Joey Jo Jo Junior Shabadoo"
            mocked_get_token_info = {
                "active": True,
                "username": name,
                "scope": ("openid https://id.fedoraproject.org/scope/groups mbs-scope"),
            }
            get_token_info.return_value = mocked_get_token_info

            get_user_info.return_value = {"groups": ["group"]}

            headers = {"authorization": "Bearer foobar"}
            request = mock.MagicMock()
            request.headers.return_value = mock.MagicMock(spec_set=dict)
            request.headers.__getitem__.side_effect = headers.__getitem__
            request.headers.__setitem__.side_effect = headers.__setitem__
            request.headers.__contains__.side_effect = headers.__contains__

            with app.app_context():
                username, groups = module_build_service.auth.get_user(request)
                username_second_call, groups_second_call = module_build_service.auth.get_user(
                    request)
            assert username == name
            if allowed_users:
                assert groups == set()
            else:
                assert groups == set(get_user_info.return_value["groups"])

            # Test the real auth method has been called just once.
            get_user_info.assert_called_once()
            assert username_second_call == username
            assert groups_second_call == groups

    @patch.object(mbs_config.Config, "no_auth", new_callable=PropertyMock, return_value=True)
    def test_disable_authentication(self, conf_no_auth):
        request = mock.MagicMock()
        username, groups = module_build_service.auth.get_user(request)
        assert username == "anonymous"
        assert groups == {"packager"}

    @patch("module_build_service.auth.client_secrets", None)
    def test_misconfiguring_oidc_client_secrets_should_be_failed(self):
        request = mock.MagicMock()
        with pytest.raises(module_build_service.errors.Forbidden) as cm:
            with app.app_context():
                module_build_service.auth.get_user(request)
            assert str(cm.value) == "OIDC_CLIENT_SECRETS must be set in server config."

    @patch("module_build_service.auth._get_token_info")
    @patch("module_build_service.auth._get_user_info")
    def test_get_required_scope_not_present(self, get_user_info, get_token_info):
        base_dir = path.abspath(path.dirname(__file__))
        client_secrets = path.join(base_dir, "client_secrets.json")
        with patch.dict(
            "module_build_service.app.config",
            {"OIDC_CLIENT_SECRETS": client_secrets, "OIDC_REQUIRED_SCOPE": "mbs-scope"},
        ):
            # https://www.youtube.com/watch?v=G-LtddOgUCE
            name = "Joey Jo Jo Junior Shabadoo"
            mocked_get_token_info = {
                "active": True,
                "username": name,
                "scope": "openid https://id.fedoraproject.org/scope/groups",
            }
            get_token_info.return_value = mocked_get_token_info

            get_user_info.return_value = {"groups": ["group"]}

            headers = {"authorization": "Bearer foobar"}
            request = mock.MagicMock()
            request.headers.return_value = mock.MagicMock(spec_set=dict)
            request.headers.__getitem__.side_effect = headers.__getitem__
            request.headers.__setitem__.side_effect = headers.__setitem__
            request.headers.__contains__.side_effect = headers.__contains__

            with pytest.raises(module_build_service.errors.Unauthorized) as cm:
                with app.app_context():
                    module_build_service.auth.get_user(request)
                assert str(cm.value) == (
                    "Required OIDC scope 'mbs-scope' not present: "
                    "['openid', 'https://id.fedoraproject.org/scope/groups']"
                )

    @patch("module_build_service.auth._get_token_info")
    @patch("module_build_service.auth._get_user_info")
    def test_get_required_scope_not_set_in_cfg(self, get_user_info, get_token_info):
        base_dir = path.abspath(path.dirname(__file__))
        client_secrets = path.join(base_dir, "client_secrets.json")
        with patch.dict("module_build_service.app.config", {"OIDC_CLIENT_SECRETS": client_secrets}):
            # https://www.youtube.com/watch?v=G-LtddOgUCE
            name = "Joey Jo Jo Junior Shabadoo"
            mocked_get_token_info = {
                "active": True,
                "username": name,
                "scope": "openid https://id.fedoraproject.org/scope/groups",
            }
            get_token_info.return_value = mocked_get_token_info

            get_user_info.return_value = {"groups": ["group"]}

            headers = {"authorization": "Bearer foobar"}
            request = mock.MagicMock()
            request.headers.return_value = mock.MagicMock(spec_set=dict)
            request.headers.__getitem__.side_effect = headers.__getitem__
            request.headers.__setitem__.side_effect = headers.__setitem__
            request.headers.__contains__.side_effect = headers.__contains__

            with pytest.raises(module_build_service.errors.Forbidden) as cm:
                with app.app_context():
                    module_build_service.auth.get_user(request)
                assert str(cm.value) == "OIDC_REQUIRED_SCOPE must be set in server config."


class KerberosMockConfig(object):
    def __init__(
        self,
        uri="ldaps://test.example.local:636",
        dn="ou=groups,dc=domain,dc=local",
        kt="/path/to/keytab",
        host="mbs.domain.local",
    ):
        """
        :param uri: a string overriding config.ldap_uri
        :param dn: a string overriding config.ldap_groups_dn
        :param kt: a string overriding config.kerberos_keytab
        :param host: a string overriding config.kerberos_http_host
        """
        self.uri = uri
        self.dn = dn
        self.kt = kt
        self.host = host

    def __enter__(self):
        self.auth_method_p = patch.object(
            mbs_config.Config, "auth_method", new_callable=PropertyMock)
        mocked_auth_method = self.auth_method_p.start()
        mocked_auth_method.return_value = "kerberos"

        self.ldap_uri_p = patch.object(mbs_config.Config, "ldap_uri", new_callable=PropertyMock)
        mocked_ldap_uri = self.ldap_uri_p.start()
        mocked_ldap_uri.return_value = self.uri

        self.ldap_dn_p = patch.object(
            mbs_config.Config, "ldap_groups_dn", new_callable=PropertyMock)
        mocked_ldap_dn = self.ldap_dn_p.start()
        mocked_ldap_dn.return_value = self.dn

        self.kerberos_keytab_p = patch.object(
            mbs_config.Config, "kerberos_keytab", new_callable=PropertyMock)
        mocked_kerberos_keytab = self.kerberos_keytab_p.start()
        mocked_kerberos_keytab.return_value = self.kt

        self.kerberos_http_host_p = patch.object(
            mbs_config.Config, "kerberos_http_host", new_callable=PropertyMock)
        mocked_kerberos_http_host = self.kerberos_http_host_p.start()
        mocked_kerberos_http_host.return_value = self.host

    def __exit__(self, *args):
        self.auth_method_p.stop()
        self.ldap_uri_p.stop()
        self.ldap_dn_p.stop()
        self.kerberos_keytab_p.stop()
        self.kerberos_http_host_p.stop()


class TestAuthModuleKerberos:
    @pytest.mark.parametrize("allowed_users", (set(), set(["mprahl"])))
    @patch("kerberos.authGSSServerInit", return_value=(kerberos.AUTH_GSS_COMPLETE, object()))
    @patch("kerberos.authGSSServerStep", return_value=kerberos.AUTH_GSS_COMPLETE)
    @patch("kerberos.authGSSServerResponse", return_value="STOKEN")
    @patch("kerberos.authGSSServerUserName", return_value="mprahl@EXAMPLE.ORG")
    @patch("kerberos.authGSSServerClean")
    @patch("kerberos.getServerPrincipalDetails")
    @patch.dict("os.environ")
    @patch("module_build_service.auth.stack")
    @patch.object(mbs_config.Config, "allowed_users", new_callable=PropertyMock)
    def test_get_user_kerberos(
        self, m_allowed_users, stack, principal, clean, name, response, step, init, allowed_users
    ):
        """
        Test that authentication works with Kerberos and LDAP
        """
        m_allowed_users.return_value = allowed_users
        mock_top = Mock()
        stack.return_value = mock_top

        headers = {"Authorization": "foobar"}
        request = mock.MagicMock()
        request.headers.return_value = mock.MagicMock(spec_set=dict)
        request.headers.__getitem__.side_effect = headers.__getitem__
        request.headers.__setitem__.side_effect = headers.__setitem__
        request.headers.__contains__.side_effect = headers.__contains__

        # Create the mock LDAP instance
        server = ldap3.Server("ldaps://test.domain.local")
        connection = ldap3.Connection(server, client_strategy=ldap3.MOCK_SYNC)
        base_dn = "dc=domain,dc=local"
        factory_group_attrs = {
            "objectClass": ["top", "posixGroup"],
            "memberUid": ["mprahl", "tbrady"],
            "gidNumber": 1234,
            "cn": ["factory2-devs"],
        }
        devs_group_attrs = {
            "objectClass": ["top", "posixGroup"],
            "memberUid": ["mprahl", "mikeb"],
            "gidNumber": 1235,
            "cn": ["devs"],
        }
        athletes_group_attrs = {
            "objectClass": ["top", "posixGroup"],
            "memberUid": ["tbrady", "rgronkowski"],
            "gidNumber": 1236,
            "cn": ["athletes"],
        }
        mprahl_attrs = {
            "memberOf": ["cn=Employee,ou=groups,{0}".format(base_dn)],
            "uid": ["mprahl"],
            "cn": ["mprahl"],
            "objectClass": ["top", "person"],
        }
        connection.strategy.add_entry(
            "cn=factory2-devs,ou=groups,{0}".format(base_dn), factory_group_attrs
        )
        connection.strategy.add_entry(
            "cn=athletes,ou=groups,{0}".format(base_dn), athletes_group_attrs
        )
        connection.strategy.add_entry("cn=devs,ou=groups,{0}".format(base_dn), devs_group_attrs)
        connection.strategy.add_entry("cn=mprahl,ou=users,{0}".format(base_dn), mprahl_attrs)

        # If the user is in allowed_users, then group membership is not checked, and an empty set
        # is just returned for the groups
        if allowed_users:
            expected_groups = set()
        else:
            expected_groups = {"devs", "factory2-devs"}

        with patch("ldap3.Connection") as mock_ldap_con, KerberosMockConfig():
            mock_ldap_con.return_value = connection
            assert module_build_service.auth.get_user_kerberos(request) == (
                "mprahl", expected_groups)

    def test_auth_header_not_set(self):
        """
        Test that an Unauthorized exception is returned when there is no authorization header
        set.
        """
        headers = {}
        request = mock.MagicMock()
        request.headers.return_value = mock.MagicMock(spec_set=dict)
        request.headers.__getitem__.side_effect = headers.__getitem__
        request.headers.__setitem__.side_effect = headers.__setitem__
        request.headers.__contains__.side_effect = headers.__contains__

        with KerberosMockConfig():
            try:
                module_build_service.auth.get_user_kerberos(request)
                assert False, "Unauthorized error not raised"
            except FlaskUnauthorized as error:
                assert error.response.www_authenticate.to_header().strip() == "Negotiate"
                assert error.response.status == "401 UNAUTHORIZED"

    @patch.dict(environ)
    def test_keytab_not_set(self):
        """
        Test that authentication fails when the keytab is not set
        """
        if "KRB5_KTNAME" in environ:
            del environ["KRB5_KTNAME"]

        headers = {"Authorization": "foobar"}
        request = mock.MagicMock()
        request.headers.return_value = mock.MagicMock(spec_set=dict)
        request.headers.__getitem__.side_effect = headers.__getitem__
        request.headers.__setitem__.side_effect = headers.__setitem__
        request.headers.__contains__.side_effect = headers.__contains__

        with KerberosMockConfig(kt=""):
            try:
                module_build_service.auth.get_user_kerberos(request)
                assert False, "Unauthorized error not raised"
            except module_build_service.errors.Unauthorized as error:
                assert str(error) == (
                    'Kerberos: set the config value of "KERBEROS_KEYTAB" '
                    'or the environment variable "KRB5_KTNAME" to your keytab file'
                )

    # Set the return value to something not 0 (continue) or 1 (complete)
    @patch("kerberos.authGSSServerInit", return_value=(100, object()))
    @patch("kerberos.authGSSServerStep", return_value=kerberos.AUTH_GSS_COMPLETE)
    @patch("kerberos.authGSSServerResponse", return_value="STOKEN")
    @patch("kerberos.authGSSServerUserName", return_value="mprahl@EXAMPLE.ORG")
    @patch("kerberos.authGSSServerClean")
    @patch("kerberos.getServerPrincipalDetails")
    @patch.dict("os.environ")
    @patch("module_build_service.auth.stack")
    def test_get_user_kerberos_invalid_ticket(
        self, stack, principal, clean, name, response, step, init
    ):
        """
        Test that authentication fails with an invalid Kerberos ticket
        """
        mock_top = Mock()
        stack.return_value = mock_top

        headers = {"Authorization": "foobar"}
        request = mock.MagicMock()
        request.headers.return_value = mock.MagicMock(spec_set=dict)
        request.headers.__getitem__.side_effect = headers.__getitem__
        request.headers.__setitem__.side_effect = headers.__setitem__
        request.headers.__contains__.side_effect = headers.__contains__

        with KerberosMockConfig():
            try:
                module_build_service.auth.get_user_kerberos(request)
                assert False, "Forbidden error not raised"
            except module_build_service.errors.Forbidden as error:
                assert str(error) == ("Invalid Kerberos ticket")
