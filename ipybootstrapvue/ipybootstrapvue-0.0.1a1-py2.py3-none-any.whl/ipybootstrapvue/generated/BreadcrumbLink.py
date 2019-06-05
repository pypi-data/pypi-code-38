from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class BreadcrumbLink(VuetifyWidget):

    _model_name = Unicode('BreadcrumbLinkModel').tag(sync=True)

    active = Bool(None, allow_none=True).tag(sync=True)

    active_class = Unicode(None, allow_none=True).tag(sync=True)

    append = Bool(None, allow_none=True).tag(sync=True)

    aria_current = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    event = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    exact = Bool(None, allow_none=True).tag(sync=True)

    exact_active_class = Unicode(None, allow_none=True).tag(sync=True)

    href = Unicode(None, allow_none=True).tag(sync=True)

    html = Unicode(None, allow_none=True).tag(sync=True)

    no_prefetch = Bool(None, allow_none=True).tag(sync=True)

    rel = Unicode(None, allow_none=True).tag(sync=True)

    replace = Bool(None, allow_none=True).tag(sync=True)

    router_tag = Unicode(None, allow_none=True).tag(sync=True)

    target = Unicode(None, allow_none=True).tag(sync=True)

    text = Unicode(None, allow_none=True).tag(sync=True)

    to = Union([
        Unicode(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['BreadcrumbLink']
