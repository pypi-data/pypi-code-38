# wix.py - WiX installer functionality
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
import typing
import xml.dom.minidom

from .downloads import (
    download_entry,
)
from .py2exe import (
    build_py2exe,
)
from .util import (
    extract_zip_to_directory,
    sign_with_signtool,
)


SUPPORT_WXS = [
    ('contrib.wxs', r'contrib'),
    ('dist.wxs', r'dist'),
    ('doc.wxs', r'doc'),
    ('help.wxs', r'mercurial\help'),
    ('i18n.wxs', r'i18n'),
    ('locale.wxs', r'mercurial\locale'),
    ('templates.wxs', r'mercurial\templates'),
]


EXTRA_PACKAGES = {
    'distutils',
    'pygments',
}


def find_version(source_dir: pathlib.Path):
    version_py = source_dir / 'mercurial' / '__version__.py'

    with version_py.open('r', encoding='utf-8') as fh:
        source = fh.read().strip()

    m = re.search('version = b"(.*)"', source)
    return m.group(1)


def normalize_version(version):
    """Normalize Mercurial version string so WiX accepts it.

    Version strings have to be numeric X.Y.Z.
    """

    if '+' in version:
        version, extra = version.split('+', 1)
    else:
        extra = None

    # 4.9rc0
    if version[:-1].endswith('rc'):
        version = version[:-3]

    versions = [int(v) for v in version.split('.')]
    while len(versions) < 3:
        versions.append(0)

    major, minor, build = versions[:3]

    if extra:
        # <commit count>-<hash>+<date>
        build = int(extra.split('-')[0])

    return '.'.join('%d' % x for x in (major, minor, build))


def ensure_vc90_merge_modules(build_dir):
    x86 = (
        download_entry('vc9-crt-x86-msm', build_dir,
                       local_name='microsoft.vcxx.crt.x86_msm.msm')[0],
        download_entry('vc9-crt-x86-msm-policy', build_dir,
                       local_name='policy.x.xx.microsoft.vcxx.crt.x86_msm.msm')[0]
    )

    x64 = (
        download_entry('vc9-crt-x64-msm', build_dir,
                       local_name='microsoft.vcxx.crt.x64_msm.msm')[0],
        download_entry('vc9-crt-x64-msm-policy', build_dir,
                       local_name='policy.x.xx.microsoft.vcxx.crt.x64_msm.msm')[0]
    )
    return {
        'x86': x86,
        'x64': x64,
    }


def run_candle(wix, cwd, wxs, source_dir, defines=None):
    args = [
        str(wix / 'candle.exe'),
        '-nologo',
        str(wxs),
        '-dSourceDir=%s' % source_dir,
    ]

    if defines:
        args.extend('-d%s=%s' % define for define in sorted(defines.items()))

    subprocess.run(args, cwd=str(cwd), check=True)


def make_post_build_signing_fn(name, subject_name=None, cert_path=None,
                               cert_password=None, timestamp_url=None):
    """Create a callable that will use signtool to sign hg.exe."""

    def post_build_sign(source_dir, build_dir, dist_dir, version):
        description = '%s %s' % (name, version)

        sign_with_signtool(dist_dir / 'hg.exe', description,
                           subject_name=subject_name, cert_path=cert_path,
                           cert_password=cert_password,
                           timestamp_url=timestamp_url)

    return post_build_sign


LIBRARIES_XML = '''
<?xml version="1.0" encoding="utf-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">

  <?include {wix_dir}/guids.wxi ?>
  <?include {wix_dir}/defines.wxi ?>

  <Fragment>
    <DirectoryRef Id="INSTALLDIR" FileSource="$(var.SourceDir)">
      <Directory Id="libdir" Name="lib" FileSource="$(var.SourceDir)/lib">
        <Component Id="libOutput" Guid="$(var.lib.guid)" Win64='$(var.IsX64)'>
        </Component>
      </Directory>
    </DirectoryRef>
  </Fragment>
</Wix>
'''.lstrip()


def make_libraries_xml(wix_dir: pathlib.Path, dist_dir: pathlib.Path):
    """Make XML data for library components WXS."""
    # We can't use ElementTree because it doesn't handle the
    # <?include ?> directives.
    doc = xml.dom.minidom.parseString(
        LIBRARIES_XML.format(wix_dir=str(wix_dir)))

    component = doc.getElementsByTagName('Component')[0]

    f = doc.createElement('File')
    f.setAttribute('Name', 'library.zip')
    f.setAttribute('KeyPath', 'yes')
    component.appendChild(f)

    lib_dir = dist_dir / 'lib'

    for p in sorted(lib_dir.iterdir()):
        if not p.name.endswith(('.dll', '.pyd')):
            continue

        f = doc.createElement('File')
        f.setAttribute('Name', p.name)
        component.appendChild(f)

    return doc.toprettyxml()


