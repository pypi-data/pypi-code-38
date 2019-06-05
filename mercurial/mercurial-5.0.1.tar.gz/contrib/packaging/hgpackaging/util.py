# util.py - Common packaging utility code.
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

import distutils.version
import getpass
import os
import pathlib
import subprocess
import tarfile
import zipfile


def extract_tar_to_directory(source: pathlib.Path, dest: pathlib.Path):
    with tarfile.open(source, 'r') as tf:
        tf.extractall(dest)


def extract_zip_to_directory(source: pathlib.Path, dest: pathlib.Path):
    with zipfile.ZipFile(source, 'r') as zf:
        zf.extractall(dest)


def find_vc_runtime_files(x64=False):
    """Finds Visual C++ Runtime DLLs to include in distribution."""
    winsxs = pathlib.Path(os.environ['SYSTEMROOT']) / 'WinSxS'

    prefix = 'amd64' if x64 else 'x86'

    candidates = sorted(p for p in os.listdir(winsxs)
                  if p.lower().startswith('%s_microsoft.vc90.crt_' % prefix))

    for p in candidates:
        print('found candidate VC runtime: %s' % p)

    # Take the newest version.
    version = candidates[-1]

    d = winsxs / version

    return [
        d / 'msvcm90.dll',
        d / 'msvcp90.dll',
        d / 'msvcr90.dll',
        winsxs / 'Manifests' / ('%s.manifest' % version),
    ]


def windows_10_sdk_info():
    """Resolves information about the Windows 10 SDK."""

    base = pathlib.Path(os.environ['ProgramFiles(x86)']) / 'Windows Kits' / '10'

    if not base.is_dir():
        raise Exception('unable to find Windows 10 SDK at %s' % base)

    # Find the latest version.
    bin_base = base / 'bin'

    versions = [v for v in os.listdir(bin_base) if v.startswith('10.')]
    version = sorted(versions, reverse=True)[0]

    bin_version = bin_base / version

    return {
        'root': base,
        'version': version,
        'bin_root': bin_version,
        'bin_x86': bin_version / 'x86',
        'bin_x64': bin_version / 'x64'
    }


def find_signtool():
    """Find signtool.exe from the Windows SDK."""
    sdk = windows_10_sdk_info()

    for key in ('bin_x64', 'bin_x86'):
        p = sdk[key] / 'signtool.exe'

        if p.exists():
            return p

    raise Exception('could not find signtool.exe in Windows 10 SDK')


def sign_with_signtool(file_path, description, subject_name=None,
                       cert_path=None, cert_password=None,
                       timestamp_url=None):
    """Digitally sign a file with signtool.exe.

    ``file_path`` is file to sign.
    ``description`` is text that goes in the signature.

    The signing certificate can be specified by ``cert_path`` or
    ``subject_name``. These correspond to the ``/f`` and ``/n`` arguments
    to signtool.exe, respectively.

    The certificate password can be specified via ``cert_password``. If
    not provided, you will be prompted for the password.

    ``timestamp_url`` is the URL of a RFC 3161 timestamp server (``/tr``
    argument to signtool.exe).
    """
    if cert_path and subject_name:
        raise ValueError('cannot specify both cert_path and subject_name')

    while cert_path and not cert_password:
        cert_password = getpass.getpass('password for %s: ' % cert_path)

    args = [
        str(find_signtool()), 'sign',
        '/v',
        '/fd', 'sha256',
        '/d', description,
    ]

    if cert_path:
        args.extend(['/f', str(cert_path), '/p', cert_password])
    elif subject_name:
        args.extend(['/n', subject_name])

    if timestamp_url:
        args.extend(['/tr', timestamp_url, '/td', 'sha256'])

    args.append(str(file_path))

    print('signing %s' % file_path)
    subprocess.run(args, check=True)


PRINT_PYTHON_INFO = '''
import platform; print("%s:%s" % (platform.architecture()[0], platform.python_version()))
'''.strip()


def python_exe_info(python_exe: pathlib.Path):
    """Obtain information about a Python executable."""

    res = subprocess.check_output([str(python_exe), '-c', PRINT_PYTHON_INFO])

    arch, version = res.decode('utf-8').split(':')

    version = distutils.version.LooseVersion(version)

    return {
        'arch': arch,
        'version': version,
        'py3': version >= distutils.version.LooseVersion('3'),
    }
