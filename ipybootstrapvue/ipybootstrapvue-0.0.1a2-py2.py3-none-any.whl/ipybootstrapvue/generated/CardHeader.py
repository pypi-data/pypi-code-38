from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CardHeader(VuetifyWidget):

    _model_name = Unicode('CardHeaderModel').tag(sync=True)

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


__all__ = ['CardHeader']
