from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ListTileTitle(VuetifyWidget):

    _model_name = Unicode('ListTileTitleModel').tag(sync=True)


__all__ = ['ListTileTitle']
