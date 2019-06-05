from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormCheckbox(VuetifyWidget):

    _model_name = Unicode('FormCheckboxModel').tag(sync=True)

    aria_label = Unicode(None, allow_none=True).tag(sync=True)

    aria_labelledby = Unicode(None, allow_none=True).tag(sync=True)

    autofocus = Bool(None, allow_none=True).tag(sync=True)

    button = Bool(None, allow_none=True).tag(sync=True)

    button_variant = Unicode(None, allow_none=True).tag(sync=True)

    checked = Union([
        Unicode(),
        Float(),
        Dict(),
        List(Any()),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    form = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    indeterminate = Bool(None, allow_none=True).tag(sync=True)

    inline = Bool(None, allow_none=True).tag(sync=True)

    name = Unicode(None, allow_none=True).tag(sync=True)

    plain = Bool(None, allow_none=True).tag(sync=True)

    required = Bool(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    state = Union([
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    switch = Bool(None, allow_none=True).tag(sync=True)

    unchecked_value = Any(None, allow_none=True).tag(sync=True)

    value = Any(None, allow_none=True).tag(sync=True)


__all__ = ['FormCheckbox']
