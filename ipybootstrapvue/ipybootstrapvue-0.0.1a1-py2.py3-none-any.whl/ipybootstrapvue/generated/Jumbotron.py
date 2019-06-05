from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Jumbotron(VuetifyWidget):

    _model_name = Unicode('JumbotronModel').tag(sync=True)

    bg_variant = Unicode(None, allow_none=True).tag(sync=True)

    border_variant = Unicode(None, allow_none=True).tag(sync=True)

    container_fluid = Bool(None, allow_none=True).tag(sync=True)

    fluid = Bool(None, allow_none=True).tag(sync=True)

    header = Unicode(None, allow_none=True).tag(sync=True)

    header_html = Unicode(None, allow_none=True).tag(sync=True)

    header_level = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    header_tag = Unicode(None, allow_none=True).tag(sync=True)

    lead = Unicode(None, allow_none=True).tag(sync=True)

    lead_html = Unicode(None, allow_none=True).tag(sync=True)

    lead_tag = Unicode(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    text_variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Jumbotron']
