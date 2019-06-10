# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import os
import six
from .prompt import prompt
from .separator import Separator
from .prompts.common import default_style
from .prompt_toolkit.styles import pygments_token_to_classname

__version__ = '0.5.2'


def here(p):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), p))


class PromptParameterException(ValueError):
    def __init__(self, message, errors=None):

        # Call the base class constructor with the parameters it needs
        super(PromptParameterException, self).__init__(
            'You must provide a `%s` value' % message, errors)


def get_fragments_from_tokens(tokens):
    result = []
    for token in tokens:
        if len(token) == 2:
            token, text = token
            handler = None
        else:
            token, text, handler = token

        if not isinstance(token, six.string_types):
            token = 'class:' + pygments_token_to_classname(token)

        if handler:
            result.append((token, text, handler))
        else:
            result.append((token, text))

    return result
