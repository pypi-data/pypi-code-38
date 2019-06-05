from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Img(VuetifyWidget):

    _model_name = Unicode('ImgModel').tag(sync=True)

    alt = Unicode(None, allow_none=True).tag(sync=True)

    blank = Bool(None, allow_none=True).tag(sync=True)

    blank_color = Unicode(None, allow_none=True).tag(sync=True)

    block = Bool(None, allow_none=True).tag(sync=True)

    center = Bool(None, allow_none=True).tag(sync=True)

    fluid = Bool(None, allow_none=True).tag(sync=True)

    fluid_grow = Bool(None, allow_none=True).tag(sync=True)

    height = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    left = Bool(None, allow_none=True).tag(sync=True)

    right = Bool(None, allow_none=True).tag(sync=True)

    rounded = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    src = Unicode(None, allow_none=True).tag(sync=True)

    thumbnail = Bool(None, allow_none=True).tag(sync=True)

    width = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['Img']
