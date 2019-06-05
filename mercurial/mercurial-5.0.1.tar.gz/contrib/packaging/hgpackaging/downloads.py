# downloads.py - Code for downloading dependencies.
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

import gzip
import hashlib
import pathlib
import urllib.request


DOWNLOADS = {
    'gettext': {
        'url': 'https://versaweb.dl.sourceforge.net/project/gnuwin32/gettext/0.14.4/gettext-0.14.4-bin.zip',
        'size': 1606131,
        'sha256': '60b9ef26bc5cceef036f0424e542106cf158352b2677f43a01affd6d82a1d641',
        'version': '0.14.4',
    },
    'gettext-dep': {
        'url': 'https://versaweb.dl.sourceforge.net/project/gnuwin32/gettext/0.14.4/gettext-0.14.4-dep.zip',
        'size': 715086,
        'sha256': '411f94974492fd2ecf52590cb05b1023530aec67e64154a88b1e4ebcd9c28588',
    },
    'py2exe': {
        'url': 'https://versaweb.dl.sourceforge.net/project/py2exe/py2exe/0.6.9/py2exe-0.6.9.zip',
        'size': 149687,
        'sha256': '6bd383312e7d33eef2e43a5f236f9445e4f3e0f6b16333c6f183ed445c44ddbd',
        'version': '0.6.9',
    },
    # The VC9 CRT merge modules aren't readily available on most systems because
    # they are only installed as part of a full Visual Studio 2008 install.
    # While we could potentially extract them from a Visual Studio 2008
    # installer, it is easier to just fetch them from a known URL.
    'vc9-crt-x86-msm': {
        'url': 'https://github.com/indygreg/vc90-merge-modules/raw/9232f8f0b2135df619bf7946eaa176b4ac35ccff/Microsoft_VC90_CRT_x86.msm',
        'size': 615424,
        'sha256': '837e887ef31b332feb58156f429389de345cb94504228bb9a523c25a9dd3d75e',
    },
    'vc9-crt-x86-msm-policy': {
        'url': 'https://github.com/indygreg/vc90-merge-modules/raw/9232f8f0b2135df619bf7946eaa176b4ac35ccff/policy_9_0_Microsoft_VC90_CRT_x86.msm',
        'size': 71168,
        'sha256': '3fbcf92e3801a0757f36c5e8d304e134a68d5cafd197a6df7734ae3e8825c940',
    },
    'vc9-crt-x64-msm': {
        'url': 'https://github.com/indygreg/vc90-merge-modules/raw/9232f8f0b2135df619bf7946eaa176b4ac35ccff/Microsoft_VC90_CRT_x86_x64.msm',
        'size': 662528,
        'sha256': '50d9639b5ad4844a2285269c7551bf5157ec636e32396ddcc6f7ec5bce487a7c',
    },
    'vc9-crt-x64-msm-policy': {
        'url': 'https://github.com/indygreg/vc90-merge-modules/raw/9232f8f0b2135df619bf7946eaa176b4ac35ccff/policy_9_0_Microsoft_VC90_CRT_x86_x64.msm',
        'size': 71168,
        'sha256': '0550ea1929b21239134ad3a678c944ba0f05f11087117b6cf0833e7110686486',
    },
    'virtualenv': {
        'url': 'https://files.pythonhosted.org/packages/37/db/89d6b043b22052109da35416abc3c397655e4bd3cff031446ba02b9654fa/virtualenv-16.4.3.tar.gz',
        'size': 3713208,
        'sha256': '984d7e607b0a5d1329425dd8845bd971b957424b5ba664729fab51ab8c11bc39',
        'version': '16.4.3',
    },
    'wix': {
        'url': 'https://github.com/wixtoolset/wix3/releases/download/wix3111rtm/wix311-binaries.zip',
        'size': 34358269,
        'sha256': '37f0a533b0978a454efb5dc3bd3598becf9660aaf4287e55bf68ca6b527d051d',
        'version': '3.11.1',
    },
}


def hash_path(p: pathlib.Path):
    h = hashlib.sha256()

    with p.open('rb') as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


class IntegrityError(Exception):
    """Represents an integrity error when downloading a URL."""


def secure_download_stream(url, size, sha256):
    """Securely download a URL to a stream of chunks.

    If the integrity of the download fails, an IntegrityError is
    raised.
    """
    h = hashlib.sha256()
    length = 0

    with urllib.request.urlopen(url) as fh:
        if not url.endswith('.gz') and fh.info().get('Content-Encoding') == 'gzip':
            fh = gzip.GzipFile(fileobj=fh)

        while True:
            chunk = fh.read(65536)
            if not chunk:
                break

            h.update(chunk)
            length += len(chunk)

            yield chunk

    digest = h.hexdigest()

    if length != size:
        raise IntegrityError('size mismatch on %s: wanted %d; got %d' % (
            url, size, length))

    if digest != sha256:
        raise IntegrityError('sha256 mismatch on %s: wanted %s; got %s' % (
            url, sha256, digest))


def download_to_path(url: str, path: pathlib.Path, size: int, sha256: str):
    """Download a URL to a filesystem path, possibly with verification."""

    # We download to a temporary file and rename at the end so there's
    # no chance of the final file being partially written or containing
    # bad data.
    print('downloading %s to %s' % (url, path))

    if path.exists():
        good = True

        if path.stat().st_size != size:
            print('existing file size is wrong; removing')
            good = False

        if good:
            if hash_path(path) != sha256:
                print('existing file hash is wrong; removing')
                good = False

        if good:
            print('%s exists and passes integrity checks' % path)
            return

        path.unlink()

    tmp = path.with_name('%s.tmp' % path.name)

    try:
        with tmp.open('wb') as fh:
            for chunk in secure_download_stream(url, size, sha256):
                fh.write(chunk)
    except IntegrityError:
        tmp.unlink()
        raise

    tmp.rename(path)
    print('successfully downloaded %s' % url)


def download_entry(name: dict, dest_path: pathlib.Path, local_name=None) -> pathlib.Path:
    entry = DOWNLOADS[name]

    url = entry['url']

    local_name = local_name or url[url.rindex('/') + 1:]

    local_path = dest_path / local_name
    download_to_path(url, local_path, entry['size'], entry['sha256'])

    return local_path, entry
