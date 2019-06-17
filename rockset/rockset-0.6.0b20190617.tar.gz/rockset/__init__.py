from rockset.client import *
from rockset.collection import *
from rockset.cursor import *
from rockset.exception import *
from rockset.field_mapping import *
from rockset.integration import *
from rockset.query import *
from rockset.source import *
from rockset.value import *
from rockset.workspace import *
from rockset.swagger_client.models import *
from rockset.swagger_client.api import *

import json
import pkg_resources


def version():
    version_file = pkg_resources.resource_filename('rockset', 'version.json')
    try:
        with open(version_file, 'r') as vf:
            version = json.load(vf).get('version', None)
            if version is None:
                version = pkg_resources.require('rockset')[0].version
    except OSError as e:
        raise FileNotFoundError(
            'could not locate version.json in install dir. '
            'please uninstall and reinstall package "rockset"'
        ) from e

    return version


__all__ = [
    "Client",
    "Collection",
    "Cursor",
    "FieldMapping"
    "F",
    "FieldRef",
    "P",
    "ParamRef",
    "Q",
    "Query",
    "Source",
    "Workspace",
]
