from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class DataIterator(VuetifyWidget):

    _model_name = Unicode('DataIteratorModel').tag(sync=True)

    content_class = Unicode(None, allow_none=True).tag(sync=True)

    content_props = Dict(default_value=None, allow_none=True).tag(sync=True)

    content_tag = Unicode(None, allow_none=True).tag(sync=True)

    dark = Bool(None, allow_none=True).tag(sync=True)

    disable_initial_sort = Bool(None, allow_none=True).tag(sync=True)

    expand = Bool(None, allow_none=True).tag(sync=True)

    hide_actions = Bool(None, allow_none=True).tag(sync=True)

    item_key = Unicode(None, allow_none=True).tag(sync=True)

    items = List(Any(), default_value=None, allow_none=True).tag(sync=True)

    light = Bool(None, allow_none=True).tag(sync=True)

    loading = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    must_sort = Bool(None, allow_none=True).tag(sync=True)

    next_icon = Unicode(None, allow_none=True).tag(sync=True)

    no_data_text = Unicode(None, allow_none=True).tag(sync=True)

    no_results_text = Unicode(None, allow_none=True).tag(sync=True)

    pagination = Dict(default_value=None, allow_none=True).tag(sync=True)

    prev_icon = Unicode(None, allow_none=True).tag(sync=True)

    rows_per_page_items = List(Any(), default_value=None, allow_none=True).tag(sync=True)

    rows_per_page_text = Unicode(None, allow_none=True).tag(sync=True)

    search = Any(None, allow_none=True).tag(sync=True)

    select_all = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    total_items = Float(None, allow_none=True).tag(sync=True)

    value = List(Any(), default_value=None, allow_none=True).tag(sync=True)


__all__ = ['DataIterator']
