from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CarouselSlide(VuetifyWidget):

    _model_name = Unicode('CarouselSlideModel').tag(sync=True)

    background = Unicode(None, allow_none=True).tag(sync=True)

    caption = Unicode(None, allow_none=True).tag(sync=True)

    caption_html = Unicode(None, allow_none=True).tag(sync=True)

    caption_tag = Unicode(None, allow_none=True).tag(sync=True)

    content_tag = Unicode(None, allow_none=True).tag(sync=True)

    content_visible_up = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    img_alt = Unicode(None, allow_none=True).tag(sync=True)

    img_blank = Bool(None, allow_none=True).tag(sync=True)

    img_blank_color = Unicode(None, allow_none=True).tag(sync=True)

    img_height = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    img_src = Unicode(None, allow_none=True).tag(sync=True)

    img_width = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    text = Unicode(None, allow_none=True).tag(sync=True)

    text_html = Unicode(None, allow_none=True).tag(sync=True)

    text_tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['CarouselSlide']
