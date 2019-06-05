from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CardImg(VuetifyWidget):

    _model_name = Unicode('CardImgModel').tag(sync=True)

    alt = Unicode(None, allow_none=True).tag(sync=True)

    bottom = Bool(None, allow_none=True).tag(sync=True)

    end = Bool(None, allow_none=True).tag(sync=True)

    height = Unicode(None, allow_none=True).tag(sync=True)

    left = Bool(None, allow_none=True).tag(sync=True)

    right = Bool(None, allow_none=True).tag(sync=True)

    src = Unicode(None, allow_none=True).tag(sync=True)

    start = Bool(None, allow_none=True).tag(sync=True)

    top = Bool(None, allow_none=True).tag(sync=True)

    width = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['CardImg']
