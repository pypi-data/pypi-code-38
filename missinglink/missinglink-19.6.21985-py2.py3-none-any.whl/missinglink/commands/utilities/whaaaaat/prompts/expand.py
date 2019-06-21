# -*- coding: utf-8 -*-
"""
`expand` type question
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


# custom control based on FormattedTextControl


class InquirerControl(FormattedTextControl):
    def __init__(self, choices, default=None, **kwargs):
        self.pointer_index = 0
        self.answered = False
        self._init_choices(choices, default)
        self._help_active = False  # help is activated via 'h' key
        super(InquirerControl, self).__init__(self._get_choice_tokens, **kwargs)

    def _init_choices(self, choices, default=None):
        # helper to convert from question format to internal format

        self.choices = []  # list (key, name, value)

        if not default:
            default = 'h'

        for i, c in enumerate(choices):
            if isinstance(c, Separator):
                self.choices.append(c)
            else:
                if isinstance(c, six.string_types):
                    self.choices.append((key, c, c))
                else:
                    key = c.get('key')
                    name = c.get('name')
                    value = c.get('value', name)
                    if default and default == key:
                        self.pointer_index = i
                        key = key.upper()  # default key is in uppercase
                    self.choices.append((key, name, value))
        # append the help choice
        key = 'h'
        if not default:
            self.pointer_index = len(self.choices)
            key = key.upper()  # default key is in uppercase

        self.choices.append((key, 'Help, list all options', None))

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choice_tokens(self):
        tokens = []

        def _append(index, line):
            if isinstance(line, Separator):
                tokens.append((Token.Separator, '   %s\n' % line))
            else:
                key = line[0]
                line = line[1]
                pointed_at = (index == self.pointer_index)

                if pointed_at:
                    tokens.append((Token.Selected, '  %s) %s' % (key, line)))
                else:
                    tokens.append((Token, '  %s) %s' % (key, line)))

                tokens.append((Token, '\n'))

        if self._help_active:
            # prepare the select choices
            for i, choice in enumerate(self.choices):
                _append(i, choice)
            tokens.append((Token, '  Answer: %s' % self.choices[self.pointer_index][0]))
        else:
            tokens.append((Token.Pointer, '>> '))
            tokens.append((Token, self.choices[self.pointer_index][1]))

        return get_fragments_from_tokens(tokens)

    def get_selected_value(self):
        # get value not label
        return self.choices[self.pointer_index][2]


binding = KeyBindings()


def question(message, **kwargs):
    # TODO extract common parts for list, checkbox, rawlist, expand
    # TODO up, down navigation
    if 'choices' not in kwargs:
        raise PromptParameterException('choices')

    choices = kwargs.pop('choices', None)
    default = kwargs.pop('default', None)

    # TODO style defaults on detail level
    style = kwargs.pop('style', default_style)

    ic = InquirerControl(choices, default)

    def get_prompt_tokens():
        tokens = [(Token.QuestionMark, '?'), (Token.Question, ' %s ' % message)]

        if not ic.answered:
            tokens.append((Token.Instruction, ' (%s)' % ''.join(
                [k[0] for k in ic.choices if not isinstance(k, Separator)])))
        else:
            tokens.append((Token.Answer, ' %s' % ic.get_selected_value()))

        return get_fragments_from_tokens(tokens)

    # assemble layout
    content = HSplit([
        Window(
            height=D.exact(1),
            content=FormattedTextControl(get_prompt_tokens)),
        ConditionalContainer(
            Window(ic),
            # filter=is_help_active & ~IsDone()  # ~ bitwise inverse
            filter=~IsDone()  # ~ bitwise inverse
        )
    ])

    @binding.add(Keys.ControlQ, eager=True)
    @binding.add(Keys.ControlC, eager=True)
    def _(_event):
        _event.app.exit(exception=KeyboardInterrupt)

    def create_reg_binding(keys, index):
        def wrap():
            @binding.add(keys, eager=True)
            def select_choice(_event):
                ic.pointer_index = index

        wrap()

    # add key bindings for choices
    for i, c in enumerate(ic.choices):
        if isinstance(c, Separator):
            continue

        if c[0] not in ['h', 'H']:
            create_reg_binding(c[0], i)
            if c[0].isupper():
                create_reg_binding(c[0].lower(), i)

    @binding.add('H', eager=True)
    @binding.add('h', eager=True)
    def help_choice(_event):
        ic._help_active = True

    @binding.add(Keys.ControlM, eager=True)  # enter
    def set_answer(event):
        ic.answered = True
        event.app.future.set_result(ic.get_selected_value())

    return Application(
        layout=Layout(content),
        key_bindings=binding,
        mouse_support=kwargs.pop('mouse_support', False),
        style=style
    )
