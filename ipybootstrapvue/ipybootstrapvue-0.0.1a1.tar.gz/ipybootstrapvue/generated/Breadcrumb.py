from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Breadcrumb(VuetifyWidget):

    _model_name = Unicode('BreadcrumbModel').tag(sync=True)

    items = List(Any(), default_value=None, allow_none=True).tag(sync=True)


__all__ = ['Breadcrumb']
