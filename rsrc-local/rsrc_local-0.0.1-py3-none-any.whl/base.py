import os
from urllib.request import url2pathname

from rsrc.models import (Resource,
                         URL)

from .models import (Directory,
                     File)


def deserialize_path(string: str) -> Resource:
    if os.path.isdir(string):
        return Directory.from_string(string)
    return File.from_string(string)


def deserialize_url(string: str) -> Resource:
    url = URL.from_string(string)
    return deserialize_path(url2pathname(url.authority + url.path_string))
