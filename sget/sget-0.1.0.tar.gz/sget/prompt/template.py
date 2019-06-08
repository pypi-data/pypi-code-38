from functools import partial
import re


from prompt_toolkit.shortcuts import prompt, PromptSession
from prompt_toolkit.shortcuts.prompt import _split_multiline_prompt
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings, KeyBindings
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.filters import has_focus, is_done, Condition, renderer_height_is_known

from sget.prompt.search import SnippetSearcher, SearchControl


def fill_template(content, variables):
    session = TemplatePromptSession(content, variables)
    prompt_content = session.prompt()
    return prompt_content


class TemplatePromptSession(PromptSession):
    def __init__(self, content, variables, *args, **kwargs):
        self._orig_content = content
        self._orig_variables = variables
        super().__init__(*args, **kwargs)

    def _create_layout(self):

        default_buffer = self.default_buffer

        default_buffer_control = BufferControl(
            buffer=default_buffer,
            search_buffer_control=None,
            input_processors=[],
            include_default_input_processors=False)

        prompt_window = Window(FormattedTextControl(self._orig_content),
                               height=1,
                               dont_extend_height=True)
        return Layout(prompt_window, prompt_window)

    def _create_application(self, editing_mode, erase_when_done):

        prompt_bindings = self._create_prompt_bindings()

        application = Application(
            layout=self.layout,
            full_screen=False,
            key_bindings=prompt_bindings,
            color_depth=lambda: self.color_depth,
            input=self.input,
            output=self.output)

        return application
