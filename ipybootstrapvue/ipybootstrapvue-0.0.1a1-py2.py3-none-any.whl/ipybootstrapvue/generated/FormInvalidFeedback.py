from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormInvalidFeedback(VuetifyWidget):

    _model_name = Unicode('FormInvalidFeedbackModel').tag(sync=True)

    aria_live = Unicode(None, allow_none=True).tag(sync=True)

    force_show = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    role = Unicode(None, allow_none=True).tag(sync=True)

    state = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    tooltip = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['FormInvalidFeedback']
