from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CardSubTitle(VuetifyWidget):

    _model_name = Unicode('CardSubTitleModel').tag(sync=True)

    sub_title = Unicode(None, allow_none=True).tag(sync=True)

    sub_title_tag = Unicode(None, allow_none=True).tag(sync=True)

    sub_title_text_variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['CardSubTitle']
