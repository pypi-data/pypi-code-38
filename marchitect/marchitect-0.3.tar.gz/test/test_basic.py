#!/usr/bin/env python

import glob
import os
from pathlib import Path
import random
import string
import sys
import tempfile
from typing import (
    Any,
    Dict,
    Tuple,
    Type,
)
import textwrap
import unittest
from unittest.mock import patch

from ssh2.session import Session  # pylint: disable=E0611

from marchitect.prefab import Apt, FolderExists, LineInFile, Pip3
from marchitect.site_plan import (
    Step,
    SitePlan,
)
from marchitect.util import dict_deep_update
from marchitect.whiteprint import (
    ExecOutput,
    RemoteExecError,
    RemoteFileNotFoundError,
    RemoteTargetDirError,
    Whiteprint,
)


def _mk_siteplan_from_env_var_ssh_creds(sp_cls: Type[SitePlan]) -> SitePlan:
    user = os.getenv('SSH_USER')
    host = os.getenv('SSH_HOST')
    port = int(os.getenv('SSH_PORT', '22'))
    password = os.getenv('SSH_PASSWORD')
    private_key = os.getenv('SSH_PRIVATE_KEY')
    private_key_password = os.getenv('SSH_PRIVATE_KEY_PASSWORD')

    if user is None:
        print('SSH_USER env var must be set.', file=sys.stderr)
        sys.exit(1)
    if host is None:
        print('SSH_HOST env var must be set.', file=sys.stderr)
        sys.exit(1)
    if password is None and private_key is None:
        print(
            'SSH_PASSWORD or SSH_PRIVATE_KEY env var must be set.',
            file=sys.stderr)
        sys.exit(1)

    if password:
        return sp_cls.from_password(host, port, user, password, {}, [])
    else:
        return sp_cls.from_private_key(
            host, port, user, private_key, private_key_password, {}, [])


def _mk_session_from_env_var_ssh_creds() -> Session:
    return _mk_siteplan_from_env_var_ssh_creds(SitePlan).connect_func()


def create_blank_whiteprint() -> Whiteprint:
    return Whiteprint(_mk_session_from_env_var_ssh_creds())


class WhiteprintSimple(Whiteprint):
    def _execute(self, mode: str):
        if mode == 'install':
            self.exec('ls /')
    def _validate(self, mode: str):
        return None


class WhiteprintMissingRequiredCfg(Whiteprint):  # pylint: disable=W0223
    required_cfg = ['name']


class WhiteprintWriteTemp(Whiteprint):

    default_cfg = {
        'value': 'alice',
    }

    temp_file_path = '/tmp/architect_test_wp_write_temp'

    def _execute(self, mode: str):
        if mode == 'install':
            self.scp_up_template_from_str(
                '{{ value }}',
                self.temp_file_path,
            )
        elif mode == 'clean':
            self.exec('rm %s' % self.temp_file_path)
    def _validate(self, mode: str):
        return None


def temp_file_path() -> str:
    """Returns a possible temporary file path. Does not create the file."""
    filename = 'architect_test_' + \
               ''.join(random.choices(string.ascii_letters, k=8))
    return os.path.join(tempfile.gettempdir(), filename)


def random_data(size: int = 1024) -> str:
    """Return string is made of printable characters."""
    return ''.join(random.choices(string.printable, k=size))


def mk_random_temp_file(size: int = 1024) -> Tuple[str, str]:
    """Returns (temp file path, temp file contents)."""
    path = temp_file_path()
    data = random_data(size).encode('ascii')
    with open(path, 'wb') as f:
        f.write(data)
    return path, data


