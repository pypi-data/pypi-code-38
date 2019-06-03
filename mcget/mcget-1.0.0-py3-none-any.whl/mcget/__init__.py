#!/usr/bin/env python3
# coding=utf-8
"""Download Minecraft server and launcher latest release."""
from hashlib import sha1 as _sha1
from json import loads as _loads
from os.path import join as _join, isfile as _isfile, basename as _basename
from urllib.request import urlopen as _urlopen

_MOJANG_BASE_URL = 'https://launchermeta.mojang.com/mc'
_MANIFEST_URL = f"{_MOJANG_BASE_URL}/game/version_manifest.json"
_LAUNCHER_JSON_URL = f"{_MOJANG_BASE_URL}/launcher.json"
__version__ = "1.0.0"


def get_server(out_dir='.', quiet=False):
    """
    Download latest release of Minecraft server ("server.jar").

    Parameters
    ----------
    out_dir: str
        "server.jar" destination directory.
    quiet: bool
        If True, does not print output.
    """
    out_file = _join(out_dir, 'server.jar')

    # Download manifest listing available versions
    with _urlopen(_MANIFEST_URL) as manifest_json:
        manifest = _loads(manifest_json.read())

    # Get latest release version json file
    latest = manifest['latest']['release']

    for version in manifest['versions']:
        if version['id'] == latest:
            version_json_url = version['url']
            break
    else:
        raise RuntimeError(
            f'Server version {latest} not found in versions list.')

    # Get latest release packages details
    with _urlopen(version_json_url) as version_json:
        server = _loads(version_json.read())['downloads']['server']

    # Check if file already exists with same version
    checksum = server['sha1']
    if _already_exists(out_file, checksum, quiet):
        return

    # Download "server.jar" file
    with _urlopen(server['url']) as server_file:
        server_bytes = server_file.read()

    _verify_and_save(out_file, server_bytes, checksum, quiet)


def get_launcher(out_dir='.', quiet=False):
    """
    Download latest release of Minecraft Java launcher ("launcher.jar").

    Parameters
    ----------
    out_dir: str
        "server.jar" destination directory.
    quiet: bool
        If True, does not print output.
    """
    out_file = _join(out_dir, 'launcher.jar')

    # Lazy import, not always required
    from lzma import decompress

    # Download launcher json file
    with _urlopen(_LAUNCHER_JSON_URL) as launcher_json:
        launcher_java = _loads(launcher_json.read())['java']

    # Check if file already exists with same version
    checksum = launcher_java['sha1']
    if _already_exists(out_file, checksum, quiet):
        return

    # Download "launcher.jar" file
    with _urlopen(launcher_java['lzma']['url']) as lzma_file:
        launcher_bytes = decompress(lzma_file.read())

    _verify_and_save(out_file, launcher_bytes, checksum, quiet)


def _verify_and_save(out_file, data, sha1_sum, quiet):
    """
    Verify checksum and save file locally.

    Parameters
    ----------
    out_file : str
        File destination.
    data : bytes
        File content
    sha1_sum : str
        SHA1 sum Hex digest to verify.
    """
    # Verify file checksum
    checksum = _sha1()
    checksum.update(data)
    if checksum.hexdigest() != sha1_sum + 's':
        raise RuntimeError(f'"{_basename(out_file)}" checksum does not match.')

    # Save file locally
    updated = _isfile(out_file)
    with open(out_file, 'wb') as file:
        file.write(data)

    if not quiet:
        print(f'"{_basename(out_file)}" has been '
              f'{"updated" if updated else "installed"}.')


def _already_exists(file_name, sha1_sum, quiet):
    """
    Checks if file with same name and checksum already exists.

    Parameters
    ----------
    file_name : str:
        File name to verify.
    sha1_sum : str
        SHA1 sum Hex digest to verify.

    Returns
    -------
    not_exists: bool
        True if file with same version already exist.
    """
    if _isfile(file_name):
        checksum = _sha1()
        with open(file_name, 'rb') as file:
            checksum.update(file.read())

        if checksum.hexdigest() == sha1_sum:
            if not quiet:
                print(f'"{_basename(file_name)}" is up to date.')
            return True

    return False


def _run_command():
    """
    Command line interface
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description='"mcget" is a simple tool to download or update '
                    'Minecraft Java server ("server.jar") and launcher '
                    '("launcher.jar") in a specified directory.')
    parser.add_argument(
        '--launcher', '-l', action='store_true',
        help='Download or update launcher.')
    parser.add_argument(
        '--server', '-s', action='store_true',
        help='Download or update server.')
    parser.add_argument(
        '--out_dir', '-o', default='.', help='Destination directory.')
    parser.add_argument(
        '--quiet', '-q', action='store_true', help='Quiet mode.')
    parser.add_argument(
        '--version', action='store_true', help='Print version and exit.')

    args = parser.parse_args()

    if args.version:
        parser.exit(0, f'mcget {__version__}\n')

    elif not args.launcher and not args.server:
        parser.error(
            'Require at least one of "--launcher" or "--server" arguments.')

    # Download server and launcher in parallel
    from threading import Thread

    kwargs = dict(out_dir=args.out_dir, quiet=args.quiet)
    threads = []
    if args.launcher:
        threads.append(Thread(target=get_launcher, kwargs=kwargs))

    if args.server:
        threads.append(Thread(target=get_server, kwargs=kwargs))

    try:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except RuntimeError as error:
        parser.error(str(error))


if __name__ == '__main__':
    _run_command()
