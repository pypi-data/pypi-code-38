# -*- coding: utf-8 -*-
"""
confirm type question
"""
from __future__ import print_function, unicode_literals
from ..prompt_toolkit.application import Application
from ..prompt_toolkit.formatted_text import fragment_list_to_text
from ..prompt_toolkit.key_binding import KeyBindings
from ..prompt_toolkit.keys import Keys
from ..prompt_toolkit.layout import FormattedTextControl, Layout
from ..prompt_toolkit.layout.containers import Window, HSplit
from ..prompt_toolkit.layout.dimension import Dimension
from pygments.token import Token
from ..prompt_toolkit.styles import style_from_pygments_dict

# custom control based on TokenListControl

bindings = KeyBindings()


def question(message, **kwargs):
    # TODO need ENTER confirmation
    default = kwargs.pop('default', True)

    # TODO style defaults on detail level
    style = kwargs.pop('style', style_from_pygments_dict({
        Token.QuestionMark: '#5F819D',
        # Token.Selected: '#FF9D00',  # AWS orange
        Token.Instruction: '',  # default
        Token.Answer: '#FF9D00 bold',  # AWS orange
        Token.Question: 'bold',
    }))

    status = {}

    def get_prompt_tokens():
        tokens = [(Token.Question, '%s ' % message)]

        if isinstance(status.get('answer'), bool):
            tokens.append((Token.Answer, ' Yes' if status['answer'] else ' No'))
        else:
            if default:
                instruction = ' (Y/n)'
            else:
                instruction = ' (y/N)'

            tokens.append((Token.Instruction, instruction))

        return fragment_list_to_text(tokens)

    # assemble layout
    # TODO this does not work without the HSplit??
    content = HSplit([
        Window(
            height=Dimension.exact(1),
            content=FormattedTextControl(get_prompt_tokens),
        )
    ])

    # key bindings
    @bindings.add(Keys.ControlQ, eager=True)
    @bindings.add(Keys.ControlC, eager=True)
    def _(_event):
        _event.app.exit(exception=KeyboardInterrupt)

    def _set_result(event, val):
        status['answer'] = val
        event.app.future.set_result(val)

    @bindings.add('n')
    @bindings.add('N')
    def key_n(event):
        _set_result(event, False)

    @bindings.add('y')
    @bindings.add('Y')
    def key_y(event):
        _set_result(event, True)

    @bindings.add(Keys.ControlM, eager=True)  # enter
    def set_answer(event):
        _set_result(event, default)

    return Application(
        layout=Layout(content),
        key_bindings=bindings,
        style=style,
    )
