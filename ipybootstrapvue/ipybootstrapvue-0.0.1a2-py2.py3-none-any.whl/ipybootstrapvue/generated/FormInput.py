from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormInput(VuetifyWidget):

    _model_name = Unicode('FormInputModel').tag(sync=True)

    aria_invalid = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    autocomplete = Unicode(None, allow_none=True).tag(sync=True)

    autofocus = Bool(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    form = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    lazy_formatter = Bool(None, allow_none=True).tag(sync=True)

    list = Unicode(None, allow_none=True).tag(sync=True)

    max = Union([
        Unicode(),
        Float()
    ], default_value=None, allow_none=True).tag(sync=True)

    min = Union([
        Unicode(),
        Float()
    ], default_value=None, allow_none=True).tag(sync=True)

    name = Unicode(None, allow_none=True).tag(sync=True)

    no_wheel = Bool(None, allow_none=True).tag(sync=True)

    number = Bool(None, allow_none=True).tag(sync=True)

    placeholder = Unicode(None, allow_none=True).tag(sync=True)

    plaintext = Bool(None, allow_none=True).tag(sync=True)

    readonly = Bool(None, allow_none=True).tag(sync=True)

    required = Bool(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    state = Union([
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    step = Union([
        Unicode(),
        Float()
    ], default_value=None, allow_none=True).tag(sync=True)

    trim = Bool(None, allow_none=True).tag(sync=True)

    type = Unicode(None, allow_none=True).tag(sync=True)

    value = Union([
        Unicode(),
        Float()
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['FormInput']
