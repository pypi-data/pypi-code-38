# -*- coding: utf-8 -*-
"""
`checkbox` type question
"""
from __future__ import print_function, unicode_literals
from ..prompt_toolkit.application import Application
from ..prompt_toolkit.formatted_text import fragment_list_to_text
from ..prompt_toolkit.key_binding import KeyBindings
from ..prompt_toolkit.keys import Keys
from ..prompt_toolkit.layout import Layout
from ..prompt_toolkit.layout.containers import Window
from ..prompt_toolkit.filters import IsDone
from ..prompt_toolkit.layout.controls import FormattedTextControl
from ..prompt_toolkit.layout.containers import ConditionalContainer, \
    ScrollOffsets, HSplit
from ..prompt_toolkit.layout.dimension import Dimension
from pygments.token import Token
from .. import PromptParameterException, get_fragments_from_tokens
from ..separator import Separator
from .common import setup_simple_validator, default_style, if_mouse_down


# custom control based on TokenListControl


class InquirerControl(FormattedTextControl):
    def __init__(self, choices, **kwargs):
        self.pointer_index = 0
        self.selected_options = []  # list of names
        self.answered = False
        self._init_choices(choices)
        super(InquirerControl, self).__init__(self._get_choice_tokens, **kwargs)

    def _init_choices(self, choices):
        # helper to convert from question format to internal format
        self.choices = []  # list (name, value)
        searching_first_choice = True
        for i, c in enumerate(choices):
            if isinstance(c, Separator):
                self.choices.append(c)
                continue

            name = c['name']
            value = c.get('value', name)
            disabled = c.get('disabled', None)
            if 'checked' in c and c['checked'] and not disabled:
                self.selected_options.append(c['name'])
            self.choices.append((name, value, disabled))
            if searching_first_choice and not disabled:  # find the first (available) choice
                self.pointer_index = i
                searching_first_choice = False

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choice_tokens(self):
        tokens = []

        def append(index, line):
            if isinstance(line, Separator):
                tokens.append((Token.Separator, '  %s\n' % line))
                return

            line_name = line[0]
            line_value = line[1]
            selected = (line_value in self.selected_options)  # use value to check if option has been selected
            pointed_at = (index == self.pointer_index)

            @if_mouse_down
            def select_item(_mouse_event):
                # bind option with this index to mouse event
                if line_value in self.selected_options:
                    self.selected_options.remove(line_value)
                else:
                    self.selected_options.append(line_value)

            if pointed_at:
                tokens.append((Token.Pointer, ' \u276f', select_item))  # ' >'
            else:
                tokens.append((Token, '  ', select_item))

            # 'o ' - FISHEYE
            if choice[2]:  # disabled
                tokens.append((Token, '- %s (%s)' % (choice[0], choice[2])))
            else:
                if selected:
                    tokens.append((Token.Selected, '\u25cf ', select_item))
                else:
                    tokens.append((Token, '\u25cb ', select_item))

                if pointed_at:
                    tokens.append(('[SetCursorPosition]', ''))

                tokens.append((Token, line_name, select_item))

            tokens.append((Token, '\n'))

            return get_fragments_from_tokens(tokens)

        # prepare the select choices
        for i, choice in enumerate(self.choices):
            append(i, choice)

        tokens.pop()  # Remove last newline.

        return fragment_list_to_text(tokens)

    def get_selected_values(self):
        # get values not labels
        return [c[1] for c in self.choices if not isinstance(c, Separator) and
                c[1] in self.selected_options]

    @property
    def line_count(self):
        return len(self.choices)


bindings = KeyBindings()


def question(message, **kwargs):
    # TODO add bottom-bar (Move up and down to reveal more choices)
    # TODO extract common parts for list, checkbox, rawlist, expand
    # TODO validate
    if 'choices' not in kwargs:
        raise PromptParameterException('choices')

    # this does not implement default, use checked...
    if 'default' in kwargs:
        raise ValueError('Checkbox does not implement \'default\' '
                         'use \'checked\':True\' in choice!')

    choices = kwargs.pop('choices', None)
    validator = setup_simple_validator(kwargs)

    # TODO style defaults on detail level
    style = kwargs.pop('style', default_style)

    inquirer_control = InquirerControl(choices)

    def get_prompt_tokens():
        tokens = [
            (Token.QuestionMark, '?'),
            (Token.Question, ' %s ' % message)
        ]

        if inquirer_control.answered:
            nbr_selected = len(inquirer_control.selected_options)
            if nbr_selected == 0:
                tokens.append((Token.Answer, ' done'))
            elif nbr_selected == 1:
                tokens.append((Token.Answer, ' [%s]' % inquirer_control.selected_options[0]))
            else:
                tokens.append((Token.Answer,
                               ' done (%d selections)' % nbr_selected))
        else:
            tokens.append((Token.Instruction,
                           ' (<up>, <down> to move, <space> to select, <a> '
                           'to toggle, <i> to invert)'))

        return fragment_list_to_text(tokens)

    # assemble layout
    content = HSplit([
        Window(height=Dimension.exact(1), content=FormattedTextControl(get_prompt_tokens)),
        ConditionalContainer(
            Window(
                inquirer_control,
                width=Dimension.exact(43),
                height=Dimension(min=3),
                scroll_offsets=ScrollOffsets(top=1, bottom=1)
            ),
            filter=~IsDone()
        )
    ])

    @bindings.add(Keys.ControlQ, eager=True)
    @bindings.add(Keys.ControlC, eager=True)
    def _(_event):
        _event.app.exit(exception=KeyboardInterrupt)

    @bindings.add(' ', eager=True)
    def toggle(_event):
        pointed_choice = inquirer_control.choices[inquirer_control.pointer_index][1]  # value
        if pointed_choice in inquirer_control.selected_options:
            inquirer_control.selected_options.remove(pointed_choice)
        else:
            inquirer_control.selected_options.append(pointed_choice)

    @bindings.add('i', eager=True)
    def invert(_event):
        inverted_selection = [c[1] for c in inquirer_control.choices if
                              not isinstance(c, Separator) and
                              c[1] not in inquirer_control.selected_options and
                              not c[2]]
        inquirer_control.selected_options = inverted_selection

    @bindings.add('a', eager=True)
    def all(_event):
        all_selected = True  # all choices have been selected
        for c in inquirer_control.choices:
            if not isinstance(c, Separator) and c[1] not in inquirer_control.selected_options and not c[2]:
                # add missing ones
                inquirer_control.selected_options.append(c[1])
                all_selected = False
        if all_selected:
            inquirer_control.selected_options = []

    def _move_cursor_to(offset):
        def _next():
            inquirer_control.pointer_index = ((inquirer_control.pointer_index + offset) % inquirer_control.line_count)

            return inquirer_control.choices[inquirer_control.pointer_index]

        c = _next()
        while isinstance(c, Separator) or c[2]:
            c = _next()

    @bindings.add(Keys.Down, eager=True)
    def move_cursor_down(_event):
        _move_cursor_to(1)

    @bindings.add(Keys.Up, eager=True)
    def move_cursor_up(_event):
        _move_cursor_to(-11)

    @bindings.add(Keys.ControlM, eager=True)  # enter
    def set_answer(event):
        inquirer_control.answered = True
        # TODO use validator
        event.app.future.set_result(inquirer_control.get_selected_values())

    return Application(
        layout=Layout(content),
        key_bindings=bindings,
        mouse_support=kwargs.pop('mouse_support', False),
        style=style
    )
