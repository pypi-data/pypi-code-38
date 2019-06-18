import warnings
from typing import List, Optional

from requests import Response

from mindfoundry.optaas._version import get_versions


# If the client and server versions differ in the Major or Minor part, we display a warning.
# If they only differ in the Patch, it's ok.

def _get_pieces(version: str) -> List[int]:
    try:
        pieces = version.split('.')
        return [int(pieces[0]), int(pieces[1])]
    except BaseException:
        return []


CLIENT_VERSION = get_versions()['version'].split('.post')[0]
CLIENT_VERSION_PIECES = _get_pieces(CLIENT_VERSION)

NEWER_VERSION_MESSAGE = """
A new version of the OPTaaS client is available. Please run:
    pip install mindfoundry-optaas-client=={}
To stop these messages, use OPTaaSClient(url, api_key, disable_version_check=True)
"""

OLDER_VERSION_MESSAGE = """
Your OPTaaS client version is not in sync with your OPTaaS server. To avoid unexpected behavior, please run:
    pip install mindfoundry-optaas-client=={}
To stop these messages, use OPTaaSClient(url, api_key, disable_version_check=True)
"""


def compare_versions(response: Response) -> None:
    server_version = response.headers.get('X-ApiVersion')
    if server_version:
        server_version = server_version.split('.post')[0]
        if server_version != CLIENT_VERSION:
            server_version_pieces = _get_pieces(server_version)
            warning_message = _get_version_warning_message(server_version_pieces)
            if warning_message:
                warnings.warn(warning_message.format(server_version))


def _get_version_warning_message(server_version_pieces: List[int]) -> Optional[str]:
    for client, server in zip(CLIENT_VERSION_PIECES, server_version_pieces):
        if client < server:
            return NEWER_VERSION_MESSAGE
        if client > server:
            return OLDER_VERSION_MESSAGE
    return None
