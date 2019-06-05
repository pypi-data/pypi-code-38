from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ProgressBar(VuetifyWidget):

    _model_name = Unicode('ProgressBarModel').tag(sync=True)

    animated = Bool(None, allow_none=True).tag(sync=True)

    label = Unicode(None, allow_none=True).tag(sync=True)

    label_html = Unicode(None, allow_none=True).tag(sync=True)

    max = Float(None, allow_none=True).tag(sync=True)

    precision = Float(None, allow_none=True).tag(sync=True)

    show_progress = Bool(None, allow_none=True).tag(sync=True)

    show_value = Bool(None, allow_none=True).tag(sync=True)

    striped = Bool(None, allow_none=True).tag(sync=True)

    value = Float(None, allow_none=True).tag(sync=True)

    variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['ProgressBar']
