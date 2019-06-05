from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Card(VuetifyWidget):

    _model_name = Unicode('CardModel').tag(sync=True)

    align = Unicode(None, allow_none=True).tag(sync=True)

    bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    body_bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    body_border_variant = Unicode(None, allow_none=True).tag(sync=True)

    body_class = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    body_tag = Unicode(None, allow_none=True).tag(sync=True)

    body_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    border_variant = Unicode(None, allow_none=True).tag(sync=True)

    footer = Unicode(None, allow_none=True).tag(sync=True)

    footer_bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    footer_border_variant = Unicode(None, allow_none=True).tag(sync=True)

    footer_class = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    footer_html = Unicode(None, allow_none=True).tag(sync=True)

    footer_tag = Unicode(None, allow_none=True).tag(sync=True)

    footer_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    header = Unicode(None, allow_none=True).tag(sync=True)

    header_bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    header_border_variant = Unicode(None, allow_none=True).tag(sync=True)

    header_class = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    header_html = Unicode(None, allow_none=True).tag(sync=True)

    header_tag = Unicode(None, allow_none=True).tag(sync=True)

    header_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    img_alt = Unicode(None, allow_none=True).tag(sync=True)

    img_bottom = Bool(None, allow_none=True).tag(sync=True)

    img_end = Bool(None, allow_none=True).tag(sync=True)

    img_height = Unicode(None, allow_none=True).tag(sync=True)

    img_left = Bool(None, allow_none=True).tag(sync=True)

    img_right = Bool(None, allow_none=True).tag(sync=True)

    img_src = Unicode(None, allow_none=True).tag(sync=True)

    img_start = Bool(None, allow_none=True).tag(sync=True)

    img_top = Bool(None, allow_none=True).tag(sync=True)

    img_width = Unicode(None, allow_none=True).tag(sync=True)

    no_body = Bool(None, allow_none=True).tag(sync=True)

    overlay = Bool(None, allow_none=True).tag(sync=True)

    sub_title = Unicode(None, allow_none=True).tag(sync=True)

    sub_title_tag = Unicode(None, allow_none=True).tag(sync=True)

    sub_title_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    text_variant = Unicode(None, allow_none=True).tag(sync=True)

    title = Unicode(None, allow_none=True).tag(sync=True)

    title_tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Card']
