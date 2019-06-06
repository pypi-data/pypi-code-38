# -*- coding: utf-8 -*-
"""
`list` type question
"""
from __future__ import print_function
from __future__ import unicode_literals
import six
from ..prompt_toolkit.application import Application, get_app
from ..prompt_toolkit.formatted_text import PygmentsTokens
from ..prompt_toolkit.key_binding import KeyBindings
from ..prompt_toolkit.keys import Keys
from ..prompt_toolkit.layout import FormattedTextControl, Layout
from ..prompt_toolkit.layout.containers import Window, VerticalAlign
from ..prompt_toolkit.filters import IsDone
from ..prompt_toolkit.layout.containers import ConditionalContainer, ScrollOffsets, HSplit
from ..prompt_toolkit.layout.dimension import Dimension
from pygments.token import Token
from .. import PromptParameterException, get_fragments_from_tokens
from ..separator import Separator
from .common import if_mouse_down, default_style


class InquirerControl(FormattedTextControl):
    def __init__(self, choices, **kwargs):
        self.selected_option_index = 0
        self.answered = False
        self.choices = choices
        self._init_choices(choices)
        text = self._get_choice_tokens
        super(InquirerControl, self).__init__(text, **kwargs)

    def _init_choices(self, choices):
        # helper to convert from question format to internal format
        self.choices = []  # list (name, value, disabled)
        searching_first_choice = True
        for i, c in enumerate(choices):
            if isinstance(c, Separator):
                self.choices.append((c, None, None))
                continue

            if isinstance(c, six.string_types):
                self.choices.append((c, c, None))
            else:
                name = c.get('name')
                value = c.get('value', name)
                disabled = c.get('disabled', None)
                self.choices.append((name, value, disabled))

            if searching_first_choice:
                self.selected_option_index = i  # found the first choice
                searching_first_choice = False

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choice_tokens(self):
        tokens = []

        def append(index, current_choice):
            selected = (index == self.selected_option_index)

            @if_mouse_down
            def select_item(_mouse_event):
                current_choice_selected = self.choices[index]

                if isinstance(current_choice_selected[0], Separator):
                    return

                # bind option with this index to mouse event
                self.selected_option_index = index
                self.answered = True

                get_app().future.set_result(current_choice_selected[1])

            if selected:
                tokens.append(('[SetCursorPosition]', ''))

            tokens.append((Token.Pointer if selected else Token, ' \u276f ' if selected else '   '))

            disabled = current_choice[2]
            value = current_choice[0]
            name = '%s' % current_choice[0]
            token = Token.Selected if selected else Token

            if isinstance(value, Separator):
                token = Token.Separator

            if disabled:  # disabled
                tokens.append((token, '- %s (%s)\n' % (name, disabled)))
            else:
                tokens.append((token, name + '\n', select_item))

        # prepare the select choices
        for i, choice in enumerate(self.choices):
            append(i, choice)

        return get_fragments_from_tokens(tokens)

    def get_selection(self):
        return self.choices[self.selected_option_index]


binding = KeyBindings()


def question(message, **kwargs):
    # TODO disabled, dict choices
    if 'choices' not in kwargs:
        raise PromptParameterException('choices')

    choices = kwargs.pop('choices', None)

    # TODO style defaults on detail level
    style = kwargs.pop('style', default_style)

    inquirer_control = InquirerControl(choices)

    def get_prompt_tokens():
        tokens = [
            (Token.QuestionMark, '?'),
            (Token.Question, ' %s: ' % message)
        ]

        if inquirer_control.answered:
            tokens.append((Token.Answer, ' ' + inquirer_control.get_selection()[0]))
        else:
            tokens.append((Token.Instruction, ' (Use arrow keys)'))

        return PygmentsTokens(tokens)

    # assemble layout
    layout = Layout(
        HSplit(
            [
                Window(content=FormattedTextControl(get_prompt_tokens)),
                ConditionalContainer(
                    Window(
                        inquirer_control,
                        width=Dimension.exact(43),
                        height=Dimension(min=3),
                        scroll_offsets=ScrollOffsets(top=1, bottom=1)
                    ),
                    filter=~IsDone()
                )
            ],
        )
    )

    @binding.add(Keys.ControlQ, eager=True)
    @binding.add(Keys.ControlC, eager=True)
    def _(_event):
        _event.app.exit(exception=KeyboardInterrupt)

    def _move_selection_to(offset):
        def _offset():
            inquirer_control.selected_option_index = ((inquirer_control.selected_option_index + offset) % inquirer_control.choice_count)
            return inquirer_control.choices[inquirer_control.selected_option_index]

        choice = _offset()

        while isinstance(choice[0], Separator) or choice[2]:
            choice = _offset()

    @binding.add(Keys.Down, eager=True)
    def move_cursor_down(_event):
        _move_selection_to(1)

    @binding.add(Keys.Up, eager=True)
    def move_cursor_up(_event):
        _move_selection_to(-1)

    @binding.add(Keys.ControlM, eager=True)  # Enter
    def set_answer(event):
        inquirer_control.answered = True
        event.app.future.set_result(inquirer_control.get_selection()[1])

    return Application(
        layout=layout,
        key_bindings=binding,
        mouse_support=kwargs.pop('mouse_support', False),
        style=style
    )
