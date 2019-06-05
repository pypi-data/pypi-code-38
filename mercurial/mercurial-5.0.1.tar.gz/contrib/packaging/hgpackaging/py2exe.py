# py2exe.py - Functionality for performing py2exe builds.
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

import os
import pathlib
import subprocess

from .downloads import (
    download_entry,
)
from .util import (
    extract_tar_to_directory,
    extract_zip_to_directory,
    python_exe_info,
)


def build_py2exe(source_dir: pathlib.Path, build_dir: pathlib.Path,
                 python_exe: pathlib.Path, build_name: str,
                 venv_requirements_txt: pathlib.Path,
                 extra_packages=None, extra_excludes=None,
                 extra_dll_excludes=None,
                 extra_packages_script=None):
    """Build Mercurial with py2exe.

    Build files will be placed in ``build_dir``.

    py2exe's setup.py doesn't use setuptools. It doesn't have modern logic
    for finding the Python 2.7 toolchain. So, we require the environment
    to already be configured with an active toolchain.
    """
    if 'VCINSTALLDIR' not in os.environ:
        raise Exception('not running from a Visual C++ build environment; '
                        'execute the "Visual C++ <version> Command Prompt" '
                        'application shortcut or a vcsvarsall.bat file')

    # Identity x86/x64 and validate the environment matches the Python
    # architecture.
    vc_x64 = r'\x64' in os.environ['LIB']

    py_info = python_exe_info(python_exe)

    if vc_x64:
        if py_info['arch'] != '64bit':
            raise Exception('architecture mismatch: Visual C++ environment '
                            'is configured for 64-bit but Python is 32-bit')
    else:
        if py_info['arch'] != '32bit':
            raise Exception('architecture mismatch: Visual C++ environment '
                            'is configured for 32-bit but Python is 64-bit')

    if py_info['py3']:
        raise Exception('Only Python 2 is currently supported')

    build_dir.mkdir(exist_ok=True)

    gettext_pkg, gettext_entry = download_entry('gettext', build_dir)
    gettext_dep_pkg = download_entry('gettext-dep', build_dir)[0]
    virtualenv_pkg, virtualenv_entry = download_entry('virtualenv', build_dir)
    py2exe_pkg, py2exe_entry = download_entry('py2exe', build_dir)

    venv_path = build_dir / ('venv-%s-%s' % (build_name,
                                             'x64' if vc_x64 else 'x86'))

    gettext_root = build_dir / (
        'gettext-win-%s' % gettext_entry['version'])

    if not gettext_root.exists():
        extract_zip_to_directory(gettext_pkg, gettext_root)
        extract_zip_to_directory(gettext_dep_pkg, gettext_root)

    # This assumes Python 2. We don't need virtualenv on Python 3.
    virtualenv_src_path = build_dir / (
        'virtualenv-%s' % virtualenv_entry['version'])
    virtualenv_py = virtualenv_src_path / 'virtualenv.py'

    if not virtualenv_src_path.exists():
        extract_tar_to_directory(virtualenv_pkg, build_dir)

    py2exe_source_path = build_dir / ('py2exe-%s' % py2exe_entry['version'])

    if not py2exe_source_path.exists():
        extract_zip_to_directory(py2exe_pkg, build_dir)

    if not venv_path.exists():
        print('creating virtualenv with dependencies')
        subprocess.run(
            [str(python_exe), str(virtualenv_py), str(venv_path)],
            check=True)

    venv_python = venv_path / 'Scripts' / 'python.exe'
    venv_pip = venv_path / 'Scripts' / 'pip.exe'

    subprocess.run([str(venv_pip), 'install', '-r', str(venv_requirements_txt)],
                   check=True)

    # Force distutils to use VC++ settings from environment, which was
    # validated above.
    env = dict(os.environ)
    env['DISTUTILS_USE_SDK'] = '1'
    env['MSSdk'] = '1'

    if extra_packages_script:
        more_packages = set(subprocess.check_output(
            extra_packages_script,
            cwd=build_dir).split(b'\0')[-1].strip().decode('utf-8').splitlines())
        if more_packages:
            if not extra_packages:
                extra_packages = more_packages
            else:
                extra_packages |= more_packages

    if extra_packages:
        env['HG_PY2EXE_EXTRA_PACKAGES'] = ' '.join(sorted(extra_packages))
        hgext3rd_extras = sorted(
            e for e in extra_packages if e.startswith('hgext3rd.'))
        if hgext3rd_extras:
            env['HG_PY2EXE_EXTRA_INSTALL_PACKAGES'] = ' '.join(hgext3rd_extras)
    if extra_excludes:
        env['HG_PY2EXE_EXTRA_EXCLUDES'] = ' '.join(sorted(extra_excludes))
    if extra_dll_excludes:
        env['HG_PY2EXE_EXTRA_DLL_EXCLUDES'] = ' '.join(
            sorted(extra_dll_excludes))

    py2exe_py_path = venv_path / 'Lib' / 'site-packages' / 'py2exe'
    if not py2exe_py_path.exists():
        print('building py2exe')
        subprocess.run([str(venv_python), 'setup.py', 'install'],
                       cwd=py2exe_source_path,
                       env=env,
                       check=True)

    # Register location of msgfmt and other binaries.
    env['PATH'] = '%s%s%s' % (
        env['PATH'], os.pathsep, str(gettext_root / 'bin'))

    print('building Mercurial')
    subprocess.run(
        [str(venv_python), 'setup.py',
         'py2exe',
         'build_doc', '--html'],
        cwd=str(source_dir),
        env=env,
        check=True)
