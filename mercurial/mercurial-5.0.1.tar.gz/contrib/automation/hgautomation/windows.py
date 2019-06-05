# windows.py - Automation specific to Windows
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

import os
import pathlib
import re
import subprocess
import tempfile

from .winrm import (
    run_powershell,
)


# PowerShell commands to activate a Visual Studio 2008 environment.
# This is essentially a port of vcvarsall.bat to PowerShell.
ACTIVATE_VC9_AMD64 = r'''
Write-Output "activating Visual Studio 2008 environment for AMD64"
$root = "$env:LOCALAPPDATA\Programs\Common\Microsoft\Visual C++ for Python\9.0"
$Env:VCINSTALLDIR = "${root}\VC\"
$Env:WindowsSdkDir = "${root}\WinSDK\"
$Env:PATH = "${root}\VC\Bin\amd64;${root}\WinSDK\Bin\x64;${root}\WinSDK\Bin;$Env:PATH"
$Env:INCLUDE = "${root}\VC\Include;${root}\WinSDK\Include;$Env:PATH"
$Env:LIB = "${root}\VC\Lib\amd64;${root}\WinSDK\Lib\x64;$Env:LIB"
$Env:LIBPATH = "${root}\VC\Lib\amd64;${root}\WinSDK\Lib\x64;$Env:LIBPATH"
'''.lstrip()

ACTIVATE_VC9_X86 = r'''
Write-Output "activating Visual Studio 2008 environment for x86"
$root = "$env:LOCALAPPDATA\Programs\Common\Microsoft\Visual C++ for Python\9.0"
$Env:VCINSTALLDIR = "${root}\VC\"
$Env:WindowsSdkDir = "${root}\WinSDK\"
$Env:PATH = "${root}\VC\Bin;${root}\WinSDK\Bin;$Env:PATH"
$Env:INCLUDE = "${root}\VC\Include;${root}\WinSDK\Include;$Env:INCLUDE"
$Env:LIB = "${root}\VC\Lib;${root}\WinSDK\Lib;$Env:LIB"
$Env:LIBPATH = "${root}\VC\lib;${root}\WinSDK\Lib:$Env:LIBPATH"
'''.lstrip()

HG_PURGE = r'''
$Env:PATH = "C:\hgdev\venv-bootstrap\Scripts;$Env:PATH"
Set-Location C:\hgdev\src
hg.exe --config extensions.purge= purge --all
if ($LASTEXITCODE -ne 0) {
    throw "process exited non-0: $LASTEXITCODE"
}
Write-Output "purged Mercurial repo"
'''

HG_UPDATE_CLEAN = r'''
$Env:PATH = "C:\hgdev\venv-bootstrap\Scripts;$Env:PATH"
Set-Location C:\hgdev\src
hg.exe --config extensions.purge= purge --all
if ($LASTEXITCODE -ne 0) {{
    throw "process exited non-0: $LASTEXITCODE"
}}
hg.exe update -C {revision}
if ($LASTEXITCODE -ne 0) {{
    throw "process exited non-0: $LASTEXITCODE"
}}
hg.exe log -r .
Write-Output "updated Mercurial working directory to {revision}"
'''.lstrip()

BUILD_INNO = r'''
Set-Location C:\hgdev\src
$python = "C:\hgdev\python27-{arch}\python.exe"
C:\hgdev\python37-x64\python.exe contrib\packaging\inno\build.py --python $python
if ($LASTEXITCODE -ne 0) {{
    throw "process exited non-0: $LASTEXITCODE"
}}
'''.lstrip()

BUILD_WHEEL = r'''
Set-Location C:\hgdev\src
C:\hgdev\python27-{arch}\Scripts\pip.exe wheel --wheel-dir dist .
if ($LASTEXITCODE -ne 0) {{
    throw "process exited non-0: $LASTEXITCODE"
}}
'''

BUILD_WIX = r'''
Set-Location C:\hgdev\src
$python = "C:\hgdev\python27-{arch}\python.exe"
C:\hgdev\python37-x64\python.exe contrib\packaging\wix\build.py --python $python {extra_args}
if ($LASTEXITCODE -ne 0) {{
    throw "process exited non-0: $LASTEXITCODE"
}}
'''

RUN_TESTS = r'''
C:\hgdev\MinGW\msys\1.0\bin\sh.exe --login -c "cd /c/hgdev/src/tests && /c/hgdev/{python_path}/python.exe run-tests.py {test_flags}"
if ($LASTEXITCODE -ne 0) {{
    throw "process exited non-0: $LASTEXITCODE"
}}
'''


def get_vc_prefix(arch):
    if arch == 'x86':
        return ACTIVATE_VC9_X86
    elif arch == 'x64':
        return ACTIVATE_VC9_AMD64
    else:
        raise ValueError('illegal arch: %s; must be x86 or x64' % arch)


def fix_authorized_keys_permissions(winrm_client, path):
    commands = [
        '$ErrorActionPreference = "Stop"',
        'Repair-AuthorizedKeyPermission -FilePath %s -Confirm:$false' % path,
        r'icacls %s /remove:g "NT Service\sshd"' % path,
    ]

    run_powershell(winrm_client, '\n'.join(commands))


