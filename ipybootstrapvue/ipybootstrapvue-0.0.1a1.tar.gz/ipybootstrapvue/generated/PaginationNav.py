from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class PaginationNav(VuetifyWidget):

    _model_name = Unicode('PaginationNavModel').tag(sync=True)

    active_class = Unicode(None, allow_none=True).tag(sync=True)

    align = Unicode(None, allow_none=True).tag(sync=True)

    aria_label = Unicode(None, allow_none=True).tag(sync=True)

    base_url = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    ellipsis_text = Unicode(None, allow_none=True).tag(sync=True)

    exact = Bool(None, allow_none=True).tag(sync=True)

    exact_active_class = Unicode(None, allow_none=True).tag(sync=True)

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

    no_page_detect = Bool(None, allow_none=True).tag(sync=True)

    no_prefetch = Bool(None, allow_none=True).tag(sync=True)

    number_of_pages = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    pages = List(Any(), default_value=None, allow_none=True).tag(sync=True)

    prev_text = Unicode(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    use_router = Bool(None, allow_none=True).tag(sync=True)

    value = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['PaginationNav']
