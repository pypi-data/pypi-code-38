from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class MediaAside(VuetifyWidget):

    _model_name = Unicode('MediaAsideModel').tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    vertical_align = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['MediaAside']