def synchronize_hg(hg_repo: pathlib.Path, revision: str, ec2_instance):
    """Synchronize local Mercurial repo to remote EC2 instance."""

    winrm_client = ec2_instance.winrm_client

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)

        ssh_dir = temp_dir / '.ssh'
        ssh_dir.mkdir()
        ssh_dir.chmod(0o0700)

        # Generate SSH key to use for communication.
        subprocess.run([
            'ssh-keygen', '-t', 'rsa', '-b', '4096', '-N', '',
            '-f', str(ssh_dir / 'id_rsa')],
            check=True, capture_output=True)

        # Add it to ~/.ssh/authorized_keys on remote.
        # This assumes the file doesn't already exist.
        authorized_keys = r'c:\Users\Administrator\.ssh\authorized_keys'
        winrm_client.execute_cmd(r'mkdir c:\Users\Administrator\.ssh')
        winrm_client.copy(str(ssh_dir / 'id_rsa.pub'), authorized_keys)
        fix_authorized_keys_permissions(winrm_client, authorized_keys)

        public_ip = ec2_instance.public_ip_address

        ssh_config = temp_dir / '.ssh' / 'config'

        with open(ssh_config, 'w', encoding='utf-8') as fh:
            fh.write('Host %s\n' % public_ip)
            fh.write('  User Administrator\n')
            fh.write('  StrictHostKeyChecking no\n')
            fh.write('  UserKnownHostsFile %s\n' % (ssh_dir / 'known_hosts'))
            fh.write('  IdentityFile %s\n' % (ssh_dir / 'id_rsa'))

        env = dict(os.environ)
        env['HGPLAIN'] = '1'
        env['HGENCODING'] = 'utf-8'

        hg_bin = hg_repo / 'hg'

        res = subprocess.run(
            ['python2.7', str(hg_bin), 'log', '-r', revision, '-T', '{node}'],
            cwd=str(hg_repo), env=env, check=True, capture_output=True)

        full_revision = res.stdout.decode('ascii')

        args = [
            'python2.7', hg_bin,
            '--config', 'ui.ssh=ssh -F %s' % ssh_config,
            '--config', 'ui.remotecmd=c:/hgdev/venv-bootstrap/Scripts/hg.exe',
            'push', '-r', full_revision, 'ssh://%s/c:/hgdev/src' % public_ip,
        ]

        subprocess.run(args, cwd=str(hg_repo), env=env, check=True)

        run_powershell(winrm_client,
                       HG_UPDATE_CLEAN.format(revision=full_revision))

        # TODO detect dirty local working directory and synchronize accordingly.


def purge_hg(winrm_client):
    """Purge the Mercurial source repository on an EC2 instance."""
    run_powershell(winrm_client, HG_PURGE)


def find_latest_dist(winrm_client, pattern):
    """Find path to newest file in dist/ directory matching a pattern."""

    res = winrm_client.execute_ps(
        r'$v = Get-ChildItem -Path C:\hgdev\src\dist -Filter "%s" '
        '| Sort-Object LastWriteTime -Descending '
        '| Select-Object -First 1\n'
        '$v.name' % pattern
    )
    return res[0]


def copy_latest_dist(winrm_client, pattern, dest_path):
    """Copy latest file matching pattern in dist/ directory.

    Given a WinRM client and a file pattern, find the latest file on the remote
    matching that pattern and copy it to the ``dest_path`` directory on the
    local machine.
    """
    latest = find_latest_dist(winrm_client, pattern)
    source = r'C:\hgdev\src\dist\%s' % latest
    dest = dest_path / latest
    print('copying %s to %s' % (source, dest))
    winrm_client.fetch(source, str(dest))


def build_inno_installer(winrm_client, arch: str, dest_path: pathlib.Path,
                         version=None):
    """Build the Inno Setup installer on a remote machine.

    Using a WinRM client, remote commands are executed to build
    a Mercurial Inno Setup installer.
    """
    print('building Inno Setup installer for %s' % arch)

    extra_args = []
    if version:
        extra_args.extend(['--version', version])

    ps = get_vc_prefix(arch) + BUILD_INNO.format(arch=arch,
                                                 extra_args=' '.join(extra_args))
    run_powershell(winrm_client, ps)
    copy_latest_dist(winrm_client, '*.exe', dest_path)


def build_wheel(winrm_client, arch: str, dest_path: pathlib.Path):
    """Build Python wheels on a remote machine.

    Using a WinRM client, remote commands are executed to build a Python wheel
    for Mercurial.
    """
    print('Building Windows wheel for %s' % arch)
    ps = get_vc_prefix(arch) + BUILD_WHEEL.format(arch=arch)
    run_powershell(winrm_client, ps)
    copy_latest_dist(winrm_client, '*.whl', dest_path)


def build_wix_installer(winrm_client, arch: str, dest_path: pathlib.Path,
                        version=None):
    """Build the WiX installer on a remote machine.

    Using a WinRM client, remote commands are executed to build a WiX installer.
    """
    print('Building WiX installer for %s' % arch)
    extra_args = []
    if version:
        extra_args.extend(['--version', version])

    ps = get_vc_prefix(arch) + BUILD_WIX.format(arch=arch,
                                                extra_args=' '.join(extra_args))
    run_powershell(winrm_client, ps)
    copy_latest_dist(winrm_client, '*.msi', dest_path)


def run_tests(winrm_client, python_version, arch, test_flags=''):
    """Run tests on a remote Windows machine.

    ``python_version`` is a ``X.Y`` string like ``2.7`` or ``3.7``.
    ``arch`` is ``x86`` or ``x64``.
    ``test_flags`` is a str representing extra arguments to pass to
    ``run-tests.py``.
    """
    if not re.match(r'\d\.\d', python_version):
        raise ValueError(r'python_version must be \d.\d; got %s' %
                         python_version)

    if arch not in ('x86', 'x64'):
        raise ValueError('arch must be x86 or x64; got %s' % arch)

    python_path = 'python%s-%s' % (python_version.replace('.', ''), arch)

    ps = RUN_TESTS.format(
        python_path=python_path,
        test_flags=test_flags or '',
    )

    run_powershell(winrm_client, ps)