class TestBasic(unittest.TestCase):

    @staticmethod
    def glob_test_files():
        return glob.glob(
            os.path.join(tempfile.gettempdir(), 'architect_test_*'))

    def setUp(self):
        for path in self.glob_test_files():
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)

    def tearDown(self):
        leftovers = self.glob_test_files()
        if leftovers:
            for leftover in leftovers:
                if os.path.isdir(leftover):
                    os.rmdir(leftover)
                else:
                    os.remove(leftover)
            assert False, 'Bad clean up of temp files: %r' % leftovers

    def test_deep_dict_update(self):
        a = {'a': 1, 'b': {'c': 2}, 'd': 3, 'z': {}}
        b = {'a': 4, 'b': {'c': 5, 'e': 7}, 'z': 100}
        dict_deep_update(a, b)
        assert a['a'] == 4
        assert a['d'] == 3
        assert a['b']['c'] == 5
        assert a['b']['e'] == 7
        assert a['z'] == 100

    def test_whiteprint_missing_required_cfg(self):
        session = _mk_session_from_env_var_ssh_creds()
        with self.assertRaises(KeyError) as ctx:
            WhiteprintMissingRequiredCfg(session)
        assert ctx.exception.args[0] == "Cfg 'name' must be set"

    def test_whiteprint_exec(self):
        wp = create_blank_whiteprint()
        res = wp.exec('ls /')
        assert len(res.stdout) > 0
        assert res.stderr == b''
        assert res.exit_status == 0

        res = wp.exec('echo hello there')
        assert res.stdout == b'hello there\n'
        assert res.stderr == b''
        assert res.exit_status == 0

        res = wp.exec('echo hello there 1>&2', error_ok=True)
        assert res.stdout == b''
        assert res.stderr == b'hello there\n'
        assert res.exit_status == 0

        res = wp.exec('ls /does-not-exist', error_ok=True)
        assert res.stdout == b''
        assert res.stderr == \
            b"ls: cannot access '/does-not-exist': No such file or directory\n"
        assert res.exit_status == 2

        # Test exception raises
        with self.assertRaises(RemoteExecError) as ctx:
            wp.exec('ls /does-not-exist')
        assert ctx.exception.exec_output.exit_status == 2
        assert ctx.exception.exec_output.stdout == b''
        assert ctx.exception.exec_output.stderr == \
            b"ls: cannot access '/does-not-exist': No such file or directory\n"

    def test_whiteprint_exec_large_output(self):
        wp = create_blank_whiteprint()

        data = random_data(size=1_000_000).encode('ascii')
        dest_temp_path = temp_file_path()
        wp.scp_up_from_bytes(data, dest_temp_path)

        res = wp.exec('cat %s' % dest_temp_path)
        assert res.stdout == data
        assert res.stderr == b''
        assert res.exit_status == 0

        os.remove(dest_temp_path)

    def test_whiteprint_stdin(self):
        wp = create_blank_whiteprint()
        res = wp.exec('cat', stdin=b'test')
        assert res.stdout == b'test'

    def test_whiteprint_scp(self):
        wp = create_blank_whiteprint()

        # Upload file
        src_temp_path, data = mk_random_temp_file(1_000_000)
        dest_temp_path = temp_file_path()
        wp.scp_up(src_temp_path, dest_temp_path)

        # Download that same file
        round_trip_path = temp_file_path()
        wp.scp_down(dest_temp_path, round_trip_path)

        # Make sure the file round tripped
        with open(round_trip_path, 'rb') as f:
            d1 = f.read()
            assert d1 == data

        # Delete temp files
        os.remove(src_temp_path)
        os.remove(dest_temp_path)
        os.remove(round_trip_path)

    def test_whiteprint_scp_bytes(self):
        wp = create_blank_whiteprint()

        data = random_data().encode('ascii')
        dest_temp_path = temp_file_path()
        wp.scp_up_from_bytes(data, dest_temp_path)

        round_trip_data = wp.scp_down_to_bytes(dest_temp_path)
        assert data == round_trip_data
        os.remove(dest_temp_path)

    def test_whiteprint_scp_overwrite(self):
        wp = create_blank_whiteprint()

        data = random_data().encode('ascii')
        dest_temp_path = temp_file_path()
        wp.scp_up_from_bytes(data, dest_temp_path)
        wp.scp_up_from_bytes(data, dest_temp_path)

        round_trip_data = wp.scp_down_to_bytes(dest_temp_path)
        assert data == round_trip_data
        os.remove(dest_temp_path)

    def test_whiteprint_scp_up_error(self):
        wp = create_blank_whiteprint()

        # Try uploading to a bad target folder
        data = random_data().encode('ascii')
        with self.assertRaises(RemoteTargetDirError) as ctx:
            wp.scp_up_from_bytes(data, '/does-not-exist/file-path')
        assert ctx.exception.args[0] == \
            "'/does-not-exist/file-path' is a bad path."

        # Try uploading a file that doesn't exist locally
        with self.assertRaises(FileNotFoundError):
            wp.scp_up('/does-not-exist-locally/file-path', '/not-relevant')

    def test_whiteprint_scp_down_error(self):
        wp = create_blank_whiteprint()

        # Try downloading a non-existent file
        with self.assertRaises(RemoteFileNotFoundError) as ctx:
            wp.scp_down_to_bytes('/does-not-exist')
        assert ctx.exception.args[0] == "'/does-not-exist' not found."

        with self.assertRaises(RemoteFileNotFoundError) as ctx:
            wp.scp_down('/does-not-exist', '/tmp/will-not-be-created')
        assert ctx.exception.args[0] == "'/does-not-exist' not found."

        # Try downloading to a bad local path
        data = random_data().encode('ascii')
        dest_temp_path = temp_file_path()
        wp.scp_up_from_bytes(data, dest_temp_path)

        with self.assertRaises(FileNotFoundError):
            wp.scp_down(dest_temp_path, '/does-not-exist/file-path')
        os.remove(dest_temp_path)

    def test_whiteprint_scp_template(self):
        wp = create_blank_whiteprint()

        src_temp_path = temp_file_path()
        with open(src_temp_path, 'w') as f:
            f.write('{{ name }}')

        wp.cfg['name'] = 'Alice'
        dest_temp_path = temp_file_path()
        wp.scp_up_template(src_temp_path, dest_temp_path)

        dest_data = wp.scp_down_to_bytes(dest_temp_path)
        assert dest_data == b'Alice'

        # Test cfg override
        wp.scp_up_template(
            src_temp_path, dest_temp_path, cfg_override=dict(name='Bob'))
        dest_data = wp.scp_down_to_bytes(dest_temp_path)
        assert dest_data == b'Bob'

        wp.scp_up_template_from_str(
            '{{ name }} {{ name }}', dest_temp_path, cfg_override=dict(name='Eve'))
        dest_data = wp.scp_down_to_bytes(dest_temp_path)
        assert dest_data == b'Eve Eve'

        os.remove(src_temp_path)
        os.remove(dest_temp_path)

    def test_whiteprint_rsrc_lookup(self):
        session = _mk_session_from_env_var_ssh_creds()
        wp = Whiteprint(session, rsrc_path=Path(tempfile.tempdir))

        src_temp_path, _ = mk_random_temp_file(1_000)
        dest_temp_path = temp_file_path()
        wp.scp_up(os.path.basename(src_temp_path), dest_temp_path)

        os.remove(src_temp_path)
        os.remove(dest_temp_path)

    def test_whiteprint_execute_mode(self):
        session = _mk_session_from_env_var_ssh_creds()
        wp = WhiteprintSimple(session)
        wp.execute('install')
        wp.execute('update')
        wp.execute('clean')
        wp.execute('start')
        wp.execute('stop')
        wp.execute('--random--')

    def test_siteplan(self):
        from distutils.version import LooseVersion  # pylint: disable=E0401,E0611
        class WhiteprintAssertTargetCfg(Whiteprint):
            def _execute(self, mode: str):
                assert isinstance(self.cfg['_target'], dict)
                assert isinstance(self.cfg['_target']['distro'], str)
                assert isinstance(
                    self.cfg['_target']['distro_version'], LooseVersion)
                assert isinstance(self.cfg['_target']['hostname'], str)
                assert isinstance(self.cfg['_target']['fqdn'], str)
                assert isinstance(self.cfg['_target']['cpu_count'], int)
            def _validate(self, mode: str):
                return None

        class SitePlanSimple(SitePlan):
            plan = [
                Step(WhiteprintAssertTargetCfg),
            ]

        sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
        sp.install()

    def test_siteplan_config_overrides(self):
        class SitePlanSimple(SitePlan):
            plan = [
                Step(WhiteprintWriteTemp),
            ]

        sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
        sp.install()

        wp = create_blank_whiteprint()
        assert b'alice' == \
            wp.scp_down_to_bytes(WhiteprintWriteTemp.temp_file_path)

        # Test siteplan default override
        sp.plan[0].cfg['value'] = 'bob'
        sp.install()
        assert b'bob' == \
            wp.scp_down_to_bytes(WhiteprintWriteTemp.temp_file_path)

        # Test siteplan explicit override
        sp.cfg[WhiteprintWriteTemp] = {'value': 'eve'}
        sp.install()
        assert b'eve' == \
            wp.scp_down_to_bytes(WhiteprintWriteTemp.temp_file_path)

        # Test siteplan explicit override by alias
        sp.plan[0].alias = 'simple'
        sp.cfg['simple'] = {'value': 'foo'}
        sp.install()
        assert b'foo' == \
            wp.scp_down_to_bytes(WhiteprintWriteTemp.temp_file_path)

        sp.clean()

    def test_prefab_apt(self):
        class WhiteprintPrefab(Whiteprint):
            prefabs = [
                Apt(['python3', 'python3-dev']),
            ]

            def _execute(self, mode: str):
                pass
            def _validate(self, mode: str):
                return None

        class SitePlanSimple(SitePlan):
            plan = [
                Step(WhiteprintPrefab),
            ]

        # Test installation
        res = ExecOutput(0, b'', b'')
        with patch.object(Whiteprint, 'exec', return_value=res) as mock_method:
            sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
            sp.target_host_cfg = {}
            assert sp.install() is None
            mock_method.assert_called_once_with('apt install -y python3 python3-dev')

        # Test correct installation
        stdout = textwrap.dedent("""\
            python3/bionic-updates 3.6.7-1~18.04 amd64 [upgradable from: 3.6.5-3ubuntu1]
            python3-dev/bionic-updates 3.6.7-1~18.04 amd64 [upgradable from: 3.6.5-3ubuntu1]
            """).encode('utf-8')
        res = ExecOutput(0, stdout, b'')
        with patch.object(Whiteprint, 'exec', return_value=res) as mock_method:
            sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
            sp.target_host_cfg = {}
            assert sp.validate('install') is None
            mock_method.assert_called_once_with('apt -qq list python3 python3-dev')

        # Try bad installation
        stdout = textwrap.dedent("""\
            python3/bionic-updates 3.6.7-1~18.04 amd64 [upgradable from: 3.6.5-3ubuntu1]
            """).encode('utf-8')
        res = ExecOutput(0, stdout, b'')
        with patch.object(Whiteprint, 'exec', return_value=res) as mock_method:
            sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
            sp.target_host_cfg = {}
            assert sp.validate('install') == "Apt package 'python3-dev' missing."
            mock_method.assert_called_once_with('apt -qq list python3 python3-dev')

    def test_prefab_pip3(self):
        class WhiteprintPrefab(Whiteprint):
            prefabs = [
                Pip3(['stone', 'marchitect']),
            ]

            def _execute(self, mode: str):
                pass
            def _validate(self, mode: str):
                return None

        class SitePlanSimple(SitePlan):
            plan = [
                Step(WhiteprintPrefab),
            ]

        # Test installation
        res = ExecOutput(0, b'', b'')
        with patch.object(Whiteprint, 'exec', return_value=res) as mock_method:
            sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
            sp.target_host_cfg = {}
            assert sp.install() is None
            mock_method.assert_called_once_with('pip3 install stone marchitect')

        # Test correct installation
        stdout = textwrap.dedent("""\
            Name: stone
            Version: 0.1
            --
            Name: marchitect
            Version: 0.1
            """).encode('utf-8')
        res = ExecOutput(0, stdout, b'')
        with patch.object(Whiteprint, 'exec', return_value=res) as mock_method:
            sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
            sp.target_host_cfg = {}
            assert sp.validate('install') is None
            mock_method.assert_called_once_with('pip3 show stone marchitect')

        # Try bad installation
        stdout = textwrap.dedent("""\
            Name: stone
            Version: 0.1
            """).encode('utf-8')
        res = ExecOutput(0, stdout, b'')
        with patch.object(Whiteprint, 'exec', return_value=res) as mock_method:
            sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
            sp.target_host_cfg = {}
            assert sp.validate('install') == "Pip3 package 'marchitect' missing."
            mock_method.assert_called_once_with('pip3 show stone marchitect')

    def test_prefab_folder_exists(self):
        path = temp_file_path()
        class WhiteprintPrefab(Whiteprint):
            prefabs = [
                FolderExists(path),
            ]

            def _execute(self, mode: str):
                pass
            def _validate(self, mode: str):
                return None

        class SitePlanSimple(SitePlan):
            plan = [
                Step(WhiteprintPrefab),
            ]

        sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
        sp.execute('clean')
        sp.validate('clean')

        # Test folder creation
        sp.execute('install')
        assert os.path.exists(path)
        sp.validate('install')

        # Test mode check
        WhiteprintPrefab.prefabs[0].mode = 0o557
        res = sp.validate('install')
        assert res == "expected '%s' to have mode 557, got 775." % path

        # Test owner check
        WhiteprintPrefab.prefabs[0].group = 'theempire'
        res = sp.validate('install')
        assert res.startswith("expected '%s' to have group 'theempire', got " % path)

        # Test group check
        WhiteprintPrefab.prefabs[0].owner = 'darthvader'
        res = sp.validate('install')
        assert res.startswith("expected '%s' to have owner 'darthvader', got " % path)

        # Test clean
        sp.execute('clean')
        assert not os.path.exists(path)

        # Test missing folder
        res = sp.validate('install')
        assert res == "'{}' does not exist.".format(path)

        # Test file in place of directory
        open(path, 'w').close()
        res = sp.validate('install')
        assert res == "'%s' is not a directory." % path
        sp.execute('clean')
        assert not os.path.exists(path)

        # Test mode set on create
        WhiteprintPrefab.prefabs[0].group = None
        WhiteprintPrefab.prefabs[0].owner = None
        WhiteprintPrefab.prefabs[0].mode = 0o557
        sp.execute('install')
        sp.validate('install')

        # Test remove_on_clean flag
        WhiteprintPrefab.prefabs[0].remove_on_clean = False
        sp.execute('clean')
        assert os.path.exists(path)
        WhiteprintPrefab.prefabs[0].remove_on_clean = True
        sp.execute('clean')
        assert not os.path.exists(path)

    def test_computed_prefabs(self):
        path1 = temp_file_path()
        path2 = temp_file_path()

        class WhiteprintPrefab(Whiteprint):
            prefabs = [
                FolderExists(path1),
            ]
            @classmethod
            def _compute_prefabs(cls, cfg: Dict[str, Any]):
                return [FolderExists(cfg['path'])]
            def _execute(self, mode: str):
                pass
            def _validate(self, mode: str):
                return None

        class SitePlanSimple(SitePlan):
            plan = [
                Step(WhiteprintPrefab),
            ]

        sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
        sp.cfg[WhiteprintPrefab] = {'path': path2}
        sp.execute('install')
        assert os.path.exists(path1)
        assert os.path.exists(path2)
        sp.execute('clean')
        assert not os.path.exists(path1)
        assert not os.path.exists(path1)

    def test_prefab_line_in_file(self):
        path = temp_file_path()
        contents = 'ab c\'"'
        class WhiteprintPrefab(Whiteprint):
            prefabs = [
                LineInFile(path, contents),
            ]

            def _execute(self, mode: str):
                pass
            def _validate(self, mode: str):
                return None

        class SitePlanSimple(SitePlan):
            plan = [
                Step(WhiteprintPrefab),
            ]

        sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)

        # Test that we're clean to begin with
        sp.validate('clean')

        # Test write over non-existent file
        sp.execute('install')
        with open(path) as f:
            assert f.read() == contents + '\n'
        sp.validate('install')

        # Test cleaning process
        sp.execute('clean')
        sp.validate('clean')
        os.remove(path)

        # Test with existing content
        dummy_line = '\'test line"""'
        with open(path, 'w') as f:
            f.write(dummy_line)
            f.write('\n')
        sp.validate('clean')

        # Test append to existing file
        sp.execute('install')
        with open(path) as f:
            assert f.read() == dummy_line + '\n' + contents + '\n'

        # Test proper removal of single line
        sp.clean()
        sp.validate('clean')
        with open(path) as f:
            assert f.read() == dummy_line + '\n'
        os.remove(path)

    def test_one_off_exec(self):
        class SitePlanSimple(SitePlan):
            pass
        sp = _mk_siteplan_from_env_var_ssh_creds(SitePlanSimple)
        res = sp.one_off_exec('echo hello world')
        assert res.exit_status == 0
        assert res.stdout == b'hello world\n'


if __name__ == '__main__':
    unittest.main()
