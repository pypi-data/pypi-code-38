# -*- coding: utf-8 -*-
"""
`input` type question
"""
from ..prompt_toolkit.validation import Validator, ValidationError
from pygments.token import Token
from .. import get_fragments_from_tokens
from ..prompt_toolkit.shortcuts.prompt import PromptSession

from .common import default_style

# use std prompt-toolkit control


def question(message, **kwargs):
    validate_prompt = kwargs.pop('validate', None)
    if validate_prompt:
        if issubclass(validate_prompt, Validator):
            kwargs['validator'] = validate_prompt()
        elif callable(validate_prompt):
            class _InputValidator(Validator):
                def validate(self, document):
                    verdict = validate_prompt(document.text)
                    if not verdict:
                        verdict = 'invalid input'
                    raise ValidationError(
                        message=verdict,
                        cursor_position=len(document.text))

            kwargs['validator'] = _InputValidator()

    # TODO style defaults on detail level
        kwargs['style'] = kwargs.pop('style', default_style)

    def _get_prompt_tokens():
        return get_fragments_from_tokens([
            (Token.QuestionMark, '? '),
            (Token.Question, '%s: ' % message)
        ])

    return PromptSession(
        message=_get_prompt_tokens,
        **kwargs
    ).app
