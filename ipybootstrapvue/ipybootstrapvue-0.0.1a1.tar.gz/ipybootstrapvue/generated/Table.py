from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Table(VuetifyWidget):

    _model_name = Unicode('TableModel').tag(sync=True)

    api_url = Unicode(None, allow_none=True).tag(sync=True)

    bordered = Bool(None, allow_none=True).tag(sync=True)

    borderless = Bool(None, allow_none=True).tag(sync=True)

    busy = Bool(None, allow_none=True).tag(sync=True)

    caption = Unicode(None, allow_none=True).tag(sync=True)

    caption_html = Unicode(None, allow_none=True).tag(sync=True)

    caption_top = Bool(None, allow_none=True).tag(sync=True)

    current_page = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    dark = Bool(None, allow_none=True).tag(sync=True)

    empty_filtered_html = Unicode(None, allow_none=True).tag(sync=True)

    empty_filtered_text = Unicode(None, allow_none=True).tag(sync=True)

    empty_html = Unicode(None, allow_none=True).tag(sync=True)

    empty_text = Unicode(None, allow_none=True).tag(sync=True)

    fields = Union([
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    filter = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    fixed = Bool(None, allow_none=True).tag(sync=True)

    foot_clone = Bool(None, allow_none=True).tag(sync=True)

    foot_variant = Unicode(None, allow_none=True).tag(sync=True)

    head_variant = Unicode(None, allow_none=True).tag(sync=True)

    hover = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    items = Union([
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    label_sort_asc = Unicode(None, allow_none=True).tag(sync=True)

    label_sort_clear = Unicode(None, allow_none=True).tag(sync=True)

    label_sort_desc = Unicode(None, allow_none=True).tag(sync=True)

    no_footer_sorting = Bool(None, allow_none=True).tag(sync=True)

    no_local_sorting = Bool(None, allow_none=True).tag(sync=True)

    no_provider_filtering = Bool(None, allow_none=True).tag(sync=True)

    no_provider_paging = Bool(None, allow_none=True).tag(sync=True)

    no_provider_sorting = Bool(None, allow_none=True).tag(sync=True)

    no_sort_reset = Bool(None, allow_none=True).tag(sync=True)

    outlined = Bool(None, allow_none=True).tag(sync=True)

    per_page = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    primary_key = Unicode(None, allow_none=True).tag(sync=True)

    responsive = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    select_mode = Unicode(None, allow_none=True).tag(sync=True)

    selectable = Bool(None, allow_none=True).tag(sync=True)

    selected_variant = Unicode(None, allow_none=True).tag(sync=True)

    show_empty = Bool(None, allow_none=True).tag(sync=True)

    small = Bool(None, allow_none=True).tag(sync=True)

    sort_by = Unicode(None, allow_none=True).tag(sync=True)

    sort_desc = Bool(None, allow_none=True).tag(sync=True)

    sort_direction = Unicode(None, allow_none=True).tag(sync=True)

    stacked = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    striped = Bool(None, allow_none=True).tag(sync=True)

    table_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    tbody_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    tbody_tr_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    tbody_transition_handlers = Dict(default_value=None, allow_none=True).tag(sync=True)

    tbody_transition_props = Dict(default_value=None, allow_none=True).tag(sync=True)

    tfoot_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    tfoot_tr_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    thead_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    thead_tr_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    value = List(Any(), default_value=None, allow_none=True).tag(sync=True)


__all__ = ['Table']
