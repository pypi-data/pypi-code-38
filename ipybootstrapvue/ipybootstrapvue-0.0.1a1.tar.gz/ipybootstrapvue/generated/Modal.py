from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Modal(VuetifyWidget):

    _model_name = Unicode('ModalModel').tag(sync=True)

    body_bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    body_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    body_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    busy = Bool(None, allow_none=True).tag(sync=True)

    button_size = Unicode(None, allow_none=True).tag(sync=True)

    cancel_disabled = Bool(None, allow_none=True).tag(sync=True)

    cancel_title = Unicode(None, allow_none=True).tag(sync=True)

    cancel_title_html = Unicode(None, allow_none=True).tag(sync=True)

    cancel_variant = Unicode(None, allow_none=True).tag(sync=True)

    centered = Bool(None, allow_none=True).tag(sync=True)

    content_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    dialog_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    footer_bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    footer_border_variant = Unicode(None, allow_none=True).tag(sync=True)

    footer_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    footer_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    header_bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    header_border_variant = Unicode(None, allow_none=True).tag(sync=True)

    header_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    header_close_label = Unicode(None, allow_none=True).tag(sync=True)

    header_close_variant = Unicode(None, allow_none=True).tag(sync=True)

    header_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    hide_backdrop = Bool(None, allow_none=True).tag(sync=True)

    hide_footer = Bool(None, allow_none=True).tag(sync=True)

    hide_header = Bool(None, allow_none=True).tag(sync=True)

    hide_header_close = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    lazy = Bool(None, allow_none=True).tag(sync=True)

    modal_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    no_close_on_backdrop = Bool(None, allow_none=True).tag(sync=True)

    no_close_on_esc = Bool(None, allow_none=True).tag(sync=True)

    no_enforce_focus = Bool(None, allow_none=True).tag(sync=True)

    no_fade = Bool(None, allow_none=True).tag(sync=True)

    no_stacking = Bool(None, allow_none=True).tag(sync=True)

    ok_disabled = Bool(None, allow_none=True).tag(sync=True)

    ok_only = Bool(None, allow_none=True).tag(sync=True)

    ok_title = Unicode(None, allow_none=True).tag(sync=True)

    ok_title_html = Unicode(None, allow_none=True).tag(sync=True)

    ok_variant = Unicode(None, allow_none=True).tag(sync=True)

    return_focus = Any(None, allow_none=True).tag(sync=True)

    scrollable = Bool(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    static = Bool(None, allow_none=True).tag(sync=True)

    title = Unicode(None, allow_none=True).tag(sync=True)

    title_html = Unicode(None, allow_none=True).tag(sync=True)

    title_tag = Unicode(None, allow_none=True).tag(sync=True)

    visible = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['Modal']
