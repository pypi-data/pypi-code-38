# -*- coding: utf-8 -*-
"""
`rawlist` type question
"""
import six
from ..prompt_toolkit.application import Application
from ..prompt_toolkit.key_binding import KeyBindings
from ..prompt_toolkit.keys import Keys
from ..prompt_toolkit.layout import Layout
from ..prompt_toolkit.layout.containers import Window
from ..prompt_toolkit.filters import IsDone
from ..prompt_toolkit.layout.controls import FormattedTextControl
from ..prompt_toolkit.layout.containers import ConditionalContainer, HSplit
from ..prompt_toolkit.layout.dimension import LayoutDimension as D
from pygments.token import Token

from .. import PromptParameterException, get_fragments_from_tokens
from ..separator import Separator
from .common import default_style
from .common import if_mouse_down


# custom control based on TokenListControl

class InquirerControl(FormattedTextControl):
    def __init__(self, choices, **kwargs):
        self.pointer_index = 0
        self.answered = False
        self._init_choices(choices)
        super(InquirerControl, self).__init__(self._get_choice_tokens,
                                              **kwargs)

    def _init_choices(self, choices):
        # helper to convert from question format to internal format
        self.choices = []  # list (key, name, value)
        searching_first_choice = True
        key = 1  # used for numeric keys
        for i, c in enumerate(choices):
            if isinstance(c, Separator):
                self.choices.append(c)
            else:
                if isinstance(c, six.string_types):
                    self.choices.append((key, c, c))
                    key += 1
                if searching_first_choice:
                    self.pointer_index = i  # found the first choice
                    searching_first_choice = False

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choice_tokens(self):
        tokens = []
        T = Token

        def _append(index, line):
            if isinstance(line, Separator):
                tokens.append((T.Separator, '   %s\n' % line))
            else:
                key = line[0]
                line = line[1]
                pointed_at = (index == self.pointer_index)

                @if_mouse_down
                def select_item(mouse_event):
                    # bind option with this index to mouse event
                    self.pointer_index = index

                if pointed_at:
                    tokens.append((T.Selected, '  %d) %s' % (key, line), select_item))
                else:
                    tokens.append((T, '  %d) %s' % (key, line), select_item))

                tokens.append((T, '\n'))

        # prepare the select choices
        for i, choice in enumerate(self.choices):
            _append(i, choice)
        tokens.append((T, '  Answer: %d' % self.choices[self.pointer_index][0]))

        return get_fragments_from_tokens(tokens)

    def get_selected_value(self):
        # get value not label
        return self.choices[self.pointer_index][2]


binding = KeyBindings()


def question(message, **kwargs):
    # TODO extract common parts for list, checkbox, rawlist, expand
    if 'choices' not in kwargs:
        raise PromptParameterException('choices')
    # this does not implement default, use checked...
    # TODO
    # if 'default' in kwargs:
    #    raise ValueError('rawlist does not implement \'default\' '
    #                     'use \'checked\':True\' in choice!')

    choices = kwargs.pop('choices', None)
    if len(choices) > 9:
        raise ValueError('rawlist supports only a maximum of 9 choices!')

    # TODO style defaults on detail level
    style = kwargs.pop('style', default_style)

    inquirer_control = InquirerControl(choices)

    def get_prompt_tokens():
        tokens = []
        T = Token

        tokens.append((T.QuestionMark, '?'))
        tokens.append((T.Question, ' %s ' % message))
        if inquirer_control.answered:
            tokens.append((T.Answer, ' %s' % inquirer_control.get_selected_value()))

        return get_fragments_from_tokens(tokens)

    # assemble layout
    content = HSplit([
        Window(
            height=D.exact(1),
            content=FormattedTextControl(get_prompt_tokens)),
        ConditionalContainer(
            Window(inquirer_control),
            filter=~IsDone())
    ])

    @binding.add(Keys.ControlQ, eager=True)
    @binding.add(Keys.ControlC, eager=True)
    def _(_event):
        _event.app.exit(exception=KeyboardInterrupt)

    # add key bindings for choices
    for i, c in enumerate(inquirer_control.choices):
        if not isinstance(c, Separator):
            def _reg_binding(i, keys):
                # trick out late evaluation with a "function factory":
                # http://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
                @binding.add(keys, eager=True)
                def select_choice(event):
                    inquirer_control.pointer_index = i
            _reg_binding(i, '%d' % c[0])

    @binding.add(Keys.ControlM, eager=True)  # enter
    def set_answer(event):
        inquirer_control.answered = True
        event.cli.future.set_result(inquirer_control.get_selected_value())

    return Application(
        layout=Layout(content),
        key_bindings=binding,
        mouse_support=kwargs.pop('mouse_support', False),
        style=style
    )
