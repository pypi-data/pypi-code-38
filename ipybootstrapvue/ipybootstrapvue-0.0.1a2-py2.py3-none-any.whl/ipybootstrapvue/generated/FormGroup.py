from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormGroup(VuetifyWidget):

    _model_name = Unicode('FormGroupModel').tag(sync=True)

    breakpoint = Unicode(None, allow_none=True).tag(sync=True)

    description = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    feedback_aria_live = Unicode(None, allow_none=True).tag(sync=True)

    horizontal = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    invalid_feedback = Unicode(None, allow_none=True).tag(sync=True)

    label = Unicode(None, allow_none=True).tag(sync=True)

    label_align = Unicode(None, allow_none=True).tag(sync=True)

    label_align_lg = Unicode(None, allow_none=True).tag(sync=True)

    label_align_md = Unicode(None, allow_none=True).tag(sync=True)

    label_align_sm = Unicode(None, allow_none=True).tag(sync=True)

    label_align_xl = Unicode(None, allow_none=True).tag(sync=True)

    label_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    label_cols = Union([
        Float(),
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    label_cols_lg = Union([
        Float(),
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    label_cols_md = Union([
        Float(),
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    label_cols_sm = Union([
        Float(),
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    label_cols_xl = Union([
        Float(),
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    label_for = Unicode(None, allow_none=True).tag(sync=True)

    label_size = Unicode(None, allow_none=True).tag(sync=True)

    label_sr_only = Bool(None, allow_none=True).tag(sync=True)

    state = Union([
        Unicode(),
        Bool()
    ], default_value=None, allow_none=True).tag(sync=True)

    tooltip = Bool(None, allow_none=True).tag(sync=True)

    valid_feedback = Unicode(None, allow_none=True).tag(sync=True)

    validated = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['FormGroup']
