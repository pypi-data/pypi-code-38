from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Carousel(VuetifyWidget):

    _model_name = Unicode('CarouselModel').tag(sync=True)

    background = Unicode(None, allow_none=True).tag(sync=True)

    controls = Bool(None, allow_none=True).tag(sync=True)

    fade = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    img_height = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    img_width = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    indicators = Bool(None, allow_none=True).tag(sync=True)

    interval = Float(None, allow_none=True).tag(sync=True)

    label_goto_slide = Unicode(None, allow_none=True).tag(sync=True)

    label_indicators = Unicode(None, allow_none=True).tag(sync=True)

    label_next = Unicode(None, allow_none=True).tag(sync=True)

    label_prev = Unicode(None, allow_none=True).tag(sync=True)

    no_animation = Bool(None, allow_none=True).tag(sync=True)

    no_hover_pause = Bool(None, allow_none=True).tag(sync=True)

    no_touch = Bool(None, allow_none=True).tag(sync=True)

    value = Float(None, allow_none=True).tag(sync=True)


__all__ = ['Carousel']
