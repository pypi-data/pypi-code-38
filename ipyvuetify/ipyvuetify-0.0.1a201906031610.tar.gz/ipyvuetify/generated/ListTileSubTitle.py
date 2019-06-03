from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ListTileSubTitle(VuetifyWidget):

    _model_name = Unicode('ListTileSubTitleModel').tag(sync=True)


__all__ = ['ListTileSubTitle']
