# -*- coding: utf-8 -*-
import mimetypes
import warnings

mimetypes.init()
mimetypes.add_type(mimetypes.types_map.get('.jpg'), '.jfif')


def get_content_type(body):
    import puremagic

    if not body:
        return None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        try:
            ext = puremagic.from_string(body)
            return mimetypes.types_map.get(ext)
        except puremagic.PureError:
            return None
