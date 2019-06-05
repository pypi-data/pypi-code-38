from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Tab(VuetifyWidget):

    _model_name = Unicode('TabModel').tag(sync=True)

    active = Bool(None, allow_none=True).tag(sync=True)

    button_id = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    head_html = Unicode(None, allow_none=True).tag(sync=True)

    href = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    lazy = Bool(None, allow_none=True).tag(sync=True)

    no_body = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    title = Unicode(None, allow_none=True).tag(sync=True)

    title_item_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    title_link_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['Tab']
