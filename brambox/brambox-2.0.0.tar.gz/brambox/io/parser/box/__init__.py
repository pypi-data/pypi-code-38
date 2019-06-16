"""
Brambox generic parsers module |br|
These parsers can be used to parse and generate both annotation or detection files.
"""
from ._pandas import *

__all__ = ['box_formats']
box_formats = {
    'pandas': PandasParser,
}
