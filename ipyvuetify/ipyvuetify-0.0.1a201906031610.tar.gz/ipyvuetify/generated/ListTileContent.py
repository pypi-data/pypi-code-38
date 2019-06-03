from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ListTileContent(VuetifyWidget):

    _model_name = Unicode('ListTileContentModel').tag(sync=True)


__all__ = ['ListTileContent']
