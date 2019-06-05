from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CardBody(VuetifyWidget):

    _model_name = Unicode('CardBodyModel').tag(sync=True)

    body_bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    body_border_variant = Unicode(None, allow_none=True).tag(sync=True)

    body_class = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    body_tag = Unicode(None, allow_none=True).tag(sync=True)

    body_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    overlay = Bool(None, allow_none=True).tag(sync=True)

    sub_title = Unicode(None, allow_none=True).tag(sync=True)

    sub_title_tag = Unicode(None, allow_none=True).tag(sync=True)

    sub_title_text_variant = Unicode(None, allow_none=True).tag(sync=True)

    title = Unicode(None, allow_none=True).tag(sync=True)

    title_tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['CardBody']
