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


def select_snippet(snippets):
    snippet_searcher = SnippetSearcher(snippets)
    session = SplitPromptSession()
    prompt_content = session.prompt(HTML('> '), completer=snippet_searcher)
    text, _ = SnippetSearcher.parse_group_filters(prompt_content)
    for snippet in snippets:
        if snippet_searcher.match(snippet, text):
            return snippet
    return None


def fill_template(content):
    offset = 0
    for match in re.finditer(r'<\$>', content):
        span = match.span()
        start_pos = span[0] + offset
        end_pos = span[1] + offset
        pre = content[0:start_pos]
        post = content[end_pos:]
        formatted_text = [('fg:white', pre), ('fg:green', '_____'), ('fg:white', post + ': ')]
        answer = prompt(formatted_text)
        offset += len(answer) - len('<$>')
        content = content.replace('<$>', answer, 1)
    return content


def confirm(msg):
    print_formatted_text(HTML('<red><b>{}</b></red>'.format(msg)))
    answer = prompt('[yes/no]: ')
    return answer.lower() == 'yes'


class SplitPromptSession(PromptSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bottom_toolbar = self.update_toolbar_text

    def _create_layout(self):
        _, get_prompt_text_1, get_prompt_text_2 = \
            _split_multiline_prompt(self._get_prompt)

        default_buffer = self.default_buffer

        default_buffer_control = BufferControl(
            buffer=default_buffer,
            search_buffer_control=None,
            input_processors=[],
            include_default_input_processors=False)

        prompt_window = Window(FormattedTextControl(get_prompt_text_1),
                               dont_extend_height=True)
        default_buffer_window = Window(
            default_buffer_control,
            dont_extend_height=True,
            get_line_prefix=partial(
                self._get_line_prefix, get_prompt_text_2=get_prompt_text_2))
        divider = Window(char='_', height=1, style='fg:gray bg:black')
        search_window = Window(content=SearchControl(),
                               style='')
        bottom_toolbar = ConditionalContainer(
            Window(FormattedTextControl(lambda: self.bottom_toolbar),
                   dont_extend_height=True,
                   height=Dimension(min=1)),
            filter=(~is_done & renderer_height_is_known
                    & Condition(lambda: self.bottom_toolbar is not None)))

        layout = HSplit([
            prompt_window,
            default_buffer_window,
            divider,
            search_window,
            bottom_toolbar
        ])

        return Layout(layout, default_buffer_window)

    def _create_application(self, editing_mode, erase_when_done):

        prompt_bindings = self._create_prompt_bindings()
        search_mode_bindings = self._create_search_mode_bindings()

        application = Application(
            layout=self.layout,
            full_screen=True,
            key_bindings=merge_key_bindings([
                merge_key_bindings([
                    search_mode_bindings,
                    prompt_bindings
                ]),
            ]),
            color_depth=lambda: self.color_depth,
            input=self.input,
            output=self.output)

        return application


    def _create_search_mode_bindings(self):
        key_bindings = KeyBindings()
        handle = key_bindings.add
        default_focused = has_focus(DEFAULT_BUFFER)

        @handle('c-w', filter=default_focused)
        def _(event):
            buf = event.current_buffer
            self.completer.toggle_search_mode()
            buf.complete_state = None
            buf.start_completion()
            self.update_toolbar_text()
        return key_bindings

    def update_toolbar_text(self):
        toolbar_text = []
        for search_mode in self.completer.SEARCH_MODES.keys():
            if search_mode == self.completer.search_mode:
                style_class = 'fg:green'
            else:
                style_class = 'fg:gray'
            toolbar_text.append((style_class, search_mode))
            toolbar_text.append(('fg:gray', '  |  '))
        toolbar_text.append(('fg:gray', '(ctrl+w to toggle)'))
        return toolbar_text
