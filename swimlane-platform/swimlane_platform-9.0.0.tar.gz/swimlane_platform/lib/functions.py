import semver
from typing import Union, Tuple


def semver_try_parse(version):
    # type: (str) -> Tuple[bool, Union[semver.VersionInfo, None]]
    try:
        version_info = semver.parse_version_info(version)
        return True, version_info
    except ValueError:
        return False, None
