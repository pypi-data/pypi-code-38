from pkg_resources import resource_string
import json
import sys

if sys.version_info.major == 2:  # pragma: no cover
    __version__ = json.loads(resource_string(__name__, 'version.json'))
else:  # pragma: no cover
    __version__ = json.loads(resource_string(__name__, 'version.json').decode('utf-8'))
