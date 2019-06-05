from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Pagination(VuetifyWidget):

    _model_name = Unicode('PaginationModel').tag(sync=True)

    align = Unicode(None, allow_none=True).tag(sync=True)

    aria_controls = Unicode(None, allow_none=True).tag(sync=True)

    aria_label = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    ellipsis_text = Unicode(None, allow_none=True).tag(sync=True)

    first_text = Unicode(None, allow_none=True).tag(sync=True)

    hide_ellipsis = Bool(None, allow_none=True).tag(sync=True)

    hide_goto_end_buttons = Bool(None, allow_none=True).tag(sync=True)

    label_first_page = Unicode(None, allow_none=True).tag(sync=True)

    label_last_page = Unicode(None, allow_none=True).tag(sync=True)

    label_next_page = Unicode(None, allow_none=True).tag(sync=True)

    label_page = Union([
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    label_prev_page = Unicode(None, allow_none=True).tag(sync=True)

    last_text = Unicode(None, allow_none=True).tag(sync=True)

    limit = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    next_text = Unicode(None, allow_none=True).tag(sync=True)

    per_page = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    prev_text = Unicode(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    total_rows = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    value = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['Pagination']
