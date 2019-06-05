from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormCheckboxGroup(VuetifyWidget):

    _model_name = Unicode('FormCheckboxGroupModel').tag(sync=True)

    aria_invalid = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    autofocus = Bool(None, allow_none=True).tag(sync=True)

    button_variant = Unicode(None, allow_none=True).tag(sync=True)

    buttons = Bool(None, allow_none=True).tag(sync=True)

    checked = Union([
        Unicode(),
        Float(),
        Dict(),
        List(Any()),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    disabled_field = Unicode(None, allow_none=True).tag(sync=True)

    form = Unicode(None, allow_none=True).tag(sync=True)

    html_field = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    name = Unicode(None, allow_none=True).tag(sync=True)

    options = Union([
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    plain = Bool(None, allow_none=True).tag(sync=True)

    required = Bool(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    stacked = Bool(None, allow_none=True).tag(sync=True)

    state = Union([
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    switches = Bool(None, allow_none=True).tag(sync=True)

    text_field = Unicode(None, allow_none=True).tag(sync=True)

    validated = Bool(None, allow_none=True).tag(sync=True)

    value_field = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['FormCheckboxGroup']
