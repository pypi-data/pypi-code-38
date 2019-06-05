from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CardFooter(VuetifyWidget):

    _model_name = Unicode('CardFooterModel').tag(sync=True)

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


__all__ = ['CardFooter']