def build_installer(source_dir: pathlib.Path, python_exe: pathlib.Path,
                    msi_name='mercurial', version=None, post_build_fn=None,
                    extra_packages_script=None,
                    extra_wxs:typing.Optional[typing.Dict[str,str]]=None,
                    extra_features:typing.Optional[typing.List[str]]=None):
    """Build a WiX MSI installer.

    ``source_dir`` is the path to the Mercurial source tree to use.
    ``arch`` is the target architecture. either ``x86`` or ``x64``.
    ``python_exe`` is the path to the Python executable to use/bundle.
    ``version`` is the Mercurial version string. If not defined,
    ``mercurial/__version__.py`` will be consulted.
    ``post_build_fn`` is a callable that will be called after building
    Mercurial but before invoking WiX. It can be used to e.g. facilitate
    signing. It is passed the paths to the Mercurial source, build, and
    dist directories and the resolved Mercurial version.
    ``extra_packages_script`` is a command to be run to inject extra packages
    into the py2exe binary. It should stage packages into the virtualenv and
    print a null byte followed by a newline-separated list of packages that
    should be included in the exe.
    ``extra_wxs`` is a dict of {wxs_name: working_dir_for_wxs_build}.
    ``extra_features`` is a list of additional named Features to include in
    the build. These must match Feature names in one of the wxs scripts.
    """
    arch = 'x64' if r'\x64' in os.environ.get('LIB', '') else 'x86'

    hg_build_dir = source_dir / 'build'
    dist_dir = source_dir / 'dist'
    wix_dir = source_dir / 'contrib' / 'packaging' / 'wix'

    requirements_txt = wix_dir / 'requirements.txt'

    build_py2exe(source_dir, hg_build_dir,
                 python_exe, 'wix', requirements_txt,
                 extra_packages=EXTRA_PACKAGES,
                 extra_packages_script=extra_packages_script)

    version = version or normalize_version(find_version(source_dir))
    print('using version string: %s' % version)

    if post_build_fn:
        post_build_fn(source_dir, hg_build_dir, dist_dir, version)

    build_dir = hg_build_dir / ('wix-%s' % arch)

    build_dir.mkdir(exist_ok=True)

    wix_pkg, wix_entry = download_entry('wix', hg_build_dir)
    wix_path = hg_build_dir / ('wix-%s' % wix_entry['version'])

    if not wix_path.exists():
        extract_zip_to_directory(wix_pkg, wix_path)

    ensure_vc90_merge_modules(hg_build_dir)

    source_build_rel = pathlib.Path(os.path.relpath(source_dir, build_dir))

    defines = {'Platform': arch}

    for wxs, rel_path in SUPPORT_WXS:
        wxs = wix_dir / wxs
        wxs_source_dir = source_dir / rel_path
        run_candle(wix_path, build_dir, wxs, wxs_source_dir, defines=defines)

    for source, rel_path in sorted((extra_wxs or {}).items()):
        run_candle(wix_path, build_dir, source, rel_path, defines=defines)

    # candle.exe doesn't like when we have an open handle on the file.
    # So use TemporaryDirectory() instead of NamedTemporaryFile().
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)

        tf = td / 'library.wxs'
        with tf.open('w') as fh:
            fh.write(make_libraries_xml(wix_dir, dist_dir))

        run_candle(wix_path, build_dir, tf, dist_dir, defines=defines)

    source = wix_dir / 'mercurial.wxs'
    defines['Version'] = version
    defines['Comments'] = 'Installs Mercurial version %s' % version
    defines['VCRedistSrcDir'] = str(hg_build_dir)
    if extra_features:
        assert all(';' not in f for f in extra_features)
        defines['MercurialExtraFeatures'] = ';'.join(extra_features)

    run_candle(wix_path, build_dir, source, source_build_rel, defines=defines)

    msi_path = source_dir / 'dist' / (
        '%s-%s-%s.msi' % (msi_name, version, arch))

    args = [
        str(wix_path / 'light.exe'),
        '-nologo',
        '-ext', 'WixUIExtension',
        '-sw1076',
        '-spdb',
        '-o', str(msi_path),
    ]

    for source, rel_path in SUPPORT_WXS:
        assert source.endswith('.wxs')
        args.append(str(build_dir / ('%s.wixobj' % source[:-4])))

    for source, rel_path in sorted((extra_wxs or {}).items()):
        assert source.endswith('.wxs')
        source = os.path.basename(source)
        args.append(str(build_dir / ('%s.wixobj' % source[:-4])))

    args.extend([
        str(build_dir / 'library.wixobj'),
        str(build_dir / 'mercurial.wixobj'),
    ])

    subprocess.run(args, cwd=str(source_dir), check=True)

    print('%s created' % msi_path)

    return {
        'msi_path': msi_path,
    }


def build_signed_installer(source_dir: pathlib.Path, python_exe: pathlib.Path,
                           name: str, version=None, subject_name=None,
                           cert_path=None, cert_password=None,
                           timestamp_url=None, extra_packages_script=None,
                           extra_wxs=None, extra_features=None):
    """Build an installer with signed executables."""

    post_build_fn = make_post_build_signing_fn(
        name,
        subject_name=subject_name,
        cert_path=cert_path,
        cert_password=cert_password,
        timestamp_url=timestamp_url)

    info = build_installer(source_dir, python_exe=python_exe,
                           msi_name=name.lower(), version=version,
                           post_build_fn=post_build_fn,
                           extra_packages_script=extra_packages_script,
                           extra_wxs=extra_wxs, extra_features=extra_features)

    description = '%s %s' % (name, version)

    sign_with_signtool(info['msi_path'], description,
                       subject_name=subject_name, cert_path=cert_path,
                       cert_password=cert_password, timestamp_url=timestamp_url)
