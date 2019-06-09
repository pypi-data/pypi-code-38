"""
Intended for use in Jupyter notebooks like:
    %run -m datasci.notebook.init
"""
# pylint: disable=unused-import

# stdlib
import sys
import os
import re
import math
import time
import random
import logging

import gzip
import json
import operator
import itertools
from functools import partial, reduce
from collections import abc, Counter, defaultdict
from datetime import datetime, timedelta
from importlib import reload
from numbers import Number

from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

# IPython
import IPython
from IPython.display import display
from IPython.core.magic import Magics, magics_class, cell_magic

# general purpose
import cytoolz as toolz
import numpy as np
import markdown
import smart_open
from pyperclip import copy, paste

# data science + statistics
import scipy
import pandas as pd
import altair as alt
from datasci.pandas import drop_na_columns, drop_uninformative_columns

_np_options = {
    'precision': 5,    # default: 8
    'threshold': 100,  # default: 1000
    'linewidth': 120,  # default: 75
}
np.set_printoptions(**_np_options)

_pd_options = {
    # Unfortunately, there is no option to set precision on pd.Index formatting
    'display.chop_threshold': np.finfo(float).eps,  # default: None
    'display.max_rows': 20,        # default: 60
    'display.max_columns': 50,     # default: 20
    'display.max_colwidth': 1000,  # default: 50
    'display.precision': _np_options['precision'],  # default: 6
    'display.width': _np_options['linewidth'],  # default: 80
}
pd.set_option(*toolz.concat(_pd_options.items()))

# Disable "Export PNG/SVG" and "Open in Vega" links
alt.renderers.enable('default', embed_options={'actions': False})


def _globalFont_theme(font: str = 'Times New Roman',
                      fontSize: int = 12) -> dict:
    return {
        # the 'default' theme sets config.view.{width, height} to these dimensions,
        # but the view config's width & height apply only to continuous scales
        'width': 400,
        'height': 300,
        'config': {
            # customizations
            'mark': {
                'text': {
                    'font': font,
                    'fontSize': fontSize,
                },
            },
            'title': {
                'font': font,
                'fontSize': fontSize + 2,
            },
            # axis/legend could use practically the same config, but there's
            # some weird Altair/Vega-Lite bug that surfaces as
            # "Javascript Error: Cannot read property '0' of undefined"
            # if you assign them both to the same variable
            # (I'm inclined to blame Altair)
            'axis': {
                'labelFont': font,
                'labelFontSize': fontSize,
                'titleFont': font,
                'titleFontSize': fontSize + 1,
            },
            'legend': {
                'labelFont': font,
                'labelFontSize': fontSize - 1,
                'titleFont': font,
                'titleFontSize': fontSize,
            },
        },
    }


alt.themes.register('globalFont', _globalFont_theme)


_default_markdown_extensions = [
    'markdown.extensions.extra',
    'markdown.extensions.sane_lists',
    'markdown.extensions.smarty',
]


def asdf(*columns: List[str], index_columns=None):
    """
    Decorates a generator function, sending the results as `data` to the
    pd.DataFrame constructor. Super simple, but avoids having to nest a
    generator function inside a DataFrame-creator function. Use like:

    @asdf('x', 'y')
    def line_df():
        for x in range(100):
            yield x, 2 * x + 1
    df = line_df()
    """
    def asdf_inner(row_generator: Callable[..., Iterable[Iterable]]):
        def wrapped_row_generator(*args, **kwargs):
            data = row_generator(*args, **kwargs)
            df = pd.DataFrame(data, columns=columns)
            if index_columns:
                df = df.set_index(index_columns)
            return df
        return wrapped_row_generator
    return asdf_inner


class fmt:  # pylint: disable=too-few-public-methods
    def __init__(self, s, *args, **kwargs):
        self.text = s.format(*args, **kwargs)

    def _repr_html_(self):
        return markdown.markdown(self.text,
                                 extensions=_default_markdown_extensions,
                                 output_format='html5')

    def _repr_latex_(self):
        # maybe use pandoc?
        return self.text

    def _repr_markdown_(self):
        return self.text


def try_literal_eval(node_or_string: str) -> Any:
    """
    Try to parse node_or_string as a Python value;
    return node_or_string unchanged if ast.literal_eval raises an Error.
    """
    import ast
    try:
        return ast.literal_eval(node_or_string)
    except (SyntaxError, ValueError):
        return node_or_string


@magics_class
class PandasOptionContextMagics(Magics):
    """
    See docs at https://ipython.readthedocs.io/en/stable/config/custommagics.html
    """
    @cell_magic
    def full(self, _line, cell):
        """
        Set Pandas options `display.{max_rows,max_columns}` to None (unlimited).
        Use like:

            %%full
            df
        """
        with pd.option_context('display.max_rows', None,
                               'display.max_columns', None):
            self.shell.run_cell(cell)

    @cell_magic
    def pandas(self, line, cell):
        """
        Use like:

            %%pandas display.max_rows 100
            df
        """
        args = map(try_literal_eval, line.split())
        with pd.option_context(*args):
            self.shell.run_cell(cell)


def print_versions():
    import platform
    print(f'Python: {platform.python_version()}')
    print('Imported 3rd party packages:')
    print(f'- IPython=={IPython.__version__}')
    print(f'- cytoolz=={toolz.__version__} as toolz')
    print(f'- numpy=={np.__version__} as np')
    print(f'- scipy=={scipy.__version__} as scipy')
    print(f'- pandas=={pd.__version__} as pd')
    print(f'- altair=={alt.__version__} as alt')
    print(f'- markdown=={markdown.__version__}')
    print(f'- smart_open=={smart_open.__version__}')


DEFAULT_LOGGING_FORMAT = '%(asctime)14s %(levelname)-7s %(name)s - %(message)s'


def install_datasci_notebook(logging_level: int = logging.DEBUG,
                             logging_format: str = DEFAULT_LOGGING_FORMAT) -> logging.Logger:
    """
    Reset & configure logging, register magics, and return logger named 'notebook'
    """
    # reset logging (replace with basicConfig(force=True) when Python 3.8 comes out)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()
    # configure logging
    logging.basicConfig(format=logging_format, level=logging_level)
    # install IPython integrations
    from IPython import get_ipython
    get_ipython().register_magics(PandasOptionContextMagics)
    # return namespaced logger
    return logging.getLogger('notebook')


if __name__ == '__main__':
    install_datasci_notebook()
