# inno.py - Inno Setup functionality.
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

import os
import pathlib
import shutil
import subprocess

from .py2exe import (
    build_py2exe,
)
from .util import (
    find_vc_runtime_files,
)


EXTRA_PACKAGES = {
    'dulwich',
    'keyring',
    'pygments',
    'win32ctypes',
}


def build(source_dir: pathlib.Path, build_dir: pathlib.Path,
          python_exe: pathlib.Path, iscc_exe: pathlib.Path,
          version=None):
    """Build the Inno installer.

    Build files will be placed in ``build_dir``.

    py2exe's setup.py doesn't use setuptools. It doesn't have modern logic
    for finding the Python 2.7 toolchain. So, we require the environment
    to already be configured with an active toolchain.
    """
    if not iscc_exe.exists():
        raise Exception('%s does not exist' % iscc_exe)

    vc_x64 = r'\x64' in os.environ.get('LIB', '')

    requirements_txt = (source_dir / 'contrib' / 'packaging' /
                        'inno' / 'requirements.txt')

    build_py2exe(source_dir, build_dir, python_exe, 'inno',
                 requirements_txt, extra_packages=EXTRA_PACKAGES)

    # hg.exe depends on VC9 runtime DLLs. Copy those into place.
    for f in find_vc_runtime_files(vc_x64):
        if f.name.endswith('.manifest'):
            basename = 'Microsoft.VC90.CRT.manifest'
        else:
            basename = f.name

        dest_path = source_dir / 'dist' / basename

        print('copying %s to %s' % (f, dest_path))
        shutil.copyfile(f, dest_path)

    print('creating installer')

    args = [str(iscc_exe)]

    if vc_x64:
        args.append('/dARCH=x64')

    if version:
        args.append('/dVERSION=%s' % version)

    args.append('/Odist')
    args.append('contrib/packaging/inno/mercurial.iss')

    subprocess.run(args, cwd=str(source_dir), check=True)
