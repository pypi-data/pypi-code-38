from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ListTileAction(VuetifyWidget):

    _model_name = Unicode('ListTileActionModel').tag(sync=True)


__all__ = ['ListTileAction']
