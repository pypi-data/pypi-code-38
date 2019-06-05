import os
import json
import io

from six import PY2

import pycdstar


def pkg_path(*comps):
    return os.path.join(os.path.dirname(pycdstar.__file__), *comps)


def jsonload(path, **kw):
    """python 2 + 3 compatible version of json.load.

    :return: The python object read from path.
    """
    _kw = {}
    if not PY2:
        _kw['encoding'] = 'utf8'
    with io.open(path, **_kw) as fp:
        return json.load(fp, **kw)


def jsondumps(obj):
    return json.dumps(obj).encode('utf8') if not PY2 else json.dumps(obj)
